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
- **Phase 10A**: Cloud Deployment Security & Preparation (`render.yaml` Blueprint for Render Free Tier, Bearer-token authentication on `/metrics` for Grafana Cloud, removal of anonymous/hardcoded Grafana credentials, `.env.example`)

---

## 📁 Repository Structure

```
Cloud-Native-Platform/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI: pytest, Docker build (PR+push), GHCR publish (main only)
├── Dockerfile              # Production Docker build specification (Python 3.11 slim, dynamic $PORT)
├── .dockerignore           # Docker context exclusion rules (excludes .env and secrets)
├── .gitignore              # Git repository ignore rules (excludes .env, tracks .env.example)
├── .env.example            # Safe placeholder template for environment variables
├── render.yaml             # Render Blueprint IaC for deploying the GHCR image on the Free tier
├── docker-compose.yml      # Local multi-service stack (Flask app, Prometheus, Grafana)
├── app.py                  # Main Flask microservice, REST API, authenticated /metrics & logging
├── requirements.txt        # Python dependencies (Flask, pytest, gunicorn, prometheus-client)
├── README.md               # Documentation & viva presentation guide
├── prometheus/
│   ├── prometheus.yml              # Local Prometheus scraper configuration (Docker DNS)
│   └── prometheus-cloud.example.yml # Cloud scrape configuration reference for Grafana Cloud
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

## ⚡ Quick Start Guide (Local Development)

### 1. Configure Local Environment Variables

Copy the placeholder file `.env.example` to `.env` and set a strong local Grafana password:

```bash
cp .env.example .env
```

*(Note: `.env` is ignored by Git and Docker builds so your local credentials are never committed or baked into images).*

### 2. Launch Complete Stack with Docker Compose

```bash
docker compose up -d
```

### 3. Verify Container Health & Services

```bash
docker compose ps
```

### 4. Access Web Services

- **Task Manager Dashboard**: [http://localhost:5001](http://localhost:5001)
- **Prometheus Metrics**: [http://localhost:5001/metrics](http://localhost:5001/metrics)
- **Prometheus Web UI**: [http://localhost:9090](http://localhost:9090)
- **Grafana Monitoring Dashboard**: [http://localhost:3000](http://localhost:3000) *(Sign in using `GF_SECURITY_ADMIN_USER` and `GF_SECURITY_ADMIN_PASSWORD` from your `.env`)*

### 5. Run Automated Pytest Suite

```bash
source venv/bin/activate
pytest -v
```

### 6. View Application Logs

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

## ☁️ Cloud Deployment Architecture (Render + Grafana Cloud)

For public cloud deployment, the platform uses a zero-cost, security-hardened two-tier architecture:

1. **Render (Free Web Service)**: Runs the stateless Flask + Gunicorn container (`ghcr.io/kushagrasingh19/cloud-native-platform:latest`), terminates HTTPS automatically, and monitors container health via `GET /health`.
2. **Grafana Cloud (Free Tier)**: Scrapes `https://<your-render-service>.onrender.com/metrics` over HTTPS using a **Bearer token** (`METRICS_TOKEN`) via Grafana Cloud's **Metrics Endpoint** integration, storing time-series metrics and hosting the Grafana dashboard without exposing an unauthenticated Prometheus UI or anonymous Grafana instance to the internet.

### Environment Variables

| Variable | Where Used | Purpose |
|---|---|---|
| `PORT` | Local & Render | HTTP port Gunicorn binds to (`0.0.0.0:${PORT:-5001}`). Injected automatically by Render. |
| `METRICS_TOKEN` | Render (Secret) & Optional Local | Bearer token required to access `GET /metrics` (`Authorization: Bearer <token>`). |
| `REQUIRE_METRICS_AUTH` | Render (`"true"`) | Enforces fail-closed behavior on `/metrics` so metrics are never publicly exposed even if `METRICS_TOKEN` is unset. Note: `RENDER=true` (set automatically by Render) also enforces fail-closed behavior. |
| `GF_SECURITY_ADMIN_USER` | Local `.env` (`docker-compose.yml`) | Local Grafana administrator username. |
| `GF_SECURITY_ADMIN_PASSWORD` | Local `.env` (`docker-compose.yml`) | Local Grafana administrator password. |

### Security Notes

- **No Anonymous Grafana Access**: `GF_AUTH_ANONYMOUS_ENABLED=false` is enforced in `docker-compose.yml`, and `GF_AUTH_ANONYMOUS_ORG_ROLE=Admin` has been removed.
- **Credential Rotation**: Because earlier local development commits contained default `admin`/`admin` placeholders in `docker-compose.yml`, never reuse default passwords in any shared or cloud environment, and rotate any credentials if they were ever used outside `localhost`.
- **Protected `/metrics` Endpoint**: `GET /metrics` uses constant-time token comparison (`hmac.compare_digest`) against `METRICS_TOKEN` and fails closed (`401 Unauthorized`) in cloud environments. Meanwhile, `GET /health` remains accessible for Render health checks.
- **No Secrets in Code or Image Layers**: `.gitignore` and `.dockerignore` exclude `.env` and `.env.*` (while tracking `.env.example`), and `render.yaml` uses `sync: false` for `METRICS_TOKEN`.

### Free-Tier Limitations & Cost Safeguards

- **Render Free Web Service ($0/month)**:
  - Automatically spins down after **15 minutes of inbound inactivity**; the next request experiences a cold-start delay (~30–50 seconds). *(Note: If Grafana Cloud scrapes `/metrics` every 60s, the service will remain awake and consume Render's 750 free instance hours/month, which is sufficient for a single free web service running 24/7 in a 31-day month = 744 hours).*
  - Uses ephemeral container storage; in-memory tasks reset whenever the container restarts or redeploys.
- **Grafana Cloud Free Forever Plan ($0/month)**:
  - Includes up to **10,000 active Prometheus metric series** and **14-day retention** (our app exposes <50 series, well within the free limit).
  - Do not enter credit card details or upgrade to Pro/paid plans on either Render or Grafana Cloud.

---

## 🎓 Viva Voce Explanation Guide

1. **Microservice Core**: Modular Flask app with separation of concerns (REST API, frontend templates, Gunicorn WSGI).
2. **Containerization**: Standardized OCI container via `Dockerfile` and `docker-compose.yml` with health checks.
3. **Metrics Observability**: `/metrics` endpoint exposing low-cardinality Prometheus metrics (`http_requests_total`, `http_request_duration_seconds`, `http_requests_in_progress`).
4. **Scraping & Storage**: Prometheus pulls metrics every 5s over container DNS resolution (`task-manager-app:5001`) with volume persistence.
5. **Visual Monitoring**: Grafana displays 10 real-time panels via automated provisioning.
6. **Logging & Resilience**: Structured STDOUT logs with millisecond latency and global JSON error handlers (400, 404, 500).
7. **CI/CD Pipeline**: GitHub Actions workflow runs pytest on every push/PR, verifies Docker build, and publishes OCI-compliant image to GHCR using `GITHUB_TOKEN` with minimal scoped permissions.
