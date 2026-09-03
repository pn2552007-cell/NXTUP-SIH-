from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.models import Skill

CANONICAL_SKILL_MAP = {
    "python": "Python",
    "sql": "SQL",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "aws": "AWS",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "html": "HTML",
    "css": "CSS",
    "html/css": "HTML/CSS",
    "git": "Git",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "fastapi": "FastAPI",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "communication": "Communication",
    "data analysis": "Data Analysis",
    "machine learning": "Machine Learning",
    "power bi": "Power BI",
    "tableau": "Tableau",
    "excel": "Excel",
    "pandas": "Pandas",
    "linux": "Linux",
    "bash": "Bash",
    "terraform": "Terraform",
    "ci/cd": "CI/CD",
}

def normalize_skill_name(raw_name: str) -> str:
    cleaned = raw_name.strip()
    if not cleaned:
        return ""
    lower = cleaned.lower()
    if lower in CANONICAL_SKILL_MAP:
        return CANONICAL_SKILL_MAP[lower]
    # Default title casing for general skills
    return cleaned.title()

def get_or_create_skill(db: Session, raw_name: str, category: Optional[str] = "Technical") -> Optional[Skill]:
    normalized = normalize_skill_name(raw_name)
    if not normalized:
        return None
    skill = db.query(Skill).filter(Skill.name.ilike(normalized)).first()
    if not skill:
        skill = Skill(name=normalized, category=category)
        db.add(skill)
        db.commit()
        db.refresh(skill)
    return skill

def normalize_skill_list(skills: List[str]) -> List[str]:
    seen = set()
    result = []
    for s in skills:
        norm = normalize_skill_name(s)
        if norm and norm.lower() not in seen:
            seen.add(norm.lower())
            result.append(norm)
    return result
