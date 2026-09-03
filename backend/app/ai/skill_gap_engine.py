import math
from typing import List, Dict, Any, Optional

JOB_PROFILES: Dict[str, Dict[str, Any]] = {
    "Full Stack Developer": {
        "core_skills": {
            "JavaScript": 0.9, "React": 0.85, "Node.js": 0.8, "Python": 0.75,
            "REST APIs": 0.8, "SQL": 0.75, "HTML/CSS": 0.85, "Git": 0.8
        },
        "advanced_skills": {
            "Docker": 0.7, "AWS": 0.65, "TypeScript": 0.75, "Tailwind CSS": 0.7,
            "PostgreSQL": 0.7, "CI/CD": 0.65
        },
        "recommended_courses": [
            "Containerization & Microservices with Docker",
            "AWS Cloud Practitioner for Developers",
            "Advanced TypeScript & Full Stack Testing"
        ]
    },
    "Data Analyst": {
        "core_skills": {
            "Python": 0.85, "SQL": 0.9, "Excel": 0.85, "Data Visualization": 0.8,
            "Pandas": 0.85, "Statistics": 0.75
        },
        "advanced_skills": {
            "Power BI": 0.8, "Tableau": 0.75, "Machine Learning": 0.65,
            "NumPy": 0.8, "BigQuery": 0.7
        },
        "recommended_courses": [
            "Advanced SQL for Business Intelligence",
            "Interactive Dashboarding with Power BI",
            "Practical Machine Learning with Scikit-Learn"
        ]
    },
    "Cloud & DevOps Engineer": {
        "core_skills": {
            "Linux": 0.9, "Git": 0.85, "Docker": 0.85, "AWS": 0.85,
            "Networking": 0.75, "Python": 0.7, "Bash": 0.8
        },
        "advanced_skills": {
            "Kubernetes": 0.8, "Terraform": 0.75, "CI/CD Pipelines": 0.8,
            "Monitoring & Prometheus": 0.7, "Ansible": 0.65
        },
        "recommended_courses": [
            "Kubernetes Cluster Orchestration in Production",
            "Infrastructure as Code with Terraform",
            "Site Reliability Engineering & Observability"
        ]
    },
    "Industrial IoT & Automation Specialist": {
        "core_skills": {
            "C/C++": 0.8, "Embedded Systems": 0.85, "Microcontrollers": 0.8,
            "Sensors & Actuators": 0.8, "Python": 0.7, "MQTT": 0.75
        },
        "advanced_skills": {
            "PLC Programming": 0.75, "SCADA Systems": 0.7, "IoT Security": 0.7,
            "Edge Computing": 0.65
        },
        "recommended_courses": [
            "Industrial PLC & SCADA Automation Masterclass",
            "Edge AI on Embedded IoT Devices",
            "Industrial IoT Security & Protocol Standards"
        ]
    },
    "Healthcare Data Operations": {
        "core_skills": {
            "Medical Terminology": 0.85, "EHR Systems": 0.85, "Data Entry & Validation": 0.9,
            "Healthcare Compliance & HIPAA": 0.85, "Excel": 0.8
        },
        "advanced_skills": {
            "HL7 / FHIR Standards": 0.75, "Medical Coding (ICD-10)": 0.75,
            "SQL for Healthcare": 0.7, "Clinical Analytics": 0.65
        },
        "recommended_courses": [
            "FHIR & HL7 Interoperability Standards",
            "ICD-10 & Medical Billing Operations",
            "Healthcare Privacy & Clinical Governance"
        ]
    }
}

class SkillGapEngine:
    """
    Modular Rule-Based & Semantic Skill Gap Detection Engine.
    Evaluates trainee acquired skills, assessment scores, and course domain against
    industry benchmark job requirements.
    """

    @classmethod
    def get_supported_roles(cls) -> List[str]:
        return list(JOB_PROFILES.keys())

    @classmethod
    def analyze(
        cls,
        trainee_skills: Optional[List[str]] = None,
        course_skills: Optional[List[str]] = None,
        assessment_scores: Optional[Dict[str, float]] = None,
        target_role: str = "Full Stack Developer"
    ) -> Dict[str, Any]:
        trainee_skills = [s.strip() for s in (trainee_skills or [])]
        course_skills = [s.strip() for s in (course_skills or [])]
        assessment_scores = assessment_scores or {}

        # Default to Full Stack Developer if target_role not found
        profile = JOB_PROFILES.get(target_role, JOB_PROFILES["Full Stack Developer"])
        core_reqs = profile["core_skills"]
        adv_reqs = profile["advanced_skills"]
        all_reqs = {**core_reqs, **adv_reqs}

        # Combine all skills acquired by trainee (direct skills + course taught skills)
        trainee_skill_set = {s.lower(): s for s in trainee_skills}
        course_skill_set = {s.lower(): s for s in course_skills}
        combined_skills = {**course_skill_set, **trainee_skill_set}

        matched_skills = []
        missing_skills = []
        total_weighted_points = 0.0
        earned_weighted_points = 0.0

        for req_skill, weight in all_reqs.items():
            total_weighted_points += weight
            req_lower = req_skill.lower()

            # Check if trainee has this skill (exact or substring match)
            has_skill = False
            best_match_name = req_skill
            for t_skill_lower, orig_name in combined_skills.items():
                if req_lower == t_skill_lower or req_lower in t_skill_lower or t_skill_lower in req_lower:
                    has_skill = True
                    best_match_name = orig_name
                    break

            if has_skill:
                # Score based on assessments if present, else base proficiency (70-95%)
                base_score = 80.0
                if assessment_scores:
                    avg_assessment = sum(assessment_scores.values()) / max(len(assessment_scores), 1)
                    base_score = min(98.0, max(60.0, avg_assessment * 0.95))
                else:
                    # Slight variation based on core vs advanced
                    base_score = 88.0 if req_skill in core_reqs else 72.0

                match_pct = int(base_score)
                proficiency = "ADVANCED" if match_pct >= 85 else ("INTERMEDIATE" if match_pct >= 70 else "BEGINNER")
                
                matched_skills.append({
                    "skill": req_skill,
                    "match_pct": match_pct,
                    "proficiency": proficiency
                })
                earned_weighted_points += (weight * (match_pct / 100.0))
            else:
                missing_skills.append(req_skill)

        # Calculate Skill Gap Score (0% = perfect match, 100% = total gap)
        if total_weighted_points > 0:
            match_ratio = earned_weighted_points / total_weighted_points
            gap_percentage = round((1.0 - match_ratio) * 100.0, 1)
        else:
            gap_percentage = 40.0

        # Confidence score based on number of assessed skills & data points
        data_points_count = len(trainee_skills) + len(course_skills) + len(assessment_scores)
        confidence = min(0.96, round(0.70 + (data_points_count * 0.02), 2))

        # Recommendations
        recommendations = []
        if missing_skills:
            top_missing = missing_skills[:3]
            recommendations.append(f"Focus on mastering high-priority target competencies: {', '.join(top_missing)}.")
        recommendations.extend(profile.get("recommended_courses", [])[:2])

        return {
            "target_role": target_role,
            "skill_gap_score": max(0.0, min(100.0, gap_percentage)),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "confidence_score": confidence,
            "recommendations": recommendations
        }
