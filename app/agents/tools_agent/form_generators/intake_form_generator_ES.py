from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors


def crear_plantilla_intake_a4_es(
    path: str = "/mnt/data/intake_template_a4_es.pdf",
) -> str:
    """
    Genera un formulario PDF de ingreso médico en español (México) cuyas
    llaves de campo coinciden con el modelo `HistorialPaciente`.
    """
    # Métricas y estilos básicos
    PAGE_WIDTH, PAGE_HEIGHT = A4
    margin = 20 * mm
    label_font = ("Helvetica", 9)
    heading_font = ("Helvetica-Bold", 11.5)
    bar_color = colors.HexColor("#0078b6")
    bar_height = 18

    x_label = margin
    x_field = margin + 70 * mm
    field_width_default = PAGE_WIDTH - x_field - margin
    checkbox_size = 10
    line_gap = 12

    c = canvas.Canvas(path, pagesize=A4)
    width, height = PAGE_WIDTH, PAGE_HEIGHT
    page_num = 1
    y = height - margin

    # ----------------------------------------------------------- utilidades --
    def footer():
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(width / 2, margin / 2.2, f"Página {page_num}")

    def new_page():
        nonlocal y, page_num
        footer()
        c.showPage()
        page_num += 1
        y = height - margin
        c.setFont(*label_font)

    def ensure_space(req: int = 0):
        """Salta a nueva página si el espacio restante es insuficiente."""
        nonlocal y
        if y - req < margin + 50:
            new_page()

    def add_header(text: str):
        """Barra azul y título de sección."""
        nonlocal y
        ensure_space(bar_height + line_gap)
        c.setFillColor(bar_color)
        c.rect(margin, y - bar_height, width - 2 * margin,
               bar_height, stroke=0, fill=1)
        c.setFont(*heading_font)
        c.setFillColor(colors.white)
        c.drawString(margin + 4,
                     y - bar_height + (bar_height / 2) - 4,
                     text.upper())
        c.setFillColor(colors.black)
        y -= bar_height + line_gap
        c.setFont(*label_font)

    def add_field(label: str, name: str, h: int = 12, multiline: bool = False):
        """Crea un campo de texto."""
        nonlocal y
        ensure_space(h + line_gap)
        c.drawString(x_label, y, label)
        field_bottom = y - h - 2
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
            fieldFlags="multiline" if multiline else "",
        )
        y -= h + line_gap

    def add_checkbox(label: str, name: str):
        """Crea una casilla de verificación."""
        nonlocal y
        ensure_space(line_gap)
        c.drawString(x_label, y, label)
        box_bottom = y - checkbox_size + 2
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

    # ---------------------------------------------------------- contenido ----
    c.setFont(*label_font)

    # DATOS DEL PACIENTE
    add_header("Datos del Paciente")
    for lbl, nm in [
        ("Nombre completo:", "nombre"),
        ("Fecha de nacimiento (AAAA-MM-DD):", "fecha_nacimiento"),
        ("Sexo / Género:", "sexo"),
        ("Dirección:", "direccion"),
        ("Teléfono:", "telefono"),
        ("Correo electrónico:", "correo_electronico"),
    ]:
        add_field(lbl, nm)

    # CONTACTO DE EMERGENCIA Y MÉDICO
    add_header("Contacto de Emergencia y Médico")
    for lbl, nm in [
        ("Nombre contacto de emergencia:", "contacto_emergencia.nombre"),
        ("Teléfono contacto de emergencia:", "contacto_emergencia.telefono"),
        ("Médico de cabecera:", "medico_cabecera"),
    ]:
        add_field(lbl, nm)

    # MOTIVO DE CONSULTA
    add_header("Motivo de Consulta")
    add_field("Motivo de consulta:", "motivo_consulta")
    add_field("Duración del malestar:", "duracion_malestar")
    add_field("Descripción de síntomas:", "descripcion_sintomas",
              h=45, multiline=True)

    # HISTORIAL MÉDICO Y MEDICAMENTOS
    add_header("Historial Médico y Medicamentos")
    mh_fields = [
        ("Condiciones previas:", "condiciones_previas", 40),
        ("Cirugías / Hospitalizaciones:",
         "cirugias_hospitalizaciones", 40),
        ("Lesiones o accidentes graves:",
         "lesiones_accidentes_graves", 35),
        ("Medicamentos recetados:", "medicamentos_recetados", 40),
        ("Suplementos:", "suplementos", 35),
        ("Medicina alternativa:", "medicina_alternativa", 35),
        ("Alergias a medicamentos:", "alergias_medicamentos", 35),
        ("Alergias alimentarias:", "alergias_alimentos", 35),
        ("Alergias ambientales:", "alergias_ambientales", 35),
        ("Enfermedades infecciosas:", "enfermedades_infecciosas", 35),
    ]
    for lbl, nm, h_box in mh_fields:
        add_field(lbl, nm, h=h_box, multiline=True)

    # ANTECEDENTES FAMILIARES
    add_header("Antecedentes Familiares")
    for lbl, nm in [
        ("Enfermedad cardíaca", "antecedentes_familiares_cardiacos"),
        ("Diabetes", "antecedentes_familiares_diabetes"),
        ("Hipertensión", "antecedentes_familiares_hipertension"),
        ("Embolia / Derrame", "antecedentes_familiares_embolia"),
        ("Trastornos de salud mental",
         "antecedentes_familiares_salud_mental"),
    ]:
        add_checkbox(lbl, nm)
    for lbl, nm in [
        ("Cáncer (tipo):", "antecedentes_familiares_cancer"),
        ("Otros:", "antecedentes_familiares_otros"),
    ]:
        add_field(lbl, nm)

    # EXÁMENES Y VACUNAS
    add_header("Exámenes y Vacunas")
    for lbl, nm in [
        ("Último examen físico:", "ultimo_examen_fisico"),
        ("Último análisis de sangre:", "ultimo_examen_sangre"),
        ("Última vacunación importante:", "ultima_vacunacion"),
    ]:
        add_field(lbl, nm)

    # ESTILO DE VIDA
    add_header("Estilo de Vida")
    lifestyle_items = [
        ("Fuma tabaco", "estilo_vida.fuma_tabaco", "cb"),
        ("Cantidad tabaco/día:",
         "estilo_vida.cantidad_tabaco_por_dia", "txt"),
        ("Años fumando:", "estilo_vida.anos_fumando", "txt"),
        ("Consume alcohol", "estilo_vida.consume_alcohol", "cb"),
        ("Bebidas alcohólicas/semana:",
         "estilo_vida.bebidas_alcohol_semana", "txt"),
        ("Usa drogas recreativas",
         "estilo_vida.usa_drogas_recreativas", "cb"),
        ("Tipo y frecuencia de droga:",
         "estilo_vida.tipo_y_frecuencia_droga", "txt"),
    ]
    for lbl, nm, typ in lifestyle_items:
        if typ == "cb":
            add_checkbox(lbl, nm)
        else:
            add_field(lbl, nm)
    for lbl, nm in [
        ("Hábitos de ejercicio:", "estilo_vida.habitos_ejercicio"),
        ("Descripción de la dieta:",
         "estilo_vida.descripcion_dieta"),
    ]:
        add_field(lbl, nm, h=40, multiline=True)

    # SALUD DE LA MUJER
    add_header("Salud de la Mujer")
    add_field("Última menstruación:",
              "salud_mujer.ultima_menstruacion")
    add_checkbox("Embarazada o posiblemente embarazada",
                 "salud_mujer.embarazada_o_posiblemente")
    add_field("Último mamograma / Papanicolaou:",
              "salud_mujer.ultimo_mamograma_papanicolaou")

    # REVISIÓN DE SISTEMAS
    add_header("Revisión de Sistemas")
    for lbl, nm in [
        ("Fiebre o escalofríos",
         "revision_sistemas.fiebre_o_escalofrios"),
        ("Fatiga o debilidad",
         "revision_sistemas.fatiga_o_debilidad"),
        ("Dolor de pecho", "revision_sistemas.dolor_pecho"),
        ("Dificultad para respirar",
         "revision_sistemas.dificultad_respirar"),
        ("Tos", "revision_sistemas.tos"),
        ("Dolor de cabeza", "revision_sistemas.dolor_cabeza"),
        ("Dolor abdominal", "revision_sistemas.dolor_abdominal"),
    ]:
        add_checkbox(lbl, nm)
    add_field("Otros síntomas:",
              "revision_sistemas.otros_sintomas",
              h=40, multiline=True)

    # COMENTARIOS Y BANDERAS ROJAS
    add_header("Comentarios y Banderas Rojas")
    add_field("Comentarios adicionales:",
              "comentarios_adicionales",
              h=50, multiline=True)
    add_field("Banderas rojas para revisión médica:",
              "banderas_rojas",
              h=50, multiline=True)

    # FIRMA
    add_header("Firma")
    add_field("Firma:", "firma")
    add_field("Fecha de firma (AAAA-MM-DD):", "fecha_firma")

    # Pie de página
    footer()
    c.save()
    return path


# Ejecución directa para probar
if __name__ == "__main__":
    ruta = crear_plantilla_intake_a4_es()
    print("PDF generado en:", ruta)
