from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect

from .models import Assessment, AssessmentResult
from journeys.models import DiagnosticJourney
from doctors.models import DoctorProfile
from . import forms
from .utils import map_to_backend
from api.utils import run_prediction
from api.loader import stage1_model


class AssessmentCreateView(LoginRequiredMixin, FormView):
    template_name = 'assessments/assessment_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.journey = get_object_or_404(
            DiagnosticJourney,
            pk = kwargs['pk'],
            patient__user = request.user
        )
        self.stage = Assessment.Stage.STAGE_1
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_class(self):
        return forms.StageOneForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['journey'] = self.journey
        return context_data

    def form_valid(self, form):
        cleaned_data = map_to_backend(form.cleaned_data)
        
        assessment = Assessment.objects.create(
            journey = self.journey,
            stage = self.stage,
            data = cleaned_data,
        )
        # Auto_add_now automatically adds the created_on date
        
        result = run_prediction(stage1_model, cleaned_data, self.stage)

        AssessmentResult.objects.create(
            assessment = assessment,
            score = result['confidence'],
            risk = result['risk'],
            top_factors = result['top_factors'],
            specialist = {
                'Endocrinologist': DoctorProfile.Specialty.ENDOCRINOLOGIST,
                'Gynecologist': DoctorProfile.Specialty.GYNECOLOGIST,
                'General Practitioner': DoctorProfile.Specialty.GENERAL,
                }.get(result['specialist'], DoctorProfile.Specialty.GENERAL),
            clinical_focus = result['clinical_focus'],
            next_step = result['next_step'],
            recommendation = result['recommendation_text']
        )
        
        return redirect('journey_detail', pk = self.journey.pk)

