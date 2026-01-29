from django.db import models
from django.contrib.auth.models import User

class PredictionHistory(models.Model):
    PREDICTION_TYPES = [
        ('bmi', 'BMI Prediction'),
        ('diabetes', 'Diabetes Prediction'),
        ('heart', 'Heart Disease Prediction'),
        ('liver', 'Liver Disease Prediction'),
        ('kidney', 'Kidney Disease Prediction'),
        ('prescription', 'Prescription Recognition'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    input_data = models.JSONField()  # Store all input parameters
    result = models.JSONField()      # Store prediction results
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.prediction_type} - {self.created_at}"