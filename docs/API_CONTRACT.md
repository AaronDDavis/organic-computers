# API Contract

This document defines the expected request and response format for the staged PCOS prediction pipeline.

The prediction system supports three stages:

1. **Stage 1 — Symptom and Lifestyle Screening**
2. **Stage 2 — Clinical / Lab Evaluation**
3. **Stage 3 — Imaging / Ultrasound Evaluation**

Each stage returns:

- `risk`
- `confidence`
- `top_factors`
- `specialist`
- `clinical_focus`
- `next_step`
- `recommendation_text`
- `missing_fields_imputed`
- `differential` where applicable

---

## 1. POST `/predict/stage1`

### Purpose

Stage 1 uses patient-reported symptom and lifestyle inputs only. This is intended for early screening before blood tests or imaging are available.

### Required Input Fields

| Field | Type | Description | Example |
|---|---|---|---|
| `Age (yrs)` | number | Patient age in years | `28` |
| `BMI` | number | Body Mass Index | `27.4` |
| `Cycle(R/I)` | number | Menstrual cycle regularity. Regular = `2`, Irregular = `4` | `4` |
| `Cycle length(days)` | number | Average cycle length in days | `45` |
| `Weight gain(Y/N)` | number | Weight gain. Yes = `1`, No = `0` | `1` |
| `hair growth(Y/N)` | number | Excess hair growth / hirsutism. Yes = `1`, No = `0` | `1` |
| `Skin darkening (Y/N)` | number | Skin darkening / acanthosis. Yes = `1`, No = `0` | `0` |
| `Hair loss(Y/N)` | number | Hair loss. Yes = `1`, No = `0` | `0` |
| `Pimples(Y/N)` | number | Acne / pimples. Yes = `1`, No = `0` | `1` |
| `Fast food (Y/N)` | number | Regular fast food intake. Yes = `1`, No = `0` | `1` |
| `Reg.Exercise(Y/N)` | number | Regular exercise. Yes = `1`, No = `0` | `0` |

### Example Request

```json
{
  "Age (yrs)": 28,
  "BMI": 27.4,
  "Cycle(R/I)": 4,
  "Cycle length(days)": 45,
  "Weight gain(Y/N)": 1,
  "hair growth(Y/N)": 1,
  "Skin darkening (Y/N)": 0,
  "Hair loss(Y/N)": 0,
  "Pimples(Y/N)": 1,
  "Fast food (Y/N)": 1,
  "Reg.Exercise(Y/N)": 0
}
```

### Example Response

```json
{
  "stage": "stage1",
  "risk": "High",
  "confidence": 0.777,
  "top_factors": [
    "BMI",
    "Age",
    "Skin darkening"
  ],
  "specialist": "Gynecologist",
  "clinical_focus": "Reproductive Focus",
  "next_step": "Your symptom profile suggests elevated PCOS risk. A clinical blood test panel including AMH, LH, FSH, glucose, thyroid markers, and prolactin would help clarify your risk profile.",
  "recommendation_text": "Your profile shows multiple markers associated with PCOS. Given the reproductive focus, we recommend consultation with a Gynecologist.",
  "missing_fields_imputed": [],
  "differential": null
}
```

---

## 2. POST `/predict/stage2`

### Purpose

Stage 2 uses Stage 1 inputs plus clinical and laboratory markers. This is intended after a GP visit or basic clinical workup.

### Required Input Fields

Stage 2 includes all Stage 1 fields, plus:

| Field | Type | Description | Example |
|---|---|---|---|
| `FSH(mIU/mL)` | number | Follicle Stimulating Hormone level | `5.8` |
| `LH(mIU/mL)` | number | Luteinizing Hormone level | `11.2` |
| `FSH/LH` | number | Ratio of FSH to LH | `0.52` |
| `TSH (mIU/L)` | number | Thyroid Stimulating Hormone level | `2.1` |
| `AMH(ng/mL)` | number | Anti-Müllerian Hormone level | `5.4` |
| `PRL(ng/mL)` | number | Prolactin level | `18.0` |
| `Vit D3 (ng/mL)` | number | Vitamin D3 level | `21.5` |
| `RBS(mg/dl)` | number | Random blood sugar | `135` |
| `Hb(g/dl)` | number | Hemoglobin level | `12.8` |
| `BP _Systolic (mmHg)` | number | Systolic blood pressure | `118` |
| `BP _Diastolic (mmHg)` | number | Diastolic blood pressure | `76` |

