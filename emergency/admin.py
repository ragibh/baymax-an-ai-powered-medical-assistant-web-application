from django.contrib import admin
from .models import EmergencyContact

@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'emergency_type']
    list_filter = ['emergency_type']
    search_fields = ['name', 'address']