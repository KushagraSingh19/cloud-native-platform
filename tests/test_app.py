import pytest
from app import app, tasks


@pytest.fixture
def client():
    """Configures Flask test client and resets task state before each test."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Reset in-memory storage before each test
        global tasks
        tasks.clear()
        import app as app_module
        app_module.next_id = 1
        yield client


def test_health_check(client):
    """Test GET /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"status": "healthy"}


def test_metrics_endpoint(client):
    """Test GET /metrics endpoint returns Prometheus exposition data."""
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.content_type
    
    metrics_data = response.data.decode("utf-8")
    assert "http_requests_total" in metrics_data
    assert "http_request_duration_seconds" in metrics_data
    assert "http_requests_in_progress" in metrics_data


def test_index_route(client):
    """Test GET / dashboard route."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Cloud Task Manager" in response.data


def test_get_empty_tasks(client):
    """Test GET /api/tasks when no tasks exist."""
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_task_success(client):
    """Test POST /api/tasks with valid data."""
    payload = {"title": "Study for Final Year Viva"}
    response = client.post("/api/tasks", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert data["id"] == 1
    assert data["title"] == "Study for Final Year Viva"
    assert data["completed"] is False
    assert "created_at" in data


def test_create_task_invalid_missing_title(client):
    """Test POST /api/tasks with missing title payload."""
    response = client.post("/api/tasks", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_create_task_invalid_empty_title(client):
    """Test POST /api/tasks with empty whitespace title."""
    response = client.post("/api/tasks", json={"title": "   "})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_get_task_by_id_success(client):
    """Test GET /api/tasks/<id> for existing task."""
    create_resp = client.post("/api/tasks", json={"title": "Complete Phase 1"})
    task_id = create_resp.get_json()["id"]

    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == task_id
    assert data["title"] == "Complete Phase 1"


def test_get_task_by_id_non_existent(client):
    """Test GET /api/tasks/<id> for non-existent ID."""
    response = client.get("/api/tasks/999")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_update_task_success(client):
    """Test PUT /api/tasks/<id> to update title and completion status."""
    create_resp = client.post("/api/tasks", json={"title": "Original Title"})
    task_id = create_resp.get_json()["id"]

    update_payload = {"title": "Updated Title", "completed": True}
    response = client.put(f"/api/tasks/{task_id}", json=update_payload)
    assert response.status_code == 200

    data = response.get_json()
    assert data["title"] == "Updated Title"
    assert data["completed"] is True


def test_update_task_non_existent(client):
    """Test PUT /api/tasks/<id> for non-existent ID."""
    response = client.put("/api/tasks/999", json={"completed": True})
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_update_task_invalid_empty_title(client):
    """Test PUT /api/tasks/<id> with empty title."""
    create_resp = client.post("/api/tasks", json={"title": "Original Title"})
    task_id = create_resp.get_json()["id"]

    response = client.put(f"/api/tasks/{task_id}", json={"title": ""})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_delete_task_success(client):
    """Test DELETE /api/tasks/<id> for existing task."""
    create_resp = client.post("/api/tasks", json={"title": "Task to delete"})
    task_id = create_resp.get_json()["id"]

    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.get_json()["message"]

    # Verify task is deleted
    get_resp = client.get(f"/api/tasks/{task_id}")
    assert get_resp.status_code == 404


def test_delete_task_non_existent(client):
    """Test DELETE /api/tasks/<id> for non-existent ID."""
    response = client.delete("/api/tasks/999")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_unhandled_route_404_handler(client):
    """Test global 404 handler for undefined routes."""
    response = client.get("/api/invalid_route_xyz")
    assert response.status_code == 404
    data = response.get_json()
    assert data == {"error": "Resource not found"}


def test_global_500_exception_handler(client):
    """Test global 500 error handler catches internal server exceptions cleanly."""
    response = client.get("/test-500-error")
    assert response.status_code == 500
    data = response.get_json()
    assert data == {"error": "Internal server error"}

