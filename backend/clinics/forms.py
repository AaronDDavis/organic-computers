from django import forms
from . import models

class ClinicianSetupForm(forms.ModelForm):
    class Meta:
        model = models.ClinicianProfile
        fields = ('clinic', )
        widgets = {'clinic': forms.Select(),}

class Stage2Form(forms.Form):
    fsh          = forms.FloatField(min_value=0, max_value=200,  label='FSH (mIU/mL)')
    lh           = forms.FloatField(min_value=0, max_value=200,  label='LH (mIU/mL)')
    fsh_lh_ratio = forms.FloatField(min_value=0, max_value=20,   label='FSH/LH Ratio')
    amh          = forms.FloatField(min_value=0, max_value=50,   label='AMH (ng/mL)')
    tsh          = forms.FloatField(min_value=0, max_value=100,  label='TSH (mIU/L)')
    prolactin    = forms.FloatField(min_value=0, max_value=500,  label='Prolactin (ng/mL)')
    vit_d3       = forms.FloatField(min_value=0, max_value=150,  label='Vitamin D3 (ng/mL)')
    rbs          = forms.FloatField(min_value=0, max_value=600,  label='Random Blood Sugar (mg/dL)')
    hemoglobin   = forms.FloatField(min_value=0, max_value=25,   label='Haemoglobin (g/dL)')
    bp_systolic  = forms.IntegerField(min_value=60, max_value=250, label='BP Systolic (mmHg)')
    bp_diastolic = forms.IntegerField(min_value=40, max_value=150, label='BP Diastolic (mmHg)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'c-form-input'})


class Stage3Form(forms.Form):
    follicle_no_l = forms.IntegerField(min_value=0, max_value=50,  label='Left Ovary — Follicle Count')
    follicle_no_r = forms.IntegerField(min_value=0, max_value=50,  label='Right Ovary — Follicle Count')
    avg_f_size_l  = forms.FloatField(min_value=0,  max_value=30,   label='Left Ovary — Avg. Follicle Size (mm)')
    avg_f_size_r  = forms.FloatField(min_value=0,  max_value=30,   label='Right Ovary — Avg. Follicle Size (mm)')
    endometrium   = forms.FloatField(min_value=0,  max_value=50,   label='Endometrial Thickness (mm)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'c-form-input'})

