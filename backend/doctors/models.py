from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User
from patients.models import PatientProfile

class DoctorProfile(models.Model):
    class Specialty(models.TextChoices):
        ENDOCRINOLOGIST = 'END', _('Endocrinologist')
        GYNECOLOGIST = 'GYN', _('Gynecologist')
        GENERAL = 'GEN', _('General Practitioner')
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True, related_name = 'doctor_profile')
    specialty = models.CharField(max_length = 3, choices = Specialty.choices)
    hospital = models.CharField(max_length = 128)

    @property
    def patients(self):
        return PatientProfile.objects.filter(journeys__doctor = self).distinct()
