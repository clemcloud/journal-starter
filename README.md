# 📔 Journal API — Cloud Native Capstone Project

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

A production-ready REST API for tracking daily learning journeys — built as part of the **Learn to Cloud** bootcamp capstone.

**Live API:** [https://journal-starter.duckdns.org/docs](https://journal-starter.duckdns.org/docs)  
**Author:** Umoru Clement — Cloud Engineer  
**GitHub:** [@clemcloud](https://github.com/clemcloud)  
**LinkedIn:** [clementcloud](https://www.linkedin.com/in/clementcloud)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Data Schema](#data-schema)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [AI Analysis](#ai-analysis)
- [CI/CD Pipeline](#cicd-pipeline)
- [Roadmap](#roadmap)
- [Documentation](#documentation)

---

## 🔍 Overview

The Journal API helps developers track their daily learning journey. Each entry captures three things — what you worked on, what you struggled with, and what you plan to do next. The API also includes an AI-powered analysis feature that uses GitHub Models to return sentiment, a summary, and key topics from each entry.

This project demonstrates real-world backend development practices:

- Clean architecture separating routers, services, and models
- Input validation with Pydantic `StringConstraints`
- AI integration using the OpenAI SDK with GitHub Models
- Containerized development with Docker Dev Containers
- Automated testing with 50 tests covering all endpoints
- CI/CD with GitHub Actions running on every push and PR

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance Python web framework |
| **PostgreSQL** | Relational database for persistent storage |
| **Docker** | Containerized development and deployment |
| **Dev Containers** | Consistent development environment across machines |
| **Pydantic** | Data validation and settings management |
| **OpenAI SDK** | AI-powered entry analysis via GitHub Models |
| **pytest** | Automated testing framework |
| **GitHub Actions** | CI/CD pipeline — lint, type check, and test on every push |
| **AWS CLI** | Cloud CLI pre-configured in the Dev Container |
| **uv** | Fast Python package manager |
| **Ruff** | Python linter and formatter |
| **Pyright** | Static type checker |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Client Request                    │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                  FastAPI Router                      │
│          api/routers/journal_router.py               │
│     (Receives requests, returns responses)           │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                 Pydantic Models                      │
│              api/models/entry.py                     │
│     (Validates incoming data automatically)          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                  Entry Service                       │
│           api/services/entry_service.py              │
│              (All business logic lives here)         │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              PostgreSQL Database                     │
│         (Running in Docker Dev Container)            │
└─────────────────────────────────────────────────────┘
```

For AI analysis requests, the flow extends:

```
Entry Service → LLM Service → GitHub Models API → Returns Analysis
```

---

## 📊 Data Schema

Each journal entry follows this structure:

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `id` | string (UUID) | Unique identifier | Auto-generated |
| `work` | string | What did you work on today? | Required, 1–256 chars, whitespace stripped |
| `struggle` | string | What did you struggle with? | Required, 1–256 chars, whitespace stripped |
| `intention` | string | What will you study tomorrow? | Required, 1–256 chars, whitespace stripped |
| `created_at` | datetime | When the entry was created | Auto-generated UTC |
| `updated_at` | datetime | When the entry was last updated | Auto-updated UTC |

---

## 🚀 Getting Started

### Prerequisites

Before you begin make sure you have the following installed:

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [VS Code](https://code.visualstudio.com/) with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

---

### Step 1 — Fork and Clone

Fork this repository to your GitHub account by clicking the **Fork** button at the top right, then clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/journal-starter.git
cd journal-starter
```

Verify your remote points to your fork:

```bash
git remote -v
# Should show: origin  https://github.com/YOUR_USERNAME/journal-starter.git
```

---

### Step 2 — Configure Environment

Copy the sample environment file:

```bash
cp .env-sample .env
```

Open `.env` and update the values:

```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/career_journal
OPENAI_API_KEY=your_github_personal_access_token
OPENAI_BASE_URL=https://models.inference.ai.azure.com
OPENAI_MODEL=gpt-4o-mini
```

> 💡 Generate a free GitHub Personal Access Token at [github.com/settings/tokens](https://github.com/settings/tokens) and use it as your `OPENAI_API_KEY`. No credit card required.

---

### Step 3 — Open in Dev Container

Make sure Docker Desktop is running, then open VS Code and press `Ctrl + Shift + P`:

```
Dev Containers: Reopen in Container
```

Wait for the container to build — this automatically installs Python, all dependencies, PostgreSQL, and the AWS CLI.

![Dev Container Screenshot](docs/images/devcontainer.png)

---

### Step 4 — Start the API

Once inside the Dev Container, start the API from the project root:

```bash
./start.sh
```

You should see:

```
🎉 Starting FastAPI server...
📖 API docs will be available at: http://localhost:8000/docs
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

### Step 5 — Explore the API

Visit the interactive API documentation at:

```
http://localhost:8000/docs
```

![Docs Ui Screenshot](docs/images/docsui.png)

From the docs UI you can:
- Create your first journal entry using `POST /entries`
- View all entries using `GET /entries`
- Test the AI analysis using `POST /entries/{entry_id}/analyze`

![Create an Entry](docs/images/create-entry1.png)

![Create an Entry](docs/images/create-entry2.png)

---

## 🔌 API Endpoints

### Endpoints Overview

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| `POST` | `/entries` | Create a new journal entry | 201 |
| `GET` | `/entries` | Get all journal entries | 200 |
| `GET` | `/entries/{entry_id}` | Get a single entry by ID | 200 / 404 |
| `PATCH` | `/entries/{entry_id}` | Partially update an entry | 200 / 404 |
| `DELETE` | `/entries/{entry_id}` | Delete a single entry | 200 / 404 |
| `DELETE` | `/entries` | Delete all entries | 200 |
| `POST` | `/entries/{entry_id}/analyze` | AI analysis of an entry | 200 / 404 / 501 |

---

### Create Entry

```http
POST /entries
Content-Type: application/json

{
    "work": "Studied FastAPI and built my first REST API",
    "struggle": "Understanding async/await syntax and when to use it",
    "intention": "Practice PostgreSQL queries and database design"
}
```

**Response (201):**
```json
{
    "detail": "Entry created successfully",
    "entry": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "work": "Studied FastAPI and built my first REST API",
        "struggle": "Understanding async/await syntax and when to use it",
        "intention": "Practice PostgreSQL queries and database design",
        "created_at": "2026-05-16T14:30:00Z",
        "updated_at": "2026-05-16T14:30:00Z"
    }
}
```

---

### Get Single Entry

```http
GET /entries/123e4567-e89b-12d3-a456-426614174000
```

**Response (200):**
```json
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "work": "Studied FastAPI and built my first REST API",
    "struggle": "Understanding async/await syntax and when to use it",
    "intention": "Practice PostgreSQL queries and database design",
    "created_at": "2026-05-16T14:30:00Z",
    "updated_at": "2026-05-16T14:30:00Z"
}
```

---

### Update Entry (Partial)

Only send the fields you want to update — other fields remain unchanged:

```http
PATCH /entries/123e4567-e89b-12d3-a456-426614174000
Content-Type: application/json

{
    "work": "Studied Docker and containerization"
}
```

**Response (200):**
```json
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "work": "Studied Docker and containerization",
    "struggle": "Understanding async/await syntax and when to use it",
    "intention": "Practice PostgreSQL queries and database design",
    "created_at": "2026-05-16T14:30:00Z",
    "updated_at": "2026-05-16T15:00:00Z"
}
```

---

### Validation Error

Empty strings, whitespace-only input, and fields over 256 characters are automatically rejected:

```http
POST /entries
Content-Type: application/json

{
    "work": "",
    "struggle": "   ",
    "intention": "Practice more"
}
```

**Response (422):**
```json
{
    "detail": [
        {
            "type": "string_too_short",
            "loc": ["body", "work"],
            "msg": "String should have at least 1 character",
            "input": ""
        }
    ]
}
```

---

### AI Analysis

```http
POST /entries/123e4567-e89b-12d3-a456-426614174000/analyze
```

**Response (200):**
```json
{
    "entry_id": "123e4567-e89b-12d3-a456-426614174000",
    "sentiment": "positive",
    "summary": "The learner made solid progress with FastAPI and REST API development. They are planning to strengthen their database skills next.",
    "topics": ["FastAPI", "REST API", "async/await", "PostgreSQL"],
    "created_at": "2026-05-16T14:30:00Z"
}
```

![Ai analysis](docs/images/ai-analysis10.png)

![Ai analysis](docs/images/ai-analysis11.png)

---

## 🔄 Development Workflow

This project follows a feature branch workflow — every feature is developed in isolation and merged via a Pull Request.

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes in the api/ directory

# Run tests — make sure everything passes
uv run pytest

# Check code style
uv run ruff check .

# Auto-format code
uv run ruff format .

# Run type checker
uv run pyright

# Commit and push
git add .
git commit -m "Implement feature X"
git push -u origin feature/your-feature-name
```

Then open a Pull Request on GitHub targeting your fork's `main` branch. The CI pipeline runs automatically on every PR.

---

## 🧪 Testing

The project has **50 automated tests** covering all endpoints, models, and services.

```bash
# Run all tests
uv run pytest

# Run with verbose output to see each test
uv run pytest -v

# Run with short error details
uv run pytest -v --tb=short

# Run a specific test file
uv run pytest tests/test_api.py

# Run a specific test class
uv run pytest tests/test_api.py::TestGetSingleEntry
```

### Test Coverage

| Test File | What it Covers |
|-----------|---------------|
| `test_api.py` | All API endpoints — success and error cases |
| `test_models.py` | Pydantic model validation rules |
| `test_service.py` | Entry service business logic |
| `test_logging.py` | Logging configuration |
| `test_llm_service.py` | AI analysis function with mock client |

---

## 🤖 AI Analysis

The `POST /entries/{entry_id}/analyze` endpoint uses the **OpenAI SDK** with **GitHub Models** to analyze journal entries — completely free with a GitHub account, no credit card required.

### How It Works

The three entry fields are combined into a single prompt and sent to the model:

```python
# Entry fields are combined into prompt text
entry_text = f"{entry['work']} {entry['struggle']} {entry['intention']}"

# Sent to GitHub Models via the OpenAI SDK
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant for analyzing journal entries."
    },
    {
        "role": "user",
        "content": entry_text
    }
]

response = await client.chat.completions.create(
    model=get_settings().openai_model,
    messages=messages
)
```

The model returns a JSON response which is parsed and returned as an `AnalysisResponse` containing `entry_id`, `sentiment`, `summary`, `topics`, and `created_at`.

### Setup

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Generate a Personal Access Token
3. Add it to your `.env` file as `OPENAI_API_KEY`

---

## ⚙️ CI/CD Pipeline

Every push and pull request automatically triggers two GitHub Actions jobs:

| Job | What it Checks | Command |
|-----|---------------|---------|
| **Lint** | Code style, formatting, type safety | `ruff check . && ruff format --check . && pyright` |
| **Test** | All 50 tests against a real PostgreSQL 16 container | `pytest -v` |

Both jobs must pass before merging any PR. No secrets are required — the test job spins up a disposable PostgreSQL container and the AI analysis tests use an injected mock client so no real API calls are made during CI.

---

## 🗺️ Roadmap

This project is being built in phases — each phase adds a new layer of production readiness.

### ✅ Phase 1 — Local Development
- FastAPI + PostgreSQL running locally in Docker Dev Containers
- 50 automated tests passing
- GitHub Actions CI/CD pipeline
- AI analysis via GitHub Models

### ✅ Phase 2 — Cloud Deployment ☁️
- VPC with public and private subnets on AWS
- API server on EC2 with Nginx reverse proxy and TLS
- PostgreSQL on private EC2 — no public IP
- AI analysis migrated to Amazon Bedrock (Nova Lite)
- Live at: [https://journal-starter.duckdns.org](https://journal-starter.duckdns.org)

👉 [View Full Cloud Deployment Guide](docs/cloud-deployment.md)

### 🔄 Phase 3 — Production DevOps 🐳
Orchestrating and automating the full deployment pipeline:
- [ ] Production `Dockerfile` and `.dockerignore`
- [ ] GitHub Actions workflows for automated deployments
- [ ] Kubernetes manifests — Deployment, Service, Secrets (`k8s/` folder)
- [ ] Prometheus and Grafana observability

👉 [View DevOps Guide](docs/devops.md) _(coming soon)_

### ⏳ Phase 4 — Security 🔒
Hardening the application for production:
- [ ] JWT authentication and authorization
- [ ] Rate limiting per user
- [ ] Security scanning in CI pipeline
- [ ] Secrets management best practices

👉 [View Security Guide](docs/security.md) _(coming soon)_

---

## 📚 Documentation

As this project grows, detailed documentation for each phase lives in the `docs/` folder:

| Document | Description |
|----------|-------------|
| [☁️ Cloud Deployment Guide](docs/cloud-deployment.md) | Full AWS deployment — EC2, Nginx, TLS, Bedrock, challenges and lessons learned |
| [🐳 DevOps Guide](docs/devops.md) | Dockerfile, Kubernetes, GitHub Actions, Prometheus, Grafana _(coming soon)_ |
| [🔒 Security Guide](docs/security.md) | JWT, rate limiting, security scanning _(coming soon)_ |
| [Explore the Database](docs/explore-database.md) | Connect to PostgreSQL and run queries directly |

> More docs will be added as each phase is completed.

---

## 👨‍💻 Author

**Umoru Clement — Cloud Engineer**

- GitHub: [@clemcloud](https://github.com/clemcloud)
- LinkedIn: [clementcloud](https://www.linkedin.com/in/clementcloud)

---

## 📄 License

This project is based on the [Learn to Cloud Journal Starter](https://github.com/learntocloud/journal-starter) template.

---

<div align="center">

⭐ **If you found this project helpful, please give it a star!** ⭐

</div>