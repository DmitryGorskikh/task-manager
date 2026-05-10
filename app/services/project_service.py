from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheService
from app.repositories.project_repo import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from loguru import logger


class ProjectService:
    def __init__(self, session: AsyncSession, cache: CacheService):
        self.repo = ProjectRepository(session)
        self.cache = cache

    def _projects_key(self, owner_id: int) -> str:
        return f"projects:user:{owner_id}"

    def _project_key(self, project_id: int) -> str:
        return f"project:{project_id}"

    async def create(self, data: ProjectCreate, owner_id: int) -> ProjectResponse:
        project = await self.repo.create(
            title=data.title,
            description=data.description,
            owner_id=owner_id,
        )
        # Инвалидируем кэш списка проектов
        await self.cache.delete(self._projects_key(owner_id))
        logger.info(f"Project created: id={project.id} owner={owner_id}")
        return ProjectResponse.model_validate(project)

    async def get_all(self, owner_id: int) -> list[ProjectResponse]:
        cache_key = self._projects_key(owner_id)

        # Пробуем получить из кэша
        cached = await self.cache.get(cache_key)
        if cached is not None:
            return [ProjectResponse(**p) for p in cached]

        # Идём в БД
        projects = await self.repo.get_all_by_owner(owner_id)
        result = [ProjectResponse.model_validate(p) for p in projects]

        # Сохраняем в кэш на 5 минут
        await self.cache.set(
            cache_key,
            [p.model_dump(mode="json") for p in result],
            ttl=300,
        )
        return result

    async def get_by_id(self, project_id: int, owner_id: int) -> ProjectResponse:
        project = await self._get_own_project(project_id, owner_id)
        return ProjectResponse.model_validate(project)

    async def update(
        self, project_id: int, data: ProjectUpdate, owner_id: int
    ) -> ProjectResponse:
        project = await self._get_own_project(project_id, owner_id)

        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        project = await self.repo.update(project, update_data)

        # Инвалидируем кэш
        await self.cache.delete(self._projects_key(owner_id))
        await self.cache.delete(self._project_key(project_id))

        return ProjectResponse.model_validate(project)

    async def delete(self, project_id: int, owner_id: int) -> None:
        project = await self._get_own_project(project_id, owner_id)
        await self.repo.delete(project)

        # Инвалидируем кэш
        await self.cache.delete(self._projects_key(owner_id))
        await self.cache.delete(self._project_key(project_id))

    async def _get_own_project(self, project_id: int, owner_id: int):
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        if project.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        return project
