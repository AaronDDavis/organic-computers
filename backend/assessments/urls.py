from django.urls import path
from . import views

urlpatterns = [
    path('journeys/<int:pk>/assessment/new/<str:stage>/', views.AssessmentCreateView.as_view(), name = 'create_assessment'),
    path('assess/guest/', views.GuestAssessmentView.as_view(), name='guest_assessment'),
]