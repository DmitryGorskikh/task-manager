from pydantic import BaseModel
from datetime import datetime


class ProjectCreate(BaseModel):
    title: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str | None
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
