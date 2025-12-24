# CI/CD Pipeline Visual Guide

## File Structure

```
.github/
└── workflows/
    ├── deploy.yml          # Main deployment to Cloud Run
    └── test.yml            # Code quality & testing

services/
├── dashboard-frontend/
│   ├── main.py            # ✅ UPDATED: now passes api_base_url
│   └── templates/
│       └── index.html      # ✅ UPDATED: uses dynamic API URL
├── dashboard-api/
├── generator/
├── ingestion/
└── transformer/

Documentation (NEW):
├── CICD_SETUP_GUIDE.md              # 📘 Full setup instructions
├── CICD_QUICK_REFERENCE.md          # 📋 Quick commands
├── CICD_TROUBLESHOOTING.md          # 🆘 Common issues & fixes
├── CICD_IMPLEMENTATION_SUMMARY.md   # 📋 This file
└── README.md                         # ✅ UPDATED: added CI/CD info
```

## Deployment Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      YOU PUSH CODE TO GITHUB                        │
│                  (git push origin main/develop)                     │
└─────────────┬───────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│         GITHUB ACTIONS WORKFLOW TRIGGERS                            │
│         (.github/workflows/deploy.yml)                              │
└─────────────┬───────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 1: CHECKOUT CODE                                              │
│  - Pull your code from GitHub                                       │
└─────────────┬───────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 2: AUTHENTICATE WITH GCP                                      │
│  - Use service account key from GitHub Secrets                      │
│  - Get credentials for Cloud Run deployment                         │
└─────────────┬───────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 3: DEPLOY SERVICES (Sequential)                               │
│                                                                      │
│  ┌──────────────────────────────────────────────────────┐          │
│  │ 1. Dashboard Frontend (Port 8000)                    │          │
│  │    - Build Docker image                              │          │
│  │    - Push to Cloud Run                               │          │
│  │    - Set API_BASE_URL env var                        │          │
│  └──────────────────────────────────────────────────────┘          │
│                     ↓                                                │
│  ┌──────────────────────────────────────────────────────┐          │
│  │ 2. Dashboard API (Port 8080)                         │          │
│  │    - Build Docker image                              │          │
│  │    - Push to Cloud Run                               │          │
│  └──────────────────────────────────────────────────────┘          │
│                     ↓                                                │
│  ┌──────────────────────────────────────────────────────┐          │
│  │ 3. Generator Service (Port 8001)                     │          │
│  │    - Build Docker image                              │          │
│  │    - Push to Cloud Run                               │          │
│  └──────────────────────────────────────────────────────┘          │
│                     ↓                                                │
│  ┌──────────────────────────────────────────────────────┐          │
│  │ 4. Ingestion Service (Port 8002)                     │          │
│  │    - Build Docker image                              │          │
│  │    - Push to Cloud Run                               │          │
│  └──────────────────────────────────────────────────────┘          │
│                     ↓                                                │
│  ┌──────────────────────────────────────────────────────┐          │
│  │ 5. Transformer Service (Port 8003)                   │          │
│  │    - Build Docker image                              │          │
│  │    - Push to Cloud Run                               │          │
│  └──────────────────────────────────────────────────────┘          │
└─────────────┬───────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 4: DISPLAY RESULTS                                            │
│  - Frontend URL: https://dashboard-frontend-xxx.a.run.app           │
│  - API URL: https://dashboard-api-xxx.a.run.app                    │
│  - API Docs: https://dashboard-api-xxx.a.run.app/docs             │
└─────────────┬───────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ✅ DEPLOYMENT COMPLETE!                                             │
│  Services are live and accessible at their URLs                     │
└─────────────────────────────────────────────────────────────────────┘
```

## GitHub Secrets Setup

```
GitHub Repository
└── Settings
    └── Secrets and variables
        └── Actions
            ├── GCP_PROJECT_ID
            │   └── Value: industrial-cloud-data
            │
            └── GCP_SA_KEY
                └── Value: {
                      "type": "service_account",
                      "project_id": "industrial-cloud-data",
                      "private_key_id": "...",
                      "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
                      "client_email": "github-actions-runner@industrial-cloud-data.iam.gserviceaccount.com",
                      ...
                    }
