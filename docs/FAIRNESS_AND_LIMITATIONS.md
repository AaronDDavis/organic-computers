# 📊 Fairness & Limitations — PCOSense

## 💡 Honest Assessment

PCOSense is a hackathon prototype built on a single public dataset, trained over a short development cycle. The clinical and technical aspirations of the system are genuine, but so are its current limitations. This document states both clearly.

---

## 🗄️ Dataset Constraints

The model was trained on `PCOS_data_without_infertility.xlsx`, a single-centre dataset collected in India. This creates several constraints that any deployment evaluation must consider:

* **Demographic homogeneity.** The dataset does not include ethnicity breakdowns, geographic diversity across income settings, or representation from populations where PCOS presentation is known to differ (e.g., lean PCOS phenotypes are more prevalent in South and East Asian populations compared to Western cohorts; metabolic features are more prominent in South Asian women even at lower BMIs). A model trained on this population may not generalise to Black, Hispanic, Middle Eastern, or other population groups without revalidation.
* **Single-centre recruitment bias.** Patients in a single hospital dataset are a non-random sample of the underlying population. Women who reached clinical attention were already enough symptomatic to present — which means the model has not learned from the large proportion of the PCOS population who remain undiagnosed precisely because their symptoms are milder or less typical.
* **No external validation.** All reported metrics reflect performance on a held-out 20% split of the same dataset. The model has not been tested on an independent cohort. Performance on an external dataset may differ, potentially substantially.
* **Sample size.** The dataset contains 541 patients. While adequate for proof-of-concept modelling with regularised tree ensembles, it is small by clinical ML standards and not sufficient to reliably evaluate performance across subgroups.

---

## ⚖️ Structural Bias in Ground Truth

The diagnostic labels in the training data are themselves subject to the same systemic biases the system aims to address. If the original diagnoses were made by clinicians who applied Rotterdam criteria inconsistently, missed presentations in certain patient groups, or were influenced by implicit bias, those errors are embedded in the training signal. A model cannot be more unbiased than the data it was trained on.

This is a fundamental problem for all supervised clinical ML, not specific to this project. It is worth naming explicitly because it means that debiasing the model algorithmically is insufficient — improving training data quality is the more important intervention.

---

## 🩺 Clinical Limitations

* **Not a replacement for clinical assessment.** PCOSense produces risk probabilities and structured next-step recommendations. It does not issue diagnoses. The Rotterdam criteria require clinical judgment, physical examination findings, and laboratory and imaging results interpreted in context — none of which the system can substitute.
* **Differential diagnosis is incomplete.** The current implementation identifies PCOS risk but does not actively differentiate PCOS from closely overlapping conditions: endometriosis (which can cause cycle irregularity and pelvic pain), hypothyroidism (which overlaps on weight gain and cycle changes), hyperprolactinaemia (which requires prolactin measurement to exclude), or congenital adrenal hyperplasia (a rare but important differential for hyperandrogenism). These conditions are flagged implicitly through marker inclusion (TSH, prolactin) but not modelled explicitly as alternative diagnoses.
* **Calibration is promising but unvalidated in deployment.** Isotonic calibration was applied to improve probability reliability. The calibration curves have not been evaluated on an independent dataset, and probability estimates should not be used as if they were validated clinical risk scores.
* **Phenotype clustering is exploratory.** The three phenotypic subgroups produced by KMeans clustering are clinically interpretable, but clustering solutions are sensitive to hyperparameter choices, dataset composition, and the feature set used. The cluster labels should be treated as hypothesis-generating rather than diagnostic.

---

## 🛠️ Technical Limitations

* **No prospective validation.** The system has not been tested in a real clinical environment. Prospective studies with clinician feedback, usability testing, and outcome tracking have not been conducted.
* **Missing data handling is rudimentary.** Median imputation is used for missing values in the inference pipeline. In a real deployment, structured missingness (e.g., a test not performed because a clinician judged it unnecessary) carries clinical information that median imputation discards.
* **Feature availability assumptions.** The staged model structure assumes that Stage 1 features are always available before Stage 2, and Stage 2 before Stage 3. In practice, some patients may present with partial Stage 2 data (e.g., AMH only) without full Stage 1 documentation, or imaging data without current bloodwork. The current inference pipeline does not handle these partial-pathway inputs gracefully.
* **Model interpretability at the individual level.** Top-factor extraction in the current implementation returns global feature importance rankings, not patient-specific SHAP values. This means the "top factors" displayed for a given patient represent overall model behaviour rather than the specific features that drove that patient's individual prediction. Patient-level SHAP inference is implemented in the modelling pipeline and should be integrated into the live inference path.

---

## 🌍 Accessibility and Equity by Design

> ### 🚀 Key Architectural Wins for Equity
> 
> 
> * **Stage 1 requires no laboratory access.** A risk assessment can be completed using only information that a patient can self-report or that can be gathered in a primary care consultation without specialist equipment. This makes the system usable in community health settings, rural clinics, and telehealth contexts where blood tests or ultrasound are not immediately available.
> * **Progressive escalation reduces unnecessary cost.** By reserving Stage 3 (ultrasound) for patients who already show elevated risk at Stage 2, the system reduces the volume of expensive imaging ordered — which matters in both low-resource public health settings and insurance-constrained environments.
> * **Multi-facility support.** The clinic and doctor data models support multi-centre deployment, enabling use across a healthcare network rather than requiring individual clinician-level setup.
> * **Web-based, device-agnostic interface.** The Django/HTML frontend requires no specialist software installation and is accessible from any modern browser, including on low-specification devices.
> 
> 

---

## 🛡️ Ethical Commitments

The system is designed and documented with the following commitments:

* **Human oversight is mandatory.** All outputs are decision support, not decisions. The system must operate under clinician supervision.
* **Transparency over automation.** The recommendation engine surfaces its reasoning (next step, specialist rationale, contributing factors) rather than issuing opaque scores.
* **Limitation disclosure.** Known limitations — dataset constraints, unvalidated calibration, incomplete differential diagnosis — are stated here and should be communicated to any clinical user.
* **Consent and data protection.** Patient data fields use field-level encryption. Deployment must comply with applicable health data regulations (HIPAA, GDPR, or equivalent national frameworks).

---

## 📋 Priority Validation Steps Before Any Clinical Use

If PCOSense were to move beyond prototype status, the following would be the minimum required before deployment:

1. 🔄 External validation on an independent, demographically diverse dataset
2. 🏥 Prospective pilot study with clinician feedback and outcome tracking
3. 🧮 Patient-level (not global) SHAP explanation integration
4. 📈 Subgroup performance analysis across ethnicity, age, and BMI strata
5. ⚖️ Formal fairness evaluation against recognised equity metrics
6. 🛡️ Clinical safety review and regulatory pathway assessment
