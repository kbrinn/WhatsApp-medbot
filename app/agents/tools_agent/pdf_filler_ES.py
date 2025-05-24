"""
Ligero helper que recorre un objeto HistorialPaciente (o diccionario), hace
coincidir sus llaves con los campos de un formulario AcroForm, escribe texto
o marca casillas y devuelve la ruta absoluta del PDF generado.

Cambios mínimos para soportar formularios en español:
1.  Ampliamos los valores que se interpretan como «sí» en casillas
    (incluimos “si” y “sí”).
2.  Nada más se modifica: los nombres de campo siguen derivándose del
    atributo/clave, así que mientras tu plantilla PDF use los mismos nombres
    en español no hace falta mapeo adicional.
"""

from dataclasses import is_dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, Union

from pdfrw import PdfName, PdfObject, PdfReader, PdfString, PdfWriter

# --------------------------------------------------------------------------- #
# 1) Tokens que activan una casilla: True/Yes/1 y sus equivalentes en español
YES_TOKENS = {
    "true",
    "yes",
    "1",
    "si",
    "sí",
    "sí",
}  # la última es “sí” con tilde combinada
# --------------------------------------------------------------------------- #

# Paths relative to this module
_MODULE_DIR = Path(__file__).resolve().parent
_DEFAULT_TEMPLATE = _MODULE_DIR / "template_forms" / "intake_form_EN.pdf"
_DEFAULT_OUTPUT = (
    _MODULE_DIR.parent.parent
    / "services"
    / "database"
    / "data"
    / "intake_filled_ES.pdf"
)


def _walk_fields(obj: Union[Dict[str, Any], Any], prefix: str = ""):
    """Produce pares (nombre_campo_pdf, valor_str) para valores primitivos."""
    if is_dataclass(obj) or hasattr(obj, "__dict__"):
        items = obj.__dict__.items()
    elif isinstance(obj, dict):
        items = obj.items()
    else:
        return

    for k, v in items:
        key = f"{prefix}{k}"
        if v in (None, [], {}):
            continue
        if isinstance(v, (str, int, float, bool, date)):
            yield key, str(v)
        elif isinstance(v, list):
            yield key, ", ".join(map(str, v))
        else:
            yield from _walk_fields(v, prefix=f"{key}.")


def fill_pdf(
    patient_obj: Union[Dict[str, Any], "HistorialPaciente"],
    template_path: Union[str, Path] | None = None,
    output_path: Union[str, Path] | None = None,
) -> str:
    """Llena la plantilla indicada con los datos de ``patient_obj``."""
    template = Path(template_path) if template_path else _DEFAULT_TEMPLATE
    output = Path(output_path) if output_path else _DEFAULT_OUTPUT

    output.parent.mkdir(parents=True, exist_ok=True)

    pdf = PdfReader(str(template))
    pdf.Root.NeedAppearances = PdfObject("true")

    annotations = {
        annot.T[1:-1]: annot
        for page in pdf.pages
        for annot in (page.Annots or [])
        if annot.Subtype == "/Widget" and annot.T
    }

    for field, value in _walk_fields(patient_obj):
        annot = annotations.get(field)
        if not annot:
            continue

        # --- Casillas de verificación ---
        if annot.FT == "/Btn":
            if str(value).lower() in YES_TOKENS:
                annot.V = annot.AS = PdfName("Yes")
            else:
                annot.V = annot.AS = PdfName("Off")
            continue

        # --- Campos de texto ---
        annot.V = PdfString.encode(str(value))
        annot.AP = None

    PdfWriter().write(str(output), pdf)
    return str(output.resolve())
