# predictions/ml.py
"""
Blobax — ML model loader and predictor.
All models live in static/models/ and are loaded once at import time.
"""

import os
import pickle

import numpy as np
from django.conf import settings

MODELS_DIR = os.path.join(settings.BASE_DIR, 'static', 'models')


def _load(filename):
    path = os.path.join(MODELS_DIR, filename)
    with open(path, 'rb') as f:
        return pickle.load(f)


try:
    DIABETES_MODEL = _load('diabetes_random_forest_model.pkl')
    DIABETES_SCALER = _load('diabetes_scaler.pkl')
    DIABETES_FEATURES = _load('diabetes_features.pkl')
except Exception as e:
    print(f"[Blobax ML] WARNING: Could not load diabetes model — {e}")
    DIABETES_MODEL = DIABETES_SCALER = DIABETES_FEATURES = None

try:
    HEART_MODEL = _load('heart_model.pkl')
    HEART_SCALER = _load('heart_scaler.pkl')
    HEART_FEATURES = _load('heart_features.pkl')
except Exception as e:
    print(f"[Blobax ML] WARNING: Could not load heart model — {e}")
    HEART_MODEL = HEART_SCALER = HEART_FEATURES = None

try:
    LIVER_MODEL = _load('liver_model.pkl')
    LIVER_SCALER = _load('liver_scaler.pkl')
    LIVER_FEATURES = _load('liver_features.pkl')
except Exception as e:
    print(f"[Blobax ML] WARNING: Could not load liver model — {e}")
    LIVER_MODEL = LIVER_SCALER = LIVER_FEATURES = None


SMOKING_MAP = {
    'never': 0,
    'former': 1,
    'not current': 2,
    'ever': 3,
    'current': 4,
}


def _risk_level(probability: float) -> str:
    if probability < 30:
        return 'low'
    elif probability < 60:
        return 'medium'
    return 'high'


def _bmi_category(bmi: float) -> int:
    if bmi < 18.5:
        return 0
    if bmi < 25:
        return 1
    if bmi < 30:
        return 2
    return 3


def _age_group(age: float) -> int:
    age = int(age)
    if age < 30:
        return 0
    if age < 45:
        return 1
    if age < 60:
        return 2
    return 3


def _result_dict(prediction: int, probability: float, positive_label: str, negative_label: str) -> dict:
    return {
        'prediction': prediction,
        'probability': round(probability, 1),
        'label': positive_label if prediction == 1 else negative_label,
        'risk_level': _risk_level(probability),
    }


def predict_diabetes(data: dict) -> dict:
    if DIABETES_MODEL is None:
        return {'error': 'Diabetes model not loaded'}

    gender_enc = 1 if str(data.get('gender', 'Male')).strip().lower() == 'male' else 0
    smoking_enc = SMOKING_MAP.get(str(data.get('smoking_history', 'never')).strip().lower(), 0)
    bmi = float(data['bmi'])
    age = float(data['age'])

    row = {
        'gender': gender_enc,
        'age': age,
        'hypertension': int(data['hypertension']),
        'heart_disease': int(data['heart_disease']),
        'smoking_history': smoking_enc,
        'bmi': bmi,
        'HbA1c_level': float(data['HbA1c_level']),
        'blood_glucose_level': float(data['blood_glucose_level']),
        'bmi_category': _bmi_category(bmi),
        'age_group': _age_group(age),
    }

    features = np.array([[row[f] for f in DIABETES_FEATURES]])
    features_scaled = DIABETES_SCALER.transform(features)
    prediction = int(DIABETES_MODEL.predict(features_scaled)[0])
    probability = float(DIABETES_MODEL.predict_proba(features_scaled)[0][1]) * 100

    return _result_dict(
        prediction,
        probability,
        'Diabetes Detected',
        'No Diabetes Detected',
    )


def predict_heart(data: dict) -> dict:
    if HEART_MODEL is None:
        return {'error': 'Heart model not loaded'}

    age = int(data['age'])
    thalach = int(data['thalach'])

    row = {
        'age': age,
        'sex': int(data['sex']),
        'cp': int(data['cp']),
        'trestbps': int(data['trestbps']),
        'chol': int(data['chol']),
        'fbs': int(data['fbs']),
        'restecg': int(data['restecg']),
        'thalach': thalach,
        'exang': int(data['exang']),
        'oldpeak': float(data['oldpeak']),
        'slope': int(data['slope']),
        'ca': int(data['ca']),
        'thal': int(data['thal']),
        'age_group': _age_group(age),
        'hr_ratio': thalach / max(age * 1.1, 1),
        'risk_score': (
            int(data['cp']) * 2
            + int(data['exang']) * 3
            + int(data['fbs'])
            + int(float(data['oldpeak']) > 1)
        ),
    }

    features = np.array([[row[f] for f in HEART_FEATURES]])
    features_scaled = HEART_SCALER.transform(features)
    prediction = int(HEART_MODEL.predict(features_scaled)[0])
    probability = float(HEART_MODEL.predict_proba(features_scaled)[0][1]) * 100

    return _result_dict(
        prediction,
        probability,
        'Heart Disease Detected',
        'No Heart Disease Detected',
    )


def predict_liver(data: dict) -> dict:
    if LIVER_MODEL is None:
        return {'error': 'Liver model not loaded'}

    age = int(data['Age'])
    gender_enc = 1 if str(data.get('Gender', 'Male')).strip().lower() == 'male' else 0
    alt = float(data['ALT_SGPT'])
    ast = float(data['AST_SGOT'])
    apt = float(data['APT'])
    bili = float(data['Bilirubin_Total'])
    alb = float(data['Albumin'])
    prot = float(data['Protein'])

    row = {
        'Age': age,
        'Gender': gender_enc,
        'ALT (SGPT)': alt,
        'AST (SGOT)': ast,
        'APT': apt,
        'Bilirubin Total (mg/dl)': bili,
        'Albumin (g/dL)': alb,
        'Protein (g/dL)': prot,
        'AST_ALT_ratio': ast / max(alt, 0.1),
        'enzyme_total': alt + ast + apt,
        'bili_elevated': 1 if bili > 1.2 else 0,
        'albumin_low': 1 if alb < 3.4 else 0,
        'age_group': _age_group(age),
    }

    features = np.array([[row[f] for f in LIVER_FEATURES]])
    features_scaled = LIVER_SCALER.transform(features)
    prediction = int(LIVER_MODEL.predict(features_scaled)[0])
    probability = float(LIVER_MODEL.predict_proba(features_scaled)[0][1]) * 100

    return _result_dict(
        prediction,
        probability,
        'Liver Disease Detected',
        'No Liver Disease Detected',
    )
