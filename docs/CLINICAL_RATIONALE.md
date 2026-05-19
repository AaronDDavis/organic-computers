# 🩺 Clinical Rationale — PCOSense 🚀

## 🎯 The Problem with PCOS Diagnosis

**PCOS is the most prevalent endocrine disorder in reproductive-age women**, affecting an estimated 8–13% of this population globally. Despite this prevalence, the **WHO estimates that up to 70% of affected women remain undiagnosed**. Among those eventually diagnosed, a third wait more than two years, and nearly half consult at least three different healthcare providers before receiving the correct diagnosis.

> ⚠️ **The Core Challenge:** This is not primarily a technology gap. **It is a clinical synthesis gap.** PCOS has no single confirmatory test. Diagnosis requires a clinician to simultaneously assess:

* **Menstrual and ovulatory dysfunction** — irregular cycles, anovulation
* **Hyperandrogenism** — hirsutism, acne, hair loss, elevated androgens
* **Polycystic ovarian morphology** — follicle count and ovarian volume on ultrasound
* **Metabolic co-morbidities** — insulin resistance, dyslipidaemia, elevated BMI
* **Exclusion of overlapping conditions** — thyroid dysfunction, hyperprolactinaemia, congenital adrenal hyperplasia, Cushing's syndrome

The diagnostic burden is high, the condition is heterogeneous (no two patients present identically), and the clinical training ecosystem historically underweights women's reproductive health. **The result:** delayed, missed, or incorrect diagnoses — with downstream consequences that include progression to type 2 diabetes, cardiovascular risk, infertility, and significant psychological burden.

---

## 🛠️ Why a Staged Approach Matches Clinical Reality

The architecture of **PCOSense** is not a design choice made for technical convenience. It **directly mirrors the escalation pathway** that clinicians follow in practice.

### 📍 Stage 1 — Primary Care Screening

In a real consultation, the first available information is what the patient can report: cycle irregularity, recent weight gain, acne, hirsutism, hair loss, and lifestyle factors. No tests have been ordered yet. A GP must decide, based on this information alone, whether to investigate further.

**Stage 1 of PCOSense operates on the same inputs:** **16 symptom, anthropometric, and lifestyle features** that require no laboratory access. A high Stage 1 risk score produces a specific recommendation to pursue hormonal and metabolic bloodwork — the same next step a well-informed GP would take.

### 🩸 Stage 2 — Hormonal and Metabolic Panel

When blood results are available, the clinical picture sharpens. Key markers include **LH:FSH ratio** (elevated in many PCOS presentations), **AMH** (a sensitive marker of antral follicle pool), **TSH and prolactin** (to exclude thyroid disease and hyperprolactinaemia), **random blood sugar** (insulin resistance screening), and sex hormones.

**Stage 2 adds these 12 hormonal and metabolic features** to the Stage 1 inputs. The model benefits from the additional discriminative power of laboratory markers to **improve specificity** — reducing the rate of false positives that might lead to unnecessary specialist referral.

### 🧬 Stage 3 — Ultrasound / Imaging Integration

Pelvic ultrasound provides the third leg of Rotterdam criteria: polycystic ovarian morphology, defined by **follicle count** ($\ge12$ follicles per ovary on 2D ultrasound, or $\ge20$ on newer technology) or **increased ovarian volume** ($>10\text{ mL}$). This is the highest-cost investigation in the pathway, requiring equipment and trained operators — which is precisely why the staged architecture reserves it for patients who already show elevated risk at Stage 2.

**Stage 3 incorporates bilateral follicle counts, follicle sizes, and endometrial thickness.** The model at this stage has access to the fullest available clinical picture and produces the **highest-confidence risk estimates**.

---

## 📊 Alignment with Diagnostic Frameworks

PCOSense's three-stage feature structure maps onto the **Rotterdam 2003 consensus criteria**, the most widely used diagnostic framework for PCOS. Rotterdam requires two of three criteria:

1. Oligo/anovulation
2. Clinical or biochemical hyperandrogenism
3. Polycystic ovaries on ultrasound

### 🗺️ Feature Mapping Architecture

The staged feature groups directly correspond to these domains:

