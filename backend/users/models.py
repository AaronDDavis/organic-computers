from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from encrypted_model_fields.fields import EncryptedCharField

class User(AbstractUser):
    class Role(models.TextChoices):
        DOCTOR = 'DR', _('Doctor')
        PATIENT = 'PT', _('Patient')
        CLINICIAN = 'CL', _('Clinician')

    first_name = EncryptedCharField(max_length = 150, blank = True, verbose_name = 'first name')
    last_name = EncryptedCharField(max_length = 150, blank = True, verbose_name = 'last name')
    role = models.CharField(max_length = 2, choices = Role.choices)
    REQUIRED_FIELDS = ['email', 'role']
