# GCP Pub/Sub - Streaming & Event-Driven Architecture

Production-ready cloud microservices with Google Cloud Pub/Sub and Cloud Storage.

## Setup

### 1) Install
```powershell
pip install -r requirements.txt
```

### 2) Set up Service Accounts

Each microservice uses its own service account for security isolation.

**Generator Service:**
```bash
# Create and place key at: services/generator/config/service-account.json
# Required permissions: roles/pubsub.publisher
```

**Ingestion Service:**
```bash
# Create and place key at: services/ingestion/config/service-account.json
# Required permissions: roles/pubsub.subscriber, roles/storage.objectAdmin
```

See detailed instructions:
- `services/generator/config/README.md`
- `services/ingestion/config/README.md`

### 3) GCP resources
- Enable Pub/Sub API for the project.
- Bucket: create `telemetry-data007` (multi-region `us` or your choice) with proper permissions.
- Topics: auto-created on startup (`server-metrics`, `container-metrics`, `service-metrics`).

### 4) Run Microservices

Services auto-detect their credentials from config folders:

```powershell
# Easiest: Run launcher script
.\scripts\run_microservices.ps1
```

Or manually:
```powershell
# Terminal 1: Generator Service
cd services/generator
$env:GCP_PROJECT_ID = "industrial-cloud-data"
python main.py

# Terminal 2: Ingestion Service
cd services/ingestion
$env:GCP_PROJECT_ID = "industrial-cloud-data"
$env:GCP_BUCKET_NAME = "telemetry-data007"
python main.py
```

### 5) Verify Data
```powershell
gcloud storage ls gs://telemetry-data007
gcloud storage cat gs://telemetry-data007/server_metrics.jsonl | Select-Object -First 5
```

### 6) Deploy to Cloud Run (Production)
```bash
bash scripts/deploy_generator.sh
bash scripts/deploy_ingestion.sh
```

## Architecture

```
┌──────────────────────────────┐
│  Generator Service           │
│  (Produces telemetry)        │
└──────────────┬───────────────┘
               │ publishes
               ▼
┌──────────────────────────────┐
│  GCP Pub/Sub Topics          │
│  (Event Streaming)           │
│  - server-metrics            │
│  - container-metrics         │
│  - service-metrics           │
└──────────────┬───────────────┘
               │ consumes
               ▼
┌──────────────────────────────┐
│  Ingestion Service           │
│  (Validates & Stores)        │
└──────────────┬───────────────┘
               │ stores to
               ▼
┌──────────────────────────────┐
│  Cloud Storage (JSONL)       │
│  (Data Persistence)          │
└──────────────────────────────┘
```

## Services

### Generator (`generator_gcp.py`)
- Generates telemetry metrics
- Publishes to Pub/Sub topics
- 3 metrics per cycle (server, container, service)

### Pub/Sub Broker (`gcp_pubsub.py`)
- Cloud-native event streaming
- Topics per metric type

### Ingestion (`ingestion_gcp.py`)
- Consumes from Pub/Sub
- Validates schema
- Stores to Cloud Storage as JSONL
