# 🖥️ System Architecture — PCOSense

> **Key Highlights:**
> * **Production-Ready Security:** Features field-level encryption at rest, secure environment variable configurations, and CSRF/session protection.
> * **Scalable ML Lifecycle:** Multi-stage, calibrated XGBoost inference engine with low-latency loading designed for horizontal scaling.
> * **Robust Architecture:** Structured 12-factor Django 6.x backend backed by a clean PostgreSQL data model.

---

## 🗺️ High-Level Component Map

```
🖳 ──────────────────────────────────────────────────────────┐
│                     Frontend (Browser)                    │
│        Patient forms · Clinician dashboards               │
└───────────────────────────┬──────────────────────────────-┘
                            │ HTTP
┌───────────────────────────▼──────────────────────────────┐
│                   Django Backend                         │
│  users · patients · doctors · clinics · journeys         │
│  assessments · api                                       │
│                                                          │
│  🧠 ───────────────────────────────────────────────┐     │
│  │           ML Inference Engine (api/)            │     │
│  │  stage1_model  stage2_model  stage3_model       │     │
│  │  Calibrated XGBoost pipelines (.joblib)         │     │
│  └─────────────────────────────────────────────────┘     │
│                                                          │
│  🔀 ───────────────────────────────────────────────┐     │
│  │        Recommendation + Rules Engine            │     │
│  │  risk_category · specialist_recommendation      │     │
│  │  next_step logic · top_factors extraction       │     │
│  └─────────────────────────────────────────────────┘     │
│                                                          │
│  🗄️ ───────────────────────────────────────────────┐     │
│  │              Database (PostgreSQL)              │     │
│  │  Users · Patients · Journeys · Assessments      │     │
│  │  AssessmentResults · ClinicalNotes · Clinics    │     │
│  └─────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘

```

---

## 📦 Backend Django Apps

The backend is a standard Django project (`pcos_project/`) composed of eight focused apps. Each app owns its models, views, forms, and URL routing.

### `users/`

* **Custom User Model & Authentication:** Supports role separation between patients, doctors, and clinic staff.
* **Access Control:** Authentication state controls access throughout the platform.

### `patients/`

* **Profile Management:** Stores demographic data and links patients to their diagnostic journeys.
* **Data Access:** Patient profiles are accessed by clinicians via the doctor and journey apps.

### `doctors/`

* **Clinician Profiles:** Includes specialty tracking (`Endocrinologist`, `Gynecologist`, `General Practitioner`).
* **Smart Routing:** The specialty field drives specialist recommendation routing in assessment results.

### `clinics/`

* **Facility Registration:** Handles healthcare facility registration and `ClinicianProfile` management.
* **Multi-Facility Deployment:** Journeys are associated with a clinic, enabling multi-facility deployments.

### `journeys/`

* **Central Coordinating Record:** The `DiagnosticJourney` model serves as the central core.
* **Workflow Constraints:** Each journey has a patient, an optional assigned doctor, a clinic, a status (`IN_PROGRESS` / `COMPLETED`), and a sequential number. A journey may contain up to three assessments — one per stage.

### `assessments/`

* **Core Diagnostic Flow:** The `Assessment` model stores stage (S1/S2/S3), the input data payload as JSON, and links back to a journey.
* **Computed Outputs:** The `AssessmentResult` model stores the risk label, probability score, top contributing factors, specialist routing, clinical focus text, next-step recommendation, and free-text recommendation.
* **Data Integrity:** A database constraint enforces that each stage can only appear once per journey. The `ClinicalNote` model allows doctors to annotate assessments.

### `api/`

* **ML Inference Layer:** Three `.joblib` model artifacts are loaded at startup via `api/loader.py`.
* **Feature & Prediction Utilities:** The `run_prediction()` utility in `api/utils.py` handles feature extraction, model inference, recommendation generation, and top-factor extraction.
* **REST Endpoints:** Exposes the models externally via Django REST Framework using `PredictStage1View`, `PredictStage2View`, and `PredictStage3View`.

---

## 🔄 Diagnostic Flow (Assessment Lifecycle)

