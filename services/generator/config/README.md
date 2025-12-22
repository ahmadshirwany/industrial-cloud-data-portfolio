# Generator Service Configuration

## Service Account

Place your generator service account key here:
- `service-account.json`

## Permissions Required

This service account needs:
- `roles/pubsub.publisher` - To publish metrics to Pub/Sub topics
- `roles/pubsub.admin` - To create topics (if auto-creating)

## Example Setup

```bash
# Create service account
gcloud iam service-accounts create telemetry-generator \
  --display-name "Telemetry Generator Service"

# Grant permissions
gcloud projects add-iam-policy-binding industrial-cloud-data \
  --member="serviceAccount:telemetry-generator@industrial-cloud-data.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"

# Create key
gcloud iam service-accounts keys create service-account.json \
  --iam-account=telemetry-generator@industrial-cloud-data.iam.gserviceaccount.com
```
