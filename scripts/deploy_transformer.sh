#!/bin/bash
# Deploy Transformer Service to Cloud Run

set -e

echo "Deploying Transformer Service to Cloud Run..."

# Configuration
PROJECT_ID="industrial-cloud-data"
SERVICE_NAME="telemetry-transformer"
REGION="us-central1"
BUCKET_NAME="telemetry-data007"

# Check required environment variables
if [ -z "$DB_HOST" ] || [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
    echo "Error: Missing required database environment variables"
    echo "Please set: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD"
    exit 1
fi

# Build and push container
echo "Building container image..."
gcloud builds submit \
    --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
    --project ${PROJECT_ID} \
    --gcs-log-dir gs://${BUCKET_NAME}/build-logs

# Deploy to Cloud Run with Cloud SQL connection
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --no-allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 3600 \
    --min-instances 1 \
    --max-instances 1 \
    --set-env-vars GCP_PROJECT_ID=${PROJECT_ID},GCP_BUCKET_NAME=${BUCKET_NAME},DB_NAME=${DB_NAME},DB_USER=${DB_USER},DB_PORT=5432 \
    --set-secrets DB_PASSWORD=db-password:latest \
    --add-cloudsql-instances ${PROJECT_ID}:${REGION}:telemetry-db \
    --service-account telemetry-transformer@${PROJECT_ID}.iam.gserviceaccount.com

echo "Transformer service deployed successfully!"
echo "Note: Make sure to create secret 'db-password' in Secret Manager"
echo "  gcloud secrets create db-password --data-file=- <<< '\$DB_PASSWORD'"
