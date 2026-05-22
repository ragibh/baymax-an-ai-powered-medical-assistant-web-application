from django import forms

from .widgets import BlobaxFormMixin


class BMIPredictionForm(BlobaxFormMixin, forms.Form):
    height = forms.FloatField(label='Height (cm)', min_value=0)
    weight = forms.FloatField(label='Weight (kg)', min_value=0)

class DiabetesPredictionForm(BlobaxFormMixin, forms.Form):
    pregnancies = forms.IntegerField(label='Pregnancies', min_value=0)
    glucose = forms.FloatField(label='Glucose Level', min_value=0)
    blood_pressure = forms.FloatField(label='Blood Pressure', min_value=0)
    skin_thickness = forms.FloatField(label='Skin Thickness', min_value=0)
    insulin = forms.FloatField(label='Insulin Level', min_value=0)
    bmi = forms.FloatField(label='BMI', min_value=0)
    diabetes_pedigree = forms.FloatField(label='Diabetes Pedigree Function', min_value=0)
    age = forms.IntegerField(label='Age', min_value=0)

class HeartDiseaseForm(BlobaxFormMixin, forms.Form):
    age = forms.IntegerField(label='Age', min_value=0)
    sex = forms.ChoiceField(label='Sex', choices=[(0, 'Female'), (1, 'Male')])
    cp = forms.ChoiceField(label='Chest Pain Type', choices=[
        (0, 'Typical Angina'), (1, 'Atypical Angina'), 
        (2, 'Non-anginal Pain'), (3, 'Asymptomatic')
    ])
    trestbps = forms.FloatField(label='Resting Blood Pressure', min_value=0)
    chol = forms.FloatField(label='Cholesterol', min_value=0)
    fbs = forms.ChoiceField(label='Fasting Blood Sugar > 120 mg/dl', choices=[(0, 'No'), (1, 'Yes')])
    restecg = forms.ChoiceField(label='Resting ECG', choices=[
        (0, 'Normal'), (1, 'ST-T Wave Abnormality'), (2, 'Left Ventricular Hypertrophy')
    ])
    thalach = forms.FloatField(label='Maximum Heart Rate', min_value=0)
    exang = forms.ChoiceField(label='Exercise Induced Angina', choices=[(0, 'No'), (1, 'Yes')])
    oldpeak = forms.FloatField(label='ST Depression', min_value=0)
    slope = forms.ChoiceField(label='Slope of Peak Exercise ST Segment', choices=[
        (0, 'Upsloping'), (1, 'Flat'), (2, 'Downsloping')
    ])
    ca = forms.IntegerField(label='Number of Major Vessels', min_value=0, max_value=3)
    thal = forms.ChoiceField(label='Thalassemia', choices=[
        (0, 'Normal'), (1, 'Fixed Defect'), (2, 'Reversible Defect')
    ])