### Example Request

```json
{
  "Age (yrs)": 28,
  "BMI": 27.4,
  "Cycle(R/I)": 4,
  "Cycle length(days)": 45,
  "Weight gain(Y/N)": 1,
  "hair growth(Y/N)": 1,
  "Skin darkening (Y/N)": 0,
  "Hair loss(Y/N)": 0,
  "Pimples(Y/N)": 1,
  "Fast food (Y/N)": 1,
  "Reg.Exercise(Y/N)": 0,
  "FSH(mIU/mL)": 5.8,
  "LH(mIU/mL)": 11.2,
  "FSH/LH": 0.52,
  "TSH (mIU/L)": 2.1,
  "AMH(ng/mL)": 5.4,
  "PRL(ng/mL)": 18.0,
  "Vit D3 (ng/mL)": 21.5,
  "RBS(mg/dl)": 135,
  "Hb(g/dl)": 12.8,
  "BP _Systolic (mmHg)": 118,
  "BP _Diastolic (mmHg)": 76
}
```

### Example Response

```json
{
  "stage": "stage2",
  "risk": "Moderate",
  "confidence": 0.643,
  "top_factors": [
    "Excess hair growth",
    "AMH level",
    "Skin darkening"
  ],
  "specialist": "Gynecologist",
  "clinical_focus": "Reproductive Focus",
  "next_step": "Clinical results show some PCOS-associated markers. Follow-up with a Gynecologist may help clarify whether imaging is needed.",
  "recommendation_text": "Your profile shows some markers associated with PCOS. Follow-up with a Gynecologist may help clarify your risk.",
  "missing_fields_imputed": [],
  "differential": null
}
```

---

## 3. POST `/predict/stage3`

### Purpose

Stage 3 uses Stage 1 and Stage 2 inputs plus imaging and ultrasound markers. This is intended after specialist assessment or ultrasound investigations.

### Required Input Fields

Stage 3 includes all Stage 1 and Stage 2 fields, plus:

| Field | Type | Description | Example |
|---|---|---|---|
| `Follicle No. (L)` | number | Number of follicles in the left ovary | `14` |
| `Follicle No. (R)` | number | Number of follicles in the right ovary | `16` |
| `Avg. F size (L) (mm)` | number | Average follicle size in the left ovary | `6.2` |
| `Avg. F size (R) (mm)` | number | Average follicle size in the right ovary | `6.8` |
| `Endometrium (mm)` | number | Endometrial thickness | `8.5` |

### Example Request

```json
{
  "Age (yrs)": 28,
  "BMI": 27.4,
  "Cycle(R/I)": 4,
  "Cycle length(days)": 45,
  "Weight gain(Y/N)": 1,
  "hair growth(Y/N)": 1,
  "Skin darkening (Y/N)": 0,
  "Hair loss(Y/N)": 0,
  "Pimples(Y/N)": 1,
  "Fast food (Y/N)": 1,
  "Reg.Exercise(Y/N)": 0,
  "FSH(mIU/mL)": 5.8,
  "LH(mIU/mL)": 11.2,
  "FSH/LH": 0.52,
  "TSH (mIU/L)": 2.1,
  "AMH(ng/mL)": 5.4,
  "PRL(ng/mL)": 18.0,
  "Vit D3 (ng/mL)": 21.5,
  "RBS(mg/dl)": 135,
  "Hb(g/dl)": 12.8,
  "BP _Systolic (mmHg)": 118,
  "BP _Diastolic (mmHg)": 76,
  "Follicle No. (L)": 14,
  "Follicle No. (R)": 16,
  "Avg. F size (L) (mm)": 6.2,
  "Avg. F size (R) (mm)": 6.8,
  "Endometrium (mm)": 8.5
}
```

