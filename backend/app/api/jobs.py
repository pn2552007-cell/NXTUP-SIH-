"""
NEXTUP Jobs API — Target Industry Job Roles
============================================
SIH26135 | Team Lumora
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Job, JobRequirement
from app.auth.jwt_handler import get_current_user
from app.models.models import User

router = APIRouter(prefix="/jobs", tags=["Jobs & Career Targets"])


class JobResponse(BaseModel):
    id: int
    title: str
    domain: str
    description: Optional[str]
    salary_range_min: Optional[float]
    salary_range_max: Optional[float]
    demand_level: str
    required_skills: List[str]

    class Config:
        from_attributes = True


@router.get("", response_model=List[JobResponse])
def list_jobs(
    domain: Optional[str] = None,
    demand: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Job).filter(Job.is_active == True)
    if domain:
        q = q.filter(Job.domain.ilike(f"%{domain}%"))
    if demand:
        q = q.filter(Job.demand_level == demand.upper())
    jobs = q.order_by(Job.demand_level.desc(), Job.title).all()

    result = []
    for job in jobs:
        skills = [jr.skill_name for jr in db.query(JobRequirement).filter(JobRequirement.job_id == job.id).all()]
        result.append(JobResponse(
            id=job.id,
            title=job.title,
            domain=job.domain,
            description=job.description,
            salary_range_min=job.salary_range_min,
            salary_range_max=job.salary_range_max,
            demand_level=job.demand_level,
            required_skills=skills,
        ))
    return result
