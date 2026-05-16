from django.db import models
from django.utils.translation import gettext_lazy as _

from patients.models import PatientProfile
from doctors.models import DoctorProfile


class DiagnosticJourney(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = 'PROG', _('In Progress')
        COMPLETED = 'COMP', _('Completed')
    
    patient = models.ForeignKey(PatientProfile, on_delete = models.CASCADE, related_name = 'journeys')
    doctor = models.ForeignKey(DoctorProfile, null = True, on_delete = models.SET_NULL, related_name = 'journeys')
    number = models.PositiveSmallIntegerField(editable = False)
    status = models.CharField(max_length = 4, choices = Status.choices, default = Status.IN_PROGRESS)
    created_on = models.DateField(auto_now_add = True)
    updated_on = models.DateField(auto_now = True)

    @property
    def latest_assessment(self):
        return self.assessments.order_by('-stage').first()

