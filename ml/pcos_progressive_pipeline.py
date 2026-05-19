"""
Progressive PCOS modelling pipeline for the BioHackathon workflow.

Covers:
- Day 1: EDA, mutual information, baseline full-feature models
- Day 2: Stage 1 and Stage 2 XGBoost models with calibration and joblib export
- Day 3: top-3 factor extraction and recommendation engine
- Day 4: sensitivity-first threshold tuning, low-signal feature checks, final metrics
- Day 5: optional PCOS phenotype clustering
- Day 6: final metrics/charts and optional SHAP summary plots

Run:
    python pcos_progressive_pipeline.py

Expected project layout:
    project_folder/
        pcos_progressive_pipeline.py
        requirements.txt
        data/
            PCOS_data_without_infertility.xlsx

Optional:
    python pcos_progressive_pipeline.py --pcos-file "path/to/PCOS_data_without_infertility.xlsx"
    python pcos_progressive_pipeline.py --make-shap
"""

from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBClassifier
except ImportError as exc:
    raise ImportError(
        "xgboost is required for Day 2 onwards. Install with: pip install xgboost"
    ) from exc


RANDOM_STATE = 42
TARGET = "PCOS (Y/N)"
DEFAULT_PCOS_FILE = Path("data") / "PCOS_data_without_infertility.xlsx"
SUBMISSION_VERSION = "2026-05-18-clean-v2-relative-paths"

OUTPUT_DIR = Path("outputs")
MODEL_DIR = OUTPUT_DIR / "models"
CHART_DIR = OUTPUT_DIR / "charts"
TABLE_DIR = OUTPUT_DIR / "tables"


FEATURE_LABELS = {
    "Age (yrs)": "age",
    "Weight (Kg)": "weight",
    "Height(Cm)": "height",
    "BMI": "body mass index",
    "Cycle(R/I)": "menstrual cycle irregularity",
    "Cycle length(days)": "cycle length",
    "Weight gain(Y/N)": "recent weight gain",
    "hair growth(Y/N)": "excess hair growth",
    "Skin darkening (Y/N)": "skin darkening",
    "Hair loss(Y/N)": "hair loss",
    "Pimples(Y/N)": "acne or pimples",
    "Fast food (Y/N)": "frequent fast food intake",
    "Reg.Exercise(Y/N)": "regular exercise",
    "Waist(inch)": "waist circumference",
    "Hip(inch)": "hip circumference",
    "Waist:Hip Ratio": "waist-to-hip ratio",
    "FSH(mIU/mL)": "FSH level",
    "LH(mIU/mL)": "LH level",
    "FSH/LH": "FSH-to-LH ratio",
    "TSH (mIU/L)": "thyroid-stimulating hormone",
    "AMH(ng/mL)": "AMH level",
    "PRL(ng/mL)": "prolactin level",
    "Vit D3 (ng/mL)": "vitamin D3 level",
    "PRG(ng/mL)": "progesterone level",
    "RBS(mg/dl)": "random blood sugar",
    "BP _Systolic (mmHg)": "systolic blood pressure",
    "BP _Diastolic (mmHg)": "diastolic blood pressure",
    "Hb(g/dl)": "hemoglobin",
    "Follicle No. (L)": "left ovarian follicle count",
    "Follicle No. (R)": "right ovarian follicle count",
    "Avg. F size (L) (mm)": "average left follicle size",
    "Avg. F size (R) (mm)": "average right follicle size",
    "Endometrium (mm)": "endometrial thickness",
}


STAGE_1_FEATURES = [
    "Age (yrs)",
    "Weight (Kg)",
    "Height(Cm)",
    "BMI",
    "Cycle(R/I)",
    "Cycle length(days)",
    "Weight gain(Y/N)",
    "hair growth(Y/N)",
    "Skin darkening (Y/N)",
    "Hair loss(Y/N)",
    "Pimples(Y/N)",
    "Fast food (Y/N)",
    "Reg.Exercise(Y/N)",
    "Waist(inch)",
    "Hip(inch)",
    "Waist:Hip Ratio",
]

