from django.views.generic import TemplateView, CreateView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import OuterRef, Subquery, Q, Count, BooleanField, ExpressionWrapper, Prefetch, Exists
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from . import forms
from journeys.models import DiagnosticJourney
from assessments.models import Assessment, AssessmentResult
from patients.models import PatientProfile
from api.loader import stage2_model, stage3_model


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
        clinic = self.request.user.profile.clinic

        # Go through this

        latest_assessment_id_subquery = Assessment.objects.filter(
            journey__patient=OuterRef('patient'),
            journey__clinic=clinic
        ).order_by(
            '-journey__updated_on',
            '-journey__number',
        ).values('id')[:1]

        latest_stage_subquery = Assessment.objects.filter(
            id=Subquery(latest_assessment_id_subquery)
        ).values('stage')[:1]

        active_journeys = DiagnosticJourney.objects.filter(
            clinic=clinic,
            assessments__id=Subquery(latest_assessment_id_subquery)
        ).annotate(
            latest_stage=Subquery(latest_stage_subquery)
        )

        counts = active_journeys.aggregate(
            pending_s2=Count('id', filter=Q(latest_stage='S1')),
            pending_s3=Count('id', filter=Q(latest_stage='S2')),
            complete=Count('id', filter=Q(latest_stage='S3')),
        )

        context['pending_stage2_count'] = counts['pending_s2']
        context['pending_stage3_count'] = counts['pending_s3']
        context['complete_count'] = counts['complete']

        context['total_patients'] = (
            counts['pending_s2'] + counts['pending_s3'] + counts['complete']
        )

        context['pending_queue'] = active_journeys.filter(
            latest_stage__in=['S1', 'S2']
        ).annotate(
            stage_2_complete=ExpressionWrapper(
                Q(latest_stage='S2'), 
                output_field=BooleanField()
            ),
            stage_3_complete=ExpressionWrapper(
                Q(latest_stage='S3'), 
                output_field=BooleanField()
            )
        ).select_related('patient')

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


def unpack_stage_data(json_data, stage):
    """
    Normalises raw JSON assessment data into a simple object
    the templates can dot-access.
    """
    if not json_data:
        return None

    BOOL_FIELDS = {
        'weight_gain', 'hair_growth', 'skin_darkening',
        'hair_loss', 'pimples', 'fast_food', 'exercise',
    }
    CYCLE_MAP = {2: 'Regular', 4: 'Irregular'}

    data = dict(json_data)  # copy so we don't mutate the stored JSON

    # Normalise boolean fields (1/0 → True/False for |yesno filter)
    for field in BOOL_FIELDS:
        if field in data:
            data[field] = bool(data[field])

    # Rename exercise → regular_exercise to match template
    if 'exercise' in data:
        data['regular_exercise'] = data.pop('exercise')

    # Cycle regularity display
    if 'cycle_regularity' in data:
        data['cycle_regularity_display'] = CYCLE_MAP.get(
            data['cycle_regularity'], str(data['cycle_regularity'])
        )

    # Normalise hemoglobin key for stage 2
    if stage == 'S2' and 'hemoglobin' in data:
        data['hb'] = data.pop('hemoglobin')

    return type('StageData', (), data)()  # dot-accessible object


