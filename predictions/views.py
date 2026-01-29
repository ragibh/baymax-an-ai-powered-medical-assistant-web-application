from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import BMIPredictionForm, DiabetesPredictionForm, HeartDiseaseForm
from .models import PredictionHistory

@login_required
def home(request):
    return render(request, 'predictions/home.html')

@login_required
def bmi_prediction(request):
    result = None
    if request.method == 'POST':
        form = BMIPredictionForm(request.POST)
        if form.is_valid():
            height = form.cleaned_data['height']
            weight = form.cleaned_data['weight']
            
            # Calculate BMI
            height_m = height / 100
            bmi = weight / (height_m * height_m)
            
            # Determine category
            if bmi < 18.5:
                category = "Underweight"
            elif bmi < 25:
                category = "Normal weight"
            elif bmi < 30:
                category = "Overweight"
            else:
                category = "Obese"
            
            result = {
                'bmi': round(bmi, 2),
                'category': category
            }
            
            # Save to prediction history
            PredictionHistory.objects.create(
                user=request.user,
                prediction_type='bmi',
                input_data={'height': height, 'weight': weight},
                result=result
            )
    else:
        form = BMIPredictionForm()
    
    return render(request, 'predictions/bmi.html', {
        'form': form, 
        'result': result
    })

@login_required
def diabetes_prediction(request):
    result = None
    if request.method == 'POST':
        form = DiabetesPredictionForm(request.POST)
        if form.is_valid():
            # For now, we'll create a mock prediction
            # Later you'll integrate your actual ML model
            input_data = {k: v for k, v in form.cleaned_data.items()}
            
            # Mock prediction (replace with your ML model)
            risk_score = sum(input_data.values()) / len(input_data) if input_data else 0
            prediction = "High Risk" if risk_score > 50 else "Low Risk"
            
            result = {
                'risk_score': round(risk_score, 2),
                'prediction': prediction,
                'message': 'This is a mock prediction. Integrate your ML model here.'
            }
            
            # Save to prediction history
            PredictionHistory.objects.create(
                user=request.user,
                prediction_type='diabetes',
                input_data=input_data,
                result=result
            )
    else:
        form = DiabetesPredictionForm()
    
    return render(request, 'predictions/diabetes.html', {
        'form': form, 
        'result': result
    })

@login_required
def heart_prediction(request):
    result = None
    if request.method == 'POST':
        form = HeartDiseaseForm(request.POST)
        if form.is_valid():
            input_data = {k: v for k, v in form.cleaned_data.items()}
            
            # Mock prediction (replace with your ML model)
            risk_score = sum([v for v in input_data.values() if isinstance(v, (int, float))]) 
            prediction = "High Risk of Heart Disease" if risk_score > 100 else "Low Risk"
            
            result = {
                'risk_score': round(risk_score, 2),
                'prediction': prediction,
                'message': 'This is a mock prediction. Integrate your ML model here.'
            }
            
            # Save to prediction history
            PredictionHistory.objects.create(
                user=request.user,
                prediction_type='heart',
                input_data=input_data,
                result=result
            )
    else:
        form = HeartDiseaseForm()
    
    return render(request, 'predictions/heart.html', {
        'form': form, 
        'result': result
    })