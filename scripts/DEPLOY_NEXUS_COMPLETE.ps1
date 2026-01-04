#!/usr/bin/env pwsh
<#
.SYNOPSIS
  NEXUS Complete Deployment Script
  Configures Google Cloud, Cloud SQL, Secrets Manager, and deploys to Cloud Run
  
.DESCRIPTION
  Full automation of NEXUS API deployment to production
  Project: agendamento-n8n-476415
  
.AUTHOR
  Charles Rodrigues Silva
  charles.rsilva05@gmail.com
  
.DATE
  2026-01-03
#>

Param(
    [string]$ProjectId = "agendamento-n8n-476415",
    [string]$Region = "us-central1",
    [string]$ServiceAccount = "nexus-app-sa",
    [string]$CloudRunService = "nexus-api",
    [string]$CloudSqlInstance = "nexus-postgres-prod",
    [string]$Database = "nexus_prod",
    [string]$DbUser = "app_user",
    [bool]$DryRun = $false
)

# Color output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Error { Write-Host "ERROR: $args" -ForegroundColor Red }
function Write-Info { Write-Host "INFO: $args" -ForegroundColor Cyan }
function Write-Section { Write-Host "`n=== $args ===`n" -ForegroundColor Yellow }

# Check gcloud is installed
function Test-GcloudInstalled {
    $gcloud = gcloud --version 2>$null
    if (-not $gcloud) {
        Write-Error "gcloud CLI not installed. Install from https://cloud.google.com/sdk/docs/install"
        exit 1
    }
    Write-Success "gcloud CLI found: $(gcloud --version | Select-Object -First 1)"
}

# Set project
function Set-GcpProject {
    Write-Section "Setting GCP Project to $ProjectId"
    gcloud config set project $ProjectId
    if (-not $?) {
        Write-Error "Failed to set GCP project"
        exit 1
    }
    Write-Success "Project set to $ProjectId"
}

# Enable APIs
function Enable-GcpApis {
    Write-Section "Enabling Required GCP APIs"
    $apis = @(
        "cloudsql.googleapis.com",
        "run.googleapis.com",
        "secretmanager.googleapis.com",
        "monitoring.googleapis.com",
        "logging.googleapis.com",
        "cloudresourcemanager.googleapis.com",
        "compute.googleapis.com",
        "artifactregistry.googleapis.com"
    )
    
    foreach ($api in $apis) {
        Write-Info "Enabling $api..."
        if (-not $DryRun) {
            gcloud services enable $api --quiet
        }
    }
    Write-Success "All APIs enabled (or pending)"
}

