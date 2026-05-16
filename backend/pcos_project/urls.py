from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('user/', include('users.urls')),
    path('patient/', include('patients.urls')),
    path('doctor/', include('patients.urls')),
    path('journeys/', include('journeys.urls')),
    path('', include('assessments.urls')),

    path('admin/', admin.site.urls),
]
