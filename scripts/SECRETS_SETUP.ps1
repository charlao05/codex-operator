#!/usr/bin/env pwsh
<#
.SYNOPSIS
  NEXUS Secrets Setup Script
  Cria secrets no Google Secret Manager para Stripe, OpenAI, Clerk, JWT e Database

.DESCRIPTION
  Script PowerShell para armazenar de forma segura todas as chaves de API
  no Google Secret Manager (projeto: agendamento-n8n-476415)

.AUTHOR
  Charles Rodrigues Silva
  charles.rsilva05@gmail.com

.DATE
  2026-01-04
#>

param(
    [string]$ProjectId = "agendamento-n8n-476415",
    [string]$StripeSecretKey = "",
    [string]$StripePublishableKey = "",
    [string]$OpenAIApiKey = "",
    [string]$ClerkSecretKey = "",
    [string]$ClerkPublishableKey = "",
    [string]$JwtSecret = "",
    [string]$DatabaseUrl = "",
    [switch]$SkipValidation = $false
)

# Cores para output
$colors = @{
    Success = 'Green'
    Error   = 'Red'
    Info    = 'Cyan'
    Warning = 'Yellow'
}

function Write-Success { Write-Host "[+] $args" -ForegroundColor $colors.Success }
function Write-Error { Write-Host "[-] ERROR: $args" -ForegroundColor $colors.Error }
function Write-Info { Write-Host "[*] $args" -ForegroundColor $colors.Info }
function Write-Warning { Write-Host "[!] WARNING: $args" -ForegroundColor $colors.Warning }

function Set-Secret {
    param(
        [string]$SecretName,
        [string]$SecretValue,
        [string]$ProjectId
    )
    
    if ([string]::IsNullOrEmpty($SecretValue)) {
        Write-Error "Value for $SecretName is empty!"
        return $false
    }
    
    Write-Info "Creating/Updating secret: $SecretName"
    
    # Verificar se secret existe
    $secretExists = gcloud secrets list --project=$ProjectId --filter="name:$SecretName" --format="value(name)" 2>$null
    
    if ($secretExists) {
        Write-Warning "Secret $SecretName already exists. Adding new version..."
        $tempFile = [System.IO.Path]::GetTempFileName()
        Set-Content -Path $tempFile -Value $SecretValue -NoNewline
        gcloud secrets versions add $SecretName --data-file=$tempFile --project=$ProjectId 2>$null
        Remove-Item $tempFile -Force
    } else {
        Write-Info "Creating new secret: $SecretName"
        $tempFile = [System.IO.Path]::GetTempFileName()
        Set-Content -Path $tempFile -Value $SecretValue -NoNewline
        gcloud secrets create $SecretName --data-file=$tempFile --replication-policy=automatic --project=$ProjectId 2>$null
        Remove-Item $tempFile -Force
    }
    
    if ($?) {
        Write-Success "Secret $SecretName created/updated successfully"
        return $true
    } else {
        Write-Error "Failed to create/update secret $SecretName"
        return $false
    }
}

function Main {
    Write-Host "`n=== NEXUS Secrets Setup ==="
    Write-Info "Project: $ProjectId"
    Write-Info "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    
    # Validar gcloud
    try {
        $gcloudVersion = gcloud --version 2>$null | Select-Object -First 1
        Write-Success "gcloud CLI: $gcloudVersion"
    } catch {
        Write-Error "gcloud CLI not found. Install from https://cloud.google.com/sdk/docs/install"
        exit 1
    }
    
    # Definir projeto
    Write-Info "Setting GCP project..."
    gcloud config set project $ProjectId
    
    # Contador de sucesso
    $successCount = 0
    $totalCount = 0
    
    # Stripe Secrets
    if (-not [string]::IsNullOrEmpty($StripeSecretKey)) {
        $totalCount++
        if (Set-Secret -SecretName "stripe-secret-key" -SecretValue $StripeSecretKey -ProjectId $ProjectId) {
            $successCount++
        }
    }
    
    if (-not [string]::IsNullOrEmpty($StripePublishableKey)) {
        $totalCount++
        if (Set-Secret -SecretName "stripe-publishable-key" -SecretValue $StripePublishableKey -ProjectId $ProjectId) {
            $successCount++
        }
    }
    
    # OpenAI Secret
    if (-not [string]::IsNullOrEmpty($OpenAIApiKey)) {
        $totalCount++
        if (Set-Secret -SecretName "openai-api-key" -SecretValue $OpenAIApiKey -ProjectId $ProjectId) {
            $successCount++
        }
    }
    
    # Clerk Secrets
    if (-not [string]::IsNullOrEmpty($ClerkSecretKey)) {
        $totalCount++
        if (Set-Secret -SecretName "clerk-secret-key" -SecretValue $ClerkSecretKey -ProjectId $ProjectId) {
            $successCount++
        }
    }
    
    if (-not [string]::IsNullOrEmpty($ClerkPublishableKey)) {
        $totalCount++
        if (Set-Secret -SecretName "clerk-publishable-key" -SecretValue $ClerkPublishableKey -ProjectId $ProjectId) {
            $successCount++
        }
    }
    
    # JWT Secret
    if (-not [string]::IsNullOrEmpty($JwtSecret)) {
        $totalCount++
        if (Set-Secret -SecretName "jwt-secret" -SecretValue $JwtSecret -ProjectId $ProjectId) {
            $successCount++
        }
    }
    
    # Database URL
    if (-not [string]::IsNullOrEmpty($DatabaseUrl)) {
        $totalCount++
        if (Set-Secret -SecretName "database-url" -SecretValue $DatabaseUrl -ProjectId $ProjectId) {
            $successCount++
        }
    }
    
    # Resumo
    Write-Host "`n=== Summary ==="
    Write-Info "Secrets created/updated: $successCount/$totalCount"
    
    if ($successCount -eq $totalCount) {
        Write-Success "All secrets configured successfully!"
        Write-Info "Next: Run DEPLOY_NEXUS_COMPLETE.ps1 to deploy"
        return 0
    } else {
        Write-Error "Some secrets failed. Check errors above."
        return 1
    }
}

# Execute
exit (Main)
