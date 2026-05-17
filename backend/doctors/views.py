# from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.db.models import OuterRef, Subquery

from . import forms
from assessments.models import Assessment, AssessmentResult
from patients.models import PatientProfile

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


class DoctorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/doctor/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['high_risk_count'] = AssessmentResult.objects.filter(
            risk = AssessmentResult.RiskLabel.HIGH,
            assessment__journey__patient__in = self.request.user.profile.patients
            ).count()

        latest_assessment_subquery = Assessment.objects.filter(
            journey__patient = OuterRef('journey__patient')
        ).order_by(
            '-journey__updated_on',
            '-journey__number',
        ).values('id')[:1]

        context['stage3_wait_count'] = Assessment.objects.filter(
            id = Subquery(latest_assessment_subquery),
            stage = Assessment.Stage.STAGE_2
        ).values('journey__patient').distinct().count()

        return context