| Rotterdam Criterion | PCOSense Stage Mapping |
| --- | --- |
| **Oligo/anovulation** | Stage 1 (cycle regularity, cycle length) |
| **Clinical hyperandrogenism** | Stage 1 (acne, hirsutism, hair loss) |
| **Biochemical hyperandrogenism** | Stage 2 (LH, AMH, FSH/LH ratio) |
| **Polycystic ovarian morphology** | Stage 3 (follicle counts, ovarian volume) |

> 🔍 **System Integration Note:** The system also incorporates markers relevant to differential diagnosis and comorbidity screening: **TSH** (thyroid exclusion), **prolactin** (hyperprolactinaemia exclusion), **blood pressure**, and **fasting glucose**.

---

## 🧠 Addressing Heterogeneity Through Phenotype Clustering

One of the most clinically challenging aspects of PCOS is that it is not a single disease but a syndrome with multiple phenotypic expressions. Under Rotterdam criteria, **four distinct phenotypes are recognised (A–D)**, ranging from full classical presentation to non-hyperandrogenic variants. This heterogeneity creates diagnostic ambiguity and means that patients with the same diagnosis may have very different metabolic risks and treatment needs.

PCOSense addresses this through an **unsupervised phenotype clustering component** applied to PCOS-positive patients. **KMeans clustering over 13 metabolic, reproductive, and hyperandrogenic features** identifies three phenotypic subgroups:

* **📈 Metabolic profile** — elevated BMI, waist-hip ratio, blood sugar, and skin darkening; may benefit from early metabolic intervention
* **🪺 Reproductive/ovarian profile** — elevated AMH, high follicle counts, irregular cycles; reproductive medicine referral is prioritised
* **🧬 Mixed hyperandrogenic profile** — prominent hirsutism, acne, and mixed endocrine features

**Surfacing phenotype context alongside a risk score** gives clinicians not just a probability but a direction — which aspect of the condition is most clinically prominent for this patient.

---

## 👁️ Explainability as a Clinical Requirement

> 💡 **Product Philosophy:** Clinical AI that cannot explain its reasoning will not be used — and should not be. Clinicians are trained to justify their diagnostic decisions, and any tool that produces a risk score without supporting evidence will (correctly) be treated with suspicion.

**SHAP (SHapley Additive exPlanations) values** are used to provide both global feature importance and patient-level prediction explanations across all three stages. This enables:

* **🔍 Transparency** — which features drove a high-risk prediction for this specific patient
* **🛡️ Audit capability** — clinicians can verify that the model's reasoning aligns with clinical expectation
* **🎓 Education** — the explanation surface reinforces which symptom combinations are most predictive, supporting clinical learning
* **🤝 Trust calibration** — if the model flags an unexpected feature as highly influential, the clinician can investigate rather than accept the score uncritically

---

## 🔀 Specialist Routing Logic

A common failure mode in PCOS care is inappropriate referral — sending a patient with predominantly metabolic features to a gynaecologist, or a patient with primarily reproductive concerns to an endocrinologist. Both delay appropriate care.

PCOSense's recommendation engine uses a **heuristic scoring approach** to route patients based on their actual clinical profile:

* **🧪 Metabolic signals:** elevated BMI, raised random blood sugar, skin darkening, high waist-hip ratio $\rightarrow$ **Endocrinologist**
* **🩺 Reproductive/ovarian signals:** irregular cycles, elevated AMH, hirsutism, high follicle counts $\rightarrow$ **Gynaecologist**
* **⚖️ Balanced profiles:** recommendations indicate either specialty may be appropriate, with guidance to prioritise based on local availability

---

## 🏥 Intended Clinical Position

🏥 **Clinical Decision Support Tool** PCOSense is designed as a decision support tool — **not an autonomous diagnostic system**.

### 📋 Intended Use Case:

* Helping primary care clinicians identify patients warranting further investigation earlier in the care pathway
* Reducing inconsistency in diagnostic escalation decisions
* Supporting non-specialist clinicians (GPs, nurses, community health workers) who may have limited PCOS-specific training
* Providing a structured, evidence-linked reasoning trail alongside the risk estimate

> 🚫 **Boundary Safeguard:** The system is **explicitly not intended** to replace the clinical encounter, override clinician judgment, or issue a diagnosis. All outputs are framed as risk estimates and recommendations for next steps, not diagnoses.
