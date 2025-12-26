# Deployment Guide - CODEX-OPERATOR

## Opção 1: Heroku (Máis Fácil)

### Pré-requisitos

```bash
brew install heroku  # macOS/Linux
choco install heroku  # Windows
```

### Deploy

```bash
heroku create codex-operator-prod
heroku configset OPENAI_API_KEY=sk-proj-...
heroku config:set WHATSAPP_TOKEN=EAAfaKajjJnkBA...
heroku config:set WHATSAPP_PHONE_ID=123456789
heroku config:set DATABASE_URL=postgres://...
git push heroku main
```

### Ver Logs

```bash
heroku logs --tail -a codex-operator-prod
```

### Rollback

```bash
heroku releases
heroku rollback v10
```

---

## Opção 2: Google Cloud Run (Recomendado)

### Pré-requisitos

```bash
gcloud init
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Build e Deploy

```bash
# Build da imagem
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/codex-operator

# Deploy
gcloud run deploy codex-operator \
  --image gcr.io/YOUR_PROJECT_ID/codex-operator:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=sk-proj-... \
  --set-env-vars WHATSAPP_TOKEN=EAAfaKajjJnkBA... \
  --memory 1Gi \
  --cpu 1
```

### Ver Logs

```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 50
gcloud run services describe codex-operator --region us-central1
```

---

## Opção 3: Docker Compose (Local)

```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

---

## Opção 4: Kubernetes (Enterprise)

```bash
kubectl create namespace codex
kubectl create secret generic codex-secrets \
  --from-literal=OPENAI_API_KEY=sk-proj-... \
  --from-literal=WHATSAPP_TOKEN=EAAfaKajjJnkBA... \
  -n codex
kubectl apply -f k8s/deployment.yaml -n codex
```

---

## Health Check

```bash
curl https://seu-app.herokuapp.com/health
curl https://seu-app.run.app/health
```

Resposta esperada:
```json
{"status": "ok"}
```

---

## Monitoramento

### Heroku
```bash
heroku logs --tail
heroku stats
```

### Cloud Run
```bash
gcloud monitoring dashboards list
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

### Docker
```bash
docker logs codex-operator
docker stats
```

---

## Troubleshooting

### "Port already in use"
```bash
lsof -i :8000
kill -9 <PID>
```

### "Secret not found"
```bash
heroku config  # Heroku
gcloud run services describe codex-operator --region us-central1  # Cloud Run
```

### "Database connection failed"
Verifique DATABASE_URL em production.

---

## Próximas Etapas

- Leia [SETUP-SECRETS.md](./SETUP-SECRETS.md) para configurar secrets
- Leia [SECURITY.md](./SECURITY.md) para políticas de segurança
- Configure CI/CD com GitHub Actions
- Implemente monitoramento com Datadog ou New Relic
