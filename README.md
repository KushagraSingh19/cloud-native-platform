# Cloud-Native Application Deployment & Monitoring Platform

[![CI](https://github.com/KushagraSingh19/cloud-native-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/KushagraSingh19/cloud-native-platform/actions/workflows/ci.yml)
[![Docker Image](https://ghcr.io/kushagrasingh19/cloud-native-platform)](https://github.com/KushagraSingh19/cloud-native-platform/pkgs/container/cloud-native-platform)

A complete, production-grade microservice application featuring a Flask REST API, web dashboard, Gunicorn WSGI server, Docker containerization, Prometheus metrics & server, Grafana visualization dashboards, structured logging, automated pytest test suite, GitHub Actions CI pipeline, and automated Docker image publishing to GHCR.

---

## 🏗️ End-to-End System Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         Docker Compose Microservice                      │
│                                                                          │
│  ┌──────────────────┐    Scrapes /metrics    ┌──────────────────┐        │
│  │ task-manager-app │◄───────────────────────│ prometheus-server│        │
│  │   (Port 5001)    │      (5s interval)     │   (Port 9090)    │        │
│  └──────────────────┘                        └──────────────────┘        │
│           ▲                                           ▲                  │
│           │                                           │ PromQL Queries   │
│           │                                           │                  │
│           │ Bridge Network                            │                  │
│           │                                  ┌──────────────────┐        │
│           │                                  │  grafana-server  │        │
│           │                                  │   (Port 3000)    │        │
│           │                                  └──────────────────┘        │
└───────────┼───────────────────────────────────────────┼──────────────────┘
            │                                           │
            ▼                                           ▼
   http://localhost:5001                       http://localhost:3000
    (Task Manager UI)                           (Grafana Dashboard)
```

---

## 🚀 Completed Phases Overview

- **Phase 1**: Flask Task Manager Web Application & REST API (`app.py`, `templates/`, `static/`)
- **Phase 2**: Production Docker Containerization & Gunicorn WSGI Server (`Dockerfile`, `.dockerignore`)
- **Phase 3**: Application-Level Prometheus Instrumentation (`/metrics`, `http_requests_total`, `http_request_duration_seconds`, `http_requests_in_progress`)
- **Phase 4**: Prometheus Server Integration (`prometheus/prometheus.yml`, port `9090`)
- **Phase 5**: Grafana Visualization & Automated Provisioning (`grafana/`, port `3000`, 10-panel dashboard)
- **Phase 6**: Structured Application Logging & Global Exception Handling (`sys.stdout`, `INFO`/`WARNING`/`ERROR` levels)
- **Phase 7**: Git Repository Initialization & Version Control Preparation
- **Phase 8**: GitHub Actions Continuous Integration (`.github/workflows/ci.yml` — pytest + Docker build on every push/PR)
- **Phase 9**: Docker Image Publishing to GitHub Container Registry (`ghcr.io/kushagrasingh19/cloud-native-platform`, commit-SHA + `latest` tags, push to `main` only)

*(Note: Kubernetes and Cloud Deployment are planned for subsequent phases).*

---

## 📁 Repository Structure

```
Cloud-Native-Platform/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI: pytest, Docker build (PR+push), GHCR publish (main only)
├── Dockerfile              # Production Docker build specification (Python 3.11 slim)
├── .dockerignore           # Docker context exclusion rules
├── .gitignore              # Git repository ignore rules
├── docker-compose.yml      # Multi-service stack (Flask app, Prometheus, Grafana)
├── app.py                  # Main Flask microservice, REST API, metrics & logging
├── requirements.txt        # Python dependencies (Flask, pytest, gunicorn, prometheus-client)
├── README.md               # Documentation & viva presentation guide
├── prometheus/
│   └── prometheus.yml      # Prometheus scraper configuration (5s interval)
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── prometheus.yml  # Automated Prometheus data source provisioning
│   │   └── dashboards/
│   │       └── dashboards.yml  # Automated dashboard provider provisioning
│   └── dashboards/
│       └── cloud-native-dashboard.json # 10-panel visual monitoring dashboard
├── static/
│   ├── css/style.css       # Modern dark UI styling
│   └── js/main.js          # REST API client with JavaScript fetch()
├── templates/
│   └── index.html          # Task Manager Web Dashboard UI
└── tests/
    ├── __init__.py         # Test package initializer
    └── test_app.py         # Pytest suite (16 tests covering API, /metrics, errors)
```

---

## ⚡ Quick Start Guide

### 1. Launch Complete Stack with Docker Compose

```bash
docker compose up -d
```

### 2. Verify Container Health & Services

```bash
docker compose ps
```

### 3. Access Web Services

- **Task Manager Dashboard**: [http://localhost:5001](http://localhost:5001)
- **Prometheus Metrics**: [http://localhost:5001/metrics](http://localhost:5001/metrics)
- **Prometheus Web UI**: [http://localhost:9090](http://localhost:9090)
- **Grafana Monitoring Dashboard**: [http://localhost:3000](http://localhost:3000)

### 4. Run Automated Pytest Suite

```bash
source venv/bin/activate
pytest -v
```

### 5. View Application Logs

```bash
docker compose logs -f task-manager
```

---

## 🧪 REST API Reference

| Method | Endpoint | Description | Expected Status |
|---|---|---|---|
| `GET` | `/` | Web Dashboard UI | `200 OK` |
| `GET` | `/health` | Application Health Status | `200 OK` |
| `GET` | `/metrics` | Prometheus Exposition Feed | `200 OK` |
| `GET` | `/api/tasks` | List all tasks | `200 OK` |
| `POST` | `/api/tasks` | Create task (`{"title": "..."}`) | `201 Created` / `400 Bad Request` |
| `GET` | `/api/tasks/<id>` | Get specific task | `200 OK` / `404 Not Found` |
| `PUT` | `/api/tasks/<id>` | Update task | `200 OK` / `400` / `404` |
| `DELETE` | `/api/tasks/<id>` | Delete task | `200 OK` / `404 Not Found` |

---

## 🔄 GitHub Actions CI Pipeline

The CI pipeline is defined in [`.github/workflows/ci.yml`](.github/workflows/ci.yml) and runs automatically on:
- Every **push** to the `main` branch
- Every **pull request** targeting `main`

### Pipeline Jobs

| Job | Trigger | `needs` | Permissions | What it does |
|---|---|---|---|---|
| `test` | push + PR | — | `contents: read` | Python 3.11 → install deps → `pytest tests/ -v` |
| `docker-build` | push + PR | `test` ✅ | `contents: read` | Buildx build, **no push** — CI Dockerfile verification |
| `docker-publish` | **push to `main` only** | `test` ✅ | `contents: read` + **`packages: write`** | Login to GHCR → build & push image with SHA + `latest` tags |

> Pull requests **never** trigger `docker-publish`. The `packages: write` permission is scoped to that job only.

### Checking CI Status on GitHub

1. Go to **[https://github.com/KushagraSingh19/cloud-native-platform/actions](https://github.com/KushagraSingh19/cloud-native-platform/actions)**
2. Click on the **CI** workflow to see all runs.
3. Click any run to see per-job and per-step logs.
4. The green/red badge at the top of this README reflects the latest `main` branch status.

### Running CI Checks Locally

```bash
# Run tests (same command used in CI)
source venv/bin/activate
pytest tests/ -v

# Build the Docker image locally (same as CI docker-build job)
docker build -t cloud-native-platform:local .
```

---

## 🐳 Docker Image – GitHub Container Registry (GHCR)

The Docker image is automatically built and published to GHCR on every push to `main`.

**Image location**: `ghcr.io/kushagrasingh19/cloud-native-platform`

### Pulling the Image

```bash
# Pull the latest image (published from main branch)
docker pull ghcr.io/kushagrasingh19/cloud-native-platform:latest

# Pull a specific commit version (replace <sha> with the short commit hash)
docker pull ghcr.io/kushagrasingh19/cloud-native-platform:sha-<sha>
```

### Running the Published Image Locally

```bash
docker run -p 5001:5001 ghcr.io/kushagrasingh19/cloud-native-platform:latest
```

Then open: [http://localhost:5001](http://localhost:5001)

### Viewing Published Packages on GitHub

All published image versions are listed at:
👉 **[https://github.com/KushagraSingh19/cloud-native-platform/pkgs/container/cloud-native-platform](https://github.com/KushagraSingh19/cloud-native-platform/pkgs/container/cloud-native-platform)**

---

## 🎓 Viva Voce Explanation Guide

1. **Microservice Core**: Modular Flask app with separation of concerns (REST API, frontend templates, Gunicorn WSGI).
2. **Containerization**: Standardized OCI container via `Dockerfile` and `docker-compose.yml` with health checks.
3. **Metrics Observability**: `/metrics` endpoint exposing low-cardinality Prometheus metrics (`http_requests_total`, `http_request_duration_seconds`, `http_requests_in_progress`).
4. **Scraping & Storage**: Prometheus pulls metrics every 5s over container DNS resolution (`task-manager-app:5001`) with volume persistence.
5. **Visual Monitoring**: Grafana displays 10 real-time panels via automated provisioning.
6. **Logging & Resilience**: Structured STDOUT logs with millisecond latency and global JSON error handlers (400, 404, 500).
7. **CI/CD Pipeline**: GitHub Actions workflow runs pytest on every push/PR, verifies Docker build, and publishes OCI-compliant image to GHCR using `GITHUB_TOKEN` with minimal scoped permissions.
