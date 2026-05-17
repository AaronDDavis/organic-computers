from joblib import load
from pathlib import Path

ML_DIR = Path(__file__).resolve().parent.parent.parent / 'ml'/ 'models'

stage1_model = load(ML_DIR/ 'stage1_model.pkl')
stage2_model = load(ML_DIR/ 'stage2_model.pkl')
stage3_model = load(ML_DIR/ 'stage3_model.pkl')
