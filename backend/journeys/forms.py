from django import forms
from .models import DiagnosticJourney

class JourneyForm(forms.ModelForm):
    class Meta:
        model = DiagnosticJourney
        fields = []
