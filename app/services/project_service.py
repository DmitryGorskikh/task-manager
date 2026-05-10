from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.project_repo import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate


class ProjectService:
    def __init__(self, session: AsyncSession):
        self.repo = ProjectRepository(session)

    async def create(
        self, data: ProjectCreate, owner_id: int
    ) -> ProjectResponse:
        project = await self.repo.create(
            title=data.title,
            description=data.description,
            owner_id=owner_id,
        )
        return ProjectResponse.model_validate(project)

    async def get_all(self, owner_id: int) -> list[ProjectResponse]:
        projects = await self.repo.get_all_by_owner(owner_id)
        return [ProjectResponse.model_validate(p) for p in projects]

    async def get_by_id(
        self, project_id: int, owner_id: int
    ) -> ProjectResponse:
        project = await self._get_own_project(project_id, owner_id)
        return ProjectResponse.model_validate(project)

    async def update(
        self, project_id: int, data: ProjectUpdate, owner_id: int
    ) -> ProjectResponse:
        project = await self._get_own_project(project_id, owner_id)

        # Обновляем только переданные поля
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        project = await self.repo.update(project, update_data)
        return ProjectResponse.model_validate(project)

    async def delete(self, project_id: int, owner_id: int) -> None:
        project = await self._get_own_project(project_id, owner_id)
        await self.repo.delete(project)

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
