# CI/CD Quick Reference

## Quick Setup (5 minutes)

### 1. Create GCP Service Account
```bash
export PROJECT_ID="industrial-cloud-data"

gcloud iam service-accounts create github-actions-runner \
  --display-name="GitHub Actions Runner"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/run.admin

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/iam.serviceAccountUser

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/cloudbuild.builds.editor

gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com
```

### 2. Add GitHub Secrets
1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Add `GCP_PROJECT_ID` = your project ID
3. Add `GCP_SA_KEY` = contents of `github-actions-key.json`

### 3. Clean Up
```bash
rm github-actions-key.json
```

### 4. Deploy
```bash
git add .
git commit -m "Add CI/CD pipeline"
git push origin main
```

## Workflow Files

| File | Purpose | Trigger |
|------|---------|---------|
| `.github/workflows/deploy.yml` | Deploy to Cloud Run | Push to main/develop |
| `.github/workflows/test.yml` | Run tests & checks | PR to main/develop |

## Monitor Deployments

```bash
# View Cloud Run services
gcloud run services list --region us-central1

# View logs for a service
gcloud run services logs read dashboard-frontend --region us-central1 --limit 50

# Manual deployment (if needed)
gcloud run deploy SERVICE_NAME --source services/SERVICE_NAME --region us-central1
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| Permission denied | Add roles to service account (see full guide) |
| Invalid key | Recreate `github-actions-key.json` and update secret |
| API not enabled | Run `gcloud services enable run.googleapis.com` |
| Build fails | Check Docker file and requirements.txt |

## Common Commands

```bash
# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:github-actions-runner@*"

# Rotate service account key
gcloud iam service-accounts keys list \
  --iam-account=github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com

gcloud iam service-accounts keys delete <KEY_ID> \
  --iam-account=github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com

# Enable Cloud Run API
gcloud services enable run.googleapis.com
```

## Workflow Status

- **GitHub Actions**: https://github.com/YOUR_USERNAME/YOUR_REPO/actions
- **Cloud Run Console**: https://console.cloud.google.com/run
- **Cloud Build**: https://console.cloud.google.com/cloud-build

## See Also

- [CICD_SETUP_GUIDE.md](./CICD_SETUP_GUIDE.md) - Full setup instructions
- [README.md](./README.md) - Project overview
- [GitHub Actions Docs](https://docs.github.com/en/actions)
