# GitHub Actions CI/CD Pipeline - Setup Summary

## ✅ What's Been Created

### 1. Workflow Files (`.github/workflows/`)

#### `deploy.yml` - Main Deployment Workflow
- **Triggers:** Push to `main` or `develop` branches, or manual (`workflow_dispatch`)
- **Actions:**
  1. Authenticate with GCP using service account
  2. Deploy Dashboard Frontend (8000)
  3. Deploy Dashboard API (8080)
  4. Deploy Generator Service (8001)
  5. Deploy Ingestion Service (8002)
  6. Deploy Transformer Service (8003)
  7. Display deployed service URLs
- **Time:** ~5-10 minutes per deployment

#### `test.yml` - Quality Checks Workflow
- **Triggers:** Pull requests to `main` or `develop`, push to `develop` or feature branches
- **Checks:**
  - Pylint linting
  - Docker build validation for all services
  - Security scanning with Bandit
  - Dependency checking
  - Code format checking with Black

### 2. Documentation Files

#### `CICD_SETUP_GUIDE.md` (Full Guide)
Complete step-by-step setup instructions:
- Create GCP service account with proper permissions
- Add GitHub secrets (GCP_PROJECT_ID, GCP_SA_KEY)
- Optional database environment variables
- Testing the pipeline
- Troubleshooting guide
- Security best practices

#### `CICD_QUICK_REFERENCE.md` (Quick Start)
5-minute quick reference:
- One-command setup
- GitHub secrets addition
- Common commands
- Monitoring endpoints
- Quick troubleshooting table

#### `CICD_TROUBLESHOOTING.md` (Detailed Help)
Comprehensive troubleshooting:
- Authentication failures
- Deployment failures
- Environment variable issues
- Monitoring & debugging
- Workflow execution issues
- Cleanup procedures

### 3. Code Fixes

#### Fixed in `services/dashboard-frontend/main.py`
- Updated home route to pass `api_base_url` to template context
- Now uses `API_BASE_URL` environment variable (defaults to `http://dashboard-api:8080`)

#### Fixed in `services/dashboard-frontend/templates/index.html`
- Changed hardcoded `http://localhost:8080/docs` to dynamic `{{ api_base_url }}/docs`
- API docs link now works correctly in Cloud Run

#### Updated `README.md`
- Added CI/CD section
- Linked to setup guides
- Added deployment overview

---

## 🚀 Next Steps: Setup Instructions

### Step 1: Create GCP Service Account (5 mins)

```bash
# Set your project ID
export PROJECT_ID="industrial-cloud-data"

# Create service account
gcloud iam service-accounts create github-actions-runner \
  --display-name="GitHub Actions Runner for Cloud Run"

# Add Cloud Run admin role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/run.admin

# Add service account user role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/iam.serviceAccountUser

# Add Cloud Build role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/cloudbuild.builds.editor

# Create and export the key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com

# Display the key (copy this)
cat github-actions-key.json
```

### Step 2: Add GitHub Secrets (2 mins)

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add two secrets:

| Name | Value |
|------|-------|
| `GCP_PROJECT_ID` | `industrial-cloud-data` |
| `GCP_SA_KEY` | Entire contents of `github-actions-key.json` |

### Step 3: Clean Up & Test (1 min)

```bash
# Delete the local key file
rm github-actions-key.json

# Push the code to trigger deployment
git push origin main
```

### Step 4: Monitor Deployment

**GitHub Actions:**
```
https://github.com/YOUR_USERNAME/YOUR_REPO/actions
```

Click on the "Deploy to Cloud Run" workflow to see real-time progress.

**Cloud Run Services:**
```
https://console.cloud.google.com/run
```

View logs and service URLs.

---

## 📋 Workflow Triggers

The deployment automatically runs when:

| Event | Branch | Action |
|-------|--------|--------|
| Push | `main` | ✅ Deploy all services |
| Push | `develop` | ✅ Deploy all services |
| Pull Request | `main` | 🧪 Run tests only |
| Pull Request | `develop` | 🧪 Run tests only |
| Manual Trigger | Any | ✅ Deploy (use Actions tab) |

