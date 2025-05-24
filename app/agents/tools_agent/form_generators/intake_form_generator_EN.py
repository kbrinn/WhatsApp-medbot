from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors

def create_intake_template_a4_styled_v3(path="/mnt/data/intake_template_a4_styled_v3.pdf"):
    PAGE_WIDTH, PAGE_HEIGHT = A4
    margin = 20 * mm
    label_font = ("Helvetica", 9)
    heading_font = ("Helvetica-Bold", 11.5)
    bar_color = colors.HexColor("#0078b6")
    bar_height = 18
    x_label = margin
    label_to_field_gap = 2 * mm  # horizontal distance
    x_field = margin + 70 * mm
    field_width_default = PAGE_WIDTH - x_field - margin
    checkbox_size = 10
    line_gap = 12

    c = canvas.Canvas(path, pagesize=A4)
    width, height = PAGE_WIDTH, PAGE_HEIGHT
    page_num = 1
    y = height - margin

    def footer():
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(width / 2, margin / 2.2, f"Page {page_num}")

    def new_page():
        nonlocal y, page_num
        footer()
        c.showPage()
        page_num += 1
        y = height - margin
        c.setFont(*label_font)

    def ensure_space(req=0):
        nonlocal y
        if y - req < margin + 50:
            new_page()

    def add_header(text):
        nonlocal y
        ensure_space(bar_height + line_gap)
        c.setFillColor(bar_color)
        c.rect(margin, y - bar_height, width - 2 * margin, bar_height, stroke=0, fill=1)
        c.setFont(*heading_font)
        c.setFillColor(colors.white)
        c.drawString(margin + 4, y - bar_height + (bar_height / 2) - 4, text.upper())
        # Reset
        c.setFillColor(colors.black)
        y -= bar_height + line_gap
        c.setFont(*label_font)

    def add_field(label, name, h=12, multiline=False):
        nonlocal y
        ensure_space(h + line_gap)
        c.drawString(x_label, y, label)
        field_bottom = y - h - 2  # place field completely below label baseline
        c.acroForm.textfield(
            name=name,
            tooltip=label,
            x=x_field,
            y=field_bottom,
            width=field_width_default,
            height=h,
            borderStyle="solid",
            borderWidth=0.5,
            borderColor=colors.darkgrey,
            fillColor=colors.whitesmoke,
            forceBorder=True,
            fieldFlags="multiline" if multiline else ""
        )
        y -= h + line_gap

    def add_checkbox(label, name):
        nonlocal y
        ensure_space(line_gap)
        c.drawString(x_label, y, label)
        box_bottom = y - checkbox_size + 2  # align roughly with label baseline
        c.acroForm.checkbox(
            name=name,
            tooltip=label,
            x=x_field,
            y=box_bottom,
            size=checkbox_size,
            borderWidth=0.5,
            borderColor=colors.darkgrey,
            fillColor=colors.white,
        )
        y -= line_gap

    # Begin content
    c.setFont(*label_font)

    # PATIENT DEMOGRAPHICS
    add_header("Patient Demographics")
    for lbl, nm in [
        ("Full Name:", "name"),
        ("Date of Birth (YYYY-MM-DD):", "dob"),
        ("Sex/Gender:", "sex"),
        ("Address:", "address"),
        ("Phone Number:", "phone_number"),
        ("Email:", "email_address"),
    ]:
        add_field(lbl, nm)

    # EMERGENCY CONTACT & PCP
    add_header("Emergency Contact & PCP")
    for lbl, nm in [
        ("EC Name:", "emergency_contact.name"),
        ("EC Phone:", "emergency_contact.phone_number"),
        ("Primary Care Physician:", "primary_care_physician"),
    ]:
        add_field(lbl, nm)

    # VISIT DETAILS
    add_header("Visit Details")
    add_field("Reason for visit:", "reason_for_visit")
    add_field("Duration of concern:", "duration_of_concern")
    add_field("Symptoms description:", "symptoms_description", h=45, multiline=True)

    # MEDICAL HISTORY & MEDICATIONS
    add_header("Medical History & Medications")
    mh_fields = [
        ("Pre‑existing conditions:", "pre_conditions", 40),
        ("Surgeries / Hospitalizations:", "surgeries_or_hospitalizations", 40),
        ("Serious injuries or accidents:", "serious_injuries_or_accidents", 35),
        ("Current prescriptions:", "prescriptions", 40),
        ("Supplements:", "supplements", 35),
        ("Alternative medicine:", "alternative_medicine", 35),
        ("Medication allergies:", "allergies_medications", 35),
        ("Food allergies:", "allergies_foods", 35),
        ("Environmental allergies:", "allergies_environment", 35),
        ("Infectious diseases:", "infectious_diseases", 35),
    ]
    for lbl, nm, height_box in mh_fields:
        add_field(lbl, nm, h=height_box, multiline=True)

    # FAMILY HISTORY
    add_header("Family History")
    for lbl, nm in [
        ("Heart disease", "family_history_heart_disease"),
        ("Diabetes", "family_history_diabetes"),
        ("High blood pressure", "family_history_high_blood_pressure"),
        ("Stroke", "family_history_stroke"),
        ("Mental health conditions", "family_history_mental_health"),
    ]:
        add_checkbox(lbl, nm)
    for lbl, nm in [
        ("Cancer (type):", "family_history_cancer"),
        ("Other:", "family_history_other"),
    ]:
        add_field(lbl, nm)

    # RECENT EXAMS & VACCINATIONS
    add_header("Recent Exams & Vaccinations")
    for lbl, nm in [
        ("Last physical exam:", "last_physical_exam"),
        ("Last blood test:", "last_blood_test"),
        ("Last major vaccination:", "last_vaccination"),
    ]:
        add_field(lbl, nm)

    # LIFESTYLE
    add_header("Lifestyle")
    lifestyle_items = [
        ("Smoke tobacco", "lifestyle.smoke_tobacco", "cb"),
        ("Tobacco quantity/day:", "lifestyle.tobacco_quantity_per_day", "txt"),
        ("Tobacco duration (yrs):", "lifestyle.tobacco_duration_years", "txt"),
        ("Drink alcohol", "lifestyle.drink_alcohol", "cb"),
        ("Drinks per week:", "lifestyle.alcohol_drinks_per_week", "txt"),
        ("Use recreational drugs", "lifestyle.recreational_drugs", "cb"),
        ("Drug type & frequency:", "lifestyle.drug_type_and_frequency", "txt"),
    ]
    for lbl, nm, typ in lifestyle_items:
        if typ == "cb":
            add_checkbox(lbl, nm)
        else:
            add_field(lbl, nm)
    for lbl, nm in [
        ("Exercise habits:", "lifestyle.exercise_habits"),
        ("Diet description:", "lifestyle.diet_description"),
    ]:
        add_field(lbl, nm, h=40, multiline=True)

    # WOMEN'S HEALTH
    add_header("Women's Health")
    add_field("Last menstrual period:", "woman_health.last_menstrual_period")
    add_checkbox("Pregnant or possibly pregnant", "woman_health.pregnant_or_possibly_pregnant")
    add_field("Last mammogram / Pap smear:", "woman_health.last_mammogram_pap_smear")

    # REVIEW OF SYSTEMS
    add_header("Review of Systems")
    ros_items = [
        ("Fever or chills", "review_of_systems.fever_or_chills"),
        ("Fatigue or weakness", "review_of_systems.fatigue_or_weakness"),
        ("Weight loss or gain", "review_of_systems.weight_loss_or_gain"),
        ("Chest pain", "review_of_systems.chest_pain"),
        ("Shortness of breath", "review_of_systems.shortness_of_breath"),
        ("Cough", "review_of_systems.cough"),
        ("Headache", "review_of_systems.headache"),
        ("Vision changes", "review_of_systems.vision_changes"),
        ("Hearing changes", "review_of_systems.hearing_changes"),
        ("Abdominal pain", "review_of_systems.abdominal_pain"),
        ("Nausea or vomiting", "review_of_systems.nausea_or_vomiting"),
        ("Joint pain", "review_of_systems.joint_pain"),
        ("Skin rashes", "review_of_systems.skin_rashes"),
        ("Dizziness or fainting", "review_of_systems.dizziness_or_fainting"),
        ("Mood changes", "review_of_systems.mood_changes"),
    ]
    for lbl, nm in ros_items:
        add_checkbox(lbl, nm)
    add_field("Other symptoms:", "review_of_systems.other_symptoms", h=40, multiline=True)

    # ADDITIONAL COMMENTS & RED FLAGS
    add_header("Additional Comments & Red Flags")
    add_field("Additional comments:", "additional_comments", h=50, multiline=True)
    add_field("Red flags for MD review:", "red_flags", h=50, multiline=True)

    # SIGNATURE
    add_header("Signature")
    add_field("Signature:", "signature")
    add_field("Signature Date (YYYY-MM-DD):", "signature_date")

    footer()
    c.save()
    return path

# Generate the PDF
pdf_path = create_intake_template_a4_styled_v3()
pdf_path
