from django.db import models
from django.utils.translation import gettext_lazy as _

from doctors.models import DoctorProfile
from journeys.models import DiagnosticJourney

class Assessment(models.Model):
    class Stage(models.TextChoices):
        STAGE_1 = 'S1', _('Stage 1')
        STAGE_2 = 'S2', _('Stage 2')
        STAGE_3 = 'S3', _('Stage 3')
        
    journey = models.ForeignKey(DiagnosticJourney, on_delete = models.CASCADE, related_name = 'assessments')
    stage = models.CharField(max_length = 2, choices = Stage.choices, editable = False)
    data = models.JSONField(default = dict)
    created_on = models.DateField(auto_now_add = True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['journey', 'stage'],
                name = 'unique_stage_per_journey'
            )
        ]

class AssessmentResult(models.Model):
    class RiskLabel(models.TextChoices):
        HIGH = 'HIGH', _('High')
        MODERATE = 'MOD', _('Moderate')
        LOW = 'LOW', _('Low')
    
    assessment = models.OneToOneField(Assessment, on_delete = models.CASCADE, related_name = 'result')
    created_on = models.DateField(auto_now_add = True)
    risk = models.CharField(max_length = 4, choices = RiskLabel.choices, editable = False)
    score = models.DecimalField(max_digits = 5, decimal_places = 4, editable = False)
    top_factors = models.JSONField(default = list)
    specialist = models.CharField(max_length = 3, choices = DoctorProfile.Specialty.choices)
    clinical_focus = models.TextField()
    next_step = models.TextField()
    recommendation = models.TextField()


class ClinicalNote(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete = models.CASCADE, related_name = 'doctor_notes')

    created_on = models.DateField(auto_now_add = True)
    updated_on = models.DateField(auto_now = True)

    content = models.TextField()
