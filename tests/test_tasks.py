import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_project(auth_client: AsyncClient):
    response = await auth_client.post("/api/v1/projects", json={
        "title": "Test Project",
        "description": "Test description",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Project"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_task(auth_client: AsyncClient):
    # Сначала создаём проект
    project = await auth_client.post("/api/v1/projects", json={
        "title": "Test Project",
    })
    project_id = project.json()["id"]

    # Создаём задачу
    response = await auth_client.post("/api/v1/tasks", json={
        "title": "Test Task",
        "priority": "high",
        "project_id": project_id,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["status"] == "todo"
    assert data["priority"] == "high"


@pytest.mark.asyncio
async def test_update_task_status(auth_client: AsyncClient):
    project = await auth_client.post("/api/v1/projects", json={"title": "Project"})
    project_id = project.json()["id"]

    task = await auth_client.post("/api/v1/tasks", json={
        "title": "Task",
        "project_id": project_id,
    })
    task_id = task.json()["id"]

    response = await auth_client.patch(f"/api/v1/tasks/{task_id}", json={
        "status": "done",
    })
    assert response.status_code == 200
    assert response.json()["status"] == "done"


@pytest.mark.asyncio
async def test_filter_tasks_by_status(auth_client: AsyncClient):
    project = await auth_client.post("/api/v1/projects", json={"title": "Project"})
    project_id = project.json()["id"]

    # Создаём две задачи с разными статусами
    task1 = await auth_client.post("/api/v1/tasks", json={
        "title": "Task 1", "project_id": project_id,
    })
    await auth_client.post("/api/v1/tasks", json={
        "title": "Task 2", "project_id": project_id,
    })
    await auth_client.patch(f"/api/v1/tasks/{task1.json()['id']}", json={
        "status": "done",
    })

    # Фильтруем по статусу
    response = await auth_client.get("/api/v1/tasks?status=done")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "done"


@pytest.mark.asyncio
async def test_delete_task(auth_client: AsyncClient):
    project = await auth_client.post("/api/v1/projects", json={"title": "Project"})
    task = await auth_client.post("/api/v1/tasks", json={
        "title": "Task",
        "project_id": project.json()["id"],
    })
    task_id = task.json()["id"]

    response = await auth_client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 204

    response = await auth_client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 404
