from django.db import models
from django.contrib.auth.models import User

class EmergencyContact(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    emergency_type = models.CharField(max_length=50)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    response = models.TextField()
    is_user = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{'User' if self.is_user else 'Baymax'}: {self.message[:50]}"

# NEW: Doctor Directory Model
class Doctor(models.Model):
    post = models.CharField(max_length=100)
    provider = models.CharField(max_length=200)
    division = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    upazila = models.CharField(max_length=100)
    professional = models.CharField(max_length=100)
    contact_no = models.CharField(max_length=20)
    address = models.TextField()
    degree = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    hospital_name = models.CharField(max_length=200, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_verified = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['division', 'district', 'provider']
    
    def __str__(self):
        return f"{self.provider} - {self.department} - {self.district}"
    
    def get_map_url(self):
        if self.latitude and self.longitude:
            return f"https://maps.google.com/?q={self.latitude},{self.longitude}"
        return f"https://maps.google.com/?q={self.address}"
    
    def get_directions_url(self):
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps/dir/?api=1&destination={self.latitude},{self.longitude}"
        return f"https://www.google.com/maps/dir/?api=1&destination={self.address}"