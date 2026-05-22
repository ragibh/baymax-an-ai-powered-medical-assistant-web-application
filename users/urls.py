from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/add-vital/', views.add_vital, name='add_vital'),
    path('profile/delete-vital/<int:vital_id>/', views.delete_vital, name='delete_vital'),
    path('profile/add-donation/', views.add_donation, name='add_donation'),
]
