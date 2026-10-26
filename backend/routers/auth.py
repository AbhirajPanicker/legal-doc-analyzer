"""
Auth router — register, login, and /me endpoints.
POST /api/v1/auth/register  — create a new account
POST /api/v1/auth/login     — exchange credentials for a JWT
GET  /api/v1/auth/me        — return the current user's profile
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_current_user
from models.schemas import (
    UserCreate,
    UserLogin,
    UserOut,
    TokenResponse,
)
from services import user_registry as registry
from services.auth_service import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: UserCreate):
    """Create a new user account and return an access token immediately."""
    if len(body.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 6 characters.",
        )
    try:
        user = registry.create_user(
            email=body.email,
            password=body.password,
            full_name=body.full_name or "",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    token = create_access_token(user["id"], user["email"])
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut(**user),
    )


@router.post("/login", response_model=TokenResponse)
def login(body: UserLogin):
    """Authenticate and return a JWT access token."""
    user = registry.authenticate_user(body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    token = create_access_token(user["id"], user["email"])
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut(**user),
    )


@router.get("/me", response_model=UserOut)
def me(current_user: dict = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return UserOut(**current_user)
