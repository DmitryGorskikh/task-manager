from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.task import Task, TaskStatus, TaskPriority


class TaskRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, task_id: int) -> Task | None:
        result = await self.session.execute(
            select(Task)
            .options(selectinload(Task.assignee))
            .where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_all_filtered(
        self,
        owner_id: int,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        project_id: int | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Task]:
        query = (
            select(Task)
            .options(selectinload(Task.assignee))
            .join(Task.project)                      # JOIN с projects
            .where(Task.project.has(owner_id=owner_id))  # только свои проекты
        )

        if status is not None:
            query = query.where(Task.status == status)
        if priority is not None:
            query = query.where(Task.priority == priority)
        if project_id is not None:
            query = query.where(Task.project_id == project_id)

        query = query.offset(offset).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, data: dict) -> Task:
        task = Task(**data)
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def update(self, task: Task, data: dict) -> Task:
        for field, value in data.items():
            setattr(task, field, value)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        await self.session.delete(task)
        await self.session.commit()