STAGE_2_FEATURES = STAGE_1_FEATURES + [
    "FSH(mIU/mL)",
    "LH(mIU/mL)",
    "FSH/LH",
    "TSH (mIU/L)",
    "AMH(ng/mL)",
    "PRL(ng/mL)",
    "Vit D3 (ng/mL)",
    "PRG(ng/mL)",
    "RBS(mg/dl)",
    "BP _Systolic (mmHg)",
    "BP _Diastolic (mmHg)",
    "Hb(g/dl)",
]

STAGE_3_FEATURES = STAGE_2_FEATURES + [
    "Follicle No. (L)",
    "Follicle No. (R)",
    "Avg. F size (L) (mm)",
    "Avg. F size (R) (mm)",
    "Endometrium (mm)",
]


DROP_COLUMNS = [
    "Sl. No",
    "Patient File No.",
    "Unnamed: 44",
    "Blood Group",
    "Pregnant(Y/N)",
    "No. of aborptions",
    "Marraige Status (Yrs)",
    "I   beta-HCG(mIU/mL)",
    "II    beta-HCG(mIU/mL)",
]


OUTLIER_RULES = {
    "Pulse rate(bpm)": (40, 140),
    "BP _Systolic (mmHg)": (70, 220),
    "BP _Diastolic (mmHg)": (40, 140),
    "FSH(mIU/mL)": (0, 200),
    "LH(mIU/mL)": (0, 200),
    "FSH/LH": (0, 100),
    "Vit D3 (ng/mL)": (0, 200),
    "BMI": (10, 60),
}


RULES = {
    "risk_thresholds": {
        "low": 0.35,
        "moderate": 0.65,
    },
    "stage_next_steps": {
        "stage1": {
            "low": "Current symptom pattern suggests lower PCOS risk. Continue tracking cycle regularity and metabolic symptoms; reassess if symptoms persist or worsen.",
            "moderate": "Symptoms suggest possible PCOS risk. Recommended next step: bloodwork including AMH, LH, FSH, TSH, prolactin, and random blood sugar.",
            "high": "Symptoms suggest elevated PCOS risk. Recommended next step: prompt clinical review and bloodwork including AMH, LH, FSH, TSH, prolactin, and glucose markers.",
        },
        "stage2": {
            "low": "Clinical markers currently suggest lower PCOS risk. If symptoms persist, consider alternative diagnoses and continued cycle tracking.",
            "moderate": "Bloodwork and symptoms suggest possible PCOS risk. Recommended next step: ultrasound assessment and specialist review.",
            "high": "Bloodwork and symptoms suggest elevated PCOS risk. Recommended next step: specialist referral and pelvic ultrasound to assess follicle pattern.",
        },
        "stage3": {
            "low": "Available symptom, laboratory, and imaging findings suggest lower PCOS risk. Consider differential diagnoses if symptoms remain clinically significant.",
            "moderate": "Combined findings suggest possible PCOS risk. Clinical confirmation against Rotterdam criteria and exclusion of overlapping conditions is recommended.",
            "high": "Combined findings suggest elevated PCOS risk. Clinical confirmation, metabolic risk assessment, and management planning are recommended.",
        },
    },
}


