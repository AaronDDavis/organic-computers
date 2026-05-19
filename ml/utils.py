RISK_THRESHOLDS = {
    'High': 0.65,
    'Moderate': 0.35,
}

# EDIT THRESHOLD once received

def score_to_risk(score):
    return (
        'High' if score > RISK_THRESHOLDS['High']
        else 'Moderate' if score >= RISK_THRESHOLDS['Moderate']
        else 'Low'
    )


def calculate_referral(data: dict) -> tuple[str, str]:
    metabolic_score = 0
    if data.get('BMI', 0) > 25:
        metabolic_score += 1
    if data.get('Skin darkening (Y/N)', 0) == 1:
        metabolic_score += 2  # Strong clinical indicator
    if data.get('RBS(mg/dl)', 0) > 140:
        metabolic_score += 2
    # Waist-to-hip ignored because not accepted in forms

    reproductive_score = 0
    if data.get('Cycle(R/I)', 2) == 4:
        reproductive_score += 2
    if data.get('Follicle No. (L)', 0) >= 12 or \
       data.get('Follicle No. (R)', 0) >= 12:
        reproductive_score += 2

    age = data.get('Age (yrs)', 30)
    amh = data.get('AMH(ng/mL)', 0)
    if (amh > 3.0 and age <= 30) or \
       (amh > 2.0 and 30 < age <= 35) or \
       (amh > 1.0 and 35 < age <= 40) or \
       (amh > 0.5 and age > 40):
        reproductive_score += 1

    if metabolic_score > reproductive_score and metabolic_score >= 2:
        return 'Endocrinologist', 'Metabolic Focus'
    elif reproductive_score >= metabolic_score and reproductive_score >= 2:
        return 'Gynecologist', 'Reproductive Focus'
    return 'General Practitioner', 'Baseline Health'


def compute_rotterdam(data: dict) -> int:
    score = 0

    # Criterion 1: Irregular cycle
    if data.get('Cycle(R/I)', 2) in [4, 5]:
        score += 1

    # Criterion 2: Hyperandrogenism (hair growth as proxy)
    age = data.get('Age (yrs)', 30)
    amh = data.get('AMH(ng/mL)', 0)
    if (amh > 3.0 and age <= 30) or \
       (amh > 2.0 and 30 < age <= 35) or \
       (amh > 1.0 and 35 < age <= 40) or \
       (amh > 0.5 and age > 40) or \
        data.get('hair growth(Y/N)', 0) == 1:
        score += 1

    # Criterion 3: Polycystic ovaries (follicle count >= 12 on either side)
    if data.get('Follicle No. (L)', 0) >= 12 or \
       data.get('Follicle No. (R)', 0) >= 12:
        score += 1

    return score  # 0–3; >= 2 meets Rotterdam criteria


def get_recommendation(data: dict, model_score: float) -> dict:
    risk = score_to_risk(model_score)
    specialist, focus = calculate_referral(data)

    # Rotterdam as a safety net override
    rotterdam = compute_rotterdam(data)
    if rotterdam >= 2:
        risk = 'High'  # Hard clinical override

    if risk == 'High':
        text = f"Your profile strongly aligns with PCOS diagnostic criteria. Given your {focus}, we recommend a priority consultation with a {specialist}."
        next_step = ""
    elif risk == 'Moderate':
        text = f"You show some markers associated with PCOS. We suggest a follow-up with a {specialist} to monitor your {focus} parameters."
        next_step = ""
    else:
        text = "Your results are within normal ranges. Continue regular screenings and maintain a balanced lifestyle."
        next_step = ""

    return {
        'risk_level': risk,
        'specialist': specialist,
        'focus': focus,
        'next_step': next_step,
        'recommendation_text': text
    }
