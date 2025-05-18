# Security Approach

This project avoids storing protected health information (PHI) directly in the database.
Instead of persisting the raw message and response text, the application writes those
values to a protected storage service (implemented locally as a JSON file).  A unique
reference ID for the stored entry is saved in the `message` and `response` columns of
the `conversations` table.  This keeps the database free of PHI while still allowing
conversations to be looked up if needed.

The protected storage logic lives in `app/services/secure_storage.py`.
