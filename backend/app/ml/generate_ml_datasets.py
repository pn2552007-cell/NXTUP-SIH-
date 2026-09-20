"""
NXTUP Placement Risk Model — Dataset Generator
==============================================
Generates logically separated, statistically realistic training and independent
test datasets for the NXTUP Longitudinal Skilling Outcome Platform.

To strictly prevent data leakage:
- Training dataset (nxtup_ml_train.csv): Generated with Seed A (4242).
- Independent holdout test dataset (nxtup_ml_test.csv): Generated with Seed B (8888).
- The two datasets have independent distributions and zero row overlap.

SIH 2026 | Problem ID: SIH26135 | Team Lumora
"""

import csv
import math
from pathlib import Path
import numpy as np

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DOMAINS = [
    "Information Technology",
    "Cloud Infrastructure",
    "Data Science & AI",
    "Industrial Electronics",
    "Healthcare Technology",
]

DOMAIN_WEIGHTS = [0.32, 0.22, 0.20, 0.14, 0.12]

STATES = [
    "Maharashtra",
    "Karnataka",
    "Tamil Nadu",
    "Telangana",
    "Gujarat",
    "Uttar Pradesh",
    "Delhi",
    "Kerala",
    "West Bengal",
    "Rajasthan",
]

STATE_WEIGHTS = [0.22, 0.18, 0.14, 0.12, 0.08, 0.08, 0.06, 0.04, 0.04, 0.04]


def generate_cohort(n_samples: int, seed: int, cohort_name: str) -> list:
    """
    Generates realistic skilling telemetry records with realistic probabilistic
    placement outcomes governed by domain skill dynamics.
    """
    rng = np.random.default_rng(seed)
    records = []

    for _ in range(n_samples):
        domain = rng.choice(DOMAINS, p=DOMAIN_WEIGHTS)
        state = rng.choice(STATES, p=STATE_WEIGHTS)

        # Baseline trainee capability (latent factor representing aptitude & dedication)
        latent_ability = rng.beta(a=3.5, b=2.2)  # Skewed toward competent (mean ~0.61)

        # 1. Attendance percentage: correlated with dedication, with realistic variance
        attendance_pct = float(np.clip(latent_ability * 50 + rng.uniform(45, 52), 48.0, 99.5))
        attendance_pct = round(attendance_pct, 1)

        # 2. Assessment average score: strong correlation with latent ability + attendance
        base_score = latent_ability * 55 + (attendance_pct / 100.0) * 35 + rng.normal(0, 4.0)
        assessment_avg_score = float(np.clip(base_score, 32.0, 98.5))
        assessment_avg_score = round(assessment_avg_score, 1)

        # 3. Certification status: high scores & attendance strongly increase probability
        cert_prob = 1.0 / (1.0 + math.exp(-(0.08 * (assessment_avg_score - 62.0) + 0.04 * (attendance_pct - 75.0))))
        certification_status = int(rng.random() < cert_prob)

        # 4. Skill gap score: lower is better (0-100 scale). Inversely related to ability
        base_gap = 100.0 - (latent_ability * 65.0 + rng.uniform(10, 25))
        skill_gap_score = float(np.clip(base_gap + (0 if certification_status else 12), 8.0, 85.0))
        skill_gap_score = round(skill_gap_score, 1)

        # 5. Apprenticeship / Internship: 35% overall rate, higher for technical domains
        appr_prob = 0.42 if domain in ["Information Technology", "Cloud Infrastructure"] else 0.28
        has_apprenticeship = int(rng.random() < appr_prob)

        # 6. Training duration (weeks): courses range from 10 to 24 weeks
        if domain == "Information Technology":
            duration_weeks = int(rng.choice([14, 16, 18, 20]))
        elif domain == "Cloud Infrastructure":
            duration_weeks = int(rng.choice([12, 14, 16]))
        elif domain == "Data Science & AI":
            duration_weeks = int(rng.choice([14, 16, 20]))
        elif domain == "Industrial Electronics":
            duration_weeks = int(rng.choice([12, 16, 24]))
        else:
            duration_weeks = int(rng.choice([10, 12, 14]))

        # 7. Prior experience (years): mostly freshers with some early-career trainees
        prior_exp = int(rng.choice([0, 0, 0, 1, 1, 2, 3, 4], p=[0.45, 0.15, 0.10, 0.12, 0.08, 0.05, 0.03, 0.02]))

        # 8. Number of job applications submitted: 0 to 28
        app_mean = 12 if latent_ability > 0.5 else 7
        num_job_apps = int(np.clip(rng.poisson(app_mean), 0, 30))

        # 9. Verified skill count: between 1 and 14
        base_skills = int(latent_ability * 8 + (2 if certification_status else 0) + rng.integers(1, 4))
        verified_skill_count = int(np.clip(base_skills, 1, 14))

        # --- Ground Truth Placement Outcome Generation ---
        # Domain realistic logistic regression model with realistic noise
        logit = (
            -4.2
            + 0.035 * attendance_pct
            + 0.045 * assessment_avg_score
            + 0.85 * certification_status
            - 0.038 * skill_gap_score
            + 0.90 * has_apprenticeship
            + 0.22 * prior_exp
            + 0.045 * num_job_apps
            + 0.12 * verified_skill_count
            + (0.35 if domain in ["Information Technology", "Cloud Infrastructure"] else 0.0)
            + (0.25 if state in ["Karnataka", "Maharashtra", "Telangana"] else 0.0)
        )
        prob_placement = 1.0 / (1.0 + math.exp(-logit))
        placement_status = int(rng.random() < prob_placement)

        records.append({
            "attendance_pct": attendance_pct,
            "assessment_avg_score": assessment_avg_score,
            "certification_status": certification_status,
            "skill_gap_score": skill_gap_score,
            "has_apprenticeship": has_apprenticeship,
            "training_duration_weeks": duration_weeks,
            "prior_experience_years": prior_exp,
            "course_domain": domain,
            "state": state,
            "num_job_applications": num_job_apps,
            "verified_skill_count": verified_skill_count,
            "placement_status": placement_status,
        })

    return records


