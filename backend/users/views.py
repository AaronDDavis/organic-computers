# from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import login

from . import forms
from .models import User


class SignupView(CreateView):
    form_class = forms.SignupForm
    template_name = 'users/registration/signup.html'
    success_url = reverse_lazy('setup')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


@login_required
def setup_redirect(request):
    if request.user.role == User.Role.PATIENT:
        return redirect('setup_patient')
    elif request.user.role == User.Role.DOCTOR:
        return redirect('setup_doctor')
    else:
        return redirect('setup_clinician')


class CustomLoginView(LoginView):
    form_class = forms.LoginForm
    template_name = 'users/registration/login.html'


@login_required
def dashboard_redirect(request):
    if request.user.role == User.Role.PATIENT:
        return redirect('dashboard_patient')
    elif request.user.role == User.Role.DOCTOR:
        return redirect('dashboard_doctor')
    else:
        return redirect('dashboard_clinician')


@login_required
def profile_redirect(request):
    if request.user.role == User.Role.PATIENT:
        return redirect('profile_patient')
    elif request.user.role == User.Role.DOCTOR:
        return redirect('profile_doctor')
    else:
        return redirect('profile_clinician')
