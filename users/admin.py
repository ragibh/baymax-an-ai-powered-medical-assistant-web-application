from django.contrib import admin

from .models import BloodDonationHistory, HealthVital, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'blood_group', 'age', 'created_at']
    search_fields = ['user__username']


@admin.register(HealthVital)
class HealthVitalAdmin(admin.ModelAdmin):
    list_display = ['user', 'vital_type', 'value', 'recorded_at']
    list_filter = ['vital_type']


@admin.register(BloodDonationHistory)
class BloodDonationHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'donated_at', 'location', 'units']
