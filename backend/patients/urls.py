from django.urls import path
from . import views

urlpatterns = [
    path('profile/setup/', views.PatientSetupView.as_view(), name = 'setup_patient'),
    path('dashboard/', views.PatientDashboardView.as_view(), name = 'dashboard_patient'),
    path('profile/', views.PatientProfileView.as_view(), name = 'profile_patient'),
]
