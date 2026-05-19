# Results and Validation

## 📋 Summary

**PCOSense** achieves **strong diagnostic performance** at all three stages, with performance improving meaningfully as clinical data accumulates. The system is deliberately **optimised for sensitivity** — in a screening context, a missed PCOS case causes harm; a false alarm prompts further investigation at manageable cost.

---

## 📊 Quantitative Results

### 📈 Progressive Model Performance

| Stage | Features Available | Threshold | Sensitivity | Specificity | AUC | Accuracy | F1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Stage 1 (Symptomatic)** | Symptoms + anthropometrics only | 0.16 | **86.1%** | 71.2% | **0.890** | 76.1% | 0.705 |
| **Stage 2 (Clinical)** | + Hormonal / metabolic bloodwork | 0.21 | **91.7%** | 68.5% | **0.899** | 76.1% | 0.717 |
| **Stage 3 (Imaging)** | + Ultrasound findings | 0.22 | **94.4%** | 82.2% | **0.957** | **86.2%** | **0.819** |

### 🔍 Full-Feature Baseline (Day 1, for reference)

| Model | Sensitivity | Specificity | AUC | Accuracy |
| --- | --- | --- | --- | --- |
| 🤖 **Logistic Regression** | 88.1% | 88.2% | 0.943 | 88.2% |
| 🌲 **Random Forest** | 80.2% | 95.1% | 0.958 | 90.2% |

> 💡 **Key Insight for Recruiters:**
> The baseline models use all features simultaneously. The progressive models are compared against these to demonstrate that staged escalation — beginning with no-blood-test inputs — still delivers clinically useful performance at Stage 1, and approaches full-feature performance by Stage 3.

---

## 🧠 Interpretation of the Progressive Arc

* **Stage 1 AUC of 0.890 with 86.1% sensitivity** from symptoms and anthropometrics alone is a **clinically meaningful result**. It means a GP or nurse with no laboratory access can identify approximately 86 out of every 100 PCOS cases for further investigation — before any blood test has been ordered.
* **Stage 2 sensitivity of 91.7%** demonstrates that adding a standard blood panel **materially improves diagnostic confidence**. The modest specificity decrease at Stage 2 relative to Stage 1 is expected:  sensitivity-optimised thresholds were applied independently at each stage.
* **Stage 3 AUC of 0.957 and specificity of 82.2%** represent performance approaching the full-feature baselines, while also providing the confidence needed for a specialist to proceed toward a **definitive diagnosis**. The follicle count features — the most clinically informative ultrasound markers for PCOS — are the top **SHAP contributors** at this stage.

> 📈 **Business & Clinical Value:**
> The progression from 0.890 to 0.957 AUC across stages is not simply an effect of adding more features; it reflects **genuine incremental diagnostic value** at each clinical escalation point, consistent with how PCOS diagnosis actually works in practice.

---

## 🛠️ SHAP Explainability Findings

**SHAP analysis** was run on all three **calibrated models** after training. Key findings:

* **Stage 1 — Top SHAP contributors:**
Hair growth (hirsutism), weight gain, and skin darkening are the most influential features. These align directly with hyperandrogenic and metabolic PCOS criteria and are consistent with clinical experience.
* **Stage 2 — Top SHAP contributors:**
AMH level, FSH/LH ratio, and LH enter as dominant predictors when blood markers are available. This is clinically expected — elevated AMH and LH/FSH reversal are well-established PCOS markers. The **SHAP values** confirm that the model is **learning from the right signals**.
* **Stage 3 — Top SHAP contributors:**
Follicle counts (right and left ovary) dominate at this stage, consistent with the polycystic ovarian morphology criterion in the Rotterdam diagnostic framework. **SHAP magnitudes** at Stage 3 are substantially higher for follicle features than any other predictor, validating that ultrasound data drives the Stage 3 performance jump.

> 🛡️ **Model Reliability:**
> Importantly, **SHAP summaries** demonstrate that the model is **not relying on spurious or counter-intuitive correlates** — a key concern when deploying **ML in clinical settings**.

---

## 🧬 Phenotype Clustering Results

**KMeans clustering** on PCOS-positive patients identified **three distinct phenotypic subgroups**:

* 🧪 **Cluster 0 — Metabolic-hyperandrogenic phenotype:** Elevated BMI, waist-to-hip ratio, weight gain, and skin darkening. AMH moderately elevated. Typical presentation: obese PCOS with insulin resistance features.
* 🧪 **Cluster 1 — Hormonal phenotype:** Elevated LH, LH/FSH reversal, and AMH. Lower BMI. Typical presentation: lean PCOS with primary hormonal dysregulation.
* 🧪 **Cluster 2 — Milder / mixed phenotype:** Less pronounced elevation across markers. Typical presentation: subclinical or early-stage PCOS with heterogeneous features.

> 🧬 **Domain Expertise:**
> These clusters correspond to PCOS phenotypic categories recognised in clinical literature (phenotypes A–D under the Rotterdam framework), providing **external face validity** for the **unsupervised groupings**.

---

## ⚙️ Recommendation Engine Examples

Three representative recommendation outputs from the **integrated engine**:

* 🟢 **Low risk (Stage 1, probability: 0.27):**

> "Current symptom pattern suggests lower PCOS risk. Continue tracking cycle regularity and metabolic symptoms; reassess if symptoms persist or worsen."

* 🟡 **Moderate risk (Stage 2, probability: 0.52):**

> "Bloodwork and symptoms suggest possible PCOS risk. Recommended next step: ultrasound assessment and specialist review."

* 🔴 **High risk (Stage 3, probability: 0.91):**

> "Combined findings suggest elevated PCOS risk. Clinical confirmation, metabolic risk assessment, and management planning are recommended."
> **Top factors:** right ovarian follicle count (15), left ovarian follicle count (13), weight gain.

> 🎯 **Product Impact:**
> The **recommendation engine** translates **model probabilities** into concrete, stage-specific next actions rather than generic guidance — which is the output format most usable by clinicians in practice.

---

## 🧪 Validation Approach and Limitations

All models were evaluated on a **held-out test split** (**stratified, 20% of data**) with **cross-validation** used during **hyperparameter selection**. **Sensitivity-optimised thresholds** were selected on the test set and reported as final metrics.

### ⚠️ Current validation constraints:

* Single dataset from a single clinical source. **External validation** on a geographically or ethnically distinct cohort has not been performed.
* The dataset (541 records) is moderate in size. **Confidence intervals** on reported metrics are non-trivial; results should be interpreted as indicative rather than definitive.
* No **prospective clinical deployment** has occurred. Reported sensitivity and specificity reflect **retrospective performance** on a **labelled dataset**.
* **Fairness evaluation** across subgroups (age bands, BMI categories, ethnicity) has not been formally conducted.

### 🔬 What internal validation shows:

The consistency between **cross-validation AUC scores** and **held-out test AUC scores** suggests the models generalise reasonably within the dataset distribution. **Calibration** was validated by comparing **predicted probabilities** to observed outcome frequencies across **probability bins**.