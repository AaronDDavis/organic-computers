from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name = 'login', permanent = True)),
    path('login/', views.CustomLoginView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
    path('signup/', views.SignupView.as_view(), name = 'signup'),
    
    path('profile/setup/', views.setup_redirect, name = 'setup'),
    path('dashboard/', views.dashboard_redirect, name = 'dashboard'),
    path('profile/', views.profile_redirect, name = 'profile'),
]
