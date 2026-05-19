from django import forms
from .utils import yes_no_field

class StageOneForm(forms.Form):
    age = forms.IntegerField(
        label = 'Age',
        widget = forms.NumberInput()
    )

    weight = forms.IntegerField(
        label = 'Weight',
        widget = forms.NumberInput()
    )

    height = forms.IntegerField(
        label = 'Height',
        widget = forms.NumberInput()
    )

    bmi = forms.FloatField(
        label = 'BMI',
        widget = forms.NumberInput()
    )

    cycle_regularity = forms.ChoiceField(
        label = 'Cycle regularity',
        choices = [(2, 'Regular'), (4, 'Irregular')],
        widget = forms.Select()
    )

    cycle_length = forms.IntegerField(
        label = 'Cycle length (days)',
        widget = forms.NumberInput()
    )

    waist = forms.IntegerField(
        label = 'Waist length',
        widget = forms.NumberInput()
    )

    hip = forms.IntegerField(
        label = 'Hip length',
        widget = forms.NumberInput()
    )

    waist_hip_ratio = forms.IntegerField(
        label = 'Waist:Hip Ratio',
        widget = forms.NumberInput()
    )

    weight_gain     = yes_no_field('Weight gain')
    hair_growth     = yes_no_field('Excess hair growth')
    skin_darkening  = yes_no_field('Skin darkening')
    hair_loss       = yes_no_field('Hair loss')
    pimples         = yes_no_field('Acne / pimples')
    fast_food       = yes_no_field('Regular fast food intake')
    exercise        = yes_no_field('Regular exercise')


'''
class StageTwoForm(StageOneForm):
    fsh = float_field('FSH level (mIU/mL)', placeholder='5.8')
    lh = float_field('LH level (mIU/mL)', placeholder='11.2')
    fsh_lh_ratio = float_field('FSH/LH ratio', placeholder='0.52')

    tsh = float_field('TSH level (mIU/L)', placeholder='2.1')
    amh = float_field('AMH level (ng/mL)', placeholder='5.4')

    prolactin = float_field('Prolactin level (ng/mL)', placeholder='18.0')
    vit_d3 = float_field('Vitamin D3 (ng/mL)', placeholder='21.5')
    rbs = float_field('Random blood sugar (mg/dl)', placeholder='135')
    hemoglobin = float_field('Hemoglobin (g/dl)', placeholder='12.8')

    bp_systolic = float_field('Systolic blood pressure (mmHg)', placeholder='118')
    bp_diastolic = float_field('Diastolic blood pressure (mmHg)', placeholder='76')
'''