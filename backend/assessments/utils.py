from django.forms import ChoiceField, RadioSelect, Select, FloatField, NumberInput

def yes_no_field(label):
    return ChoiceField(
        label = label,
        choices = [(0, 'No'), (1, 'Yes')],
        widget = Select()
    )

def radio_yes_no_field(label):
    return ChoiceField(
        label = label,
        choices = [(0, 'No'), (1, 'Yes')],
        widget = RadioSelect()
    )

def float_field(label, **kwargs):
    return FloatField(
        label = label,
        widget = NumberInput(attrs = kwargs)
    )

FIELD_MAP = {
    'age':            'Age (yrs)',
    'bmi':            'BMI',
    'cycle_regularity': 'Cycle(R/I)',
    'cycle_length':   'Cycle length(days)',
    'weight_gain':    'Weight gain(Y/N)',
    'hair_growth':    'hair growth(Y/N)',
    'skin_darkening': 'Skin darkening (Y/N)',
    'pimples':        'Pimples(Y/N)',
    'fast_food':      'Fast food (Y/N)',
    'hip':            'Hip(inch)',
    'waist':          'Waist(inch)',
    'waist_hip_ratio':'Waist:Hip Ratio',
    'weight':         'Weight (Kg)',
    'height':         'Height(Cm)',
    'hair_loss':      'Hair loss(Y/N)',
    'exercise':       'Reg.Exercise(Y/N)',

    # Stage 2 additions
    'fsh':            'FSH(mIU/mL)',
    'lh':             'LH(mIU/mL)',
    'fsh_lh_ratio':   'FSH/LH',
    'tsh':            'TSH (mIU/L)',
    'amh':            'AMH(ng/mL)',
    'prolactin':      'PRL(ng/mL)',
    'vit_d3':         'Vit D3 (ng/mL)',
    'rbs':            'RBS(mg/dl)',
    'hemoglobin':     'Hb(g/dl)',
    'bp_systolic':    'BP _Systolic (mmHg)',
    'bp_diastolic':   'BP _Diastolic (mmHg)',

    # Stage 3 additions (Ultrasound / Clinical Metrics)
    'follicle_no_l':  'Follicle No. (L)',
    'follicle_no_r':  'Follicle No. (R)',
    'avg_f_size_l':   'Avg. F size (L) (mm)',
    'avg_f_size_r':   'Avg. F size (R) (mm)',
    'endometrium':    'Endometrium (mm)',
}

INT_FIELDS = {
    'weight_gain', 'hair_growth', 'skin_darkening',
    'hair_loss', 'pimples', 'fast_food', 'exercise', 'cycle_regularity'
}

def map_to_backend(cleaned_data):
    return {
        backend_key: (
            int(cleaned_data[form_key])
            if form_key in INT_FIELDS
            else float(cleaned_data[form_key])
        )
        for form_key, backend_key in FIELD_MAP.items()
        if form_key in cleaned_data
    }
