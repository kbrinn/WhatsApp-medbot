# -*- coding: utf-8 -*-
#  Versión en español (México) del esquema de historia clínica

from datetime import date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, root_validator


class ContactoEmergencia(BaseModel):
    nombre: str = Field(..., description="Nombre completo del contacto de emergencia")
    telefono: str = Field(..., description="Número telefónico del contacto de emergencia")


class Medicamento(BaseModel):
    nombre: str = Field(..., description="Nombre del medicamento")
    dosis: Optional[str] = Field(None, description="Información de la dosis")
    horario: Optional[str] = Field(None, description="Horario o frecuencia de administración")


class InfoEstiloVida(BaseModel):
    fuma_tabaco: bool = Field(..., description="¿El paciente fuma tabaco?")
    cantidad_tabaco_por_dia: Optional[str] = Field(
        None, description="Cantidad de unidades de tabaco al día"
    )
    anos_fumando: Optional[str] = Field(
        None, description="¿Cuántos años ha fumado?"
    )
    consume_alcohol: bool = Field(..., description="¿El paciente consume alcohol?")
    bebidas_alcohol_semana: Optional[str] = Field(
        None, description="Número de bebidas alcohólicas por semana"
    )
    usa_drogas_recreativas: bool = Field(
        ..., description="¿El paciente usa drogas recreativas?"
    )
    tipo_y_frecuencia_droga: Optional[str] = Field(
        None, description="Tipo y frecuencia de uso de drogas recreativas"
    )
    habitos_ejercicio: Optional[str] = Field(
        None, description="Descripción de los hábitos de ejercicio"
    )
    descripcion_dieta: Optional[str] = Field(
        None, description="Descripción de la dieta habitual"
    )
    # Los validadores condicionales se omiten aquí para mantener la lógica original
    # (solo se traduce la parte de esquema)


class SaludMujer(BaseModel):
    ultima_menstruacion: Optional[str] = Field(
        None, description="Fecha de la última menstruación"
    )
    embarazada_o_posiblemente: Optional[bool] = Field(
        None, description="Estado de embarazo"
    )
    ultimo_mamograma_papanicolaou: Optional[str] = Field(
        None, description="Fecha del último mamograma o Papanicolaou"
    )


class RevisionSistemas(BaseModel):
    fiebre_o_escalofrios: bool = False
    fatiga_o_debilidad: bool = False
    perdida_o_aumento_peso: bool = False
    dolor_pecho: bool = False
    dificultad_respirar: bool = False
    tos: bool = False
    dolor_cabeza: bool = False
    cambios_vision: bool = False
    cambios_audicion: bool = False
    dolor_abdominal: bool = False
    nausea_o_vomito: bool = False
    dolor_articular: bool = False
    erupciones_cutaneas: bool = False
    mareo_o_desmayo: bool = False
    cambios_humor: bool = False
    otros_sintomas: Optional[str] = None


class HistorialPaciente(BaseModel):
    """Información estructurada de triage extraída de la conversación de admisión"""

    nombre: str = Field(..., description="Nombre legal completo del paciente")
    fecha_nacimiento: date = Field(
        ..., description="Fecha de nacimiento en formato ISO-8601"
    )
    sexo: Optional[str] = Field(
        None, description="Sexo asignado al nacer o identidad de género"
    )
    direccion: Optional[str] = Field(None, description="Dirección de domicilio")
    telefono: Optional[str] = Field(None, description="Número telefónico")
    correo_electronico: Optional[str] = Field(None, description="Correo electrónico")
    contacto_emergencia: Optional[ContactoEmergencia] = None
    medico_cabecera: Optional[str] = Field(
        None, description="Nombre del médico de cabecera"
    )

    motivo_consulta: Optional[str] = Field(
        None, description="Motivo principal de la consulta"
    )
    duracion_malestar: Optional[str] = Field(
        None, description="Duración del problema principal"
    )
    descripcion_sintomas: Optional[str] = Field(
        None, description="Descripción detallada de los síntomas"
    )

    condiciones_previas: List[str] = Field(
        default_factory=list,
        description="Diagnósticos crónicos o antecedentes médicos relevantes",
    )
    cirugias_hospitalizaciones: Optional[str] = Field(
        None, description="Cirugías o hospitalizaciones importantes"
    )
    lesiones_accidentes_graves: Optional[str] = Field(
        None, description="Lesiones o accidentes graves"
    )

    alergias_medicamentos: List[str] = Field(
        default_factory=list, description="Alergias a medicamentos"
    )
    alergias_alimentos: List[str] = Field(
        default_factory=list, description="Alergias alimentarias"
    )
    alergias_ambientales: List[str] = Field(
        default_factory=list, description="Alergias ambientales"
    )
    enfermedades_infecciosas: List[str] = Field(
        default_factory=list, description="Enfermedades infecciosas actuales o pasadas"
    )

    medicamentos_recetados: List[Medicamento] = Field(
        default_factory=list, description="Medicamentos recetados que toma regularmente"
    )
    suplementos: List[Medicamento] = Field(
        default_factory=list,
        description="Suplementos de venta libre, vitaminas o productos herbales",
    )
    medicina_alternativa: List[Medicamento] = Field(
        default_factory=list,
        description="Tratamientos fuera de la medicina basada en evidencia",
    )

    antecedentes_familiares_cardiacos: Optional[bool] = Field(
        None, description="Antecedentes familiares de enfermedad cardíaca"
    )
    antecedentes_familiares_diabetes: Optional[bool] = Field(
        None, description="Antecedentes familiares de diabetes"
    )
    antecedentes_familiares_cancer: Optional[str] = Field(
        None, description="Antecedentes familiares de cáncer (tipo)"
    )
    antecedentes_familiares_hipertension: Optional[bool] = Field(
        None, description="Antecedentes familiares de hipertensión"
    )
    antecedentes_familiares_embolia: Optional[bool] = Field(
        None, description="Antecedentes familiares de derrame cerebral"
    )
    antecedentes_familiares_salud_mental: Optional[bool] = Field(
        None, description="Antecedentes familiares de trastornos de salud mental"
    )
    antecedentes_familiares_otros: Optional[str] = Field(
        None, description="Otros antecedentes familiares relevantes"
    )

    estilo_vida: Optional[InfoEstiloVida] = None

    ultimo_examen_fisico: Optional[str] = Field(
        None, description="Fecha del último examen físico"
    )
    ultimo_examen_sangre: Optional[str] = Field(
        None, description="Fecha del último análisis de sangre"
    )
    ultima_vacunacion: Optional[str] = Field(
        None, description="Fecha de la última vacunación importante"
    )
    salud_mujer: Optional[SaludMujer] = None

    revision_sistemas: Optional[RevisionSistemas] = None

    comentarios_adicionales: Optional[str] = Field(
        None, description="Otra información que el paciente desea que el médico conozca"
    )

    banderas_rojas: List[str] = Field(
        default_factory=list,
        description="Posibles hallazgos clínicos preocupantes para revisión médica",
    )

    firma: Optional[str] = Field(None, description="Firma del paciente o tutor")
    fecha_firma: Optional[date] = Field(
        None, description="Fecha de la firma (formato ISO-8601)"
    )
