from django.contrib import admin
from .models import PredictionHistory

@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'prediction_type', 'created_at']
    list_filter = ['prediction_type', 'created_at']
    search_fields = ['user__username']