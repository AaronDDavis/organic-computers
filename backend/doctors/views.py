# from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, View
from django.urls import reverse_lazy
from django.db.models import OuterRef, Subquery, Exists, Prefetch
from django.shortcuts import redirect, get_object_or_404

from . import forms
from assessments.models import Assessment, AssessmentResult, ClinicalNote
from journeys.models import DiagnosticJourney
from patients.models import PatientProfile
from api.utils import get_phenotype

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
            assessment__journey__patient__in = self.request.user.doctor_profile.patients
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


class DoctorPatientListView(LoginRequiredMixin, ListView):
    model = DiagnosticJourney
    template_name = 'users/doctor/patient_list.html'
    context_object_name = 'journeys'

    def get_queryset(self):
        journeys = self.request.user.doctor_profile.journeys
        self.journeys = journeys.all().select_related(
            'patient__user'
            )
        '''.prefetch_related(
                Prefetch(
                    'assessments',
                    queryset=Assessment.objects.select_related('result')
                    ))'''
        return self.journeys


class DoctorPatientDetailView(LoginRequiredMixin, DetailView):
    model = PatientProfile
    template_name = 'users/doctor/patient_detail.html'
    context_object_name = 'patient'
    pk_url_kwarg = 'user_id'

    def get_object(self, queryset = None):
        self.patient = PatientProfile.objects.filter(pk=self.kwargs['user_id']).select_related('user').first()
        return self.patient
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        journey = self.patient.latest_journey

        assessments = {a.stage: a for a in journey.assessments.all()}
        s1 = assessments.get('S1')
        s2 = assessments.get('S2')
        s3 = assessments.get('S3')

        data = s1.data
        data2 = s2.data or {}
        data3 = s3.data or {}

        context['stage1_data'] = {
            'cycle_irregular': data.get('Cycle(R/I)') == 2,  # 2 = Irregular, 1 = Regular
            'cycle_regularity_display': 'Irregular' if data.get('Cycle(R/I)') == 2 else 'Regular',
            'cycle_length': data.get('Cycle length(days)'),
            'age': data.get('Age (yrs)'),
            'bmi': data.get('BMI'),
            'weight_gain': data.get('Weight gain(Y/N)') == 1,
            'hair_growth': data.get('hair growth(Y/N)') == 1,
            'skin_darkening': data.get('Skin darkening (Y/N)') == 1,
            'pimples': data.get('Pimples(Y/N)') == 1,
            'fast_food': data.get('Fast food (Y/N)') == 1,
            'hip': data.get('Hip(inch)'),
            'waist': data.get('Waist(inch)'),
            'waist_hip_ratio': data.get('Waist:Hip Ratio'),
            'weight': data.get('Weight (Kg)'),
            'height': data.get('Height(Cm)'),
            'hair_loss': data.get('Hair loss(Y/N)') == 1,
            'regular_exercise': data.get('Reg.Exercise(Y/N)') == 1,
        }
        
        context['stage2_data'] = {
            'fsh': data2.get('FSH(mIU/mL)'),
            'lh': data2.get('LH(mIU/mL)'),
            'fsh_lh_ratio': data2.get('FSH/LH'),
            'tsh': data2.get('TSH (mIU/L)'),
            'amh': data2.get('AMH(ng/mL)'),
            'prl': data2.get('PRL(ng/mL)'),
            'vit_d3': data2.get('Vit D3 (ng/mL)'),
            'rbs': data2.get('RBS(mg/dl)'),
            'hb': data2.get('Hb(g/dl)'),
            'bp_systolic': data2.get('BP _Systolic (mmHg)'),
            'bp_diastolic': data2.get('BP _Diastolic (mmHg)'),
        }

        context['stage3_data'] = {
            'follicle_no_left': data3.get('Follicle No. (L)'),
            'follicle_no_right': data3.get('Follicle No. (R)'),
            'avg_f_size_l': data3.get('Avg. F size (L) (mm)'),
            'avg_follicle_size_right': data3.get('Avg. F size (R) (mm)'),
            'endometrium': data3.get('Endometrium (mm)'),
        }

        descriptions = {
            0: "Characterized by classical ovulatory dysfunction combined with clinical or biochemical hyperandrogenism.",
            1: "Predominantly reproductive variant showing marked alterations in LH/FSH ratios and follicle counts.",
            2: "Associated with insulin resistance metabolic risk factors, elevated BMI, higher waist-hip ratio, and metabolic markers."
        }
        
        criteria = {
            0: "Hyperandrogenism + Ovulatory Dysfunction",
            1: "Ovulatory Dysfunction + Polycystic Ovaries",
            2: "Weight Gain/BMI + Hyperandrogenism Symptoms + Metabolic Markers"
        }

        phenotype_subtype = get_phenotype({**(s1.data), **(s2.data), **(s3.data)})
        phenotype_subtype['description'] = descriptions.get(phenotype_subtype['cluster'])
        phenotype_subtype['criteria'] = criteria.get(phenotype_subtype['cluster'])
        context['phenotype_subtype'] = phenotype_subtype
        context['journey'] = journey
        return context



class DoctorSaveNoteView(LoginRequiredMixin, View):
    def post(self, request, journey_id):
        journey = get_object_or_404(DiagnosticJourney, journey__id=journey_id)
        content = request.POST.get('clinical_note', '').strip()

        if content:
            ClinicalNote.objects.create(
                assessment=journey.latest_assessment,
                content=content
            )

        return redirect('doctor_patient_detail', journey.patient.user_id)
