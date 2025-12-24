# CI/CD Troubleshooting Guide

## Common Issues and Solutions

### 1. Authentication Failures

#### Issue: "Invalid service account key"
**Symptoms:** 
- Workflow fails immediately with authentication error
- Message: "The provided JSON is invalid"

**Solution:**
1. Verify the entire JSON key was copied to the secret:
   ```bash
   # Check key file locally
   cat github-actions-key.json
   ```
2. The secret should contain the complete JSON (including `{` and `}`)
3. Recreate and update the secret:
   ```bash
   gcloud iam service-accounts keys create github-actions-key.json \
     --iam-account=github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com
   # Copy entire contents to GitHub secret GCP_SA_KEY
   ```

#### Issue: "Permission denied" error
**Symptoms:**
- Error: `PERMISSION_DENIED`
- Message about `cloudbuild.builds` or `run.admin`

**Solution:**
Ensure service account has all required roles:
```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/run.admin

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/iam.serviceAccountUser

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/cloudbuild.builds.editor
```

Verify with:
```bash
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:github-actions-runner@*"
```

---

### 2. Deployment Failures

#### Issue: "Cloud Run API not enabled"
**Symptoms:**
- Error: `API "run.googleapis.com" not enabled on project`

**Solution:**
```bash
gcloud services enable run.googleapis.com --project=$PROJECT_ID
```

#### Issue: "Service not found" or "Build failed"
**Symptoms:**
- Error during deployment step
- Message: `FAILED_PRECONDITION` or `BUILD_FAILURE`

**Solution:**
1. Check the Dockerfile exists:
   ```bash
   # Should exist at:
   # services/SERVICE_NAME/Dockerfile
   ls services/dashboard-frontend/Dockerfile
   ```

2. Verify Dockerfile is valid:
   ```bash
   # Test local build
   docker build -f services/dashboard-frontend/Dockerfile .
   ```

3. Check requirements.txt:
   ```bash
   # Verify all packages are installable
   pip install -r services/dashboard-frontend/requirements.txt
   ```

4. View detailed logs in GitHub Actions:
   - Go to workflow run → Click failed step
   - Scroll to see full error output

#### Issue: "Port conflict" or "Service already exists"
**Symptoms:**
- Error: `Port 8080 is already in use`
- Dashboard frontend not deployed

**Solution:**
This is usually not an issue with Cloud Run (ports are isolated), but if you see binding errors:
1. Wait a few minutes (services might be cleaning up)
2. Manually delete the service:
   ```bash
   gcloud run services delete SERVICE_NAME --region us-central1 --quiet
   ```
3. Retry the workflow or push again

---

### 3. Environment Variable Issues

#### Issue: "API_BASE_URL not set correctly"
**Symptoms:**
- Frontend shows "localhost" URLs instead of GCP URL
- API calls fail with CORS errors

**Solution:**
The workflow tries to auto-detect the API URL. If it fails:
1. Manually update the frontend after API deploys:
   ```bash
   # Get the API URL
   gcloud run services describe dashboard-api --region us-central1 --format='value(status.url)'
   
   # Update frontend with it
   gcloud run deploy dashboard-frontend \
     --update-env-vars API_BASE_URL=https://dashboard-api-xxx.a.run.app \
     --region us-central1
   ```

2. Or update the workflow to set it manually in `.github/workflows/deploy.yml`:
   ```yaml
   - name: Deploy Dashboard Frontend
     env:
      API_URL: "https://dashboard-api-esne4epeha-uc.a.run.app"
     run: |
       gcloud run deploy dashboard-frontend \
         ...
         --set-env-vars API_BASE_URL=${{ env.API_URL }} \
   ```

#### Issue: Database credentials not working
**Symptoms:**
- Transformer service fails to connect
- Error: `could not connect to database`

**Solution:**
1. Add database secrets to GitHub:
   - Settings → Secrets → Actions
   - Add: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