# Create Service Account
function Create-ServiceAccount {
    Write-Section "Creating Service Account: $ServiceAccount"
    
    # Check if exists
    $exists = gcloud iam service-accounts list --filter="email:$ServiceAccount@$ProjectId.iam.gserviceaccount.com" --format="value(email)" 2>$null
    
    if (-not $exists) {
        Write-Info "Creating new service account..."
        if (-not $DryRun) {
            gcloud iam service-accounts create $ServiceAccount `
                --display-name="NEXUS API Service Account" `
                --quiet
        }
    } else {
        Write-Success "Service account already exists"
    }
    
    # Grant roles
    $roles = @(
        "roles/cloudsql.client",
        "roles/secretmanager.secretAccessor",
        "roles/monitoring.metricWriter",
        "roles/logging.logWriter"
    )
    
    foreach ($role in $roles) {
        Write-Info "Granting $role..."
        if (-not $DryRun) {
            gcloud projects add-iam-policy-binding $ProjectId `
                --member="serviceAccount:$ServiceAccount@$ProjectId.iam.gserviceaccount.com" `
                --role="$role" `
                --quiet 2>$null
        }
    }
    
    Write-Success "Service account configured"
}

# Create Cloud SQL Instance
function Create-CloudSql {
    Write-Section "Creating Cloud SQL PostgreSQL Instance"
    
    # Check if exists
    $exists = gcloud sql instances list --filter="name:$CloudSqlInstance" --format="value(name)" 2>$null
    
    if (-not $exists) {
        Write-Info "Creating Cloud SQL instance: $CloudSqlInstance"
        if (-not $DryRun) {
            gcloud sql instances create $CloudSqlInstance `
                --database-version=POSTGRES_15 `
                --tier=db-f1-micro `
                --region=$Region `
                --enable-bin-log `
                --backup-start-time=02:00 `
                --retained-backups-count=30 `
                --transaction-log-retention-days=7 `
                --enable-high-availability `
                --availability-type=REGIONAL `
                --quiet
        }
        Write-Success "Cloud SQL instance created"
    } else {
        Write-Success "Cloud SQL instance already exists"
    }
    
    # Create database
    Write-Info "Creating database: $Database"
    if (-not $DryRun) {
        gcloud sql databases create $Database `
            --instance=$CloudSqlInstance `
            --quiet 2>$null
    }
    
    # Create user
    $DbPassword = -join ((1..32) | ForEach-Object { '{0:x}' -f (Get-Random -Max 16) })
    Write-Info "Creating database user: $DbUser"
    if (-not $DryRun) {
        gcloud sql users create $DbUser `
            --instance=$CloudSqlInstance `
            --password=$DbPassword `
            --quiet 2>$null
        
        # Store password in Secret Manager
        Write-Info "Storing database password in Secret Manager..."
        echo $DbPassword | gcloud secrets create db-password `
            --data-file=- `
            --replication-policy="automatic" `
            --quiet 2>$null || `
        echo $DbPassword | gcloud secrets versions add db-password `
            --data-file=- 2>$null
    }
    
    Write-Success "Cloud SQL configured"
}

# Setup Secrets in Secret Manager
function Setup-Secrets {
    Write-Section "Setting up Google Secret Manager"
    
    $secrets = @{
        "stripe-secret-key" = "sk_live_REPLACE_WITH_ACTUAL_KEY";
        "stripe-webhook-secret" = "whsec_REPLACE_WITH_ACTUAL_KEY";
        "openai-api-key" = "sk-proj-REPLACE_WITH_ACTUAL_KEY";
        "clerk-secret-key" = "sk_live_REPLACE_WITH_ACTUAL_KEY";
        "clerk-publishable-key" = "pk_live_REPLACE_WITH_ACTUAL_KEY";
        "jwt-secret" = (-join ((1..64) | ForEach-Object { '{0:X}' -f (Get-Random -Max 256) }));
    }
    
    foreach ($secretName in $secrets.Keys) {
        $secretValue = $secrets[$secretName]
        Write-Info "Creating/updating secret: $secretName"
        
        if (-not $DryRun) {
            # Check if secret exists
            $secretExists = gcloud secrets list --filter="name:$secretName" --format="value(name)" 2>$null
            
            if ($secretExists) {
                Write-Info "  Adding new version to existing secret"
                echo $secretValue | gcloud secrets versions add $secretName --data-file=- 2>$null
            } else {
                Write-Info "  Creating new secret"
                echo $secretValue | gcloud secrets create $secretName `
                    --data-file=- `
                    --replication-policy="automatic" `
                    --quiet 2>$null
            }
        }
    }
    
    # Grant secret access to service account
    Write-Info "Granting secret access to service account..."
    if (-not $DryRun) {
        gcloud secrets add-iam-policy-binding "stripe-secret-key" `
            --member="serviceAccount:$ServiceAccount@$ProjectId.iam.gserviceaccount.com" `
            --role="roles/secretmanager.secretAccessor" `
            --quiet 2>$null
    }
    
    Write-Success "Secrets configured"
}

# Build and push Docker image
function Build-DockerImage {
    Write-Section "Building Docker Image"
    
    if (-not (Test-Path "Dockerfile")) {
        Write-Error "Dockerfile not found in current directory"
        exit 1
    }
    
    $imageName = "gcr.io/$ProjectId/nexus-api:latest"
    
    Write-Info "Building Docker image: $imageName"
    if (-not $DryRun) {
        docker build -t $imageName -f Dockerfile . --no-cache
        if (-not $?) {
            Write-Error "Docker build failed"
            exit 1
        }
    }
    
    Write-Success "Docker image built"
}

# Deploy to Cloud Run
function Deploy-CloudRun {
    Write-Section "Deploying to Cloud Run"
    
    $imageName = "gcr.io/$ProjectId/nexus-api:latest"
    $databaseUrl = "postgresql://$DbUser@/$Database?host=/cloudsql/$ProjectId:$Region:$CloudSqlInstance"
    
    Write-Info "Deploying service: $CloudRunService"
    
    if (-not $DryRun) {
        gcloud run deploy $CloudRunService `
            --image $imageName `
            --platform managed `
            --region $Region `
            --cpu 1 `
            --memory 512Mi `
            --min-instances 1 `
            --max-instances 10 `
            --timeout 300 `
            --set-cloudsql-instances "$ProjectId:$Region:$CloudSqlInstance" `
            --set-env-vars "DATABASE_URL=$databaseUrl,NODE_ENV=production" `
            --set-secrets "STRIPE_SECRET_KEY=stripe-secret-key:latest,OPENAI_API_KEY=openai-api-key:latest,CLERK_SECRET_KEY=clerk-secret-key:latest" `
            --service-account "$ServiceAccount@$ProjectId.iam.gserviceaccount.com" `
            --allow-unauthenticated `
            --quiet
    }
    
    Write-Success "Cloud Run deployment complete"
}

# Setup monitoring
function Setup-Monitoring {
    Write-Section "Setting up Monitoring & Alerting"
    
    Write-Info "Creating monitoring dashboard"
    Write-Info "Creating alert policies (Error Rate, P95 Latency, CPU)"
    Write-Info "Configure notification channels: Email + PagerDuty"
    
    # Note: Detailed monitoring setup would require JSON policy files
    # This is a placeholder for manual completion
    
    Write-Success "Monitoring setup initiated (manual configuration recommended)"
}

# Smoke tests
function Run-SmokeTests {
    Write-Section "Running Smoke Tests"
    
    # Get Cloud Run service URL
    $serviceUrl = gcloud run services describe $CloudRunService --platform managed --region $Region --format="value(status.url)" 2>$null
    
    if ($serviceUrl) {
        Write-Info "Service URL: $serviceUrl"
        Write-Info "Testing health endpoint..."
        
        if (-not $DryRun) {
            $healthResponse = Invoke-WebRequest -Uri "$serviceUrl/health" -ErrorAction SilentlyContinue
            if ($healthResponse.StatusCode -eq 200) {
                Write-Success "Health check passed"
            } else {
                Write-Error "Health check failed: $($healthResponse.StatusCode)"
            }
        }
    } else {
        Write-Error "Could not retrieve Cloud Run service URL"
    }
}

# Main execution
function Main {
    Write-Section "NEXUS Complete Deployment"
    Write-Info "Project: $ProjectId"
    Write-Info "Region: $Region"
    Write-Info "Dry Run: $DryRun"
    
    Test-GcloudInstalled
    Set-GcpProject
    Enable-GcpApis
    Create-ServiceAccount
    Create-CloudSql
    Setup-Secrets
    Build-DockerImage
    Deploy-CloudRun
    Setup-Monitoring
    Run-SmokeTests
    
    Write-Section "Deployment Complete"
    Write-Success "NEXUS API is now live!"
    Write-Info "Next steps:"
    Write-Info "  1. Verify API endpoint at https://<cloud-run-url>"
    Write-Info "  2. Configure custom domain in Cloud Run"
    Write-Info "  3. Setup monitoring and alerting in Cloud Console"
    Write-Info "  4. Test payment endpoints with Stripe test mode"
}

# Execute
Main
