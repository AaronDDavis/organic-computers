# from django.shortcuts import render
from django.views.generic import DetailView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect

from .models import DiagnosticJourney
from assessments.models import Assessment
from doctors.models import DoctorProfile
from clinics.models import Clinic
from .utils import build_stage_context

class JourneyDetailView(LoginRequiredMixin, DetailView):
    model = DiagnosticJourney
    template_name = 'journeys/journey_detail.html'
    context_object_name = 'journey'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        journey = self.object

        context['stages'] = build_stage_context(journey)
        context['num_completed_stages'] = journey.assessments.count()
        context['assigned_clinic'] = None
        context['assigned_doctor'] = DoctorProfile.objects.first()  # TODO: wire up recommendation logic

        return context


class JourneyListView(LoginRequiredMixin, ListView):
    model = DiagnosticJourney
    template_name = 'journeys/journey_list.html'
    context_object_name = 'journeys'

    def get_queryset(self):
        return super().get_queryset().filter(patient__user = self.request.user).order_by('-updated_on', '-number')
    
    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['status'] = DiagnosticJourney.Status
        return context_data


class JourneyCreateView(LoginRequiredMixin, View):
    def get(self, request):
        journey = DiagnosticJourney.objects.create(
            patient = request.user.profile,
            number = request.user.profile.journeys.count() + 1
        )
        return redirect(reverse('create_assessment', args=[journey.pk, 'stage1']))
    


class DoctorConfirmView(LoginRequiredMixin, View):
    def post(self, request, pk):
        journey = get_object_or_404(DiagnosticJourney, pk = pk, patient__user = request.user)
        doctor_id = request.POST.get('doctor_id')
        journey.doctor = get_object_or_404(DoctorProfile, user__pk = doctor_id)
        journey.save()
        return redirect('journey_detail', pk=journey.pk)


class DoctorSearchView(LoginRequiredMixin, ListView):
    model = DoctorProfile
    template_name = 'journeys/doctor_search.html'

    def get_queryset(self):
        self.assessment = get_object_or_404(DiagnosticJourney, pk = self.kwargs['pk'], patient = self.request.user.profile).latest_assessment
        return DoctorProfile.objects.filter(specialty = self.assessment.result.specialist)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['journey'] = self.assessment.journey
        return context


class ClinicConfirmView(LoginRequiredMixin, View):
    def post(self, request, pk):
        journey = get_object_or_404(DiagnosticJourney, pk = pk, patient__user = request.user)
        clinic_id = request.POST.get('clinic_id')
        journey.clinic = get_object_or_404(Clinic, pk = clinic_id)
        journey.save()
        return redirect('journey_detail', pk=journey.pk)


class ClinicSearchView(LoginRequiredMixin, ListView):
    model = Clinic
    template_name = 'journeys/clinic_search.html'

    # Later filter queryset based on clinic country and user country

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['journey'] = get_object_or_404(DiagnosticJourney, pk = self.kwargs['pk'], patient__user = self.request.user)
        return context
