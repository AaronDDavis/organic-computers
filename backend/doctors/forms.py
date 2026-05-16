from django.forms import TextInput, Select, ModelForm
from . import models

class DoctorSetupForm(ModelForm):
    class Meta:
        model = models.DoctorProfile

        fields = ('hospital', 'specialty')

        widgets = {
            'hospital': TextInput(),
            'specialty': Select(),
        }