2. Update the workflow to use them:
   ```yaml
   - name: Deploy Transformer Service
     run: |
       gcloud run deploy telemetry-transformer \
         ...
         --set-env-vars DB_HOST=${{ secrets.DB_HOST }},DB_NAME=${{ secrets.DB_NAME }},DB_USER=${{ secrets.DB_USER }} \
         --set-secrets DB_PASSWORD=db-password:latest
   ```

3. Create the secret in Secret Manager:
   ```bash
   echo -n "$DB_PASSWORD" | gcloud secrets create db-password --data-file=-
   ```

---

### 4. Monitoring & Debugging

#### View workflow logs:
```
GitHub → Actions → Deploy to Cloud Run → [Click the run] → [Click step name]
```

#### View Cloud Run logs:
```bash
# Get logs for a specific service
gcloud run services logs read dashboard-frontend --region us-central1 --limit 100

# Follow logs in real-time
gcloud run services logs read dashboard-frontend --region us-central1 --limit 50 --follow

# Filter by severity
gcloud run services logs read dashboard-frontend --region us-central1 \
  --filter="severity>=ERROR"

# View revision details
gcloud run services describe dashboard-frontend --region us-central1
```

#### Manually test the deployment:
```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe dashboard-frontend --region us-central1 --format='value(status.url)')

# Test connectivity
curl -v $SERVICE_URL

# Check health
curl $SERVICE_URL/health

# Check API docs
curl ${API_URL}/docs
```

---

### 5. Workflow Execution Issues

#### Issue: "Workflow not triggering"
**Symptoms:**
- Pushed code but no workflow runs
- No activity in Actions tab

**Solution:**
1. Check branch name:
   - Workflow triggers on `main` and `develop` branches
   - For other branches, use manual trigger: `workflow_dispatch`

2. Check workflow file syntax:
   ```bash
   # Install actionlint locally
   brew install actionlint  # macOS
   # or: https://github.com/rhysd/actionlint/releases
   
   # Validate workflow
   actionlint .github/workflows/deploy.yml
   ```

3. Force re-run workflow:
   - GitHub → Actions → [Latest run] → Re-run jobs

#### Issue: "Jobs running sequentially instead of in parallel"
**Symptoms:**
- Deployment takes 30+ minutes
- Services deploy one at a time

**Note:** The current workflow design deploys services sequentially by design for stability. To parallelize:

Update `.github/workflows/deploy.yml`:
```yaml
jobs:
  deploy-services:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service:
          - name: dashboard-frontend
            port: 8000
            allow_unauth: true
          # ... add all services here
```

---

### 6. Cleanup & Reset

#### Remove a service from Cloud Run:
```bash
gcloud run services delete SERVICE_NAME --region us-central1 --quiet
```

#### Reset deployment (start fresh):
```bash
# Delete all services
gcloud run services delete dashboard-frontend --region us-central1 --quiet
gcloud run services delete dashboard-api --region us-central1 --quiet
gcloud run services delete telemetry-generator --region us-central1 --quiet
gcloud run services delete telemetry-ingestion --region us-central1 --quiet
gcloud run services delete telemetry-transformer --region us-central1 --quiet

# Delete and recreate service account
gcloud iam service-accounts delete github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com --quiet
# Then follow setup guide again
```

#### Rotate service account key:
```bash
# List existing keys
gcloud iam service-accounts keys list \
  --iam-account=github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com

# Delete old key
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com

# Create new key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions-runner@$PROJECT_ID.iam.gserviceaccount.com

# Update GitHub secret GCP_SA_KEY with new contents
```

---

## Getting Help

1. **Check GitHub Actions logs** - Most detailed error messages
2. **Check Cloud Run logs** - Service-specific errors
3. **Enable debug logging** - Add to workflow:
   ```yaml
   - name: Enable debug logging
     run: gcloud config set compute/region us-central1 --verbosity=debug
   ```
4. **Test locally** - Run gcloud commands manually to debug
5. **Check GCP Console** - Cloud Run, Cloud Build, Logs

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Google Cloud IAM Roles](https://cloud.google.com/iam/docs)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