```
Clinician/Patient opens journey
        │
        ▼
AssessmentCreateView — Stage 1 form submitted
        │
        ├─ map_to_backend() — form field names ➔ model feature names
        ├─ Assessment saved (stage=S1, data=JSON payload)
        ├─ run_prediction(stage1_model, data, stage)
        │       ├─ construct DataFrame from expected features
        │       ├─ model.predict_proba() ➔ risk score
        │       ├─ get_recommendation() ➔ risk level, next step, specialist
        │       └─ get_top_factors() ➔ top contributing features
        └─ AssessmentResult saved ➔ redirect to journey_detail
                │
                ▼
        Stage 2 form (adds hormonal/metabolic fields)
                │
                ▼
        Stage 3 form (adds ultrasound/imaging fields)
                │
                ▼
        Journey marked COMPLETED

```

Stages are cumulative: each subsequent stage adds its feature group to those from the previous stage. This mirrors clinical practice, where early screenings inform whether further investigation is warranted.

---

## 🧠 ML Architecture

Three independently trained, calibrated XGBoost pipelines are loaded at application startup:

| Artifact | Feature Set | Clinical Analogy |
| --- | --- | --- |
| `stage1_model.joblib` | 16 symptom/lifestyle/anthropometric features | GP-level initial consultation |
| `stage2_model.joblib` | Stage 1 + 12 hormonal/metabolic/lab features | Endocrine blood panel |
| `stage3_model.joblib` | Stage 2 + 5 ultrasound/ovarian features | Pelvic ultrasound |
| `phenotype_model.joblib` | 13 metabolic/reproductive/androgenic features | Phenotype subgrouping (PCOS-positive only) |

Each calibrated model uses isotonic calibration (4-fold CV) to improve probability reliability. Thresholds are tuned post-calibration with a sensitivity-first objective, prioritising recall (sensitivity) over precision given the clinical cost of missed diagnoses.

---

## 🔀 Recommendation Engine

The recommendation engine operates on the output of each stage model and produces structured clinical guidance:

* **Risk category** — thresholds of 0.35 (low/moderate boundary) and 0.65 (moderate/high boundary) applied to calibrated probability.
* **Next step** — stage- and risk-specific textual guidance (e.g., "Symptoms suggest elevated PCOS risk. Recommended next step: prompt clinical review and bloodwork…").
* **Specialist routing** — heuristic scoring of metabolic vs. reproductive feature values determines whether an Endocrinologist or Gynaecologist is recommended.
* **Top factors** — the three highest-importance features from the stage model's XGBoost feature importance array are surfaced to the clinician.

---

## 🔒 Security and Data Handling

* Patient data fields use `django-encrypted-model-fields` for field-level encryption at rest.
* `SECRET_KEY` and `FIELD_ENCRYPTION_KEY` are loaded from environment variables, never hard-coded.
* `DEBUG` mode is controlled via `DJANGO_DEBUG` environment variable (defaults to `False`).
* `WhiteNoise` middleware handles static file serving in production without requiring a separate CDN.
* The REST API layer uses Django REST Framework with session and CSRF protection.

---

## 🚀 Deployment Design

### Recommended Production Stack

```
Internet
    │
  Nginx  ◄── static files (WhiteNoise fallback)
    │
  Gunicorn (pcos_project.wsgi:application)
    │
  Django 6.x
    │
  PostgreSQL

```

Dependencies are pinned in `requirements.txt`. The application supports `dj-database-url` for 12-factor-style `DATABASE_URL` configuration.

### Scalability

The modular app structure supports horizontal scaling (multiple Gunicorn workers behind Nginx). The ML model artifacts are loaded once per worker process at startup, keeping inference latency low. The staged architecture allows individual stage models to be retrained and replaced without disrupting the rest of the system.

---

## 🛠️ Technology Stack Summary

| Layer | Technology |
| --- | --- |
| **Backend framework** | Django 6.x, Django REST Framework |
| **ML inference** | XGBoost 3.x, scikit-learn, joblib |
| **Database** | PostgreSQL (production), SQLite (development) |
| **Static files** | WhiteNoise |
| **Data encryption** | django-encrypted-model-fields |
| **WSGI server** | Gunicorn |
| **Data processing** | pandas, NumPy |
| **Explainability** | SHAP (optional, pipeline flag) |