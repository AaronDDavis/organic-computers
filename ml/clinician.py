import pandas as pd
import numpy as np
import json

df = pd.read_csv('(Main_Dataset)_PCOS_data_without_infertility.csv')
df['AMH(ng/mL)'] = pd.to_numeric(df['AMH(ng/mL)'], errors='coerce')
df = df.dropna()

# Feature Clusters for Referral Logic
def calculate_referral(row):
    # Metabolic Cluster - High BMI, Skin Darkening, High Waist:Hip, Elevated Sugar
    metabolic_score = 0
    if row['BMI'] > 25: metabolic_score += 1
    if row['Skin darkening (Y/N)'] == 1: metabolic_score += 2  # Strong clinical indicator
    if row['Waist:Hip Ratio'] > 0.85: metabolic_score += 1
    if row['RBS(mg/dl)'] > 140: metabolic_score += 2

    # Reproductive Cluster - Irregular Cycle, High Follicle Count, High AMH
    reproductive_score = 0
    if row['Cycle(R/I)'] in [4, 5]: reproductive_score += 2
    if (row['Follicle No. (L)'] >= 12) or (row['Follicle No. (R)'] >= 12): reproductive_score += 2
    if (
        (row['AMH(ng/mL)'] > 3.0) & (row[' Age (yrs)'] <= 25) |
        (row['AMH(ng/mL)'] > 3.0) & (row[' Age (yrs)'] > 25) & (row[' Age (yrs)'] <= 30) |
        (row['AMH(ng/mL)'] > 2.0) & (row[' Age (yrs)'] > 30) & (row[' Age (yrs)'] <= 35) |
        (row['AMH(ng/mL)'] > 1.0) & (row[' Age (yrs)'] > 35) & (row[' Age (yrs)'] <= 40) |
        (row['AMH(ng/mL)'] > 0.5) & (row[' Age (yrs)'] > 40)
        ): reproductive_score += 1

    if metabolic_score > reproductive_score and metabolic_score >= 2:
        return "Endocrinologist", "Metabolic Focus"
    elif reproductive_score >= metabolic_score and reproductive_score >= 2:
        return "Gynecologist", "Reproductive Focus"
    else:
        return "General Practitioner", "Baseline Health"

def get_recommendation(row):
    specialist, focus = calculate_referral(row)
    rotterdam_score = (1 if row['Cycle(R/I)'] in [4, 5] else 0) + \
                      (1 if (
                            (row['AMH(ng/mL)'] > 3.0) & (row[' Age (yrs)'] <= 25) |
                            (row['AMH(ng/mL)'] > 3.0) & (row[' Age (yrs)'] > 25) & (row[' Age (yrs)'] <= 30) |
                            (row['AMH(ng/mL)'] > 2.0) & (row[' Age (yrs)'] > 30) & (row[' Age (yrs)'] <= 35) |
                            (row['AMH(ng/mL)'] > 1.0) & (row[' Age (yrs)'] > 35) & (row[' Age (yrs)'] <= 40) |
                            (row['AMH(ng/mL)'] > 0.5) & (row[' Age (yrs)'] > 40))
                        or row['hair growth(Y/N)'] == 1 else 0) + \
                      (1 if row['Follicle No. (L)'] >= 12 or row['Follicle No. (R)'] >= 12 else 0)
    if rotterdam_score >= 2:
        risk = "3" #high
        text = f"Your profile strongly aligns with PCOS diagnostic criteria. Given your {focus}, we recommend a priority consultation with a {specialist}."
    elif rotterdam_score == 1 or row['BMI'] > 25:
        risk = "2"
        text = f"You show some markers associated with PCOS. We suggest a follow-up with a {specialist} to monitor your {focus} parameters."
    else:
        risk = "1"
        text = "Your results are within normal ranges. Continue regular screenings and maintain a balanced lifestyle."

    return risk, specialist, text

df[['Risk_Level', 'Recommended_Specialist', 'Recommendation_Text']] = df.apply(
    lambda row: pd.Series(get_recommendation(row)), axis=1
)

rules = {
    "risk_bands": {
        "High": {"criteria": "Rotterdam >= 2", "action": "Immediate Specialist Referral"},
        "Moderate": {"criteria": "Rotterdam == 1 OR BMI > 25", "action": "Primary Care Follow-up"},
        "Low": {"criteria": "Default", "action": "Routine Monitoring"}
    },
    "referral_logic": {
        "Endocrinologist": "Metabolic Score > Reproductive Score (Indicators: BMI, RBS, Acanthosis)",
        "Gynecologist": "Reproductive Score >= Metabolic Score (Indicators: Cycles, Follicles, AMH)"
    }
}

with open('rules.json', 'w') as f:
    json.dump(rules, f, indent=4)
df = df[['Sl. No', 'Patient File No.', 'Risk_Level', 'Recommended_Specialist', 'Recommendation_Text']]
df.to_csv('recommendations.csv', index=False)
#print(df[['Risk_Level', 'Recommended_Specialist', 'Recommendation_Text']].head())