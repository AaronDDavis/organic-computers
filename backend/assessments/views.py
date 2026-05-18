from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect

from .models import Assessment, AssessmentResult
from journeys.models import DiagnosticJourney
from . import forms
from .utils import map_to_backend
from api.utils import run_prediction
from api.loader import stage1_model, stage2_model


class AssessmentCreateView(LoginRequiredMixin, FormView):
    template_name = 'assessments/assessment_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.journey = get_object_or_404(
            DiagnosticJourney,
            pk = kwargs['pk'],
            patient__user = request.user
        )
        self.stage = kwargs['stage']
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_class(self):
        return forms.StageOneForm if self.stage == 'stage1' else forms.StageTwoForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['journey'] = self.journey
        context_data['stage'] = self.stage
        return context_data

    def form_valid(self, form):
        cleaned_data = map_to_backend(form.cleaned_data)
        stage = Assessment.Stage.STAGE_1 if self.stage == 'stage1' else Assessment.Stage.STAGE_2
        
        assessment = Assessment.objects.create(
            journey = self.journey,
            stage = stage,
            data = cleaned_data,
        )
        # Auto_add_now automatically adds the created_on date
        
        model = stage1_model if self.stage == 'Stage_1' else stage2_model
        result = run_prediction(model, cleaned_data, self.stage)

        AssessmentResult.objects.create(
            assessment = assessment,
            score = result['confidence'],
            risk = result['risk'],
            top_factors = result['top_factors'],
            specialist = result['specialist'],
            clinical_focus = result['clinical_focus'],
            next_step = result['next_step'],
            recommendation = result['recommendation_text']
        )
        
        return redirect('journey_detail', pk = self.journey.pk)

