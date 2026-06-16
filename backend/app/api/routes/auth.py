"""
Authentication API endpoints: signup, login, me, logout.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models.db_models import User
from app.models.schemas import UserCreate, UserLogin, UserOut, Token
from app.utils.auth_utils import hash_password, verify_password, create_access_token
from app.api.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=dict)
async def signup(req: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    Returns user profile and JWT token.
    """
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    try:
        password_hash = hash_password(req.password)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )

    user = User(
        name=req.name,
        email=req.email,
        password_hash=password_hash,
        is_active=True,
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        user_id=str(user.id),
        email=user.email,
        role=user.role,
    )

    return {
        "status": "success",
        "data": {
            "user": UserOut.model_validate(user).model_dump(),
            "token": Token(access_token=token).model_dump(),
        },
        "message": "Account created successfully",
    }


@router.post("/login", response_model=dict)
async def login(req: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate an existing user.
    Returns user profile and JWT token.
    """
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    token = create_access_token(
        user_id=str(user.id),
        email=user.email,
        role=user.role,
    )

    return {
        "status": "success",
        "data": {
            "user": UserOut.model_validate(user).model_dump(),
            "token": Token(access_token=token).model_dump(),
        },
        "message": "Login successful",
    }


@router.get("/me", response_model=dict)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.
    """
    return {
        "status": "success",
        "data": {
            "user": UserOut.model_validate(current_user).model_dump(),
        },
    }


@router.post("/logout", response_model=dict)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout the current user.
    Stateless JWT — client should discard the token.
    """
    return {
        "status": "success",
        "data": None,
        "message": "Logged out successfully",
    }
