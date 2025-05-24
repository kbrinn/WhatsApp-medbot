"""
Light-weight helper that walks a PatientHistory object (or plain dict),
matches keys to AcroForm fields, writes text or toggles check-boxes, and
returns the absolute path of the filled PDF.
"""

from datetime import date
from pathlib import Path
from typing import Any, Dict, Union, TYPE_CHECKING

from dataclasses import is_dataclass
from pdfrw import (
    PdfReader,
    PdfWriter,
    PdfDict,
    PdfName,
    PdfString,
    PdfObject,
)

# ──────────────────────────────────────────────────────────────────────────────
# NEW: import the Pydantic model at runtime so type-hint resolution succeeds
# ──────────────────────────────────────────────────────────────────────────────
from ..schemas.patient_form_EN import PatientHistory  # ← added

# (You can now drop the TYPE_CHECKING block entirely, but it won’t hurt if it stays)


# --------------------------------------------------------------------------- #
# Internal helper – flattens nested objects to ("dot.notation", "value") pairs
# --------------------------------------------------------------------------- #
def _walk_fields(obj: Union[Dict[str, Any], Any], prefix: str = ""):
    """Yield (pdf_field_name, str_value) for primitives inside obj."""
    # Accept dataclass / Pydantic model / plain dict
    if is_dataclass(obj) or hasattr(obj, "__dict__"):
        items = obj.__dict__.items()
    elif isinstance(obj, dict):
        items = obj.items()
    else:
        return                            # unsupported leaf

    for k, v in items:
        key = f"{prefix}{k}"
        if v in (None, [], {}):
            continue                      # skip empty
        if isinstance(v, (str, int, float, bool, date)):
            yield key, str(v)
        elif isinstance(v, list):
            # join lists nicely (comma-space); change to '\n'.join(...) if needed
            yield key, ", ".join(map(str, v))
        else:
            yield from _walk_fields(v, prefix=f"{key}.")


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def fill_pdf(
    patient_obj: Union[Dict[str, Any], PatientHistory],  # ← use the real class
    template_path: str = "app/agents/tools_agent/template_forms/intake_form_EN.pdf",
    output_path: str = "app/services/database/data/intake_filled.pdf",
) -> str:
    """Fill the intake template with `patient_obj` and write `output_path`."""
    pdf = PdfReader(template_path)

    # Ensure viewers regenerate appearances for edited fields
    pdf.Root.NeedAppearances = PdfObject("true")

    # Build a quick lookup: field-name → annotation object
    annotations = {
        annot.T[1:-1]: annot               # strip the surrounding parentheses
        for page in pdf.pages
        for annot in (page.Annots or [])
        if annot.Subtype == "/Widget" and annot.T
    }

    # Walk the patient data and push values into matching annotations
    for field, value in _walk_fields(patient_obj):
        annot = annotations.get(field)
        if not annot:
            continue                       # template has no such field

        # Check-box handling
        if annot.FT == "/Btn":             # button == check/radio
            yes = PdfName("Yes")
            if str(value).lower() in ("true", "yes", "1"):
                annot.V  = yes
                annot.AS = yes
            else:
                annot.V  = PdfName("Off")
                annot.AS = PdfName("Off")
            continue

        # Text fields
        annot.V  = PdfString.encode(str(value))
        annot.AP = None                    # let the viewer rebuild appearance

    PdfWriter().write(output_path, pdf)
    return str(Path(output_path).resolve())