from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .forms import BMIPredictionForm
from .ml import predict_diabetes, predict_heart, predict_liver
from .models import Prediction, PredictionHistory


def _post_dict(request):
    return {k: request.POST.get(k) for k in request.POST}


def _save_ml_result(user, prediction_type, post_data, result):
    if not result or result.get('error'):
        return
    Prediction.objects.create(
        user=user,
        prediction_type=prediction_type,
        result=result['label'],
        probability=result['probability'],
    )
    PredictionHistory.objects.create(
        user=user,
        prediction_type=prediction_type,
        input_data=post_data,
        result=result,
    )


@login_required
def predictions_home(request):
    return render(request, 'predictions/home.html')


@login_required
def diabetes_view(request):
    result = None
    if request.method == 'POST':
        try:
            result = predict_diabetes(request.POST)
            _save_ml_result(request.user, 'diabetes', _post_dict(request), result)
        except Exception as e:
            result = {'error': str(e)}
    return render(request, 'predictions/diabetes.html', {'result': result})


@login_required
def heart_view(request):
    result = None
    if request.method == 'POST':
        try:
            result = predict_heart(request.POST)
            _save_ml_result(request.user, 'heart', _post_dict(request), result)
        except Exception as e:
            result = {'error': str(e)}
    return render(request, 'predictions/heart.html', {'result': result})


@login_required
def liver_view(request):
    result = None
    if request.method == 'POST':
        try:
            result = predict_liver(request.POST)
            _save_ml_result(request.user, 'liver', _post_dict(request), result)
        except Exception as e:
            result = {'error': str(e)}
    return render(request, 'predictions/liver.html', {'result': result})


@login_required
def bmi_prediction(request):
    result = None
    if request.method == 'POST':
        form = BMIPredictionForm(request.POST)
        if form.is_valid():
            height = form.cleaned_data['height']
            weight = form.cleaned_data['weight']
            height_m = height / 100
            bmi = weight / (height_m * height_m)

            if bmi < 18.5:
                category = 'Underweight'
            elif bmi < 25:
                category = 'Normal weight'
            elif bmi < 30:
                category = 'Overweight'
            else:
                category = 'Obese'

            result = {'bmi': round(bmi, 2), 'category': category}
            PredictionHistory.objects.create(
                user=request.user,
                prediction_type='bmi',
                input_data={'height': height, 'weight': weight},
                result=result,
            )
    else:
        form = BMIPredictionForm()

    return render(request, 'predictions/bmi.html', {'form': form, 'result': result})


@login_required
def kidney_prediction(request):
    return render(request, 'predictions/coming_soon.html', {
        'title': 'Kidney Disease Prediction',
        'description': 'Kidney ML model coming soon.',
        'icon': 'fa-kidneys',
        'prediction_type': 'kidney',
    })


@login_required
def prescription_prediction(request):
    return render(request, 'predictions/coming_soon.html', {
        'title': 'Prescription OCR',
        'description': 'Prescription recognition coming soon.',
        'icon': 'fa-file-prescription',
        'prediction_type': 'prescription',
    })
