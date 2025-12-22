# Transformer Service Configuration

## Service Account

Place your transformer service account key here:
- `service-account.json`

## Permissions Required

This service account needs:
- `roles/storage.objectViewer` - To read from Cloud Storage bucket
- `roles/cloudsql.client` - To connect to Cloud SQL PostgreSQL

## Cloud SQL Connection

This service connects to PostgreSQL using:
- **Public IP**: Set DB_HOST to Cloud SQL public IP
- **Private IP** (recommended): Use Cloud SQL Proxy or Private IP
- **Cloud SQL Connector**: Recommended for production

## Example Setup

```bash
# Create service account
gcloud iam service-accounts create telemetry-transformer \
  --display-name "Telemetry Transformer Service"

# Grant Storage permissions
gcloud storage buckets add-iam-policy-binding gs://telemetry-data007 \
  --member="serviceAccount:telemetry-transformer@industrial-cloud-data.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# Grant Cloud SQL client permissions
gcloud projects add-iam-policy-binding industrial-cloud-data \
  --member="serviceAccount:telemetry-transformer@industrial-cloud-data.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# Create key
gcloud iam service-accounts keys create service-account.json \
  --iam-account=telemetry-transformer@industrial-cloud-data.iam.gserviceaccount.com
```

## Environment Variables

Required:
- `GCP_PROJECT_ID` - GCP project ID
- `GCP_BUCKET_NAME` - Cloud Storage bucket name
- `DB_HOST` - PostgreSQL host (Cloud SQL instance connection)
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_PORT` - Database port (default: 5432)
