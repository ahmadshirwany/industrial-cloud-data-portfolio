#!/bin/bash
# Deploy Ingestion Microservice to Cloud Run

echo "🚀 Deploying Ingestion Microservice to Cloud Run..."

gcloud run deploy telemetry-ingestion \
  --source ../services/ingestion \
  --region us-central1 \
  --project industrial-cloud-data \
  --set-env-vars GCP_PROJECT_ID=industrial-cloud-data,GCP_BUCKET_NAME=telemetry-data007 \
  --no-allow-unauthenticated \
  --cpu 1 \
  --memory 512Mi \
  --min-instances 1 \
  --max-instances 5 \
  --timeout 3600

echo "✅ Ingestion Microservice deployed"
echo "📥 Service runs continuously, consuming from Pub/Sub and storing to GCS"
