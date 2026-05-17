from django.urls import path
from . import views

urlpatterns = [
    path('stage1/', views.PredictStage1View.as_view(), name = 'stage_1_model'),
    path('stage2/', views.PredictStage2View.as_view(), name = 'stage_2_model'),
    path('stage2/', views.PredictStage3View.as_view(), name = 'stage_3_model'),
]