class ClinicianPatientDetailView(LoginRequiredMixin, DetailView):
    model = PatientProfile
    template_name = 'users/clinician/patient_detail.html'
    context_object_name = 'patient'
    pk_url_kwarg = 'patient_id'

    def get_queryset(self):
        return PatientProfile.objects.select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.object
        clinic = self.request.user.clinician_profile.clinic

        journey = (
            DiagnosticJourney.objects
            .filter(patient=patient, clinic=clinic)
            .prefetch_related(
                'assessments',
                'assessments__result',
            )
            .select_related('doctor__user')
            .order_by('-updated_on', '-number')
            .first()
        )

        if not journey:
            context['journey'] = None
            return context

        # Index assessments by stage
        assessments = {a.stage: a for a in journey.assessments.all()}

        s1 = assessments.get('S1')
        s2 = assessments.get('S2')
        s3 = assessments.get('S3')

        # Stage completion flags (used in template conditionals)
        journey.stage1_complete = s1 is not None
        journey.stage2_complete = s2 is not None
        journey.stage3_complete = s3 is not None

        context['journey']       = journey

        # Stage data objects (dot-accessible) — None if stage not done yet
        context['stage1_data']   = unpack_stage_data(s1.data if s1 else None, 'S1')
        context['stage2_data']   = unpack_stage_data(s2.data if s2 else None, 'S2')
        context['stage3_data']   = unpack_stage_data(s3.data if s3 else None, 'S3')

        # Results — None if no result yet
        context['stage1_result'] = getattr(s1, 'result', None) if s1 else None
        context['stage2_result'] = getattr(s2, 'result', None) if s2 else None

        # created_on for submitted_at references in stage 2 & 3 cards
        context['stage2_assessment'] = s2
        context['stage3_assessment'] = s3

        return context



def flag(value, high=None, low=None, elevated_high=None, elevated_low=None):
    """Returns 'flagged', 'elevated', or '' based on thresholds."""
    if (high is not None and value > high) or (low is not None and value < low):
        return 'flagged'
    if (elevated_high is not None and value > elevated_high) or \
       (elevated_low is not None and value < elevated_low):
        return 'elevated'
    return ''


def build_stage1_rows(data):
    return [
        ('Age',             f"{data.get('age')} yrs",                          ''),
        ('BMI',             data.get('bmi'),                                    flag(data.get('bmi', 0), elevated_high=25, high=30)),
        ('Cycle Regularity',{2: 'Regular', 4: 'Irregular'}.get(data.get('cycle_regularity'), '—'), ''),
        ('Cycle Length',    f"{data.get('cycle_length')} days",                 flag(data.get('cycle_length', 0), elevated_high=30, high=35)),
        ('Excess Hair Growth', 'Yes' if data.get('hair_growth') else 'No',     ''),
        ('Skin Darkening',  'Yes' if data.get('skin_darkening') else 'No',     ''),
        ('Hair Loss',       'Yes' if data.get('hair_loss') else 'No',          ''),
        ('Acne / Pimples',  'Yes' if data.get('pimples') else 'No',            ''),
        ('Weight Gain',     'Yes' if data.get('weight_gain') else 'No',        'elevated' if data.get('weight_gain') else ''),
        ('Regular Fast Food','Yes' if data.get('fast_food') else 'No',         'elevated' if data.get('fast_food') else ''),
        ('Regular Exercise','Yes' if data.get('exercise') else 'No',           '' if data.get('exercise') else 'elevated'),
    ]


def build_stage2_rows(data):
    rows = [
        ('FSH',              f"{data.get('fsh')} mIU/mL",                      ''),
        ('LH',               f"{data.get('lh')} mIU/mL",                       flag(data.get('lh', 0), high=10)),
        ('FSH/LH Ratio',     f"{float(data.get('fsh_lh_ratio', 0)):.2f}",      flag(data.get('fsh_lh_ratio', 1), low=1)),
        ('AMH',              f"{data.get('amh')} ng/mL",                        flag(data.get('amh', 0), high=4.5)),
        ('TSH',              f"{data.get('tsh')} mIU/L",                        flag(data.get('tsh', 2), elevated_high=4.5, elevated_low=0.4)),
        ('Prolactin',        f"{data.get('prolactin')} ng/mL",                  flag(data.get('prolactin', 0), elevated_high=25)),
        ('Vitamin D3',       f"{data.get('vit_d3')} ng/mL",                    flag(data.get('vit_d3', 30), low=20, elevated_low=30)),
        ('Random Blood Sugar',f"{data.get('rbs')} mg/dL",                      flag(data.get('rbs', 0), elevated_high=110, high=140)),
        ('Haemoglobin',      f"{data.get('hemoglobin')} g/dL",                 flag(data.get('hemoglobin', 13), low=11, elevated_low=12)),
        ('BP Systolic',      f"{data.get('bp_systolic')} mmHg",                flag(data.get('bp_systolic', 0), elevated_high=130)),
        ('BP Diastolic',     f"{data.get('bp_diastolic')} mmHg",               flag(data.get('bp_diastolic', 0), elevated_high=85)),
    ]
    return rows


