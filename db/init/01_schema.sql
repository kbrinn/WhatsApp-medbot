-- 01_schema.sql
-- Core schema for MedBot clinic database (single-clinic, single-provider, FHIR‑aligned)
-- NOTE: Replace <<KMS-key-alias>> with your pgcrypto encryption key label or remove encryption if not used.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;
SET TIME ZONE 'UTC';

-- Core tables --------------------------------------------------------------
CREATE TABLE clinic (
    clinic_id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name              TEXT NOT NULL,
    address_json      JSONB NOT NULL,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE provider (
    provider_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id         UUID REFERENCES clinic(clinic_id) ON DELETE CASCADE,
    npi_number        TEXT UNIQUE NOT NULL,
    display_name      TEXT NOT NULL,
    specialty         TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE patient (
    patient_id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name         BYTEA
        DEFAULT pgp_sym_encrypt('', '<<KMS-key-alias>>', 'compress-always'),
    date_of_birth     DATE,
    phone_e164        TEXT UNIQUE,
    email             TEXT UNIQUE,
    address_json      JSONB,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_dob CHECK (date_of_birth <= current_date)
);

COMMENT ON COLUMN patient.full_name IS
'PHI: encrypted using pgcrypto; expose via a SECURITY DEFINER view';

-- FHIR-aligned scheduling --------------------------------------------------
CREATE TABLE schedule (
    schedule_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id       UUID REFERENCES provider(provider_id) ON DELETE CASCADE,
    service_category  TEXT,
    service_type      TEXT,
    period_start      TIMESTAMPTZ NOT NULL,
    period_end        TIMESTAMPTZ NOT NULL,
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_period CHECK (period_end > period_start)
);

CREATE TABLE slot (
    slot_id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schedule_id       UUID REFERENCES schedule(schedule_id) ON DELETE CASCADE,
    start_time        TIMESTAMPTZ NOT NULL,
    end_time          TIMESTAMPTZ NOT NULL,
    status            TEXT NOT NULL CHECK (status IN ('free','busy','reserved','cancelled')),
    service_type      TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (start_time, end_time, schedule_id)
);

CREATE INDEX idx_slot_status_time ON slot(status, start_time);

CREATE TABLE appointment (
    appointment_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slot_id           UUID UNIQUE REFERENCES slot(slot_id) ON DELETE RESTRICT,
    patient_id        UUID REFERENCES patient(patient_id) ON DELETE RESTRICT,
    reason_code       TEXT,
    status            TEXT NOT NULL DEFAULT 'booked'
        CHECK (status IN ('booked','checked_in','fulfilled','no_show','cancelled')),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Wait‑list ----------------------------------------------------------------
CREATE TABLE waitlist_request (
    request_id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id        UUID REFERENCES patient(patient_id) ON DELETE CASCADE,
    desired_from      TIMESTAMPTZ,
    desired_to        TIMESTAMPTZ,
    priority          INTEGER NOT NULL DEFAULT 0,
    requested_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    fulfilled_slot    UUID REFERENCES slot(slot_id),
    fulfilled_at      TIMESTAMPTZ
);

CREATE INDEX idx_waitlist_unfilled ON waitlist_request(fulfilled_at) WHERE fulfilled_at IS NULL;

-- Notification outbox ------------------------------------------------------
CREATE TABLE notification_outbox (
    outbox_id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id        UUID REFERENCES patient(patient_id),
    appointment_id    UUID REFERENCES appointment(appointment_id),
    channel           TEXT NOT NULL CHECK (channel IN ('sms','email')),
    template_name     TEXT NOT NULL,
    payload_json      JSONB NOT NULL,
    send_after        TIMESTAMPTZ NOT NULL,
    sent_at           TIMESTAMPTZ,
    status            TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','sent','failed')),
    retry_count       SMALLINT NOT NULL DEFAULT 0,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Audit log ----------------------------------------------------------------
CREATE TABLE audit_log (
    audit_id          BIGSERIAL PRIMARY KEY,
    table_name        TEXT NOT NULL,
    record_id         UUID,
    action            TEXT NOT NULL,
    changed_by        TEXT NOT NULL DEFAULT current_user,
    changed_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    diff_json         JSONB NOT NULL
);

CREATE OR REPLACE FUNCTION fn_audit_trigger() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log(table_name, record_id, action, diff_json)
        VALUES (TG_TABLE_NAME, NEW.*::json->>'id', 'INSERT', to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log(table_name, record_id, action, diff_json)
        VALUES (TG_TABLE_NAME, OLD.*::json->>'id', 'DELETE', to_jsonb(OLD));
        RETURN OLD;
    ELSE
        INSERT INTO audit_log(table_name, record_id, action, diff_json)
        VALUES (TG_TABLE_NAME, NEW.*::json->>'id', 'UPDATE',
                jsonb_strip_nulls(to_jsonb(NEW) - to_jsonb(OLD)));
        RETURN NEW;
    END IF;
END; $$;

CREATE TRIGGER trg_patient_audit
AFTER INSERT OR UPDATE OR DELETE ON patient
FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

CREATE TRIGGER trg_appointment_audit
AFTER INSERT OR UPDATE OR DELETE ON appointment
FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

-- Row‑level security stubs --------------------------------------------------
ALTER TABLE patient ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointment ENABLE ROW LEVEL SECURITY;

CREATE POLICY patient_app_select ON patient
    FOR SELECT USING (true); -- Placeholder: replace with your policy
CREATE POLICY patient_app_insert ON patient
    FOR INSERT WITH CHECK (true);
CREATE POLICY patient_app_update ON patient
    FOR UPDATE USING (true);