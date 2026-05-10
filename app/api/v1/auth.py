from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.user import (
    RefreshTokenRequest,
    TokenResponse,
    UserRegister,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: UserRegister,
    session: AsyncSession = Depends(get_db),
):
    service = AuthService(session)
    return await service.register(email=data.email, password=data.password)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserRegister,
    session: AsyncSession = Depends(get_db),
):
    service = AuthService(session)
    return await service.login(email=data.email, password=data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db),
):
    service = AuthService(session)
    return await service.refresh(refresh_token=data.refresh_token)
