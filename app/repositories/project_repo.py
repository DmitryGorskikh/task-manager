from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.project import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, project_id: int) -> Project | None:
        return await self.session.get(Project, project_id)

    async def get_all_by_owner(self, owner_id: int) -> list[Project]:
        result = await self.session.execute(
            select(Project).where(Project.owner_id == owner_id)
        )
        return list(result.scalars().all())

    async def create(
        self, title: str, description: str | None, owner_id: int
    ) -> Project:
        project = Project(
            title=title, description=description, owner_id=owner_id
        )
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def update(self, project: Project, data: dict) -> Project:
        for field, value in data.items():
            setattr(project, field, value)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def delete(self, project: Project) -> None:
        await self.session.delete(project)
        await self.session.commit()
