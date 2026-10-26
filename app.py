import hmac
import logging
import os
import sys
import time
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template, request, g, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# -----------------------------------------------------------------------------
# Security: Metrics Endpoint Bearer-Token Authentication
# -----------------------------------------------------------------------------
# When METRICS_TOKEN is set, or when running in cloud/production mode
# (REQUIRE_METRICS_AUTH=true or RENDER=true), GET /metrics requires:
#   Authorization: Bearer <METRICS_TOKEN>
# When neither is set (local Docker Compose / default pytest), /metrics is open.
# /health is always unauthenticated so Render health checks always pass.
def is_metrics_authorized() -> bool:
    """Verify whether the current request is authorized to access /metrics."""
    token = os.environ.get("METRICS_TOKEN", "").strip()
    require_auth = (
        os.environ.get("REQUIRE_METRICS_AUTH", "").strip().lower() == "true"
        or os.environ.get("RENDER", "").strip().lower() == "true"
    )

    if not token:
        # Fail closed in cloud/production if METRICS_TOKEN was not configured
        return not require_auth

    auth_header = request.headers.get("Authorization", "")
    expected_header = f"Bearer {token}"
    return hmac.compare_digest(auth_header, expected_header)

# -----------------------------------------------------------------------------
# Centralized Logging Configuration
# -----------------------------------------------------------------------------
logger = logging.getLogger("task_manager")
logger.setLevel(logging.INFO)

# Create stream handler for stdout
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
stream_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(stream_handler)

# Synchronize Flask app logger with Gunicorn or standalone logger
gunicorn_logger = logging.getLogger("gunicorn.error")
if gunicorn_logger.handlers:
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
else:
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)

# In-memory storage for tasks
tasks = []
next_id = 1

# -----------------------------------------------------------------------------
# Prometheus Metrics Instrumentation
# -----------------------------------------------------------------------------
HTTP_REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status_code"]
)

HTTP_REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Duration in Seconds",
    ["method", "endpoint"]
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["method", "endpoint"]
)


def get_endpoint_name():
    """Returns a clean low-cardinality endpoint identifier."""
    return request.endpoint if request.endpoint else "unknown"


@app.before_request
def before_request_hook():
    """Record request start time and increment active request gauge."""
    g.start_time = time.time()
    endpoint = get_endpoint_name()
    HTTP_REQUESTS_IN_PROGRESS.labels(method=request.method, endpoint=endpoint).inc()


@app.after_request
def after_request_hook(response):
    """Record latency, request counts, decrement active request gauge, and log request."""
    endpoint = get_endpoint_name()
    latency_ms = 0.0

    if hasattr(g, "start_time"):
        duration = time.time() - g.start_time
        latency_ms = round(duration * 1000, 2)
        HTTP_REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(duration)

    HTTP_REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status_code=str(response.status_code)
    ).inc()

    HTTP_REQUESTS_IN_PROGRESS.labels(method=request.method, endpoint=endpoint).dec()

    # Formatted Request Log Message
    log_msg = f"{request.method} {request.path} -> HTTP {response.status_code} ({latency_ms}ms)"

    if response.status_code >= 500:
        app.logger.error(log_msg)
    elif response.status_code >= 400:
        app.logger.warning(log_msg)
    else:
        app.logger.info(log_msg)

    return response


# -----------------------------------------------------------------------------
# Global Exception Handlers
# -----------------------------------------------------------------------------
@app.errorhandler(404)
def handle_not_found(e):
    """Handles 404 Not Found errors with structured JSON response."""
    app.logger.warning(f"404 Not Found: {request.method} {request.path}")
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(400)
def handle_bad_request(e):
    """Handles 400 Bad Request errors with structured JSON response."""
    app.logger.warning(f"400 Bad Request: {request.method} {request.path}")
    return jsonify({"error": "Bad request"}), 400


@app.errorhandler(Exception)
def handle_unexpected_exception(e):
    """Global exception handler for unexpected server errors (500)."""
    app.logger.error(f"500 Internal Server Error: {request.method} {request.path} - Exception: {str(e)}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500


def find_task(task_id):
    """Helper function to find a task by its ID."""
    return next((task for task in tasks if task["id"] == task_id), None)


# -----------------------------------------------------------------------------
# Frontend Route
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    """Renders the main Task Manager dashboard UI."""
    return render_template("index.html")


# -----------------------------------------------------------------------------
# Health Monitoring Endpoint
# -----------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint indicating application status."""
    return jsonify({"status": "healthy"}), 200


# -----------------------------------------------------------------------------
# Prometheus Metrics Endpoint
# -----------------------------------------------------------------------------
@app.route("/metrics", methods=["GET"])
def metrics():
    """Returns application metrics in Prometheus exposition format.

    Protected by Bearer-token authentication when METRICS_TOKEN is configured
    or when REQUIRE_METRICS_AUTH=true / RENDER=true is set.
    """
    if not is_metrics_authorized():
        app.logger.warning(
            "401 Unauthorized: GET /metrics — missing or invalid Bearer token"
        )
        return Response(
            "Unauthorized: valid Bearer token required",
            status=401,
             headers={"WWW-Authenticate": 'Bearer realm="metrics"'},
            mimetype="text/plain"
        )
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


# -----------------------------------------------------------------------------
# REST API Endpoints for Tasks
# -----------------------------------------------------------------------------
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Retrieve all tasks."""
    return jsonify(tasks), 200


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """Retrieve a single task by ID."""
    task = find_task(task_id)
    if not task:
        return jsonify({"error": f"Task with ID {task_id} not found"}), 404
    return jsonify(task), 200


@app.route("/api/tasks", methods=["POST"])
def create_task():
    """Create a new task."""
    global next_id

    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid request payload. Must be JSON."}), 400

    title = data.get("title")
    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Task title is required and cannot be empty."}), 400

    new_task = {
        "id": next_id,
        "title": title.strip(),
        "completed": False,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    }

    tasks.append(new_task)
    next_id += 1

    return jsonify(new_task), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Update an existing task's title or completion status."""
    task = find_task(task_id)
    if not task:
        return jsonify({"error": f"Task with ID {task_id} not found"}), 404

    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid request payload. Must be JSON."}), 400

    if "title" in data:
        new_title = data["title"]
        if not isinstance(new_title, str) or not new_title.strip():
            return jsonify({"error": "Task title cannot be empty."}), 400
        task["title"] = new_title.strip()

    if "completed" in data:
        new_completed = data["completed"]
        if not isinstance(new_completed, bool):
            return jsonify({"error": "'completed' field must be a boolean value."}), 400
        task["completed"] = new_completed

    return jsonify(task), 200


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task by ID."""
    task = find_task(task_id)
    if not task:
        return jsonify({"error": f"Task with ID {task_id} not found"}), 404

    tasks.remove(task)
    return jsonify({"message": f"Task with ID {task_id} deleted successfully", "id": task_id}), 200


@app.route("/test-500-error", methods=["GET"])
def trigger_500_error():
    """Test endpoint that raises an unhandled exception for global 500 handler verification.

    Restricted strictly to test execution (app.config['TESTING'] == True);
    returns 404 Not Found in production/non-test environments.
    """
    if not app.config.get("TESTING"):
        app.logger.warning(f"404 Not Found: {request.method} {request.path}")
        return jsonify({"error": "Resource not found"}), 404
    raise RuntimeError("Simulated internal exception for testing")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)

