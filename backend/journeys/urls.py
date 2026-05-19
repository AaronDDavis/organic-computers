from django.urls import path
from . import views

urlpatterns = [
    path('', views.JourneyListView.as_view(), name = 'journey_list'),
    path('<int:pk>/', views.JourneyDetailView.as_view(), name = 'journey_detail'),
    path('new/', views.JourneyCreateView.as_view(), name = 'create_journey'),
    
    path('<int:pk>/confirm_doctor/', views.DoctorConfirmView.as_view(), name = 'confirm_doctor'),
    path('<int:pk>/search_doctor/', views.DoctorSearchView.as_view(), name = 'search_doctor'),

    path('confirm_clinic/<int:pk>/', views.ClinicConfirmView.as_view(), name = 'confirm_clinic'),
    path('search_clinic/<int:pk>/', views.ClinicSearchView.as_view(), name = 'search_clinic'),
]
