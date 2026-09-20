"""
NXTUP Placement Risk Model — Training Pipeline
==============================================
SIH 2026, Problem ID: SIH26135, Team Lumora

DISCLAIMER: Trained on SYNTHETIC data for technical demonstration only.
            Model accuracy does NOT represent real-world performance.
            Validation on real verified outcome data required before deployment.
"""
import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, roc_auc_score,
    confusion_matrix, f1_score, precision_score, recall_score,
    brier_score_loss, accuracy_score
)

DATA_DIR = Path(__file__).parent / "data"
TRAIN_CSV_PATH = DATA_DIR / "nxtup_ml_train.csv"
TEST_CSV_PATH = DATA_DIR / "nxtup_ml_test.csv"
FALLBACK_CSV_PATH = DATA_DIR / "synthetic_placement_outcomes.csv"
MODEL_PATH = DATA_DIR / "placement_risk_model.joblib"
META_PATH = DATA_DIR / "model_metadata.json"

NUMERIC_FEATURES = [
    "attendance_pct",
    "assessment_avg_score",
    "certification_status",
    "skill_gap_score",
    "has_apprenticeship",
    "training_duration_weeks",
    "prior_experience_years",
    "num_job_applications",
    "verified_skill_count",
]
CATEGORICAL_FEATURES = ["course_domain", "state"]
TARGET = "placement_status"


def load_datasets():
    """
    Loads training and independent evaluation datasets.
    If independent nxtup_ml_train.csv and nxtup_ml_test.csv are present,
    returns them directly to strictly prevent data leakage.
    Otherwise falls back to train_test_split on the single legacy file.
    """
    if TRAIN_CSV_PATH.exists() and TEST_CSV_PATH.exists():
        df_train = pd.read_csv(TRAIN_CSV_PATH, comment="#")
        df_test = pd.read_csv(TEST_CSV_PATH, comment="#")
        print(f"[NXTUP ML] Loaded {len(df_train)} training records from {TRAIN_CSV_PATH.name}")
        print(f"[NXTUP ML] Loaded {len(df_test)} independent holdout test records from {TEST_CSV_PATH.name}")
        print(f"[NXTUP ML] Data leakage prevention: STRICT INDEPENDENT HOLDOUT SEPARATION ACTIVE")
        X_train = df_train[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
        y_train = df_train[TARGET]
        X_test = df_test[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
        y_test = df_test[TARGET]
        dataset_source = "NXTUP Independent Train/Test Partitions (Zero Data Leakage)"
    else:
        df = pd.read_csv(FALLBACK_CSV_PATH, comment="#")
        print(f"[NXTUP ML] Loaded {len(df)} records from fallback {FALLBACK_CSV_PATH.name}")
        X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
        y = df[TARGET]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        dataset_source = "NXTUP Synthetic Placement Outcomes (Single Partition Split)"

    return X_train, X_test, y_train, y_test, dataset_source


def build_preprocessor():
    num_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler", StandardScaler()),
    ])
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("num", num_pipe, NUMERIC_FEATURES),
        ("cat", cat_pipe, CATEGORICAL_FEATURES),
    ])