def write_dataset_csv(filepath: Path, records: list, description: str, seed: int):
    fieldnames = [
        "attendance_pct",
        "assessment_avg_score",
        "certification_status",
        "skill_gap_score",
        "has_apprenticeship",
        "training_duration_weeks",
        "prior_experience_years",
        "course_domain",
        "state",
        "num_job_applications",
        "verified_skill_count",
        "placement_status",
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        f.write("# =============================================================================\n")
        f.write(f"# NXTUP Platform - {description}\n")
        f.write("# =============================================================================\n")
        f.write("# PURPOSE: Independent dataset generation for NXTUP Placement Risk Modeling.\n")
        f.write(f"# RECORDS: {len(records)} | RANDOM SEED: {seed}\n")
        f.write("# SIH 2026 (Problem ID: SIH26135) | Team Lumora\n")
        f.write("# =============================================================================\n")
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)


def main():
    print("Generating NXTUP Machine Learning Datasets...")
    
    # 1. Training Cohort (Seed 4242, 1200 records)
    train_records = generate_cohort(n_samples=1200, seed=4242, cohort_name="NXTUP Training Cohort")
    train_file = DATA_DIR / "nxtup_ml_train.csv"
    write_dataset_csv(
        train_file,
        train_records,
        "Training Dataset (Zero Data Leakage)",
        seed=4242
    )
    placed_train = sum(r["placement_status"] for r in train_records)
    print(f"Saved: {train_file.name} ({len(train_records)} records, Placement Rate: {placed_train/len(train_records)*100:.1f}%)")

    # 2. Independent Holdout Test Cohort (Seed 8888, 400 records)
    test_records = generate_cohort(n_samples=400, seed=8888, cohort_name="NXTUP Independent Holdout Test Cohort")
    test_file = DATA_DIR / "nxtup_ml_test.csv"
    write_dataset_csv(
        test_file,
        test_records,
        "Independent Holdout Evaluation Dataset (Strictly Unseen by Training)",
        seed=8888
    )
    placed_test = sum(r["placement_status"] for r in test_records)
    print(f"Saved: {test_file.name} ({len(test_records)} records, Placement Rate: {placed_test/len(test_records)*100:.1f}%)")

    print("\nNXTUP ML datasets generated successfully with zero data leakage!")


if __name__ == "__main__":
    main()
