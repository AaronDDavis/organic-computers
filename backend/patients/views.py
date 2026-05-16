from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.urls import reverse_lazy

from . import forms

# Need to add user passes test mixin: to ensure only patients call views like patientprofileview and similarly for doctors

class PatientSetupView(LoginRequiredMixin, CreateView):
    form_class = forms.PatientSetupForm
    template_name = 'users/registration/patient_setup.html'
    success_url = reverse_lazy('dashboard_patient')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PatientDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/patient/dashboard/dashboard.html'
    # Not an error. File structure is this way, because of many partial files for dashboard

    def get_context_data(self, **kwargs):
        context_data =  super().get_context_data(**kwargs)
        
        context_data['latest_journey'] = self.request.user.profile.journeys.order_by('-updated_on').first()

        context_data['latest_assessment'] = context_data['latest_journey'].latest_assessment if context_data['latest_journey'] else None

        context_data['latest_result'] = context_data['latest_assessment'].result if (context_data['latest_assessment'] and hasattr(context_data['latest_assessment'], 'result')) else None

        context_data['specialist_label'] = None
        # Need to edit specialist_label

        return context_data


class PatientProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/patient/profile.html'