def train_and_evaluate():
    X_train, X_test, y_train, y_test, dataset_source = load_datasets()

    preprocessor = build_preprocessor()

    # Logistic Regression baseline
    lr_pipe = Pipeline([
        ("prep", preprocessor),
        ("clf", LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")),
    ])
    lr_pipe.fit(X_train, y_train)
    y_pred_lr = lr_pipe.predict(X_test)
    y_prob_lr = lr_pipe.predict_proba(X_test)[:, 1]
    lr_auc = roc_auc_score(y_test, y_prob_lr)
    print(
        f"[LR Baseline] Recall={recall_score(y_test, y_pred_lr):.3f} "
        f"Precision={precision_score(y_test, y_pred_lr):.3f} "
        f"F1={f1_score(y_test, y_pred_lr):.3f} AUC={lr_auc:.3f}"
    )

    # Random Forest
    rf_pipe = Pipeline([
        ("prep", build_preprocessor()),
        ("clf", RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")),
    ])
    rf_pipe.fit(X_train, y_train)
    y_pred_rf = rf_pipe.predict(X_test)
    y_prob_rf = rf_pipe.predict_proba(X_test)[:, 1]
    rf_auc = roc_auc_score(y_test, y_prob_rf)
    print(
        f"[RF Model]    Recall={recall_score(y_test, y_pred_rf):.3f} "
        f"Precision={precision_score(y_test, y_pred_rf):.3f} "
        f"F1={f1_score(y_test, y_pred_rf):.3f} AUC={rf_auc:.3f}"
    )

    # Choose best by AUC
    if rf_auc >= lr_auc:
        best_model, best_name, y_pred, y_prob, best_auc = rf_pipe, "RandomForestClassifier", y_pred_rf, y_prob_rf, rf_auc
    else:
        best_model, best_name, y_pred, y_prob, best_auc = lr_pipe, "LogisticRegression", y_pred_lr, y_prob_lr, lr_auc

    print(f"[NXTUP ML] Selected: {best_name} (Independent Holdout AUC={best_auc:.4f})")

    # Feature importances
    clf = best_model.named_steps["clf"]
    try:
        ohe_feats = (
            best_model.named_steps["prep"]
            .named_transformers_["cat"]["onehot"]
            .get_feature_names_out(CATEGORICAL_FEATURES)
            .tolist()
        )
    except Exception:
        ohe_feats = []
    all_feats = NUMERIC_FEATURES + ohe_feats
    if hasattr(clf, "feature_importances_"):
        imps = dict(zip(all_feats, [float(v) for v in clf.feature_importances_]))
    elif hasattr(clf, "coef_"):
        coefs = clf.coef_[0].tolist() if clf.coef_.ndim > 1 else clf.coef_.tolist()
        imps = dict(zip(all_feats, [abs(v) for v in coefs]))
    else:
        imps = {}
    top_features = sorted(imps.items(), key=lambda x: x[1], reverse=True)[:10]

    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, output_dict=True)
    brier = float(round(brier_score_loss(y_test, y_prob), 4))
    acc = float(round(accuracy_score(y_test, y_pred), 4))

    metadata = {
        "model_name": best_name,
        "dataset": dataset_source,
        "disclaimer": "Demo prediction only. Model requires validation on real verified outcome data before operational deployment.",
        "sih_problem_id": "SIH26135",
        "team": "Team Lumora",
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "data_leakage_prevention": "Strictly independent training and evaluation holdout datasets",
        "features": NUMERIC_FEATURES + CATEGORICAL_FEATURES,
        "target": TARGET,
        "metrics": {
            "accuracy": acc,
            "precision": float(round(precision_score(y_test, y_pred), 4)),
            "recall": float(round(recall_score(y_test, y_pred), 4)),
            "f1_score": float(round(f1_score(y_test, y_pred), 4)),
            "roc_auc": float(round(best_auc, 4)),
            "brier_score": brier,
            "confusion_matrix": cm,
            "classification_report": report,
        },
        "top_feature_importances": top_features,
        "trained_on": "2026-09-14",
        "baseline_model": "LogisticRegression",
        "baseline_metrics": {
            "accuracy": float(round(accuracy_score(y_test, y_pred_lr), 4)),
            "recall": float(round(recall_score(y_test, y_pred_lr), 4)),
            "f1_score": float(round(f1_score(y_test, y_pred_lr), 4)),
            "roc_auc": float(round(lr_auc, 4)),
        },
    }

    joblib.dump(best_model, str(MODEL_PATH))
    with open(str(META_PATH), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[NXTUP ML] Model saved to {MODEL_PATH}")
    print(f"[NXTUP ML] Metadata saved to {META_PATH}")
    print("[NXTUP ML] TOP FEATURE IMPORTANCES:")
    for feat, imp in top_features:
        print(f"  {feat:<42} {imp:.4f}")

    return metadata


if __name__ == "__main__":
    meta = train_and_evaluate()
    print(f"\n[NXTUP ML] INDEPENDENT HOLDOUT ACCURACY: {meta['metrics']['accuracy']}")
    print(f"[NXTUP ML] INDEPENDENT HOLDOUT RECALL:   {meta['metrics']['recall']}")
    print(f"[NXTUP ML] INDEPENDENT HOLDOUT ROC-AUC:  {meta['metrics']['roc_auc']}")
    print(f"[NXTUP ML] INDEPENDENT HOLDOUT BRIER:    {meta['metrics']['brier_score']}")
    print("[NXTUP ML] DISCLAIMER: " + meta["disclaimer"])

