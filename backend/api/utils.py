import pandas as pd
from ...ml.utils import get_recommendation
from .constants import FEATURE_LABELS_BY_STAGE


def run_prediction(model, data, stage):
    df = pd.DataFrame([data])
    score = float(model.predict_proba(df)[0][1])
    recommendation = get_recommendation(data, score)
    top_factors = get_top_factors(model, stage)

    return {
        'stage': stage,
        'risk': recommendation['risk_level'],
        'confidence': round(score, 3),
        'top_factors': top_factors,
        'specialist': recommendation['specialist'],
        'clinical_focus': recommendation['focus'],
        'next_step': recommendation['next_step'],
        'recommendation_text': recommendation['recommendation_text'],
        'missing_fields_imputed': [],
        'differential': None # if stage != 3 else {},  # Plug differential model here
    }


def get_top_factors(model, stage):
    FEATURE_LABELS = FEATURE_LABELS_BY_STAGE[stage]
    
    feature_names = model.feature_names_in_
    top_indices = model.feature_importances_.argsort()[::-1][:3]
    
    return [FEATURE_LABELS.get(feature_names[i], feature_names[i]) for i in top_indices]

