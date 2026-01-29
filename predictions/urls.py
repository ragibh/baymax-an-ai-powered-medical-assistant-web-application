from django.urls import path
from . import views

app_name = 'predictions'

urlpatterns = [
    path('', views.home, name='home'),
    path('bmi/', views.bmi_prediction, name='bmi'),
    path('diabetes/', views.diabetes_prediction, name='diabetes'),
    path('heart/', views.heart_prediction, name='heart'),
    # We'll add liver, kidney, prescription later
]