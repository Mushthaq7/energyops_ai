# ⚡ EnergyOps AI — GenAI Energy Analytics Backend

A production-ready FastAPI backend for renewable energy plant analytics, featuring a RAG pipeline, LLM integration, Prometheus monitoring, MLflow experiment tracking, and Docker deployment.

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Project Structure](#-project-structure)
3. [Prerequisites](#-prerequisites)
4. [Step 1 — Clone & Setup Virtual Environment](#step-1--clone--setup-virtual-environment)
5. [Step 2 — Install Dependencies](#step-2--install-dependencies)
6. [Step 3 — Configure Environment Variables](#step-3--configure-environment-variables)
7. [Step 4 — Setup PostgreSQL Database](#step-4--setup-postgresql-database)
8. [Step 5 — Populate Sample Data](#step-5--populate-sample-data)
9. [Step 6 — Run the Application](#step-6--run-the-application)
10. [Step 7 — Test the API Endpoints](#step-7--test-the-api-endpoints)
11. [Step 8 — RAG Pipeline (Ask Questions)](#step-8--rag-pipeline-ask-questions)
12. [Step 9 — Run Evaluation & MLflow](#step-9--run-evaluation--mlflow)
13. [Step 10 — Prometheus Monitoring](#step-10--prometheus-monitoring)
14. [Step 11 — LoRA Fine-tuning (Optional)](#step-11--lora-fine-tuning-optional)
15. [Step 12 — Docker Deployment](#step-12--docker-deployment)
16. [Step 13 — Deploy to Cloud (Azure / GCP)](#step-13--deploy-to-cloud-azure--gcp)
17. [API Reference](#-api-reference)
18. [Architecture](#-architecture)

---

## 🔍 Project Overview

**EnergyOps AI** is a GenAI-powered system for renewable energy operations. It provides:

- **Energy Analytics API** — Query production data, detect anomalies, get plant summaries
- **RAG Pipeline** — Ask natural language questions about maintenance documents and get grounded answers with citations
- **LLM Integration** — Pluggable LLM backend (Mistral 7B / Llama 3 / OpenAI)
- **Evaluation** — Measure latency, token count, and log results to MLflow
- **Monitoring** — Prometheus metrics for request latency, error rates, and model response times
- **LoRA Fine-tuning** — Fine-tune Mistral 7B on domain-specific instruction data using PEFT

---

## 📁 Project Structure

```
energyops-ai/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py                 # Router aggregation
│   │       └── endpoints/
│   │           ├── energy.py          # Energy data endpoints
│   │           ├── rag.py             # RAG + /ask endpoint
│   │           └── evaluation.py      # /evaluate endpoint
│   ├── core/
│   │   ├── config.py                  # Pydantic settings
│   │   ├── exceptions.py             # Global error handlers
│   │   ├── log_config.py             # Structured JSON logging
│   │   ├── metrics.py                # Prometheus metric definitions
│   │   └── middleware.py             # Prometheus auto-instrumentation
│   ├── db/
│   │   ├── base.py                    # Alembic model imports
│   │   └── session.py                # SQLAlchemy session factory
│   ├── models/
│   │   ├── base.py                    # SQLAlchemy DeclarativeBase
│   │   └── energy.py                 # EnergyProduction table
│   ├── schemas/
│   │   └── energy.py                 # Pydantic response schemas
│   ├── services/
│   │   ├── rag/
│   │   │   └── service.py            # RAG service (FAISS + LLM)
│   │   └── evaluation/
│   │       └── service.py            # MLflow evaluation service
│   └── main.py                        # FastAPI app entry point
├── data/
│   ├── documents/                     # Maintenance manuals (.txt)
│   │   ├── solar_maintenance.txt
│   │   └── wind_maintenance.txt
│   └── energy_instructions.json       # LoRA training data
├── Dockerfile                         # Backend container
├── docker-compose.yml                 # Full stack (DB + API + Prometheus + Grafana + MLflow)
├── prometheus.yml                     # Prometheus scrape config
├── requirements.txt                   # Python dependencies
├── generate_data.py                   # Synthetic DB data generator
├── evaluate_rag.py                    # Batch evaluation script
├── finetune_lora.py                   # LoRA fine-tuning script
├── .env.example                       # Environment template
└── .gitignore
```

---

## ✅ Prerequisites

- **Python 3.9+**
- **PostgreSQL** running locally (or via Docker)
- **Docker & Docker Compose** (for containerized deployment)
- **GPU with 16GB+ VRAM** (only for LoRA fine-tuning)

---

## Step 1 — Clone & Setup Virtual Environment

```bash
cd /path/to/energyops-ai

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate
```

---

## Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: FastAPI, SQLAlchemy, LangChain, FAISS, Sentence Transformers, MLflow, Prometheus client, PEFT, and more.

---

## Step 3 — Configure Environment Variables

```bash
# Copy the template
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=energyops_db
POSTGRES_PORT=5432
```

---

## Step 4 — Setup PostgreSQL Database

```bash
# Start PostgreSQL (if not running)
brew services start postgresql   # macOS

# Create the database
psql postgres -c "CREATE DATABASE energyops_db;"
```

---

## Step 5 — Populate Sample Data

```bash
python3 generate_data.py
```

This creates the `energy_production` table and inserts synthetic data for solar and wind plants.

---

## Step 6 — Run the Application

```bash
python3 -m uvicorn app.main:app --reload
```

The server starts at **http://localhost:8000**.

Verify it's running:

```bash
curl http://localhost:8000/health
# → {"status": "ok"}
```

---

## Step 7 — Test the API Endpoints

### Get latest energy readings
```bash
curl http://localhost:8000/api/v1/energy/latest
```

### Get anomalies
```bash
curl http://localhost:8000/api/v1/energy/anomalies
```

### Get plant summary
```bash
curl http://localhost:8000/api/v1/energy/summary
```

---

## Step 8 — RAG Pipeline (Ask Questions)

### Index the maintenance documents
```bash
curl -X POST http://localhost:8000/api/v1/rag/index
# → {"status": "indexing completed"}
```

### Ask a question (retrieval + LLM generation + citations)
```bash
curl -X POST http://localhost:8000/api/v1/rag/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I check wind turbine gearbox oil levels?"}'
```

Returns:
```json
{
  "question": "How do I check wind turbine gearbox oil levels?",
  "answer": "...",
  "citations": [
    {
      "content": "Check oil levels monthly...",
      "source": "wind_maintenance.txt",
      "score": 1.17
    }
  ]
}
```

### Retrieve documents only (no LLM)
```bash
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "solar panel cleaning", "k": 3}'
```

---

## Step 9 — Run Evaluation & MLflow

### Run evaluation via API
```bash
curl -X POST http://localhost:8000/api/v1/evaluation/evaluate \
  -H "Content-Type: application/json" \
  -d '{"questions": ["How to check oil levels?", "How to clean solar panels?"]}'
# → {"status": "success", "results_logged": 2}
```

### Run evaluation via script
```bash
python3 evaluate_rag.py
```

### View results in MLflow
```bash
mlflow ui
```
Open **http://127.0.0.1:5000** to view experiment runs with latency, token counts, and citation metrics.

---

## Step 10 — Prometheus Monitoring

### View raw metrics
```bash
curl http://localhost:8000/metrics
```

### Key metrics exposed

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total requests by method, endpoint, status |
| `http_request_duration_seconds` | Histogram | Request latency (p50, p95, p99) |
| `http_request_errors_total` | Counter | 4xx / 5xx error count |
| `http_active_requests` | Gauge | In-flight requests |
| `model_response_duration_seconds` | Histogram | Retrieval / generation / total RAG time |
| `model_requests_total` | Counter | Model call count (success / error) |
| `documents_indexed_total` | Counter | Documents indexed |

### Example PromQL queries (for Grafana)

```promql
# Request rate (per second)
rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_request_errors_total[5m])

# Average model response time
rate(model_response_duration_seconds_sum{operation="ask"}[5m])
  / rate(model_response_duration_seconds_count{operation="ask"}[5m])
```

---

## Step 11 — LoRA Fine-tuning (Optional)

Fine-tune Mistral 7B on renewable energy instruction data using QLoRA:

```bash
python3 finetune_lora.py
```

> ⚠️ **Requires a GPU with 16GB+ VRAM.** Training on CPU will be extremely slow.

- **Dataset**: `data/energy_instructions.json` (10 instruction-response pairs)
- **Output**: LoRA adapter saved to `./lora_output/`
- **Config**: LoRA rank=16, alpha=32, targets=`[q_proj, k_proj, v_proj, o_proj]`

---

## Step 12 — Docker Deployment

### Build and start all services

```bash
docker-compose up -d
```

This starts **5 containers**:

| Container | Port | Service |
|-----------|------|---------|
| `energyops-db` | 5432 | PostgreSQL 15 |
| `energyops-api` | 8000 | FastAPI Backend |
| `energyops-mlflow` | 5000 | MLflow UI |
| `energyops-prometheus` | 9090 | Prometheus |
| `energyops-grafana` | 3000 | Grafana (admin / admin) |

### Useful commands
```bash
# View API logs
docker-compose logs -f api

# Restart API only
docker-compose restart api

# Tear down everything
docker-compose down -v
```

---

## Step 13 — Deploy to Cloud (Azure / GCP)

### On Azure VM

```bash
# 1. Create an Azure VM (Ubuntu 22.04, Standard_D2s_v3 or higher)
# 2. SSH into the VM
ssh azureuser@<your-vm-ip>

# 3. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 4. Clone the repo
git clone <your-repo-url>
cd energyops-ai

# 5. Create .env with production values
cp .env.example .env
nano .env

# 6. Start all services
docker-compose up -d

# 7. Open firewall ports
# Azure Portal → VM → Networking → Add inbound rules for 8000, 9090, 3000
```

### On GCP VM

```bash
# 1. Create a GCP Compute Engine instance (e2-medium or higher, Ubuntu 22.04)
# 2. SSH into the VM
gcloud compute ssh <instance-name>

# 3. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 4. Clone, configure .env, and run docker-compose up -d
# 5. Open firewall:
gcloud compute firewall-rules create energyops-allow \
  --allow tcp:8000,tcp:9090,tcp:3000 \
  --source-ranges 0.0.0.0/0
```

---

## 📚 API Reference

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| `GET` | `/health` | — | Health check |
| `GET` | `/metrics` | — | Prometheus metrics |
| `GET` | `/api/v1/energy/latest` | — | Latest energy readings |
| `GET` | `/api/v1/energy/anomalies` | — | Anomaly detection |
| `GET` | `/api/v1/energy/summary` | — | Plant summary statistics |
| `POST` | `/api/v1/rag/index` | — | Index maintenance documents |
| `POST` | `/api/v1/rag/query` | `{"query": "...", "k": 3}` | Retrieve relevant chunks |
| `POST` | `/api/v1/rag/ask` | `{"question": "..."}` | Ask with LLM + citations |
| `POST` | `/api/v1/evaluation/evaluate` | `{"questions": [...]}` | Evaluate & log to MLflow |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client / cURL                        │
└─────────────┬───────────────────────────────┬───────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────┐   ┌───────────────────────────────┐
│  FastAPI Backend :8000  │   │  Prometheus :9090 ◄─ scrape   │
│                         │   │       │                       │
│  ┌───────────────────┐  │   │       ▼                       │
│  │  /metrics         │──┼───┤  Grafana :3000                │
│  │  /health          │  │   └───────────────────────────────┘
│  │  /api/v1/energy/* │  │
│  │  /api/v1/rag/ask  │  │   ┌───────────────────────────────┐
│  │  /api/v1/eval/*   │  │   │  MLflow :5000                 │
│  └───────────────────┘  │   │  (Experiment Tracking)        │
│           │              │   └───────────────────────────────┘
│           ▼              │
│  ┌─────────────────┐    │
│  │   RAG Service    │    │
│  │  ┌───────────┐   │    │
│  │  │ FAISS     │   │    │
│  │  │ HuggingFace│  │    │
│  │  │ LLM       │   │    │
│  │  └───────────┘   │    │
│  └─────────────────┘    │
│           │              │
│           ▼              │
│  ┌─────────────────┐    │
│  │  PostgreSQL      │    │
│  │  :5432           │    │
│  └─────────────────┘    │
└─────────────────────────┘
```

---

**Built with** FastAPI · SQLAlchemy · LangChain · FAISS · HuggingFace · Prometheus · Grafana · MLflow · PEFT · Docker
