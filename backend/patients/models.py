from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User

class PatientProfile(models.Model):
    class BloodGroup(models.TextChoices):
        A_POS = 'A+', _('A+')
        A_NEG = 'A-', _('A-')
        B_POS = 'B+', _('B+')
        B_NEG = 'B-', _('B-')
        O_POS = 'O+', _('O+')
        O_NEG = 'O-', _('O-')
        AB_POS = 'AB+', _('AB+')
        AB_NEG = 'AB-', _('AB-')
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True, related_name = 'profile')
    dob = models.DateField(null = True, blank = True)
    blood_group = models.CharField(max_length = 3, choices = BloodGroup.choices, null = True, blank = True)

    @property
    def latest_journey(self):
        return self.journeys.order_by('-updated_on', '-number').first()