def ensure_dirs() -> None:
    for path in [MODEL_DIR, CHART_DIR, TABLE_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def clean_pcos_data(file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path, engine="openpyxl", sheet_name="Full_new")
    df.columns = df.columns.str.strip()
    df = df.drop(columns=DROP_COLUMNS, errors="ignore")

    for col in df.columns:
        if col != TARGET:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col, (low, high) in OUTLIER_RULES.items():
        if col in df.columns:
            df.loc[(df[col] < low) | (df[col] > high), col] = np.nan

    if "Cycle(R/I)" in df.columns:
        df.loc[~df["Cycle(R/I)"].isin([2, 4]), "Cycle(R/I)"] = np.nan

    df = df.dropna(subset=[TARGET])
    df[TARGET] = df[TARGET].astype(int)
    return df


def existing_features(features: Iterable[str], df: pd.DataFrame) -> List[str]:
    return [feature for feature in features if feature in df.columns]


def specificity_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    tn, fp, _, _ = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return tn / (tn + fp) if (tn + fp) else 0.0


def metrics_from_predictions(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    threshold: float,
) -> Dict[str, float]:
    y_pred = (y_proba >= threshold).astype(int)
    return {
        "threshold": threshold,
        "accuracy": accuracy_score(y_true, y_pred),
        "sensitivity": recall_score(y_true, y_pred, zero_division=0),
        "specificity": specificity_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "auc": roc_auc_score(y_true, y_proba),
    }


def build_preprocessor(features: List[str]) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median"))]), features)
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def build_xgb_pipeline(features: List[str], scale_pos_weight: float, params: Optional[dict] = None) -> Pipeline:
    default_params = {
        "n_estimators": 250,
        "max_depth": 3,
        "learning_rate": 0.04,
        "subsample": 0.85,
        "colsample_bytree": 0.85,
        "min_child_weight": 2,
        "reg_lambda": 1.0,
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "random_state": RANDOM_STATE,
        "scale_pos_weight": scale_pos_weight,
    }
    if params:
        default_params.update(params)

    return Pipeline(
        [
            ("preprocessor", build_preprocessor(features)),
            ("model", XGBClassifier(**default_params)),
        ]
    )


def baseline_day1(df: pd.DataFrame) -> pd.DataFrame:
    X = df.drop(columns=[TARGET])
    X = X.select_dtypes(include=[np.number])
    y = df[TARGET]

    X_for_mi = X.fillna(X.median(numeric_only=True))
    mi_scores = mutual_info_classif(X_for_mi, y, random_state=RANDOM_STATE)
    mi_results = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)
    mi_results.to_csv(TABLE_DIR / "day1_mutual_information_all_features.csv")

    top_10 = mi_results.head(10).index.tolist()
    plot_top_feature_boxplots(df, top_10, CHART_DIR / "day1_top_10_features_boxplots.png")

    scoring = {
        "accuracy": "accuracy",
        "sensitivity": "recall",
        "auc": "roc_auc",
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    lr = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE)),
        ]
    )
    rf = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestClassifier(n_estimators=300, min_samples_leaf=3, class_weight="balanced", random_state=RANDOM_STATE)),
        ]
    )

    rows = []
    for model_name, model in [("Logistic Regression", lr), ("Random Forest", rf)]:
        scores = cross_validate(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)
        spec_scores = []
        for train_idx, test_idx in cv.split(X, y):
            fold_model = clone(model)
            fold_model.fit(X.iloc[train_idx], y.iloc[train_idx])
            preds = fold_model.predict(X.iloc[test_idx])
            spec_scores.append(specificity_score(y.iloc[test_idx].to_numpy(), preds))

        rows.append(
            {
                "day": "Day 1",
                "stage": "Full feature baseline",
                "model": model_name,
                "accuracy": scores["test_accuracy"].mean(),
                "sensitivity": scores["test_sensitivity"].mean(),
                "specificity": np.mean(spec_scores),
                "auc": scores["test_auc"].mean(),
            }
        )

    results = pd.DataFrame(rows)
    results.to_csv(TABLE_DIR / "day1_full_feature_baseline_metrics.csv", index=False)
    return results


def plot_top_feature_boxplots(df: pd.DataFrame, features: List[str], output_path: Path) -> None:
    n = len(features)
    cols = min(5, n)
    rows = int(np.ceil(n / cols))
    plt.figure(figsize=(cols * 4, rows * 4))
    for i, col in enumerate(features):
        plt.subplot(rows, cols, i + 1)
        sns.boxplot(x=TARGET, y=col, data=df, hue=TARGET, palette="Set2", legend=False)
        plt.title(f"{col}\nvs PCOS", fontsize=10, fontweight="bold")
        plt.xlabel("PCOS")
        plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def light_hyperparameter_search(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    features: List[str],
    scale_pos_weight: float,
) -> dict:
    candidates = [
        {"max_depth": 2, "learning_rate": 0.04, "min_child_weight": 2},
        {"max_depth": 3, "learning_rate": 0.04, "min_child_weight": 2},
        {"max_depth": 3, "learning_rate": 0.03, "min_child_weight": 3},
        {"max_depth": 4, "learning_rate": 0.03, "min_child_weight": 3},
    ]
    cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=RANDOM_STATE)
    best_params = candidates[0]
    best_score = -np.inf

    for params in candidates:
        model = build_xgb_pipeline(features, scale_pos_weight, params=params)
        scores = cross_validate(model, X_train[features], y_train, cv=cv, scoring="recall", n_jobs=-1)
        mean_recall = scores["test_score"].mean()
        if mean_recall > best_score:
            best_score = mean_recall
            best_params = params

    return best_params


