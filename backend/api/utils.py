import os
import sys
from pathlib import Path
from dotenv import load_dotenv

CURRENT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = CURRENT_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

if "PYTHONPATH" in os.environ:
    root_dir = (CURRENT_DIR / os.environ["PYTHONPATH"]).resolve()
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))


import pandas as pd
from ml.utils import get_recommendation
from .constants import FEATURE_LABELS_BY_STAGE, STAGE_EXPECTED_FEATURES


def run_prediction(model, data, stage):
    expected_features = STAGE_EXPECTED_FEATURES.get(stage)
    model_input_data = {
        feature: data.get(feature) for feature in expected_features
    }

    df = pd.DataFrame([model_input_data], columns=expected_features)
    score = float(model.predict_proba(df)[0, 1])
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
    return list(FEATURE_LABELS_BY_STAGE[stage].values())[:3]

