from django.forms import Select, DateInput, ModelForm
from . import models

class PatientSetupForm(ModelForm):
    class Meta:
        model = models.PatientProfile

        fields = ('dob', 'blood_group')

        widgets = {
            'dob': DateInput(),
            'blood_group': Select(),
        }
