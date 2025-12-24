# GitHub Actions CI/CD Pipeline Setup Guide

This guide walks you through setting up automatic deployment to Google Cloud Run whenever you push code to GitHub.

## Overview

The CI/CD pipeline automatically deploys all microservices to Cloud Run when you push to `main` or `develop` branches.

**What gets deployed:**
- Dashboard Frontend (8000)
- Dashboard API (8080)
- Telemetry Generator (8001)
- Telemetry Ingestion (8002)
- Telemetry Transformer (8003)

## Prerequisites

1. GitHub repository with this code
2. Google Cloud Project (GCP) with billing enabled
3. Cloud Run API enabled in GCP
4. `gcloud` CLI installed locally

## Step 1: Create a GCP Service Account

A service account allows GitHub Actions to authenticate with GCP.

### 1.1 Create the service account

```bash
# Set your project ID
export PROJECT_ID="industrial-cloud-data"

# Create service account
gcloud iam service-accounts create github-actions-runner \
  --display-name="GitHub Actions Runner for Cloud Run Deployment" \
  --project=$PROJECT_ID
```

### 1.2 Grant required permissions

```bash
# Grant Cloud Run deployment permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/run.admin

# Grant Service Account User permission
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/iam.serviceAccountUser

# Grant Cloud Build permission (for source builds)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/cloudbuild.builds.editor
```

### 1.3 Create and export the service account key

```bash
# Create key file
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com

# Display the key (you'll paste this into GitHub)
cat github-actions-key.json
```

**Important:** This JSON file contains sensitive credentials. Keep it secure and delete it after adding to GitHub Secrets.

## Step 2: Add GitHub Secrets

GitHub Secrets allow you to safely store sensitive information used by the workflow.

### 2.1 Add GCP_PROJECT_ID

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `GCP_PROJECT_ID`
5. Value: `industrial-cloud-data` (or your actual project ID)

### 2.2 Add GCP_SA_KEY

1. Click "New repository secret"
2. Name: `GCP_SA_KEY`
3. Value: Paste the entire contents of `github-actions-key.json`

**Screenshot example:**
```
Settings → Secrets and variables → Actions

┌─────────────────────────────────┐
│ Repository secrets              │
├─────────────────────────────────┤
│ GCP_PROJECT_ID: industrial-... │
│ GCP_SA_KEY: (JSON key file)    │
└─────────────────────────────────┘
```

## Step 3: Optional - Add Database Environment Variables

If your transformer service needs database access, add these secrets:

```
DB_HOST          → Cloud SQL instance IP
DB_NAME          → postgres
DB_USER          → postgres
DB_PASSWORD      → your secure password
```

Then update `.github/workflows/deploy.yml` to use them for the transformer:

```yaml
- name: Deploy Transformer Service
  env:
    DB_HOST: ${{ secrets.DB_HOST }}
    DB_NAME: ${{ secrets.DB_NAME }}
    DB_USER: ${{ secrets.DB_USER }}
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
  run: |
    gcloud run deploy telemetry-transformer \
      --source services/transformer \
      --region us-central1 \
      --project ${{ env.GCP_PROJECT_ID }} \
      --port 8000 \
      --no-allow-unauthenticated \
      --cpu 1 \
      --memory 512Mi \
      --set-env-vars DB_HOST=${{ env.DB_HOST }},DB_NAME=${{ env.DB_NAME }},DB_USER=${{ env.DB_USER }} \
      --set-secrets DB_PASSWORD=${{ env.DB_PASSWORD }} \
      ...
```

## Step 4: Clean Up Locally

After adding secrets to GitHub, delete the local key file:

```bash
rm github-actions-key.json
```

## Step 5: Test the Pipeline

### 5.1 Push to GitHub

```bash
git add .
git commit -m "feat: add GitHub Actions CI/CD pipeline"
git push origin main
```

### 5.2 Monitor the workflow

1. Go to your GitHub repository
2. Click "Actions" tab
3. Watch the "Deploy to Cloud Run" workflow run
4. Check logs if any step fails

## How It Works

```
You push code to GitHub
         ↓
GitHub Actions workflow triggers (on main/develop)
         ↓
Checkout code
         ↓
Authenticate with GCP using service account key
         ↓
Deploy each service to Cloud Run in sequence:
  1. Dashboard Frontend
  2. Dashboard API
  3. Generator Service
  4. Ingestion Service
  5. Transformer Service
         ↓
Print deployed service URLs
         ↓
Done! ✅
```

## Workflow Files

- **`.github/workflows/deploy.yml`** - Main deployment workflow (triggered on push)
- **`.github/workflows/test.yml`** - Optional testing workflow (see below)

## Optional: Add Testing Workflow

Create `.github/workflows/test.yml` to run tests before deployment:

```yaml
name: Tests

on:
  pull_request:
    branches:
      - main
      - develop

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11']

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest tests/ -v --cov=services/
```

Then tests will run on pull requests, and deployment only happens after merge.

## Troubleshooting

### Issue: "Permission denied" error

**Solution:** Ensure the service account has these roles:
- `roles/run.admin`
- `roles/iam.serviceAccountUser`
- `roles/cloudbuild.builds.editor`

Check with:
```bash
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:github-actions-runner@*"
```

### Issue: "Service account key is invalid"

**Solution:** 
1. Check that you copied the entire JSON file into the secret
2. Recreate the key:
   ```bash
   gcloud iam service-accounts keys delete <KEY_ID> \
     --iam-account=github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com
   
   gcloud iam service-accounts keys create github-actions-key.json \
     --iam-account=github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com
   ```

### Issue: "Cloud Run API not enabled"

**Solution:**
```bash
gcloud services enable run.googleapis.com --project=$PROJECT_ID
```

### Issue: Deployment fails for specific service

Check the workflow logs:
1. Go to Actions → Deploy to Cloud Run → Click the failed run
2. Expand the failed step to see the error
3. Common issues:
   - Missing Dockerfile
   - Invalid environment variables
   - Cloud SQL connection issues (for transformer)

## Monitoring & Logs

### View workflow history:
```
GitHub → Actions → Deploy to Cloud Run
```

### View Cloud Run deployment logs:
```bash
gcloud run services describe SERVICE_NAME --region us-central1
gcloud run services logs read SERVICE_NAME --region us-central1 --limit 50
```

## Security Best Practices

✅ **Do:**
- Store sensitive data in GitHub Secrets
- Use service accounts with minimal permissions
- Rotate service account keys periodically
- Review workflow logs for errors
- Restrict branch deployments (currently main + develop)

❌ **Don't:**
- Commit service account keys to GitHub
- Store credentials in code or `.env` files
- Grant service account overly broad permissions
- Share secret values in issues/discussions

## Next Steps

1. ✅ Service account created and configured
2. ✅ GitHub Secrets added
3. ✅ Workflow file in place
4. 🔄 Push code and trigger deployment
5. 📊 Monitor Cloud Run services
6. 🔄 Iterate and improve workflow

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Cloud Run Deployment](https://cloud.google.com/run/docs/quickstarts/deploy)
- [Google Cloud IAM Roles](https://cloud.google.com/iam/docs/understanding-custom-roles)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference)
