from django.urls import path
from . import views

urlpatterns = [
    path('profile/setup/', views.DoctorSetupView.as_view(), name = 'setup_doctor'),
    path('dashboard/', views.DoctorSetupView.as_view(), name = 'dashboard_doctor'),
    path('profile/', views.DoctorProfileView.as_view(), name = 'profile_doctor'),
]
