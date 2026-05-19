from django.urls import path
from . import views

urlpatterns = [
    path('profile/setup/', views.DoctorSetupView.as_view(), name = 'setup_doctor'),
    path('dashboard/', views.DoctorDashboardView.as_view(), name = 'dashboard_doctor'),
    path('profile/', views.DoctorProfileView.as_view(), name = 'profile_doctor'),

    path('patient_list/', views.DoctorPatientListView.as_view(), name = 'doctor_patient_list'),
    path('patient/<int:user_id>', views.DoctorPatientDetailView.as_view(), name = 'doctor_patient_detail'),
    path('journey/<int:journey_id>/save_note', views.DoctorSaveNoteView.as_view(), name = 'save_clinical_note'),
]