def build_stage3_rows(data):
    return [
        ('Left Ovary — Follicle Count',      data.get('follicle_no_l'),         flag(data.get('follicle_no_l', 0), high=11)),
        ('Right Ovary — Follicle Count',     data.get('follicle_no_r'),         flag(data.get('follicle_no_r', 0), high=11)),
        ('Left Ovary — Avg. Follicle Size',  f"{data.get('avg_f_size_l')} mm",  ''),
        ('Right Ovary — Avg. Follicle Size', f"{data.get('avg_f_size_r')} mm",  ''),
        ('Endometrial Thickness',            f"{data.get('endometrium')} mm",    flag(data.get('endometrium', 10), low=7, elevated_low=14)),
    ]


class ClinicianPatientDetailView(LoginRequiredMixin, DetailView):
    model = PatientProfile
    template_name = 'users/clinician/patient_detail.html'
    context_object_name = 'patient'
    pk_url_kwarg = 'patient_id'

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
        context['stage1_rows']      = build_stage1_rows(s1.data) if s1 else None
        context['stage2_rows']      = build_stage2_rows(s2.data) if s2 else None
        context['stage3_rows']      = build_stage3_rows(s3.data) if s3 else None

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

            assessment = Assessment.objects.create(
                journey=journey,
                stage=Assessment.Stage.STAGE_2,
                data=cleaned_data,
            )

            result = run_prediction(stage2_model, cleaned_data, 'stage2')

            AssessmentResult.objects.create(
                assessment=assessment,
                score=result['confidence'],
                risk=result['risk'],
                top_factors=result['top_factors'],
                specialist=result['specialist'],
                clinical_focus=result['clinical_focus'],
                next_step=result['next_step'],
                recommendation=result['recommendation_text']
            )

            messages.success(request, 'Stage 2 submitted successfully.')
            return redirect('clinician_patient_detail', patient_id=journey.patient_id)

        messages.error(request, 'Please correct the errors below.')
        return redirect('clinician_patient_detail', patient_id=journey.patient_id)


class ClinicianStage3SubmitView(LoginRequiredMixin, View):
    def post(self, request, journey_id):
        journey = get_object_or_404(
            DiagnosticJourney,
            id=journey_id,
            clinic=request.user.clinician_profile.clinic
        )
        form = forms.Stage3Form(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data

            assessment = Assessment.objects.create(
                journey=journey,
                stage=Assessment.Stage.STAGE_3,
                data=cleaned_data,
            )

            result = run_prediction(stage3_model, cleaned_data, 'stage3')

            AssessmentResult.objects.create(
                assessment=assessment,
                score=result['confidence'],
                risk=result['risk'],
                top_factors=result['top_factors'],
                specialist=result['specialist'],
                clinical_focus=result['clinical_focus'],
                next_step=result['next_step'],
                recommendation=result['recommendation_text']
            )

            messages.success(request, 'Stage 3 submitted successfully.')
            return redirect('clinician_patient_detail', patient_id=journey.patient_id)

        messages.error(request, 'Please correct the errors below.')
        return redirect('clinician_patient_detail', patient_id=journey.patient_id)


class ClinicianStage2EditView(LoginRequiredMixin, View):
    def post(self, request, journey_id):
        journey = get_object_or_404(
            DiagnosticJourney,
            id=journey_id,
            clinic=request.user.clinician_profile.clinic
        )
        form = forms.Stage2Form(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data

            assessment = get_object_or_404(Assessment, journey=journey, stage=Assessment.Stage.STAGE_2)
            assessment.data = cleaned_data
            assessment.save()

            # Re-run prediction and overwrite existing result
            result = run_prediction(stage2_model, cleaned_data, 'stage2')
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
