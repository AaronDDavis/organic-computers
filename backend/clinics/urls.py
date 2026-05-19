from django.urls import path
from . import views

urlpatterns = [
    path('patients/setup/', views.ClinicianSetupView.as_view(), name='setup_clinician'),
    path('patients/dashboard/', views.ClinicianDashboardView.as_view(), name='dashboard_clinician'),
    path('patients/profile/', views.ClinicianProfileView.as_view(), name='profile_clinician'),


    # Patient detail
    path('patients/<int:user_id>/', views.ClinicianPatientDetailView.as_view(), name='clinician_patient_detail'),

    # Patient list
    path('patients/', views.ClinicianPatientListView.as_view(), name='clinician_patient_list'),

    # Stage 2
    path('patients/journey/<int:journey_id>/stage2/submit/', views.ClinicianStage2SubmitView.as_view(), name='clinician_stage2_submit'),
    
    path('patients/journey/<int:journey_id>/stage2/edit/', views.ClinicianStage2EditView.as_view(), name='clinician_stage2_edit'),

    # Stage 3
    path('patients/journey/<int:journey_id>/stage3/submit/', views.ClinicianStage3SubmitView.as_view(), name='clinician_stage3_submit'),
    path('patients/journey/<int:journey_id>/stage3/edit/', views.ClinicianStage3EditView.as_view(), name='clinician_stage3_edit'),
]