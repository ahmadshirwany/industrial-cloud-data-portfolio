#!/bin/bash
# Deploy Generator Microservice to Cloud Run

echo "🚀 Deploying Generator Microservice to Cloud Run..."

gcloud run deploy telemetry-generator \
  --source ../services/generator \
  --region us-central1 \
  --project industrial-cloud-data \
  --set-env-vars GCP_PROJECT_ID=industrial-cloud-data \
  --no-allow-unauthenticated \
  --cpu 1 \
  --memory 512Mi \
  --min-instances 1 \
  --max-instances 3 \
  --timeout 3600

echo "✅ Generator Microservice deployed"
echo "📡 Service runs continuously, publishing metrics every 5 seconds"
