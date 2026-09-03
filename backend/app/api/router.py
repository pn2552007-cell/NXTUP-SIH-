from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.consent import router as consent_router
from app.api.trainee import router as trainee_router
from app.api.employment import router as employment_router
from app.api.followups import router as followups_router
from app.api.employer import router as employer_router
from app.api.provider import router as provider_router
from app.api.admin import router as admin_router
from app.api.ai import router as ai_router
from app.api.analytics import router as analytics_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(consent_router)
api_router.include_router(trainee_router)
api_router.include_router(employment_router)
api_router.include_router(followups_router)
api_router.include_router(employer_router)
api_router.include_router(provider_router)
api_router.include_router(admin_router)
api_router.include_router(ai_router)
api_router.include_router(analytics_router)