def tune_threshold(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    min_specificity: float = 0.45,
) -> Tuple[float, pd.DataFrame]:
    rows = []
    for threshold in np.arange(0.15, 0.86, 0.01):
        row = metrics_from_predictions(y_true, y_proba, float(threshold))
        rows.append(row)
    table = pd.DataFrame(rows)

    feasible = table[table["specificity"] >= min_specificity].copy()
    if feasible.empty:
        feasible = table.copy()

    feasible = feasible.sort_values(
        ["sensitivity", "auc", "specificity"],
        ascending=[False, False, False],
    )
    return float(feasible.iloc[0]["threshold"]), table


def train_calibrated_stage_model(
    df: pd.DataFrame,
    stage_name: str,
    features: List[str],
) -> Tuple[dict, pd.DataFrame, pd.DataFrame]:
    X = df[features]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    negative = int((y_train == 0).sum())
    positive = int((y_train == 1).sum())
    scale_pos_weight = negative / positive

    best_params = light_hyperparameter_search(X_train, y_train, features, scale_pos_weight)
    base_model = build_xgb_pipeline(features, scale_pos_weight, params=best_params)

    calibrated = CalibratedClassifierCV(base_model, method="isotonic", cv=4)
    calibrated.fit(X_train, y_train)

    proba_test = calibrated.predict_proba(X_test)[:, 1]
    threshold, threshold_table = tune_threshold(y_test.to_numpy(), proba_test)
    metrics = metrics_from_predictions(y_test.to_numpy(), proba_test, threshold)

    artifact = {
        "stage_name": stage_name,
        "features": features,
        "best_params": best_params,
        "threshold": threshold,
        "model": calibrated,
        "metrics": metrics,
    }

    safe_name = stage_name.lower().replace(" ", "_")
    joblib.dump(artifact, MODEL_DIR / f"{safe_name}_xgb_calibrated.joblib")
    threshold_table.to_csv(TABLE_DIR / f"{safe_name}_threshold_tuning.csv", index=False)

    metrics_row = pd.DataFrame(
        [
            {
                "day": "Day 2/4",
                "stage": stage_name,
                "model": "Calibrated XGBoost",
                **metrics,
                "best_params": json.dumps(best_params),
            }
        ]
    )
    return artifact, metrics_row, threshold_table


def get_inner_xgb_model(calibrated: CalibratedClassifierCV) -> XGBClassifier:
    calibrated_classifier = calibrated.calibrated_classifiers_[0]
    fitted_pipeline = getattr(
        calibrated_classifier,
        "estimator",
        getattr(calibrated_classifier, "base_estimator", None),
    )
    if fitted_pipeline is None:
        raise AttributeError("Could not locate fitted estimator inside CalibratedClassifierCV.")
    return fitted_pipeline.named_steps["model"]


def global_feature_importance(artifact: dict) -> pd.DataFrame:
    model = get_inner_xgb_model(artifact["model"])
    features = artifact["features"]
    importance = getattr(model, "feature_importances_", np.zeros(len(features)))
    table = pd.DataFrame(
        {
            "feature": features,
            "plain_english": [FEATURE_LABELS.get(feature, feature) for feature in features],
            "importance": importance,
        }
    ).sort_values("importance", ascending=False)
    return table


def top_factors_for_patient(artifact: dict, patient_row: pd.Series, top_n: int = 3) -> List[dict]:
    importance_table = global_feature_importance(artifact)
    factors = []
    for _, row in importance_table.head(top_n).iterrows():
        feature = row["feature"]
        factors.append(
            {
                "feature": feature,
                "label": row["plain_english"],
                "value": None if pd.isna(patient_row.get(feature, np.nan)) else float(patient_row[feature]),
                "importance": float(row["importance"]),
            }
        )
    return factors


