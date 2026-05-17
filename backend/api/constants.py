FEATURE_LABELS_STAGE1 = {
    "Age (yrs)":              "Age",
    "BMI":                    "BMI",
    "Cycle(R/I)":             "Cycle regularity",
    "Cycle length(days)":     "Cycle length in days",
    "Weight gain(Y/N)":       "Weight gain",
    "hair growth(Y/N)":       "Excess hair growth",
    "Skin darkening (Y/N)":   "Skin darkening",
    "Hair loss(Y/N)":         "Hair loss",
    "Pimples(Y/N)":           "Acne / pimples",
    "Fast food (Y/N)":        "Regular fast food intake",
    "Reg.Exercise(Y/N)":      "Regular exercise",
}


FEATURE_LABELS_STAGE2 = {
    **FEATURE_LABELS_STAGE1,  # Includes all Stage 1 features
    "FSH(mIU/mL)":            "FSH level",
    "LH(mIU/mL)":             "LH level",
    "FSH/LH":                 "FSH/LH ratio",
    "TSH (mIU/L)":            "TSH level",
    "AMH(ng/mL)":             "AMH level",
    "PRL(ng/mL)":             "Prolactin level",
    "Vit D3 (ng/mL)":         "Vitamin D3 level",
    "RBS(mg/dl)":             "Random blood sugar",
    "Hb(g/dl)":               "Hemoglobin level",
    "BP _Systolic (mmHg)":    "Systolic blood pressure",
    "BP _Diastolic (mmHg)":   "Diastolic blood pressure",
}


FEATURE_LABELS_STAGE3 = {
    **FEATURE_LABELS_STAGE2,  # Includes all Stage 2 features
    "Follicle No. (L)":       "Left ovary follicle count",
    "Follicle No. (R)":       "Right ovary follicle count",
    "Avg. F size (L) (mm)":   "Average left follicle size",
    "Avg. F size (R) (mm)":   "Average right follicle size",
    "Endometrium (mm)":       "Endometrial thickness",
}


FEATURE_LABELS_BY_STAGE = {
    'S1': FEATURE_LABELS_STAGE1,
    'S2': FEATURE_LABELS_STAGE2,
    'S3': FEATURE_LABELS_STAGE3,
}

