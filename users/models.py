from django.contrib.auth.models import User
from django.db import models


def user_avatar_path(instance, filename):
    return f'avatars/user_{instance.user.id}/{filename}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    age = models.IntegerField(null=True, blank=True)
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        null=True,
        blank=True,
        help_text='Profile photo (optional)',
    )
    blood_group = models.CharField(
        max_length=5,
        blank=True,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
            ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None


class HealthVital(models.Model):
    VITAL_TYPES = [
        ('bp_systolic', 'Blood Pressure (Systolic)'),
        ('bp_diastolic', 'Blood Pressure (Diastolic)'),
        ('glucose', 'Blood Glucose (mg/dL)'),
        ('weight', 'Weight (kg)'),
        ('heart_rate', 'Heart Rate (bpm)'),
        ('oxygen_sat', 'Oxygen Saturation (%)'),
        ('temperature', 'Body Temperature (°C)'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vitals')
    vital_type = models.CharField(max_length=30, choices=VITAL_TYPES)
    value = models.FloatField()
    note = models.CharField(max_length=200, blank=True)
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.user.username} — {self.vital_type}: {self.value}"


class BloodDonationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    donated_at = models.DateField()
    location = models.CharField(max_length=200, blank=True)
    recipient_note = models.CharField(max_length=200, blank=True)
    units = models.FloatField(default=1.0, help_text='Units of blood donated')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-donated_at']

    def __str__(self):
        return f"{self.user.username} donated on {self.donated_at}"
