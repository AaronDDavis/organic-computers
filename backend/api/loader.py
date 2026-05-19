from joblib import load
from pathlib import Path

ML_DIR = Path(__file__).resolve().parent.parent.parent / 'ml'/ 'models'

stage1_model = load(ML_DIR/ 'stage1_model.joblib')['model']
stage2_model = load(ML_DIR/ 'stage2_model.joblib')['model']
stage3_model = load(ML_DIR/ 'stage3_model.joblib')['model']
phenotype_model_artifact = load(ML_DIR/ 'phenotype_model.joblib')
