# from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.urls import reverse_lazy

from . import forms

# Need to add user passes test mixin: to ensure only patients call views like patientprofileview and similarly for doctors

class DoctorSetupView(LoginRequiredMixin, CreateView):
    form_class = forms.DoctorSetupForm
    template_name = 'users/registration/doctor_setup.html'
    success_url = reverse_lazy('dashboard_doctor')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class DoctorProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/doctor/profile.html'