---

## 🔍 How It Works

```
You push code to GitHub
        ↓
GitHub Actions workflow triggers
        ↓
Checkout your code
        ↓
Authenticate with GCP using service account key
        ↓
Deploy each service to Cloud Run:
  ┌─ Dashboard Frontend (8000)
  ├─ Dashboard API (8080)
  ├─ Generator Service (8001)
  ├─ Ingestion Service (8002)
  └─ Transformer Service (8003)
        ↓
Display deployed URLs in workflow summary
        ↓
Done! ✅ Services live at https://...a.run.app
```

---

## 🔗 Deployed Service URLs

After deployment, you can access your services:

```bash
# Get all service URLs
gcloud run services list --region us-central1

# Or specific services:
gcloud run services describe dashboard-frontend --region us-central1 --format='value(status.url)'
gcloud run services describe dashboard-api --region us-central1 --format='value(status.url)'
```

Example URLs (actual values from your deployment):
- Frontend: `https://dashboard-frontend-abc123def456.a.run.app`
- API: `https://dashboard-api-xyz789uvw012.a.run.app`
- API Docs: `https://dashboard-api-xyz789uvw012.a.run.app/docs`

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [CICD_SETUP_GUIDE.md](./CICD_SETUP_GUIDE.md) | Complete setup with all details |
| [CICD_QUICK_REFERENCE.md](./CICD_QUICK_REFERENCE.md) | Quick commands & reference |
| [CICD_TROUBLESHOOTING.md](./CICD_TROUBLESHOOTING.md) | Solutions to common issues |
| [README.md](./README.md) | Project overview (updated) |

---

## ⚠️ Important Notes

### Security
✅ **Do:**
- Store credentials in GitHub Secrets only
- Rotate service account keys periodically
- Review workflow logs for errors
- Use minimal permissions (least privilege)

❌ **Don't:**
- Commit service account keys to GitHub
- Share secret values in issues/PRs
- Grant overly broad permissions
- Store credentials in `.env` or code

### Costs
- **Cloud Run:** Pay only for execution time (very cheap for these services)
- **Cloud Build:** Free tier includes 120 minutes/day
- **Cloud Storage:** Storage costs for telemetry data
- Monitor spending: `https://console.cloud.google.com/billing`

### Monitoring
```bash
# View recent deployments
gcloud run services describe dashboard-api --region us-central1

# Check service logs
gcloud run services logs read dashboard-api --region us-central1 --limit 50

# Monitor in real-time
gcloud run services logs read dashboard-api --region us-central1 --follow
```

---

## ✨ What's Next?

1. ✅ Service account created
2. ✅ GitHub secrets added
3. ✅ Workflow files in place
4. 🔄 **Push code to trigger deployment**
5. 📊 Monitor in GitHub Actions & Cloud Run
6. 🔧 Iterate and improve

---

## 🆘 Need Help?

1. **Setup issues?** → See [CICD_SETUP_GUIDE.md](./CICD_SETUP_GUIDE.md)
2. **Deployment failed?** → See [CICD_TROUBLESHOOTING.md](./CICD_TROUBLESHOOTING.md)
3. **Quick commands?** → See [CICD_QUICK_REFERENCE.md](./CICD_QUICK_REFERENCE.md)
4. **General info?** → See [README.md](./README.md#cloud-deployment)

---

## 📞 Common Commands

```bash
# Check service account permissions
gcloud projects get-iam-policy industrial-cloud-data \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:github-actions-runner@*"

# View deployment logs
gcloud run services logs read dashboard-frontend --region us-central1 --limit 100

# Manual deployment (if needed)
gcloud run deploy dashboard-api --source services/dashboard-api --region us-central1

# Check deployed services
gcloud run services list --region us-central1 --format='table(name,status.url)'

# Delete a service
gcloud run services delete SERVICE_NAME --region us-central1 --quiet
```

---

**Ready to deploy? Start with Step 1 above, then push your code!** 🚀