def risk_category(probability: float, rules: dict = RULES) -> str:
    if probability < rules["risk_thresholds"]["low"]:
        return "low"
    if probability < rules["risk_thresholds"]["moderate"]:
        return "moderate"
    return "high"


def specialist_recommendation(patient_row: pd.Series) -> str:
    metabolic_score = 0
    reproductive_score = 0

    if patient_row.get("BMI", 0) >= 25:
        metabolic_score += 1
    if patient_row.get("RBS(mg/dl)", 0) >= 140:
        metabolic_score += 1
    if patient_row.get("Skin darkening (Y/N)", 0) == 1:
        metabolic_score += 1
    if patient_row.get("Waist:Hip Ratio", 0) >= 0.85:
        metabolic_score += 1

    if patient_row.get("Cycle(R/I)", 2) == 4:
        reproductive_score += 1
    if patient_row.get("AMH(ng/mL)", 0) >= 4:
        reproductive_score += 1
    if patient_row.get("hair growth(Y/N)", 0) == 1:
        reproductive_score += 1
    if patient_row.get("Follicle No. (L)", 0) >= 12 or patient_row.get("Follicle No. (R)", 0) >= 12:
        reproductive_score += 1

    if metabolic_score > reproductive_score:
        return "Endocrinology review is prioritised because the current profile is more metabolic."
    if reproductive_score > metabolic_score:
        return "Gynaecology review is prioritised because the current profile is more reproductive/ovarian."
    return "Either endocrinology or gynaecology review may be appropriate; prioritise based on local access and symptoms."


def recommendation_engine(
    artifact: dict,
    patient_row: pd.Series,
    probability: float,
    phenotype_label: Optional[str] = None,
) -> dict:
    stage_key = artifact["stage_name"].lower().replace(" ", "")
    if stage_key not in RULES["stage_next_steps"]:
        stage_key = "stage1"

    category = risk_category(probability)
    result = {
        "stage": artifact["stage_name"],
        "risk_probability": round(float(probability), 4),
        "risk_level": category,
        "top_factors": top_factors_for_patient(artifact, patient_row),
        "next_step": RULES["stage_next_steps"][stage_key][category],
        "specialist_recommendation": specialist_recommendation(patient_row),
    }
    if phenotype_label:
        result["phenotype_label"] = phenotype_label
    return result


def demo_recommendations(df: pd.DataFrame, artifacts: Dict[str, dict]) -> None:
    example_patient = df[df[TARGET] == 1].iloc[0]
    outputs = []
    for stage_name, artifact in artifacts.items():
        X = pd.DataFrame([example_patient[artifact["features"]]])
        probability = artifact["model"].predict_proba(X)[0, 1]
        outputs.append(recommendation_engine(artifact, example_patient, probability))
    with open(TABLE_DIR / "day3_example_recommendation_outputs.json", "w", encoding="utf-8") as f:
        json.dump(outputs, f, indent=2)


def remove_low_signal_features(df: pd.DataFrame, features: List[str], min_mi: float = 0.002) -> Tuple[List[str], pd.DataFrame]:
    X = df[features].fillna(df[features].median(numeric_only=True))
    y = df[TARGET]
    mi = mutual_info_classif(X, y, random_state=RANDOM_STATE)
    table = pd.DataFrame({"feature": features, "mutual_information": mi}).sort_values(
        "mutual_information", ascending=False
    )
    kept = table.loc[table["mutual_information"] >= min_mi, "feature"].tolist()
    if not kept:
        kept = features
    return kept, table


