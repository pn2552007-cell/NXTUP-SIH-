from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User, Trainee, Provider, Employer
from app.schemas.schemas import UserRegister, UserLogin, Token, UserResponse
from app.auth.jwt_handler import (
    verify_password, get_password_hash, create_access_token, get_current_user
)
from app.utils.id_generator import generate_nextup_id
from app.utils.audit import log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Standardize role
    role = user_in.role.upper()
    if role == "PROVIDER":
        role = "TRAINING_PROVIDER"
    if role not in ("TRAINEE", "TRAINING_PROVIDER", "EMPLOYER"):
        raise HTTPException(403, "This role cannot be created through public registration.")

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=role,
        full_name=user_in.full_name,
        phone=user_in.phone,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    nextup_id = None
    consent_given = False

    # Create associated role profile
    if user.role == "TRAINEE":
        nextup_id = generate_nextup_id(db)
        trainee = Trainee(
            user_id=user.id,
            nextup_id=nextup_id,
            skillpulse_id=nextup_id,  # keep backward compat field identical
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            state=user_in.state,
            district=user_in.district,
            consent_given=False
        )
        db.add(trainee)
        db.commit()
    elif user.role in ("TRAINING_PROVIDER", "PROVIDER"):
        # Normalize every provider variant to TRAINING_PROVIDER so provider
        # APIs and frontend role checks stay consistent.
        user.role = "TRAINING_PROVIDER"
        db.flush()
        provider = Provider(
            user_id=user.id,
            organization_name=user_in.organization_name or user_in.full_name,
            code=f"PRV-{user.id:04d}",
            contact_person=user_in.full_name,
            email=user_in.email,
            phone=user_in.phone,
            state=user_in.state,
            district=user_in.district
        )
        db.add(provider)
        db.commit()
    elif user.role == "EMPLOYER":
        employer = Employer(
            user_id=user.id,
            company_name=user_in.organization_name or f"{user_in.full_name} Org",
            contact_person=user_in.full_name,
            email=user_in.email,
            phone=user_in.phone,
            state=user_in.state,
            district=user_in.district,
            is_verified=False
        )
        db.add(employer)
        db.commit()

    log_audit_event(
        db=db,
        action="USER_REGISTERED",
        entity_type="USER",
        entity_id=str(user.id),
        user_id=user.id,
        details={"role": user.role, "email": user.email}
    )

    token_data = {"sub": str(user.id), "role": user.role, "email": user.email}
    access_token = create_access_token(data=token_data)

    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        nextup_id=nextup_id,
        skillpulse_id=nextup_id,
        consent_given=consent_given
    )

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not user.is_active or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    nextup_id = None
    consent_given = False
    if user.trainee_profile:
        nextup_id = user.trainee_profile.nextup_id or user.trainee_profile.skillpulse_id
        consent_given = user.trainee_profile.consent_given

    log_audit_event(
        db=db,
        action="LOGIN",
        entity_type="USER",
        entity_id=str(user.id),
        user_id=user.id,
        details={"email": user.email}
    )

    token_data = {"sub": str(user.id), "role": user.role, "email": user.email}
    access_token = create_access_token(data=token_data)

    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        nextup_id=nextup_id,
        skillpulse_id=nextup_id,
        consent_given=consent_given
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    nextup_id = None
    consent_given = False
    if current_user.trainee_profile:
        nextup_id = current_user.trainee_profile.nextup_id or current_user.trainee_profile.skillpulse_id
        consent_given = current_user.trainee_profile.consent_given

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        phone=current_user.phone,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        nextup_id=nextup_id,
        skillpulse_id=nextup_id,
        consent_given=consent_given
    )
