from django.db import models
from users.models import User

class Clinic(models.Model):
    name = models.TextField()
    address = models.TextField()
    city = models.TextField()
    # country = models.CharField() with TextChoices

    def __str__(self):
        return f"{self.name}, {self.address}, {self.city}"

class ClinicianProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True, related_name = 'clinician_profile')
    clinic = models.ForeignKey(Clinic, on_delete = models.CASCADE, related_name = 'clinician')