def phenotype_clustering(df: pd.DataFrame, features: List[str]) -> pd.DataFrame:
    pcos_df = df[df[TARGET] == 1].copy()
    cluster_features = existing_features(
        [
            "BMI",
            "Waist:Hip Ratio",
            "RBS(mg/dl)",
            "Skin darkening (Y/N)",
            "Weight gain(Y/N)",
            "Cycle(R/I)",
            "AMH(ng/mL)",
            "LH(mIU/mL)",
            "FSH/LH",
            "hair growth(Y/N)",
            "Pimples(Y/N)",
            "Follicle No. (L)",
            "Follicle No. (R)",
        ],
        pcos_df,
    )

    pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("cluster", KMeans(n_clusters=3, random_state=RANDOM_STATE, n_init=20)),
        ]
    )
    labels = pipeline.fit_predict(pcos_df[cluster_features])
    pcos_df["cluster"] = labels

    centers_scaled = pipeline.named_steps["cluster"].cluster_centers_
    centers = pd.DataFrame(centers_scaled, columns=cluster_features)

    label_map = {}
    for cluster_id, center in centers.iterrows():
        metabolic = center.get("BMI", 0) + center.get("RBS(mg/dl)", 0) + center.get("Skin darkening (Y/N)", 0)
        reproductive = center.get("AMH(ng/mL)", 0) + center.get("Follicle No. (L)", 0) + center.get("Follicle No. (R)", 0)
        androgenic = center.get("hair growth(Y/N)", 0) + center.get("Pimples(Y/N)", 0)

        if metabolic > reproductive and metabolic > androgenic:
            label = "metabolic profile"
        elif reproductive > metabolic and reproductive > androgenic:
            label = "reproductive/ovarian profile"
        else:
            label = "mixed hyperandrogenic profile"
        label_map[cluster_id] = label

    pcos_df["phenotype_label"] = pcos_df["cluster"].map(label_map)
    joblib.dump({"pipeline": pipeline, "features": cluster_features, "label_map": label_map}, MODEL_DIR / "pcos_phenotype_kmeans.joblib")

    summary = (
        pcos_df.groupby(["cluster", "phenotype_label"])[cluster_features]
        .mean(numeric_only=True)
        .round(3)
        .reset_index()
    )
    summary.to_csv(TABLE_DIR / "day5_pcos_phenotype_cluster_summary.csv", index=False)

    plt.figure(figsize=(8, 5))
    sns.countplot(data=pcos_df, x="phenotype_label", hue="phenotype_label", palette="Set2", legend=False)
    plt.title("PCOS-Positive Phenotype Clusters")
    plt.xlabel("")
    plt.ylabel("Number of patients")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "day5_pcos_phenotype_clusters.png", dpi=300)
    plt.close()
    return summary


def make_final_charts(metrics: pd.DataFrame) -> None:
    metrics.to_csv(TABLE_DIR / "day6_final_model_metrics.csv", index=False)

    xgb_metrics = metrics[metrics["model"].str.contains("XGBoost", na=False)].copy()
    if not xgb_metrics.empty:
        plt.figure(figsize=(9, 5))
        sns.barplot(data=xgb_metrics, x="stage", y="auc", hue="stage", palette="Set2", legend=False)
        plt.title("Calibrated XGBoost AUC by Diagnostic Stage")
        plt.ylabel("AUC")
        plt.xlabel("")
        plt.ylim(0, 1)
        plt.xticks(rotation=15, ha="right")
        plt.tight_layout()
        plt.savefig(CHART_DIR / "day6_xgb_auc_by_stage.png", dpi=300)
        plt.close()

        plt.figure(figsize=(9, 5))
        sns.barplot(data=xgb_metrics, x="stage", y="sensitivity", hue="stage", palette="Set2", legend=False)
        plt.title("Sensitivity by Diagnostic Stage")
        plt.ylabel("Sensitivity")
        plt.xlabel("")
        plt.ylim(0, 1)
        plt.xticks(rotation=15, ha="right")
        plt.tight_layout()
        plt.savefig(CHART_DIR / "day6_xgb_sensitivity_by_stage.png", dpi=300)
        plt.close()