```

## Workflow File Locations

### Main Deployment Workflow
```
.github/workflows/deploy.yml
│
├─ Trigger: push to main or develop
├─ Trigger: manual (workflow_dispatch)
│
├─ Job: Deploy 5 services to Cloud Run
│   ├─ Dashboard Frontend
│   ├─ Dashboard API
│   ├─ Generator Service
│   ├─ Ingestion Service
│   └─ Transformer Service
│
└─ Output: Service URLs in workflow summary
```

### Testing/Quality Workflow
```
.github/workflows/test.yml
│
├─ Trigger: pull request to main/develop
├─ Trigger: push to develop or feature branches
│
├─ Job 1: Lint with Pylint
├─ Job 2: Test Docker builds
├─ Job 3: Security checks with Bandit
├─ Job 4: Check dependencies
└─ Job 5: Code format check with Black
```

## Deployment Checklist

### Before First Deployment

- [ ] GCP project created and Cloud Run API enabled
- [ ] Service account created with proper roles
- [ ] Service account key file downloaded
- [ ] GitHub Secrets added (GCP_PROJECT_ID, GCP_SA_KEY)
- [ ] Service account key file deleted locally
- [ ] Workflow files in `.github/workflows/` directory
- [ ] Code changes committed to main/develop branch

### During Deployment

- [ ] Watch GitHub Actions workflow run
- [ ] Check each service deployment step
- [ ] Verify no authentication errors
- [ ] Monitor Cloud Build logs if needed

### After Deployment

- [ ] Verify all 5 services are running
- [ ] Test Frontend URL in browser
- [ ] Check API Docs at API URL + /docs
- [ ] Test health endpoints
- [ ] Monitor logs for errors

## Monitoring & Debugging

### GitHub Actions

```
Repository → Actions tab → Deploy to Cloud Run
├─ Click workflow run to see details
├─ Expand each step to see logs
├─ Check for red X (failed) steps
└─ Copy error messages for troubleshooting
```

### Cloud Run Console

```
https://console.cloud.google.com/run
├─ View service list
├─ Check service health
├─ View logs
├─ Monitor traffic
└─ Check metrics (CPU, memory, latency)
```

### Command Line

```bash
# Check service status
gcloud run services describe SERVICE_NAME --region us-central1

# View logs
gcloud run services logs read SERVICE_NAME --region us-central1 --limit 50

# List all services
gcloud run services list --region us-central1
```

## Common Scenarios

### ✅ Successful Deployment

```
✓ Checkout code
✓ Authenticate with GCP
✓ Deploy dashboard-frontend
✓ Deploy dashboard-api
✓ Deploy telemetry-generator
✓ Deploy telemetry-ingestion
✓ Deploy telemetry-transformer
✓ Get deployed service URLs

Result: Green checkmark ✅ All services running
```

### ❌ Failed Deployment

```
✓ Checkout code
✓ Authenticate with GCP
✓ Deploy dashboard-frontend
✓ Deploy dashboard-api
✗ Deploy telemetry-generator
  ERROR: (gcloud.run.deploy) ...

Result: Red X ❌ Check error message
         See CICD_TROUBLESHOOTING.md
```

### 🧪 Test-Only Run (Pull Request)

```
✓ Checkout code
✓ Lint with Pylint
✓ Test Docker builds
✓ Security checks
✓ Check dependencies
✓ Format checks

Result: Tests pass, ready for merge
        (No services deployed)
```

## Cost Estimation

### Cloud Run Pricing

| Component | Cost | Monthly |
|-----------|------|---------|
| 2M invocations/month | $0.24 | ~$0.50 |
| 500 GB-seconds | $0.20 | ~$0.20 |
| Outbound data | Varies | $0.01-$1.00 |
| **Total** | | **~$0.71-$1.71** |

*Note: Actual costs depend on traffic and service configuration*

### How to Minimize Costs

1. Set `--min-instances 0` (auto-scales to zero when idle)
2. Limit `--max-instances` to prevent runaway costs
3. Monitor logs for errors (troubleshoot quickly)
4. Delete unused services
5. Set up billing alerts in GCP Console

## Security Architecture

```
GitHub Repository
└── (Your code, public)

GitHub Secrets (Encrypted)
├── GCP_PROJECT_ID (public, harmless)
└── GCP_SA_KEY (private, encrypted)

GitHub Actions Runner
└── Decrypts secrets at runtime
    └── Uses only for CI/CD job
        └── Never exposed in logs

GCP Service Account
├── Limited permissions (Cloud Run only)
├── No human access
├── Keys rotated periodically
└── Audited in Cloud Audit Logs
```

## File Permissions

| Role | What They Can Do | How They Get It |
|------|------------------|-----------------|
| Service Account | Deploy to Cloud Run | Roles: run.admin, iam.serviceAccountUser, cloudbuild.builds.editor |
| GitHub Actions | Use secrets at runtime | Workflow file references secrets |
| You (Developer) | Trigger deployments | Push code to main/develop |

## Environment Variables Flow

```
GCP Service Account
└── Authenticates with Cloud Run API

Workflow (deploy.yml)
├── Sets GCP_PROJECT_ID from secret
├── Sets GCP_REGION = us-central1
│
├─ For Dashboard Frontend:
│  └── API_BASE_URL = <auto-detected dashboard-api URL>
│
├─ For Dashboard API:
│  └── (no special env vars)
│
└─ For Services (Generator, Ingestion, Transformer):
    └── GCP_PROJECT_ID, GCP_BUCKET_NAME, etc.
```

## Next Steps

1. **Right now:**
   - Read CICD_SETUP_GUIDE.md
   - Create GCP service account
   - Add GitHub secrets

2. **After setup:**
   - Push code to GitHub
   - Watch workflow run
   - Test deployed services

3. **Ongoing:**
   - Monitor logs
   - Iterate on code
   - Deployments happen automatically

---

**Ready to set up CI/CD? Start with CICD_SETUP_GUIDE.md** 🚀
