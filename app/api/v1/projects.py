from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheService
from app.core.dependencies import get_cache, get_current_user, get_db
from app.db.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


def get_project_service(
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
) -> ProjectService:
    return ProjectService(session, cache)


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    return await service.create(data=data, owner_id=current_user.id)


@router.get("", response_model=list[ProjectResponse])
async def get_projects(
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_all(owner_id=current_user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_by_id(project_id=project_id, owner_id=current_user.id)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    return await service.update(
        project_id=project_id, data=data, owner_id=current_user.id
    )


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    await service.delete(project_id=project_id, owner_id=current_user.id)
