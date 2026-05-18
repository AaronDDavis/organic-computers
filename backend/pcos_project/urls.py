from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name = 'login', permanent = True)),
    path('user/', include('users.urls')),
    path('patient/', include('patients.urls')),
    path('doctor/', include('doctors.urls')),
    path('clinic/', include('clinics.urls')),
    path('journeys/', include('journeys.urls')),
    path('', include('assessments.urls')),
    path('predict/', include('api.urls')),

    path('admin/', admin.site.urls),
]
