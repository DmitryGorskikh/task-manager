from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.rate_limit import rate_limit
from app.schemas.user import (
    RefreshTokenRequest,
    TokenResponse,
    UserRegister,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


async def login_rate_limit(request: Request):
    await rate_limit(
        request=request,
        key_prefix="login",
        max_requests=5,       # максимум 5 попыток
        window_seconds=60,    # за 60 секунд
    )


async def register_rate_limit(request: Request):
    await rate_limit(
        request=request,
        key_prefix="register",
        max_requests=3,       # максимум 3 регистрации
        window_seconds=3600,  # за час
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    dependencies=[Depends(register_rate_limit)],
)
async def register(
    data: UserRegister,
    session: AsyncSession = Depends(get_db),
):
    service = AuthService(session)
    return await service.register(email=data.email, password=data.password)


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(login_rate_limit)],
)
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