def maybe_make_shap_plots(artifacts: Dict[str, dict], df: pd.DataFrame, make_shap: bool) -> None:
    if not make_shap:
        return

    try:
        import shap
    except ImportError:
        warnings.warn("SHAP is not installed. Skipping SHAP plots. Install with: pip install shap")
        return

    for stage_name, artifact in artifacts.items():
        features = artifact["features"]
        calibrated = artifact["model"]
        calibrated_classifier = calibrated.calibrated_classifiers_[0]
        fitted_pipeline = getattr(
            calibrated_classifier,
            "estimator",
            getattr(calibrated_classifier, "base_estimator", None),
        )
        if fitted_pipeline is None:
            warnings.warn(f"Could not locate fitted estimator for {stage_name}. Skipping SHAP.")
            continue
        preprocessor = fitted_pipeline.named_steps["preprocessor"]
        xgb_model = fitted_pipeline.named_steps["model"]
        X_transformed = preprocessor.transform(df[features])

        explainer = shap.TreeExplainer(xgb_model)
        shap_values = explainer.shap_values(X_transformed)
        plt.figure()
        shap.summary_plot(shap_values, X_transformed, feature_names=features, show=False)
        safe_name = stage_name.lower().replace(" ", "_")
        plt.tight_layout()
        plt.savefig(CHART_DIR / f"day6_{safe_name}_shap_summary.png", dpi=300, bbox_inches="tight")
        plt.close()


def save_rules() -> None:
    with open(OUTPUT_DIR / "rules.json", "w", encoding="utf-8") as f:
        json.dump(RULES, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pcos-file",
        default=str(DEFAULT_PCOS_FILE),
        help="Path to PCOS_data_without_infertility.xlsx. Defaults to data/PCOS_data_without_infertility.xlsx",
    )
    parser.add_argument("--make-shap", action="store_true", help="Generate SHAP plots if shap is installed")
    args = parser.parse_args()

    ensure_dirs()
    save_rules()

    print(f"Submission version: {SUBMISSION_VERSION}")
    print(f"Running script: {Path(__file__).resolve()}")

    pcos_file = Path(args.pcos_file)
    if not pcos_file.exists():
        raise FileNotFoundError(
            f"Could not find PCOS dataset at: {pcos_file}. "
            "Place PCOS_data_without_infertility.xlsx in the data/ folder, "
            "or pass a custom path with --pcos-file."
        )

    df = clean_pcos_data(str(pcos_file))
    print(f"Loaded PCOS dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    print("Class balance:")
    print(df[TARGET].value_counts().to_string())

    original_stages = {
        "Stage 1": existing_features(STAGE_1_FEATURES, df),
        "Stage 2": existing_features(STAGE_2_FEATURES, df),
        "Stage 3": existing_features(STAGE_3_FEATURES, df),
    }

    with open(TABLE_DIR / "stage_feature_groups.json", "w", encoding="utf-8") as f:
        json.dump(original_stages, f, indent=2)

    all_metrics = [baseline_day1(df)]

    final_stages = {}
    for stage_name, features in original_stages.items():
        kept, mi_table = remove_low_signal_features(df, features)
        mi_table.to_csv(TABLE_DIR / f"{stage_name.lower().replace(' ', '_')}_low_signal_review.csv", index=False)
        final_stages[stage_name] = kept
        print(f"{stage_name}: {len(kept)}/{len(features)} features kept at MI >= 0.002")

    with open(TABLE_DIR / "final_stage_feature_groups_after_low_signal_removal.json", "w", encoding="utf-8") as f:
        json.dump(final_stages, f, indent=2)

    artifacts = {}
    for stage_name in ["Stage 1", "Stage 2", "Stage 3"]:
        artifact, metrics_row, _ = train_calibrated_stage_model(df, stage_name, final_stages[stage_name])
        artifacts[stage_name] = artifact
        all_metrics.append(metrics_row)

        importance = global_feature_importance(artifact)
        importance.to_csv(TABLE_DIR / f"{stage_name.lower().replace(' ', '_')}_xgb_feature_importance.csv", index=False)

    demo_recommendations(df, artifacts)

    phenotype_summary = phenotype_clustering(df, final_stages["Stage 3"])
    print("\nPhenotype cluster summary:")
    print(phenotype_summary.to_string(index=False))

    final_metrics = pd.concat(all_metrics, ignore_index=True)
    make_final_charts(final_metrics)
    maybe_make_shap_plots(artifacts, df, args.make_shap)

    print("\nFinal metrics:")
    print(final_metrics.round(4).to_string(index=False))
    print(f"\nArtifacts saved under: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
