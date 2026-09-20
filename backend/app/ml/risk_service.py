"""
NEXTUP Placement Risk Prediction Service
=========================================
Provides inference from the trained RandomForest/LogisticRegression model.
Includes explainability via feature contributions and top contributing factors.

DISCLAIMER: All predictions are based on a SYNTHETIC training dataset for
technical demonstration (SIH26135, Team Lumora). Not validated on real data.
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("nextup.risk_service")

DATA_DIR = Path(__file__).parent / "data"
MODEL_PATH = DATA_DIR / "placement_risk_model.joblib"
META_PATH = DATA_DIR / "model_metadata.json"

DISCLAIMER = (
    "Demo prediction — model requires validation on real verified outcome data. "
    "Trained on synthetic placement dataset."
)

# Human-readable feature explanations for UI display
FEATURE_LABELS = {
    "attendance_pct":           "Attendance Percentage",
    "assessment_avg_score":     "Assessment Score",
    "certification_status":     "Certification Status",
    "skill_gap_score":          "Skill Gap Score",
    "has_apprenticeship":       "Apprenticeship/Internship",
    "training_duration_weeks":  "Training Duration",
    "prior_experience_years":   "Prior Work Experience",
    "num_job_applications":     "Job Applications Submitted",
    "verified_skill_count":     "Verified Skill Count",
    "course_domain":            "Course Domain",
    "state":                    "State/Location",
}

RISK_THRESHOLDS = {"LOW": 40, "MEDIUM": 65, "HIGH": 100}


def _get_risk_level(risk_score: float) -> str:
    if risk_score < 40:
        return "LOW"
    elif risk_score < 65:
        return "MEDIUM"
    return "HIGH"


def _get_contributing_factors(features: Dict[str, Any]) -> List[str]:
    """Rule-based explainability for contributing risk factors (human-readable)."""
    factors = []
    if features.get("skill_gap_score", 0) > 50:
        factors.append("High skill gap score")
    if features.get("assessment_avg_score", 100) < 60:
        factors.append("Low assessment score")
    if features.get("attendance_pct", 100) < 70:
        factors.append("Low training attendance")
    if not features.get("has_apprenticeship", 0):
        factors.append("No apprenticeship/internship experience")
    if not features.get("certification_status", 0):
        factors.append("No certification obtained")
    if features.get("prior_experience_years", 1) == 0:
        factors.append("No prior work experience")
    if features.get("num_job_applications", 0) < 3:
        factors.append("Very few job applications submitted")
    if features.get("verified_skill_count", 1) < 4:
        factors.append("Low number of verified skills")
    return factors[:5]  # Return top 5


class PlacementRiskService:
    """
    Inference service for the NEXTUP Placement Risk Model.
    Lazy-loads the model on first use for fast startup.
    """

    def __init__(self):
        self._model = None
        self._metadata = None

    def _load(self):
        if self._model is not None:
            return
        try:
            import joblib
            if not MODEL_PATH.exists():
                raise FileNotFoundError(
                    f"Model file not found at {MODEL_PATH}. "
                    "Run: py app/ml/pipeline_train.py to train the model."
                )
            self._model = joblib.load(str(MODEL_PATH))
            if META_PATH.exists():
                with open(str(META_PATH), encoding="utf-8") as f:
                    self._metadata = json.load(f)
            logger.info("[NEXTUP ML] Placement risk model loaded from %s", MODEL_PATH)
        except ImportError:
            logger.error("joblib not installed. Run: pip install joblib scikit-learn")
            raise

    def is_available(self) -> bool:
        if self.get_model_info().get("status") == "PLANNED":
            return False
        try:
            self._load()
            return True
        except Exception:
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata and evaluation metrics."""
        if META_PATH.exists():
            with open(str(META_PATH), encoding="utf-8") as f:
                metadata = json.load(f)
                return {
                    "status": "READY", "available": True,
                    "model_name": metadata.get("model_name"),
                    "features": metadata.get("features", []),
                    "dataset": metadata.get("dataset"),
                    "metrics": metadata.get("metrics"),
                    "disclaimer": metadata.get("disclaimer", DISCLAIMER),
                }
        return {"error": "Model metadata not found. Run pipeline_train.py first."}

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict placement risk for a trainee.

        Args:
            features: Dict with keys matching the training feature set.

        Returns:
            Dict with risk_score (0-100), risk_level, contributing_factors, disclaimer.
        """
        if self.get_model_info().get("status") == "PLANNED":
            return {
                "available": False, "status": "PLANNED", "risk_score": None,
                "risk_level": "PLANNED", "prob_placed": None,
                "contributing_factors": [],
                "disclaimer": self.get_model_info()["disclaimer"],
            }
        try:
            self._load()
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "risk_score": None,
                "risk_level": "UNKNOWN",
                "contributing_factors": [],
                "disclaimer": DISCLAIMER,
            }

        try:
            import pandas as pd

            NUMERIC_FEATURES = [
                "attendance_pct", "assessment_avg_score", "certification_status",
                "skill_gap_score", "has_apprenticeship", "training_duration_weeks",
                "prior_experience_years", "num_job_applications", "verified_skill_count",
            ]
            CATEGORICAL_FEATURES = ["course_domain", "state"]

            row = {
                "attendance_pct": float(features.get("attendance_pct", 75.0)),
                "assessment_avg_score": float(features.get("assessment_avg_score", 60.0)),
                "certification_status": int(features.get("certification_status", 0)),
                "skill_gap_score": float(features.get("skill_gap_score", 50.0)),
                "has_apprenticeship": int(features.get("has_apprenticeship", 0)),
                "training_duration_weeks": int(features.get("training_duration_weeks", 12)),
                "prior_experience_years": int(features.get("prior_experience_years", 0)),
                "num_job_applications": int(features.get("num_job_applications", 0)),
                "verified_skill_count": int(features.get("verified_skill_count", 3)),
                "course_domain": str(features.get("course_domain", "Information Technology")),
                "state": str(features.get("state", "Maharashtra")),
            }

            df = pd.DataFrame([row])
            prob_placed = float(self._model.predict_proba(df[NUMERIC_FEATURES + CATEGORICAL_FEATURES])[0][1])
            # Risk score = probability of NOT being placed (0–100)
            risk_score = round((1.0 - prob_placed) * 100, 1)
            risk_level = _get_risk_level(risk_score)
            factors = _get_contributing_factors(row)

            return {
                "available": True,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "prob_placed": round(prob_placed * 100, 1),
                "contributing_factors": factors,
                "disclaimer": DISCLAIMER,
                "features_used": row,
            }

        except Exception as e:
            logger.exception("Placement risk prediction failed: %s", e)
            return {
                "available": False,
                "error": f"Prediction error: {str(e)}",
                "risk_score": None,
                "risk_level": "UNKNOWN",
                "contributing_factors": [],
                "disclaimer": DISCLAIMER,
            }


# Module-level singleton
risk_service = PlacementRiskService()
