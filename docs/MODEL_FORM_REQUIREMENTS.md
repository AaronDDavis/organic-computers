# Model Feature Requirements for Web

This file lists the exact data fields required by each staged model.

Important:

- The backend model currently expects the **backend field names exactly as written**.
- Web can display friendlier labels, but the submitted JSON should either use these backend names directly or be mapped to these names before prediction.
- The models are **not using all PCOS dataset columns**. They use 11, 22, and 27 selected fields for Stage 1, Stage 2, and Stage 3 respectively.

---

## Stage 1 — Symptom and Lifestyle Screening

Endpoint: `/predict/stage1`

Number of model features: **11**

| Backend field name | Frontend label | Type / values | Example |
| --- | --- | --- | --- |
| `Age (yrs)` | Age | number | `28` |
| `BMI` | BMI | number | `27.4` |
| `Cycle(R/I)` | Cycle regularity | 2=Regular, 4=Irregular | `4` |
| `Cycle length(days)` | Cycle length in days | number | `45` |
| `Weight gain(Y/N)` | Weight gain | 0=No, 1=Yes | `1` |
| `hair growth(Y/N)` | Excess hair growth | 0=No, 1=Yes | `1` |
| `Skin darkening (Y/N)` | Skin darkening | 0=No, 1=Yes | `0` |
| `Hair loss(Y/N)` | Hair loss | 0=No, 1=Yes | `0` |
| `Pimples(Y/N)` | Acne / pimples | 0=No, 1=Yes | `1` |
| `Fast food (Y/N)` | Regular fast food intake | 0=No, 1=Yes | `1` |
| `Reg.Exercise(Y/N)` | Regular exercise | 0=No, 1=Yes | `0` |

---

## Stage 2 — Clinical / Lab Evaluation

Endpoint: `/predict/stage2`

Number of model features: **22**

Stage 2 includes all Stage 1 fields plus the following lab/clinical fields:

| Backend field name | Frontend label | Type / values | Example |
| --- | --- | --- | --- |
| `FSH(mIU/mL)` | FSH level | number | `5.8` |
| `LH(mIU/mL)` | LH level | number | `11.2` |
| `FSH/LH` | FSH/LH ratio | number | `0.52` |
| `TSH (mIU/L)` | TSH level | number | `2.1` |
| `AMH(ng/mL)` | AMH level | number | `5.4` |
| `PRL(ng/mL)` | Prolactin level | number | `18.0` |
| `Vit D3 (ng/mL)` | Vitamin D3 level | number | `21.5` |
| `RBS(mg/dl)` | Random blood sugar | number | `135` |
| `Hb(g/dl)` | Hemoglobin level | number | `12.8` |
| `BP _Systolic (mmHg)` | Systolic blood pressure | number | `118` |
| `BP _Diastolic (mmHg)` | Diastolic blood pressure | number | `76` |

---

## Stage 3 — Imaging / Ultrasound Evaluation

Endpoint: `/predict/stage3`

Number of model features: **27**

Stage 3 includes all Stage 1 and Stage 2 fields plus the following imaging fields:

| Backend field name | Frontend label | Type / values | Example |
| --- | --- | --- | --- |
| `Follicle No. (L)` | Left ovary follicle count | number | `14` |
| `Follicle No. (R)` | Right ovary follicle count | number | `16` |
| `Avg. F size (L) (mm)` | Average left follicle size | number | `6.2` |
| `Avg. F size (R) (mm)` | Average right follicle size | number | `6.8` |
| `Endometrium (mm)` | Endometrial thickness | number | `8.5` |

---

## Recommended Frontend Form Structure

1. **Stage 1 form**: patient-facing self-reported fields only.
2. **Stage 2 form**: doctor/clinical fields or optional patient upload/manual entry after blood tests.
3. **Stage 3 form**: ultrasound/imaging fields, likely entered after specialist review.

---

## Notes

- Binary fields should be stored as `0` for No and `1` for Yes.
- `Cycle(R/I)` should be stored as `2` for Regular and `4` for Irregular.
- Missing fields can technically be imputed by the model pipeline, but Web should still try to collect the relevant fields for the selected stage.
- The three `.pkl` model files were trained with `scikit-learn==1.5.1`; backend should use the same version to avoid joblib/pickle compatibility warnings.
