from django.views.generic import TemplateView, CreateView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import OuterRef, Subquery, Prefetch, Exists, Sum, Case, When, IntegerField
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from . import forms
from journeys.models import DiagnosticJourney
from assessments.models import Assessment, AssessmentResult
from patients.models import PatientProfile
from doctors.models import DoctorProfile
from api.utils import run_prediction
from api.loader import stage2_model, stage3_model
from assessments.utils import map_to_backend, float_field

class ClinicianProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/clinician/profile.html'


class ClinicianSetupView(LoginRequiredMixin, CreateView):
    form_class = forms.ClinicianSetupForm
    template_name = 'users/registration/clinician_setup.html'
    success_url = reverse_lazy('dashboard_clinician')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ClinicianDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/clinician/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic = self.request.user.clinician_profile.clinic

        # Go through this

        latest_assessment_id_subquery_1 = Assessment.objects.filter(
            journey__patient=OuterRef('patient'),
            journey__clinic=clinic
        ).order_by(
            '-journey__updated_on',
            '-journey__number',
        ).values('id')[:1]

        latest_assessment_id_subquery_2 = Assessment.objects.filter(
            journey__patient=OuterRef(OuterRef('patient')),
            journey__clinic=clinic
        ).order_by(
            '-journey__updated_on',
            '-journey__number',
        ).values('id')[:1]

        latest_stage_subquery = Assessment.objects.filter(
            id=Subquery(latest_assessment_id_subquery_2)
        ).values('stage')[:1]

        stage1_done = Assessment.objects.filter(journey=OuterRef('pk'), stage='S1')
        stage2_done = Assessment.objects.filter(journey=OuterRef('pk'), stage='S2')
        stage3_done = Assessment.objects.filter(journey=OuterRef('pk'), stage='S3')

        active_journeys = DiagnosticJourney.objects.filter(
            clinic=clinic,
            assessments__id=Subquery(latest_assessment_id_subquery_1)
        ).annotate(
            latest_stage=Subquery(latest_stage_subquery)
        )

        context['pending_queue'] = active_journeys.filter(
            latest_stage__in=['S1', 'S2']
        ).distinct().annotate(
            stage1_complete=Exists(stage1_done),
            stage2_complete=Exists(stage2_done),
            stage3_complete=Exists(stage3_done),
        ).select_related('patient')

        stage1_completed_count = context['pending_queue'].aggregate(
            total_stage1_complete=Sum(
                Case(
                    When(stage1_complete=True, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )['total_stage1_complete'] or 0  # 'or 0' handles the case where the queryset is empty

        stage2_completed_count = context['pending_queue'].aggregate(
            total_stage2_complete=Sum(
                Case(
                    When(stage2_complete=True, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )['total_stage2_complete'] or 0  # 'or 0' handles the case where the queryset is empty

        stage3_completed_count = context['pending_queue'].aggregate(
            total_stage3_complete=Sum(
                Case(
                    When(stage3_complete=True, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )['total_stage3_complete'] or 0  # 'or 0' handles the case where the queryset is empty

        context['pending_stage2_count'] = stage2_completed_count - stage1_completed_count
        context['pending_stage3_count'] = stage3_completed_count - stage2_completed_count
        context['complete_count'] = stage3_completed_count

        context['total_patients'] = stage1_completed_count


        return context
    

class ClinicianPatientListView(LoginRequiredMixin, ListView):
    model = DiagnosticJourney
    template_name = 'users/clinician/patient_list.html'
    context_object_name = 'journeys'

    def get_queryset(self):
        clinic = self.request.user.clinician_profile.clinic

        latest_assessment_id_subquery = Assessment.objects.filter(
            journey__patient=OuterRef('patient'),
            journey__clinic=clinic
        ).order_by(
            '-journey__updated_on',
            '-journey__number',
            '-stage',
        ).values('id')[:1]

        stage1_done = Assessment.objects.filter(journey=OuterRef('pk'), stage='S1')
        stage2_done = Assessment.objects.filter(journey=OuterRef('pk'), stage='S2')
        stage3_done = Assessment.objects.filter(journey=OuterRef('pk'), stage='S3')

        self.journeys = DiagnosticJourney.objects.filter(
            clinic=clinic,
            assessments__id=Subquery(latest_assessment_id_subquery)
        ).distinct().annotate(
            stage1_complete=Exists(stage1_done),
            stage2_complete=Exists(stage2_done),
            stage3_complete=Exists(stage3_done),
        ).select_related(
            'doctor__user',
            'patient__user',
        ).prefetch_related(
            Prefetch('assessments', queryset=Assessment.objects.select_related('result'))
        )

        return self.journeys



def flag(value, high=None, low=None, elevated_high=None, elevated_low=None):
    """Returns 'flagged', 'elevated', or '' based on thresholds."""
    if (high is not None and value > high) or (low is not None and value < low):
        return 'flagged'
    if (elevated_high is not None and value > elevated_high) or \
       (elevated_low is not None and value < elevated_low):
        return 'elevated'
    return ''


class ClinicianPatientDetailView(LoginRequiredMixin, DetailView):
    model = PatientProfile
    template_name = 'users/clinician/patient_detail.html'
    context_object_name = 'patient'
    pk_url_kwarg = 'user_id'

    def get_queryset(self):
        return PatientProfile.objects.select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.object
        clinic = self.request.user.clinician_profile.clinic

        journey = (
            DiagnosticJourney.objects
            .filter(patient=patient, clinic=clinic)
            .prefetch_related('assessments__result')
            .select_related('doctor__user')
            .order_by('-updated_on', '-number')
            .first()
        )

        if not journey:
            context['journey'] = None
            return context

        assessments = {a.stage: a for a in journey.assessments.all()}
        s1 = assessments.get('S1')
        s2 = assessments.get('S2')
        s3 = assessments.get('S3')

        journey.stage1_complete = s1 is not None
        journey.stage2_complete = s2 is not None
        journey.stage3_complete = s3 is not None

        context['journey']          = journey
        context['stage2_assessment'] = s2
        context['stage3_assessment'] = s3
        context['stage1_result']    = getattr(s1, 'result', None) if s1 else None
        context['stage2_result']    = getattr(s2, 'result', None) if s2 else None

        # Pre-built rows: list of (label, value, css_class)
        context['stage1_rows']      = s1.data
        context['stage2_rows']      = s2.data if s2 else None
        context['stage3_rows']      = s3.data if s3 else None

        # Forms (pass back with errors if session has them)
        context['stage2_form']      = forms.Stage2Form()
        context['stage3_form']      = forms.Stage3Form()

        return context


class ClinicianStage2SubmitView(LoginRequiredMixin, View):
    def post(self, request, journey_id):
        journey = get_object_or_404(
            DiagnosticJourney,
            id=journey_id,
            clinic=request.user.clinician_profile.clinic
        )
        form = forms.Stage2Form(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data

            '''
            fsh = cleaned_data.get('fsh')
            lh = cleaned_data.get('lh')

            cleaned_data['fsh_lh_ratio'] = round(fsh / lh, 2) if fsh is not None and lh else 0
            '''

            cleaned_data = map_to_backend(cleaned_data)

            assessment = Assessment.objects.create(
                journey=journey,
                stage=Assessment.Stage.STAGE_2,
                data=cleaned_data,
            )

            cleaned_data = {**assessment.previous.data, **cleaned_data}

            result = run_prediction(stage2_model, cleaned_data, Assessment.Stage.STAGE_2)

            AssessmentResult.objects.create(
                assessment=assessment,
                score=result['confidence'],
                risk=result['risk'],
                top_factors=result['top_factors'],
                specialist={
                'Endocrinologist': DoctorProfile.Specialty.ENDOCRINOLOGIST,
                'Gynecologist': DoctorProfile.Specialty.GYNECOLOGIST,
                'General Practitioner': DoctorProfile.Specialty.GENERAL,
                }.get(result['specialist'], DoctorProfile.Specialty.GENERAL),
                clinical_focus=result['clinical_focus'],
                next_step=result['next_step'],
                recommendation=result['recommendation_text']
            )

            messages.success(request, 'Stage 2 submitted successfully.')
            return redirect('clinician_patient_detail', user_id=journey.patient.user_id)

        messages.error(request, 'Please correct the errors below.')
        return redirect('clinician_patient_detail', user_id=journey.patient.user_id)


class ClinicianStage3SubmitView(LoginRequiredMixin, View):
    def post(self, request, journey_id):
        journey = get_object_or_404(
            DiagnosticJourney,
            id=journey_id,
            clinic=request.user.clinician_profile.clinic
        )
        form = forms.Stage3Form(request.POST)
        if form.is_valid():
            cleaned_data = map_to_backend(form.cleaned_data)

            assessment = Assessment.objects.create(
                journey=journey,
                stage=Assessment.Stage.STAGE_3,
                data=cleaned_data,
            )

            cleaned_data = {**assessment.previous.previous.data, **assessment.previous.data, **cleaned_data}

            result = run_prediction(stage3_model, cleaned_data, Assessment.Stage.STAGE_3)

            AssessmentResult.objects.create(
                assessment=assessment,
                score=result['confidence'],
                risk=result['risk'],
                top_factors=result['top_factors'],
                specialist={
                'Endocrinologist': DoctorProfile.Specialty.ENDOCRINOLOGIST,
                'Gynecologist': DoctorProfile.Specialty.GYNECOLOGIST,
                'General Practitioner': DoctorProfile.Specialty.GENERAL,
                }.get(result['specialist'], DoctorProfile.Specialty.GENERAL),
                clinical_focus=result['clinical_focus'],
                next_step=result['next_step'],
                recommendation=result['recommendation_text']
            )

            journey.status = DiagnosticJourney.Status.COMPLETED

            messages.success(request, 'Stage 3 submitted successfully.')
            return redirect('clinician_patient_detail', user_id=journey.patient.user_id)

        messages.error(request, 'Please correct the errors below.')
        return redirect('clinician_patient_detail', user_id=journey.patient.user_id)


class ClinicianStage2EditView(LoginRequiredMixin, View):
    def post(self, request, journey_id):
        journey = get_object_or_404(
            DiagnosticJourney,
            id=journey_id,
            clinic=request.user.clinician_profile.clinic
        )
        form = forms.Stage2Form(request.POST)
        if form.is_valid():
            fsh = cleaned_data.get('fsh')
            lh = cleaned_data.get('lh')
            cleaned_data = form.cleaned_data
            cleaned_data['fsh_lh_ratio'] = round(fsh / lh, 2) if fsh is not None and lh else 0

            assessment = get_object_or_404(Assessment, journey=journey, stage=Assessment.Stage.STAGE_2)
            assessment.data = cleaned_data
            assessment.save()

            # Re-run prediction and overwrite existing result
            # result = run_prediction(stage2_model, cleaned_data, 'stage2')
            AssessmentResult.objects.update_or_create(
                assessment=assessment,
                defaults={
                    'score': result['confidence'],
                    'risk': result['risk'],
                    'top_factors': result['top_factors'],
                    'specialist': result['specialist'],
                    'clinical_focus': result['clinical_focus'],
                    'next_step': result['next_step'],
                    'recommendation': result['recommendation_text'],
                }
            )

            messages.success(request, 'Stage 2 updated.')
            return redirect('clinician_patient_detail', patient_id=journey.patient_id)

        messages.error(request, 'Please correct the errors below.')
        return redirect('clinician_patient_detail', patient_id=journey.patient_id)


class ClinicianStage3EditView(LoginRequiredMixin, View):
    def post(self, request, journey_id):
        journey = get_object_or_404(
            DiagnosticJourney,
            id=journey_id,
            clinic=request.user.clinician_profile.clinic
        )
        form = forms.Stage3Form(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data

            assessment = get_object_or_404(Assessment, journey=journey, stage=Assessment.Stage.STAGE_3)
            assessment.data = cleaned_data
            assessment.save()

            result = run_prediction(stage3_model, cleaned_data, 'stage3')
            AssessmentResult.objects.update_or_create(
                assessment=assessment,
                defaults={
                    'score': result['confidence'],
                    'risk': result['risk'],
                    'top_factors': result['top_factors'],
                    'specialist': result['specialist'],
                    'clinical_focus': result['clinical_focus'],
                    'next_step': result['next_step'],
                    'recommendation': result['recommendation_text'],
                }
            )

            messages.success(request, 'Stage 3 updated.')
            return redirect('clinician_patient_detail', patient_id=journey.patient_id)

        messages.error(request, 'Please correct the errors below.')
        return redirect('clinician_patient_detail', patient_id=journey.patient_id)
