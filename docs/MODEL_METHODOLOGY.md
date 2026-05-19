# Model Methodology

## 🗃️ Dataset

The primary dataset is `PCOS_data_without_infertility.xlsx`, containing **541 patient records** from a clinical study on PCOS diagnosis. Features span **four clinical domains**:

* **Reproductive / gynaecological:** menstrual cycle regularity and length, follicle counts (left and right ovary), average follicle sizes, endometrial thickness
* **Metabolic / anthropometric:** weight, height, BMI, waist and hip circumference, waist-to-hip ratio, blood pressure
* **Hormonal / biochemical:** FSH, LH, FSH/LH ratio, AMH, TSH, prolactin, progesterone, vitamin D3, haemoglobin, random blood sugar
* **Symptom / lifestyle:** weight gain, excess hair growth, skin darkening, hair loss, acne, fast food consumption, exercise frequency

**Target variable:** `PCOS (Y/N)` — **binary classification**.

---

## 🧼 Data Cleaning

The pipeline applies the following cleaning steps before any modelling:

* **Strip leading/trailing whitespace** from column names (present in the raw file)
* **Drop the identifier columns** and `Unnamed: 44` (sparse, >90% missing)
* **Convert string tokens and known dirty values to `NaN`** — AMH in particular has a known encoding issue in the source file
* **Treat clinical outliers as missing** (e.g. extreme AMH values, menstrual cycle coding values outside `{2, 4}`)
* ⚠️ **Defer all imputation to inside model pipelines to prevent data leakage**

---

## 🔀 Feature Grouping Strategy

Features are partitioned into **three cumulative groups** corresponding to the **cost and invasiveness** of data collection:

🔹 **`Stage 1` — Symptom and Anthropometric (16 features)**
Available **without any laboratory or imaging investigation**. Suitable for community screening, primary care, or patient-facing self-assessment. Includes menstrual cycle characteristics, BMI, anthropometric measurements, and self-reported symptoms (hirsutism, skin darkening, weight gain, acne, hair loss, diet, exercise).

🔸 **`Stage 2` — Hormonal and Metabolic (Stage 1 + 12 additional features)**
Adds **standard blood panel markers**: FSH, LH, FSH/LH ratio, AMH, TSH, prolactin, progesterone, vitamin D3, haemoglobin, blood glucose, systolic and diastolic blood pressure. These require a laboratory visit but are routinely available in primary and secondary care.

⚡ **`Stage 3` — Imaging (Stage 2 + 5 additional features)**
Adds **ultrasound-derived measurements**: left and right follicle counts, average follicle sizes, and endometrial thickness. These require a sonographer and are typically ordered by a specialist.

> **Production Design Note:** The cumulative design means Stage 2 and Stage 3 models always have access to all prior-stage features. Each stage trains on its own feature set; there is no artificial constraint preventing Stage 2 from using Stage 1 predictors.

---

## 🔍 Mutual Information Screening

Before model training, **mutual information (MI) scores** are calculated between all features and the target. Features with **MI below 0.002** are flagged as low-signal and reviewed for removal. MI-ranked features guide the feature group design and provide a **data-grounded justification** for which predictors matter most at each stage.

Top-ranked features by MI in the full feature set include menstrual cycle regularity, follicle counts, AMH, and waist-to-hip ratio — all **consistent with clinical PCOS criteria**.

---

## ⚙️ Model Architecture

All three stage models follow the same pipeline structure:

```
ColumnTransformer
  └── SimpleImputer (median strategy) → StandardScaler
XGBClassifier (with light hyperparameter tuning)
CalibratedClassifierCV (isotonic regression, 4-fold CV)

```

> **Why XGBoost?** > Gradient-boosted trees are consistently strong on tabular clinical data. They handle nonlinear feature interactions, are robust to the moderate sample sizes typical of clinical datasets, and do not require all features to be present (missing values can be handled by the imputer upstream).

> **Why calibration?** > Raw XGBoost probability estimates are often poorly calibrated — a model that predicts 0.8 may not actually be right 80% of the time. `CalibratedClassifierCV` with isotonic regression corrects this using a secondary fitting step on held-out fold predictions. **Calibrated probabilities are essential for clinical use**, where the displayed risk percentage needs to be interpretable as a genuine probability estimate.

---

## 🧪 Hyperparameter Tuning

Hyperparameters are selected via a lightweight grid search over:

* `max_depth`: `[2, 3]`
* `learning_rate`: `[0.03, 0.04, 0.05]`
* `min_child_weight`: `[2, 3]`

Search is conducted using **5-fold stratified cross-validation, optimising for ROC-AUC**. Shallow trees and conservative learning rates are preferred to **reduce overfitting** on the 541-sample dataset.

