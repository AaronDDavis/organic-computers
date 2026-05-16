from django.urls import path
from . import views

urlpatterns = [
    path('', views.JourneyListView.as_view(), name = 'journey_list'),
    path('<int:pk>/', views.JourneyDetailView.as_view(), name = 'journey_details'),
    path('new/', views.JourneyCreateView.as_view(), name = 'create_journey'),
    
    path('<int:pk>/confirm-doctor/', views.DoctorConfirmView.as_view(), name = 'confirm_doctor'),
    path('<int:pk>/search-doctor/', views.DoctorSearchView.as_view(), name = 'search_doctor'),
]
