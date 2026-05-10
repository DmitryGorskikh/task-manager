from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.project_repo import ProjectRepository
from app.repositories.task_repo import TaskRepository
from app.schemas.task import TaskCreate, TaskFilter, TaskResponse, TaskUpdate


class TaskService:
    def __init__(self, session: AsyncSession):
        self.repo = TaskRepository(session)
        self.project_repo = ProjectRepository(session)

    async def create(self, data: TaskCreate, owner_id: int) -> TaskResponse:
        # Проверяем что проект существует и принадлежит юзеру
        project = await self.project_repo.get_by_id(data.project_id)
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

        task = await self.repo.create(data.model_dump())
        return TaskResponse.model_validate(task)

    async def get_all(
        self,
        owner_id: int,
        filters: TaskFilter,
        offset: int = 0,
        limit: int = 20,
    ) -> list[TaskResponse]:
        tasks = await self.repo.get_all_filtered(
            owner_id=owner_id,
            status=filters.status,
            priority=filters.priority,
            project_id=filters.project_id,
            offset=offset,
            limit=limit,
        )
        return [TaskResponse.model_validate(t) for t in tasks]

    async def get_by_id(self, task_id: int, owner_id: int) -> TaskResponse:
        task = await self._get_own_task(task_id, owner_id)
        return TaskResponse.model_validate(task)

    async def update(
        self, task_id: int, data: TaskUpdate, owner_id: int
    ) -> TaskResponse:
        task = await self._get_own_task(task_id, owner_id)

        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        task = await self.repo.update(task, update_data)
        return TaskResponse.model_validate(task)

    async def delete(self, task_id: int, owner_id: int) -> None:
        task = await self._get_own_task(task_id, owner_id)
        await self.repo.delete(task)

    async def _get_own_task(self, task_id: int, owner_id: int):
        task = await self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        # Проверяем владельца через проект
        project = await self.project_repo.get_by_id(task.project_id)
        if not project or project.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        return task
