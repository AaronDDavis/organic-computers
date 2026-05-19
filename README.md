# 🩺 PCOSense — Progressive Clinical Decision Support for PCOS Diagnosis

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://www.python.org)
[![Django](https://img.shields.io/badge/Django-5.x-green?style=flat-square&logo=django)](https://www.djangoproject.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-Latest-red?style=flat-square&logo=xgboost)](https://xgboost.readthedocs.io)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Latest-orange?style=flat-square&logo=scikit-learn)](https://scikit-learn.org)

🌐 **[Live Demo](https://github.com)**

---

## 💡 What is PCOSense?

> **Core Design Principle:** **Progressive diagnostic escalation** — rather than demanding all clinical data upfront, PCOSense meets patients and clinicians where they are.

PCOSense is a staged clinical decision-support platform built to reduce diagnostic delay and misdiagnosis in Polycystic Ovary Syndrome (PCOS). It combines a progressive three-stage machine learning pipeline, SHAP-based explainability, phenotype clustering, and a structured clinical workflow — all surfaced through a Django web application with real-time risk scoring.

A GP with no lab results can still run Stage 1. A specialist with bloodwork can run Stage 2. A radiologist adding ultrasound findings completes Stage 3. Each stage refines the risk estimate, and together they mirror real-world PCOS diagnostic pathways.

---

## 🛑 The Problem We Are Solving

PCOS affects 8–13% of reproductive-age women globally, yet up to **70% of cases remain undiagnosed** (WHO). Among those eventually diagnosed, one-third wait more than two years, and nearly half see three or more clinicians first. This is not primarily a data problem — it is a synthesis problem. PCOS presents heterogeneously: some patients are obese, some are not; some have hyperandrogenic symptoms, some have only metabolic ones. No single biomarker confirms the condition, and clinicians must synthesise symptoms, hormonal markers, and imaging under time pressure.

PCOSense directly addresses this synthesis burden.

---

## ⚙️ How the System Works

### 📋 Stage 1 — Symptomatic Screening

* **Inputs:** Menstrual cycle regularity and length, BMI, weight, height, waist and hip measurements, waist-to-hip ratio, and self-reported symptoms including weight gain, excess hair growth, skin darkening, hair loss, acne, fast food frequency, and exercise habits.

**No blood test required.** This stage is designed to be completable by the patient herself or a primary care clinician in under five minutes. It is the entry point for community screening and telehealth triage.

* **Model:** Calibrated XGBoost (Stage 1)
* **Metrics:** **AUC: 0.890**, **Sensitivity: 86.1%**, Specificity: 71.2% (threshold tuned to 0.16 for sensitivity-first screening)

### 🩸 Stage 2 — Hormonal and Metabolic Evaluation

* **Inputs:** All Stage 1 features plus FSH, LH, FSH/LH ratio, AMH, TSH, prolactin, progesterone, vitamin D3, random blood sugar, blood pressure, and haemoglobin.

This stage is triggered when Stage 1 returns a moderate or high risk score, or when bloodwork is available. Adding hormonal markers substantially improves discrimination, particularly for patients whose symptoms alone are ambiguous.

* **Model:** Calibrated XGBoost (Stage 2)
* **Metrics:** **AUC: 0.899**, **Sensitivity: 91.7%**, Specificity: 68.5% (threshold: 0.21)

### 🔬 Stage 3 — Imaging Integration

* **Inputs:** All Stage 2 features plus left and right ovarian follicle counts, average follicle sizes, and endometrial thickness.

This stage integrates ultrasound findings — the most definitive available marker of polycystic ovarian morphology — to produce the highest-confidence diagnostic support estimate.

* **Model:** Calibrated XGBoost (Stage 3)
* **Metrics:** **AUC: 0.957**, **Sensitivity: 94.4%**, Specificity: 82.2% (threshold: 0.22)

> The progressive sensitivity arc (**86% → 92% → 94%**) and AUC arc (**0.890 → 0.899 → 0.957**) demonstrate that the system meaningfully improves with each data layer — not just as an artefact of feature count, but as a clinically coherent escalation.

---

## 🛠️ Key Design Decisions

* **🎯 Sensitivity-First Thresholds:** All three stage models use thresholds tuned to **maximise sensitivity** rather than accuracy. In a screening context, missing a PCOS case (false negative) is more harmful than a false alarm that prompts further investigation. Thresholds were selected by scanning the probability range and identifying the point that preserved sensitivity above 85% while minimising specificity loss.
* **📊 Probability Calibration:** Raw XGBoost probability outputs are often overconfident. All three models use isotonic regression calibration (via `CalibratedClassifierCV` with 4-fold CV) so that a reported 75% risk score genuinely means approximately 75% probability under the training distribution. This is critical for clinical usability — a clinician acting on a risk score needs to trust that it is a real probability estimate.
* **🔍 SHAP Explainability:** Each stage model includes SHAP (SHapley Additive exPlanations) analysis. The SHAP layer allows clinicians to see not just "this patient is high risk" but "these three factors are driving that assessment." SHAP values at Stage 3 show that follicle counts dominate prediction as expected clinically, while at Stage 1 the top contributors are menstrual irregularity, weight gain, and excess hair growth — all consistent with PCOS clinical criteria.
* **🧬 Phenotype Clustering:** PCOS does not present uniformly. After identifying PCOS-positive patients, a KMeans clustering model segments them into phenotypic subgroups based on hormonal and metabolic profiles. This supports personalised interpretation and reflects the clinical reality that treatment and follow-up differ across phenotypes.
* **🤖 Recommendation Engine:** A rule-based recommendation layer maps risk scores to actionable clinical guidance. The thresholds (`low < 0.35 < moderate < 0.65 < high`) were set conservatively to avoid under-flagging borderline cases. At each stage, the recommendation text specifies the next investigation step — bloodwork at Stage 1, specialist referral and ultrasound at Stage 2, Rotterdam confirmation and metabolic risk assessment at Stage 3.

---

## 🏗️ Application Architecture

PCOSense is deployed as a multi-user Django web application. The architecture separates concerns cleanly across Django apps:

| App | Purpose |
| --- | --- |
| `users/` | Authentication, role-based access |
| `patients/` | Patient profiles, blood group, date of birth |
| `doctors/` | Clinician profiles, specialty (Endocrinologist / Gynaecologist / GP) |
| `clinics/` | Clinic registration and management |
| `assessments/` | Assessment forms, staged data capture, result storage |
| `journeys/` | Longitudinal diagnostic journey tracking across assessments |
| `api/` | Model loading, inference integration, REST endpoints |

Each patient has a `DiagnosticJourney` that progresses through stages. Stage 1 is self-service. Stage 2 is unlocked after Stage 1. Stage 3 requires a specialist to enter imaging data. This mirrors the real diagnostic pathway and prevents clinicians from skipping stages inappropriately.

The assessment result stores the risk score, risk label, top contributing factors, recommended specialist type, clinical focus text, next step, and full recommendation — giving clinicians a structured decision-support output rather than a bare number.

---

## 🚀 Setup

### 🖥️ Backend

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

```

### 🧠 ML Pipeline (re-training from source)

```bash
cd PCOS_Modelling_Submission_v2/
pip install -r requirements.txt
python pcos_progressive_pipeline.py
# Optional: generate SHAP plots
python pcos_progressive_pipeline.py --make-shap

```

Pre-trained model artefacts are already included under `models/` and loaded at application startup via `api/loader.py`.

---

## 💻 Technology Stack

* **Backend:** Django, Django REST Framework, SQLite (dev) / PostgreSQL (production)
* **Machine Learning:** XGBoost, Scikit-learn (pipelines, imputation, calibration, clustering), SHAP, Pandas, NumPy, Joblib
* **Visualisation:** Matplotlib, Seaborn, SHAP summary plots

---

## ⚠️ Limitations and Honest Caveats

* The models are trained and validated on a single dataset (the provided PCOS dataset). External validation on independent cohorts has not been performed.
* The dataset has limited demographic diversity. Model performance may vary across ethnic groups with different PCOS prevalence or presentation patterns.
* PCOSense is a **decision support tool, not a diagnostic system.** All outputs are intended to assist clinician judgement, not replace it.
* The differential diagnosis component (distinguishing PCOS from endometriosis, hypothyroidism, hyperprolactinaemia) is partially implemented through the recommendation text but not yet a formal classification output.