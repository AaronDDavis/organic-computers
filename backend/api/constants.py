FEATURE_LABELS_STAGE1 = {
    "Weight gain(Y/N)":       "Weight gain",
    "hair growth(Y/N)":       "Excess hair growth",
    "Skin darkening (Y/N)":   "Skin darkening",
    "Age (yrs)":              "Age",
    "BMI":                    "BMI",
    "Cycle(R/I)":             "Cycle regularity",
    "Cycle length(days)":     "Cycle length in days",
    "Hair loss(Y/N)":         "Hair loss",
    "Pimples(Y/N)":           "Acne / pimples",
    "Fast food (Y/N)":        "Regular fast food intake",
    "Reg.Exercise(Y/N)":      "Regular exercise",
}


FEATURE_LABELS_STAGE2 = {
    "AMH(ng/mL)":             "AMH level",
    "BP _Diastolic (mmHg)":   "Diastolic blood pressure",
    "PRL(ng/mL)":             "Prolactin level",
    **FEATURE_LABELS_STAGE1,  # Includes all Stage 1 features
    "FSH(mIU/mL)":            "FSH level",
    "LH(mIU/mL)":             "LH level",
    "FSH/LH":                 "FSH/LH ratio",
    "TSH (mIU/L)":            "TSH level",
    "Vit D3 (ng/mL)":         "Vitamin D3 level",
    "RBS(mg/dl)":             "Random blood sugar",
    "Hb(g/dl)":               "Hemoglobin level",
    "BP _Systolic (mmHg)":    "Systolic blood pressure",
}


FEATURE_LABELS_STAGE3 = {
    "Follicle No. (R)":       "Right ovary follicle count",
    "Follicle No. (L)":       "Left ovary follicle count",
    "Endometrium (mm)":       "Endometrial thickness",
    **FEATURE_LABELS_STAGE2,  # Includes all Stage 2 features
    "Avg. F size (L) (mm)":   "Average left follicle size",
    "Avg. F size (R) (mm)":   "Average right follicle size",
}


FEATURE_LABELS_BY_STAGE = {
    'S1': FEATURE_LABELS_STAGE1,
    'S2': FEATURE_LABELS_STAGE2,
    'S3': FEATURE_LABELS_STAGE3,
}


STAGE_EXPECTED_FEATURES = {
    'S1': ["hair growth(Y/N)",
            "Weight gain(Y/N)",
            "Skin darkening (Y/N)",
            "Fast food (Y/N)",
            "Cycle(R/I)",
            "Cycle length(days)",
            "Hip(inch)",
            "Waist:Hip Ratio",
            "Pimples(Y/N)",
            "Weight (Kg)",
            "Age (yrs)",
            "BMI",
            "Height(Cm)",
            "Waist(inch)"
            ],
    'S2': [    "hair growth(Y/N)",
                "Skin darkening (Y/N)",
                "Weight gain(Y/N)",
                "AMH(ng/mL)",
                "Fast food (Y/N)",
                "FSH/LH",
                "PRL(ng/mL)",
                "Weight (Kg)",
                "Cycle length(days)",
                "Pimples(Y/N)",
                "Cycle(R/I)",
                "TSH (mIU/L)",
                "Hair loss(Y/N)",
                "BP _Diastolic (mmHg)",
                "LH(mIU/mL)",
                "BMI",
                "FSH(mIU/mL)",
                "PRG(ng/mL)",
                "Vit D3 (ng/mL)",
                "Waist:Hip Ratio",
                "Waist(inch)",
                "Reg.Exercise(Y/N)",
                "Hb(g/dl)",
                "Hip(inch)",
                "Age (yrs)"
            ], 
    'S3': ["Follicle No. (R)",
            "Follicle No. (L)",
            "Weight gain(Y/N)",
            "Skin darkening (Y/N)",
            "hair growth(Y/N)",
            "Cycle length(days)",
            "AMH(ng/mL)",
            "PRL(ng/mL)",
            "FSH/LH",
            "Cycle(R/I)",
            "Weight (Kg)",
            "Fast food (Y/N)",
            "Waist:Hip Ratio",
            "FSH(mIU/mL)",
            "Waist(inch)",
            "Age (yrs)",
            "LH(mIU/mL)",
            "TSH (mIU/L)",
            "Hip(inch)",
            "BMI",
            "PRG(ng/mL)",
            "Vit D3 (ng/mL)",
            "Hair loss(Y/N)",
            "Endometrium (mm)",
            "Hb(g/dl)"
            ],
}


PHENOTYPE_EXPECTED_FEATURES = [
    "BMI",
    "Waist:Hip Ratio",
    "RBS(mg/dl)",
    "Skin darkening (Y/N)",
    "Weight gain(Y/N)",
    "Cycle(R/I)",
    "AMH(ng/mL)",
    "LH(mIU/mL)",
    "FSH(mIU/mL)",
    "hair growth(Y/N)",
    "Pimples(Y/N)",
    "Follicle No. (L)",
    "Follicle No. (R)",
    "FSH/LH",
]