### 📍 Final Selected Parameters

* **`Stage 1`:** max_depth=2, learning_rate=0.04, min_child_weight=2
* **`Stage 2`:** max_depth=3, learning_rate=0.03, min_child_weight=3
* **`Stage 3`:** max_depth=2, learning_rate=0.04, min_child_weight=2

---

## 📈 Threshold Tuning

Default XGBoost thresholds (0.5) are **not appropriate for a screening context** where false negatives are more harmful than false positives. After training, each model's threshold is tuned by scanning the probability range and selecting the value that **maximises sensitivity** while maintaining acceptable specificity.

| 🎚️ Stage | 🎯 Threshold | 🧬 Sensitivity | 🎯 Specificity | 📊 AUC |
| --- | --- | --- | --- | --- |
| **`Stage 1`** | 0.16 | **86.1%** | 71.2% | **0.890** |
| **`Stage 2`** | 0.21 | **91.7%** | 68.5% | **0.899** |
| **`Stage 3`** | 0.22 | **94.4%** | **82.2%** | **0.957** |

The low thresholds at Stages 1 and 2 reflect the screening intent: **cast wide, escalate for review**. By Stage 3, with full imaging data, the model can afford to be more specific without sacrificing sensitivity.

---

## 🧠 SHAP Explainability

**SHAP (SHapley Additive exPlanations)** is applied to each stage model to produce both **global and local interpretability** outputs.

* **Global SHAP:** Mean absolute SHAP values across the test set reveal which features most consistently influence predictions. At Stage 3, follicle counts dominate. At Stage 1, the top contributors are menstrual irregularity, weight gain, and excess hair growth — **directly mapping to clinical PCOS criteria**.
* **Local SHAP:** Patient-level SHAP values identify which specific features are driving an individual's risk score. **This is the output surfaced to clinicians in the recommendation layer** — the top three factors displayed alongside the risk score are derived from patient-level SHAP contributions.

ℹ️ *SHAP plots are generated during pipeline execution with the `--make-shap` flag and saved under `charts/shap/`.*

---

## 🧬 Phenotype Clustering

After training the diagnostic models, PCOS-positive patients are further analysed using **KMeans clustering** to identify clinical subgroups. Clustering is performed on a subset of the **most clinically discriminative features**: hormonal markers, metabolic indicators, and reproductive parameters.

### 🛠️ The Pipeline:

1. Filters to PCOS-positive patients only
2. Applies the same imputation and scaling preprocessor
3. Fits KMeans (`k=3`, **selected by silhouette analysis**)
4. Labels clusters with clinically interpretable phenotype names based on centroid profiles

The three identified phenotype clusters reflect real subgroups described in PCOS literature: a **hyperandrogenic-metabolic phenotype**, a **predominantly hormonal phenotype**, and a **milder symptom phenotype**. The cluster model is exported as `pcos_phenotype_kmeans.joblib` and integrated into the recommendation engine for phenotype-aware guidance.

---

## 🤖 Recommendation Engine

The recommendation engine maps a patient's risk score and stage to **structured clinical guidance**. The logic is:

1. **Map probability to risk tier:** `low (< 0.35)`, `moderate (0.35–0.65)`, `high (> 0.65)`
2. **Select stage-appropriate next-step text** from `rules.json`
3. **Determine recommended specialist type** (Endocrinologist, Gynaecologist, or GP) based on symptom profile heuristics
4. **Optionally incorporate phenotype label** for PCOS-positive subgroup guidance

> **Clinical Utility:** The recommendation text at each stage specifies **concrete next actions** — bloodwork panels at Stage 1, ultrasound and specialist referral at Stage 2, Rotterdam criteria confirmation and metabolic risk assessment at Stage 3 — rather than generic risk statements.

---

## 🏁 Baseline Comparison

Day 1 of the pipeline trains **full-feature Logistic Regression and Random Forest baselines** on all available features to establish reference performance:

| 🤖 Model | 🎯 Accuracy | 🧬 Sensitivity | 🎯 Specificity | 📊 AUC |
| --- | --- | --- | --- | --- |
| **Logistic Regression (full features)** | 88.2% | 88.1% | 88.2% | 0.943 |
| **Random Forest (full features)** | **90.2%** | 80.2% | **95.1%** | **0.958** |

These baselines confirm that the feature set is **highly predictive**. The progressive models trade some overall accuracy for two things the baselines lack: **accessibility** (Stage 1 requires no blood tests) and **clinical usability** (calibrated probabilities, sensitivity-optimised thresholds, SHAP explanations, and recommendation output).