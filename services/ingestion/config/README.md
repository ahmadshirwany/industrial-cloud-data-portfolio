# Ingestion Service Configuration

## Service Account

Place your ingestion service account key here:
- `service-account.json`

## Permissions Required

This service account needs:
- `roles/pubsub.subscriber` - To consume from Pub/Sub topics
- `roles/pubsub.admin` - To create subscriptions (if auto-creating)
- `roles/storage.objectAdmin` - To write to Cloud Storage bucket

## Example Setup

```bash
# Create service account
gcloud iam service-accounts create telemetry-ingestion \
  --display-name "Telemetry Ingestion Service"

# Grant Pub/Sub permissions
gcloud projects add-iam-policy-binding industrial-cloud-data \
  --member="serviceAccount:telemetry-ingestion@industrial-cloud-data.iam.gserviceaccount.com" \
  --role="roles/pubsub.subscriber"

# Grant Storage permissions
gcloud storage buckets add-iam-policy-binding gs://telemetry-data007 \
  --member="serviceAccount:telemetry-ingestion@industrial-cloud-data.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Create key
gcloud iam service-accounts keys create service-account.json \
  --iam-account=telemetry-ingestion@industrial-cloud-data.iam.gserviceaccount.com
```
