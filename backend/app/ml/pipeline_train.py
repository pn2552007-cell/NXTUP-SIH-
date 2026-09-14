"""
NEXTUP Placement Risk Model — Training Pipeline
================================================
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
    confusion_matrix, f1_score, precision_score, recall_score
)

DATA_DIR = Path(__file__).parent / "data"
CSV_PATH = DATA_DIR / "synthetic_placement_outcomes.csv"
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


def load_data():
    df = pd.read_csv(CSV_PATH, comment="#")
    print(f"[NEXTUP ML] Loaded {len(df)} synthetic training records.")
    dist = df[TARGET].value_counts().to_dict()
    print(f"[NEXTUP ML] Target distribution: {dist}")
    return df


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
    df = load_data()
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    preprocessor = build_preprocessor()

    # Logistic Regression baseline
    lr_pipe = Pipeline([
        ("prep", preprocessor),
        ("clf", LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")),
    ])
    lr_pipe.fit(X_train, y_train)
    y_pred_lr = lr_pipe.predict(X_test)
    lr_auc = roc_auc_score(y_test, lr_pipe.predict_proba(X_test)[:, 1])
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
    rf_auc = roc_auc_score(y_test, rf_pipe.predict_proba(X_test)[:, 1])
    print(
        f"[RF Model]    Recall={recall_score(y_test, y_pred_rf):.3f} "
        f"Precision={precision_score(y_test, y_pred_rf):.3f} "
        f"F1={f1_score(y_test, y_pred_rf):.3f} AUC={rf_auc:.3f}"
    )

    # Choose best by AUC
    if rf_auc >= lr_auc:
        best_model, best_name, y_pred, best_auc = rf_pipe, "RandomForestClassifier", y_pred_rf, rf_auc
    else:
        best_model, best_name, y_pred, best_auc = lr_pipe, "LogisticRegression", y_pred_lr, lr_auc

    print(f"[NEXTUP ML] Selected: {best_name} (AUC={best_auc:.4f})")

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

    metadata = {
        "model_name": best_name,
        "dataset": "SYNTHETIC — Not real government data",
        "disclaimer": "Demo prediction only. Model requires validation on real verified outcome data before operational deployment.",
        "sih_problem_id": "SIH26135",
        "team": "Team Lumora",
        "n_samples": int(len(df)),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "features": NUMERIC_FEATURES + CATEGORICAL_FEATURES,
        "target": TARGET,
        "metrics": {
            "precision": float(round(precision_score(y_test, y_pred), 4)),
            "recall": float(round(recall_score(y_test, y_pred), 4)),
            "f1_score": float(round(f1_score(y_test, y_pred), 4)),
            "roc_auc": float(round(best_auc, 4)),
            "confusion_matrix": cm,
            "classification_report": report,
        },
        "top_feature_importances": top_features,
        "trained_on": "2026-09-12",
        "baseline_model": "LogisticRegression",
        "baseline_metrics": {
            "recall": float(round(recall_score(y_test, y_pred_lr), 4)),
            "f1_score": float(round(f1_score(y_test, y_pred_lr), 4)),
            "roc_auc": float(round(lr_auc, 4)),
        },
    }

    joblib.dump(best_model, str(MODEL_PATH))
    with open(str(META_PATH), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[NEXTUP ML] Model saved to {MODEL_PATH}")
    print(f"[NEXTUP ML] Metadata saved to {META_PATH}")
    print("[NEXTUP ML] TOP FEATURE IMPORTANCES:")
    for feat, imp in top_features:
        print(f"  {feat:<42} {imp:.4f}")

    return metadata


if __name__ == "__main__":
    meta = train_and_evaluate()
    print(f"\n[NEXTUP ML] RECALL (at-risk detection): {meta['metrics']['recall']}")
    print(f"[NEXTUP ML] ROC-AUC: {meta['metrics']['roc_auc']}")
    print("[NEXTUP ML] DISCLAIMER: " + meta["disclaimer"])
