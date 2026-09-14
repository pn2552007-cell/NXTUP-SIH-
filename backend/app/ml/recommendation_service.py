"""
NEXTUP Personalized Intervention Recommendation Service
========================================================
Combines: Risk Score + Skill Gap + Job Requirements + Job Demand
→ Generates explainable, personalized interventions.

SIH26135 | Team Lumora
"""
from typing import List, Dict, Any, Optional


INTERVENTION_TEMPLATES = {
    "HIGH": {
        "Python/Data skills gap": {
            "title": "Priority Upskilling: Python & Data Analytics",
            "description": (
                "Trainee is at HIGH placement risk with critical skill gaps in Python and data analysis. "
                "Immediate enrollment in an intensive Python/SQL bootcamp is recommended."
            ),
            "recommended_actions": [
                "Enroll in: Python for Data Analysis (6-week intensive)",
                "Complete SQL fundamentals module on platform",
                "Practice on Kaggle or HackerRank datasets (min 2 hrs/day)",
                "Attend mock technical interviews",
                "Apply to at least 5 entry-level data roles this week",
            ],
        },
        "General high risk": {
            "title": "High-Risk Intervention: Career Acceleration Program",
            "description": (
                "Trainee shows multiple placement risk indicators. "
                "A structured, time-bound intervention is required."
            ),
            "recommended_actions": [
                "Schedule 1-on-1 career counseling session",
                "Update and improve resume/portfolio",
                "Join job readiness workshop",
                "Increase job applications to 5+ per week",
                "Attend local employer networking event",
            ],
        },
    },
    "MEDIUM": {
        "General medium risk": {
            "title": "Skill Enhancement & Job Readiness Program",
            "description": (
                "Trainee has moderate placement risk. "
                "Targeted skill enhancement and increased job search activity will improve outcomes."
            ),
            "recommended_actions": [
                "Complete 2 missing skill modules identified in skill gap analysis",
                "Build or update online portfolio/GitHub profile",
                "Submit at least 3 job applications per week",
                "Participate in industry webinar or hackathon",
                "Seek mentorship from placed alumni",
            ],
        },
    },
    "LOW": {
        "General low risk": {
            "title": "Career Growth: Advanced Role Preparation",
            "description": (
                "Trainee has good placement prospects. "
                "Focus on advanced skills and premium employer targeting to maximize career outcomes."
            ),
            "recommended_actions": [
                "Target mid-level and premium employer listings",
                "Pursue an advanced certification or specialization",
                "Prepare for technical interviews at target companies",
                "Connect with industry mentors and LinkedIn network",
                "Explore apprenticeship or contract-to-hire opportunities",
            ],
        },
    },
}


def generate_recommendation(
    risk_level: str,
    risk_score: float,
    missing_skills: List[str],
    job_title: Optional[str] = None,
    trainee_state: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a personalized intervention recommendation.

    Args:
        risk_level: 'LOW', 'MEDIUM', 'HIGH'
        risk_score: 0.0 to 100.0
        missing_skills: list of skill names from skill-gap analysis
        job_title: target job title (optional)
        trainee_state: trainee's state for regional job recommendations

    Returns:
        Intervention dict with title, description, target_skills, recommended_actions
    """
    level = risk_level.upper() if risk_level else "MEDIUM"
    templates = INTERVENTION_TEMPLATES.get(level, INTERVENTION_TEMPLATES["MEDIUM"])

    # Select template based on skill gaps
    template_key = "General high risk" if level == "HIGH" else (
        "General medium risk" if level == "MEDIUM" else "General low risk"
    )
    python_data_keywords = {"python", "sql", "pandas", "data", "excel", "analytics"}
    if missing_skills:
        skill_names_lower = {s.lower() for s in missing_skills}
        if skill_names_lower & python_data_keywords and level == "HIGH":
            template_key = "Python/Data skills gap"

    template = templates.get(template_key, list(templates.values())[0])

    # Personalize actions
    actions = list(template["recommended_actions"])
    if missing_skills:
        top_gaps = missing_skills[:3]
        gap_action = f"Priority skill modules to complete: {', '.join(top_gaps)}"
        actions.insert(0, gap_action)
    if job_title:
        actions.append(f"Apply to '{job_title}' roles matching your updated profile")
    if trainee_state:
        actions.append(f"Explore regional employers and skilling centers in {trainee_state}")

    return {
        "risk_level": level,
        "risk_score": round(risk_score, 1),
        "title": template["title"],
        "description": template["description"],
        "target_skills": missing_skills[:5] if missing_skills else [],
        "recommended_actions": actions[:7],
        "trigger_reason": f"Placement risk {level} ({risk_score:.0f}%) with {len(missing_skills)} skill gaps",
        "is_demo": True,
        "disclaimer": "Recommendation generated from synthetic risk model — requires validation on real outcome data.",
    }