### Example Response

```json
{
  "stage": "stage3",
  "risk": "High",
  "confidence": 0.74,
  "top_factors": [
    "Right ovary follicle count",
    "Left ovary follicle count",
    "Excess hair growth"
  ],
  "specialist": "Gynecologist",
  "clinical_focus": "Reproductive Focus",
  "next_step": "Ultrasound and clinical findings suggest elevated PCOS risk with a reproductive focus. Priority consultation with a Gynecologist is recommended.",
  "recommendation_text": "Your profile shows multiple markers associated with PCOS. Given the reproductive focus, we recommend consultation with a Gynecologist.",
  "missing_fields_imputed": [],
  "differential": {
    "possible_endometriosis_overlap": null,
    "note": "Endometriosis differential layer pending integration."
  }
}
```

---

## 4. Response Field Definitions

| Field | Type | Meaning |
|---|---|---|
| `stage` | string | Current prediction stage: `stage1`, `stage2`, or `stage3` |
| `risk` | string | Risk category: `Low`, `Moderate`, or `High` |
| `confidence` | number | Model probability for PCOS-positive class, rounded to 3 decimals |
| `top_factors` | list of strings | Current top model-level factors for the selected stage |
| `specialist` | string | Recommended care route: `General Practitioner`, `Gynecologist`, or `Endocrinologist` |
| `clinical_focus` | string | `Baseline Health`, `Reproductive Focus`, or `Metabolic Focus` |
| `next_step` | string | Suggested next action for the patient or clinician |
| `recommendation_text` | string | User-facing recommendation summary |
| `missing_fields_imputed` | list of strings | Fields not provided by the user and imputed by the model pipeline |
| `differential` | object or null | Stage 3 differential placeholder; currently pending endometriosis integration |

---

## 5. Doctor Queue Mock

The doctor dashboard can use:

```text
doctor_queue_mock.csv
```

### Suggested Display Fields

| Field | Description |
|---|---|
| `Sl. No` | Dataset row index |
| `Patient File No.` | Patient identifier |
| `Risk_Level` | `1` = Low, `2` = Moderate, `3` = High |
| `Recommended_Specialist` | Recommended specialist |
| `Recommendation_Text` | Clinical recommendation |
| `risk_priority` | Numeric value used for queue sorting |

### Suggested Sorting Logic

1. Sort by `risk_priority` in descending order.
2. Within the same risk level, group by `Recommended_Specialist`.
3. Display high-risk patients first.

---

## 6. Notes for Web Integration

- Web should send field names exactly as shown in the request examples.
- The current prototype uses dataset-style column names, including spaces and brackets.
- For cleaner frontend naming, Web may use friendly field names, but backend will need a mapping layer.
- `top_factors` are currently model-level feature importance factors, not SHAP-based patient-specific explanations.
- `differential` is included only as a placeholder for Stage 3 until the endometriosis layer is integrated.
- Missing fields are imputed internally using the model pipeline, but the frontend should still collect all required fields for the selected stage where possible.

---

## 7. Current Model Metrics

| Stage | Number of Features | Accuracy | Sensitivity / Recall | Specificity | Precision | F1 | AUC |
|---|---:|---:|---:|---:|---:|---:|---:|
| Stage 1 | 11 | 0.853 | 0.694 | 0.932 | 0.833 | 0.758 | 0.902 |
| Stage 2 | 22 | 0.872 | 0.722 | 0.945 | 0.867 | 0.788 | 0.899 |
| Stage 3 | 27 | 0.927 | 0.833 | 0.973 | 0.938 | 0.882 | 0.950 |

### Metrics Interpretation

The staged approach is working as intended. Stage 3 performs best after ultrasound and imaging data are added. This supports the project’s progressive triage narrative: early screening can begin with symptom data, and the assessment becomes more confident as clinical and imaging information becomes available.

