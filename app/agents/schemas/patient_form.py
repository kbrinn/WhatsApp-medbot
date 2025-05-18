from datetime import date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, root_validator

class EmergencyContact(BaseModel):
    name: str = Field(..., description="Emergency contact's full name")
    phone_number: str = Field(..., description="Emergency contact's phone number")

class MedicationEntry(BaseModel):
    name: str = Field(..., description="Medication name")
    dosage: Optional[str] = Field(None, description="Dosage information")
    schedule: Optional[str] = Field(None, description="Administration schedule")

class LifestyleInfo(BaseModel):
    smoke_tobacco: bool = Field(..., description="Does the patient use tobacco?")
    tobacco_quantity_per_day: Optional[str] = Field(None, description="Number of tobacco units per day")
    tobacco_duration_years: Optional[str] = Field(None, description="How long have they smoked?")
    drink_alcohol: bool = Field(..., description="Does the patient drink alcohol?")
    alcohol_drinks_per_week: Optional[str] = Field(None, description="Number of alcoholic drinks per week")
    recreational_drugs: bool = Field(..., description="Does the patient use recreational drugs?")
    drug_type_and_frequency: Optional[str] = Field(None, description="Type and frequency of recreational drug use")
    exercise_habits: Optional[str] = Field(None, description="Describe exercise habits")
    diet_description: Optional[str] = Field(None, description="Describe typical diet")
    # @root_validator(pre=False)  # 'pre=False' means it runs after individual field validation
    # def check_conditional_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
    #     # Check tobacco fields
    #     if not values.get('smoke_tobacco'):
    #         if values.get('tobacco_quantity_per_day') is not None:
    #             raise ValueError("tobacco_quantity_per_day must be None if smoke_tobacco is False")
    #         if values.get('tobacco_duration_years') is not None:
    #             raise ValueError("tobacco_duration_years must be None if smoke_tobacco is False")
    #     # Alternatively, you could automatically set them to None instead of raising an error:
    #     # if not values.get('smoke_tobacco'):
    #     #     values['tobacco_quantity_per_day'] = None
    #     #     values['tobacco_duration_years'] = None
    #
    #     # Check alcohol fields
    #     if not values.get('drink_alcohol') and values.get('alcohol_drinks_per_week') is not None:
    #         raise ValueError("alcohol_drinks_per_week must be None if drink_alcohol is False")
    #         # Or: values['alcohol_drinks_per_week'] = None
    #
    #     # Check recreational drugs fields
    #     if not values.get('recreational_drugs') and values.get('drug_type_and_frequency') is not None:
    #         raise ValueError("drug_type_and_frequency must be None if recreational_drugs is False")
    #         # Or: values['drug_type_and_frequency'] = None
    #
    #     return values
    #



class WomenHealthInfo(BaseModel):
    last_menstrual_period: Optional[str] = Field(None, description="Date of last menstrual period")
    pregnant_or_possibly_pregnant: Optional[bool] = Field(None, description="Pregnancy status")
    last_mammogram_pap_smear: Optional[str] = Field(None, description="Date of last mammogram or Pap smear")

class ReviewOfSystems(BaseModel):
    fever_or_chills: bool = False
    fatigue_or_weakness: bool = False
    weight_loss_or_gain: bool = False
    chest_pain: bool = False
    shortness_of_breath: bool = False
    cough: bool = False
    headache: bool = False
    vision_changes: bool = False
    hearing_changes: bool = False
    abdominal_pain: bool = False
    nausea_or_vomiting: bool = False
    joint_pain: bool = False
    skin_rashes: bool = False
    dizziness_or_fainting: bool = False
    mood_changes: bool = False
    other_symptoms: Optional[str] = None

class PatientHistory(BaseModel):
    """Structured triage info extracted from the intake conversation"""
    name: str = Field(..., description="Full legal name of the patient")
    dob: date = Field(..., description="Date of birth in ISO-8601 format")
    sex: Optional[str] = Field(None, description="Sex assigned at birth or gender identity")
    address: Optional[str] = Field(None, description="Home address")
    phone_number: Optional[str] = Field(None, description="Phone number")
    email_address: Optional[str] = Field(None, description="Email address")
    emergency_contact: Optional[EmergencyContact] = None
    primary_care_physician: Optional[str] = Field(None, description="Primary care physician name")

    reason_for_visit: Optional[str] = Field(None, description="Chief complaint or reason for appointment")
    duration_of_concern: Optional[str] = Field(None, description="Duration of main concern")
    symptoms_description: Optional[str] = Field(None, description="Detailed symptoms")

    pre_conditions: List[str] = Field(default_factory=list, description="Chronic diagnoses or notable medical history")
    surgeries_or_hospitalizations: Optional[str] = Field(None, description="Major surgeries or hospitalizations")
    serious_injuries_or_accidents: Optional[str] = Field(None, description="Serious injuries or accidents")

    allergies_medications: List[str] = Field(default_factory=list, description="Medication allergies")
    allergies_foods: List[str] = Field(default_factory=list, description="Food allergies")
    allergies_environment: List[str] = Field(default_factory=list, description="Environmental allergies")
    infectious_diseases: List[str] = Field(default_factory=list, description="Current or past infectious diseases")

    prescriptions: List[MedicationEntry] = Field(default_factory=list, description="Physician-prescribed drugs taken regularly")
    supplements: List[MedicationEntry] = Field(default_factory=list, description="OTC vitamins, herbal or alternative products")
    alternative_medicine: List[MedicationEntry] = Field(default_factory=list, description="Treatments outside evidence-based medicine")

    family_history_heart_disease: Optional[bool] = Field(None, description="Family history of heart disease")
    family_history_diabetes: Optional[bool] = Field(None, description="Family history of diabetes")
    family_history_cancer: Optional[str] = Field(None, description="Family history of cancer (type)")
    family_history_high_blood_pressure: Optional[bool] = Field(None, description="Family history of high blood pressure")
    family_history_stroke: Optional[bool] = Field(None, description="Family history of stroke")
    family_history_mental_health: Optional[bool] = Field(None, description="Family history of mental health conditions")
    family_history_other: Optional[str] = Field(None, description="Other relevant family history")

    lifestyle: Optional[LifestyleInfo] = None

    last_physical_exam: Optional[str] = Field(None, description="Date of last physical exam")
    last_blood_test: Optional[str] = Field(None, description="Date of last blood test")
    last_vaccination: Optional[str] = Field(None, description="Date of last major vaccination")
    woman_health: Optional[WomenHealthInfo] = None

    review_of_systems: Optional[ReviewOfSystems] = None

    additional_comments: Optional[str] = Field(None, description="Other information the patient wants the doctor to know")

    red_flags: List[str] = Field(default_factory=list, description="Potential clinical concerns flagged for MD review")

    signature: Optional[str] = Field(None, description="Patient/guardian signature")
    signature_date: Optional[date] = Field(None, description="Signature date (ISO-8601)")
