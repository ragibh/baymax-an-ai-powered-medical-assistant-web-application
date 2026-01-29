from django.urls import path
from . import views

app_name = 'emergency'

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chatbot_api, name='chatbot_api'),
    path('history/', views.get_chat_history, name='chat_history'),
    path('directory/', views.emergency_directory, name='directory'),
    path('status/', views.check_status, name='status'),
    path('clear/', views.clear_chat, name='clear_chat'),  # Add clear chat
    path('doctor/<int:doctor_id>/', views.get_doctor_details, name='doctor_details'),
    path('filter-options/', views.get_filter_options, name='filter_options'),
]