# 🚀 Guia de Deployment - legenda.iaforte.com.br

## 🏗️ Arquitetura de Produção

### **Visão Geral**

O projeto será deployado usando uma arquitetura híbrida otimizada para performance e custos:

- **Frontend**: Vercel (Next.js) - `legenda.iaforte.com.br`
- **Backend**: Google Cloud Run (FastAPI) - `api.legenda.iaforte.com.br`
- **Workers**: Cloud Run Jobs com GPU - processamento assíncrono
- **Storage**: Google Cloud Storage + Cloud SQL

### **Benefícios da Arquitetura Híbrida**

✅ **Vercel para Frontend**
- Deploy instantâneo e gratuito
- CDN global automático
- Otimizações de performance built-in
- SSL automático para domínio customizado

✅ **Google Cloud para Backend**
- Suporte completo a GPU para ML
- Escalabilidade ilimitada
- Processamento de arquivos grandes
- Background jobs robustos

---

## 🔧 Configuração de Domínio

### **DNS Configuration**

```bash
# Configurar no seu provedor DNS (Cloudflare recomendado)

# Frontend (Vercel)
legenda.iaforte.com.br     CNAME    cname.vercel-dns.com
www.legenda.iaforte.com.br CNAME    cname.vercel-dns.com

# Backend API (Google Cloud)
api.legenda.iaforte.com.br CNAME    ghs.googlehosted.com

# WebSocket (se necessário)
ws.legenda.iaforte.com.br  CNAME    ghs.googlehosted.com

# CDN Assets
cdn.legenda.iaforte.com.br CNAME    storage.googleapis.com
```

### **SSL Certificates**

```yaml
# Configuração automática via Cloud Load Balancer
ssl_certificates:
  - domains:
    - api.legenda.iaforte.com.br
    - ws.legenda.iaforte.com.br
  - managed: true
  - auto_renewal: true
```

---

## 🌐 Frontend (Vercel)

### **Estrutura do Projeto Frontend**

```
frontend/
├── 📁 app/
│   ├── 📁 dashboard/
│   ├── 📁 upload/
│   ├── 📁 results/
│   └── layout.tsx
├── 📁 components/
│   ├── 📁 ui/
│   ├── FileUpload.tsx
│   ├── ProgressBar.tsx
│   └── SpeakerEditor.tsx
├── 📁 lib/
│   ├── api-client.ts
│   ├── websocket.ts
│   └── auth.ts
├── next.config.js
└── vercel.json
```

### **Configuração Vercel**

```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.legenda.iaforte.com.br",
    "NEXT_PUBLIC_WS_URL": "wss://api.legenda.iaforte.com.br"
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://api.legenda.iaforte.com.br/api/v1/:path*"
    }
  ]
}
```

### **Deploy Commands**

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy inicial
cd frontend/
vercel --prod

# Configurar domínio customizado
vercel domains add legenda.iaforte.com.br
vercel domains add www.legenda.iaforte.com.br
```

---

## ☁️ Backend (Google Cloud Run)

### **1. Configuração Inicial do GCP**

```bash
# Autenticar e configurar projeto
gcloud auth login
gcloud config set project seu-projeto-id

# Habilitar APIs necessárias
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable storage-component.googleapis.com
gcloud services enable cloudtasks.googleapis.com
gcloud services enable redis.googleapis.com
```

### **2. Cloud Storage Buckets**

```bash
# Criar buckets para diferentes tipos de arquivo
gsutil mb -p seu-projeto-id -c STANDARD -l southamerica-east1 gs://legenda-uploads
gsutil mb -p seu-projeto-id -c STANDARD -l southamerica-east1 gs://legenda-results
gsutil mb -p seu-projeto-id -c NEARLINE -l southamerica-east1 gs://legenda-archive

# Configurar CORS para uploads diretos
cat > cors.json << EOF
[
  {
    "origin": ["https://legenda.iaforte.com.br"],
    "method": ["GET", "POST", "PUT"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
EOF

gsutil cors set cors.json gs://legenda-uploads
```

### **3. Cloud SQL Database**

```bash
# Criar instância PostgreSQL
gcloud sql instances create legenda-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=southamerica-east1 \
  --storage-type=SSD \
  --storage-size=20GB \
  --backup \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=03

# Criar banco de dados
gcloud sql databases create legenda --instance=legenda-db

# Criar usuário
gcloud sql users create legenda-user \
  --instance=legenda-db \
  --password=sua_senha_segura
```

### **4. Redis Memorystore**

```bash
# Criar instância Redis
gcloud redis instances create legenda-redis \
  --size=1 \
  --region=southamerica-east1 \
  --redis-version=redis_7_0
```

---

## 🐳 Dockerfiles Otimizados

### **Backend Dockerfile**

```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Copiar e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY . .

# Criar usuário não-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 8080

# Comando de inicialização
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### **Worker Dockerfile (com GPU)**

```dockerfile
# Dockerfile.worker
FROM nvidia/cuda:11.8-devel-ubuntu22.04

# Evitar prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar Python e dependências
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar PyTorch com CUDA
RUN pip3 install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Copiar e instalar dependências
COPY requirements-worker.txt .
RUN pip3 install --no-cache-dir -r requirements-worker.txt

# Copiar código
COPY worker/ .

# Configurar usuário
RUN useradd -m -u 1000 worker && chown -R worker:worker /app
USER worker

CMD ["python3", "worker.py"]
```

---

## 🚀 Cloud Run Services

### **1. Backend API Service**

```yaml
# cloudrun-backend.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: legenda-backend
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/client-name: cloud-console
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/execution-environment: gen2
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 100
      timeoutSeconds: 3600
      containers:
      - image: gcr.io/seu-projeto-id/legenda-backend:latest
        ports:
        - containerPort: 8080
        resources:
          limits:
            cpu: "4"
            memory: "16Gi"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-url
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-url
              key: url
        - name: HF_TOKEN
          valueFrom:
            secretKeyRef:
              name: huggingface-token
              key: token
```

### **2. Worker Jobs**

```yaml
# cloudrun-worker.yaml
apiVersion: run.googleapis.com/v1
kind: Job
metadata:
  name: legenda-worker
spec:
  template:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - image: gcr.io/seu-projeto-id/legenda-worker:latest
            resources:
              limits:
                cpu: "8"
                memory: "32Gi"
                nvidia.com/gpu: "1"
            env:
            - name: JOB_ID
              value: "{{.job_id}}"
```

---

## 🔄 CI/CD Pipeline

### **GitHub Actions Workflow**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  GAR_LOCATION: southamerica-east1
  REPOSITORY: legenda
  
jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Google Auth
      uses: google-github-actions/auth@v1
      with:
        credentials_json: ${{ secrets.GCP_SA_KEY }}

    - name: Setup Cloud SDK
      uses: google-github-actions/setup-gcloud@v1

    - name: Configure Docker
      run: gcloud auth configure-docker $GAR_LOCATION-docker.pkg.dev

    - name: Build Backend
      run: |
        docker build -f Dockerfile.backend -t $GAR_LOCATION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/backend:$GITHUB_SHA .
        docker push $GAR_LOCATION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/backend:$GITHUB_SHA

    - name: Deploy Backend
      run: |
        gcloud run deploy legenda-backend \
          --image $GAR_LOCATION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/backend:$GITHUB_SHA \
          --region $GAR_LOCATION \
          --platform managed \
          --allow-unauthenticated \
          --set-env-vars="ENVIRONMENT=production"

  deploy-worker:
    runs-on: ubuntu-latest
    needs: deploy-backend
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Google Auth
      uses: google-github-actions/auth@v1
      with:
        credentials_json: ${{ secrets.GCP_SA_KEY }}

    - name: Build Worker
      run: |
        docker build -f Dockerfile.worker -t $GAR_LOCATION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/worker:$GITHUB_SHA .
        docker push $GAR_LOCATION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/worker:$GITHUB_SHA

  deploy-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v25
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.ORG_ID }}
        vercel-project-id: ${{ secrets.PROJECT_ID }}
        vercel-args: '--prod'
        working-directory: ./frontend
```

---

## 💰 Estimativa de Custos

### **Cenário: 1000 transcrições/mês**

| Serviço | Especificação | Custo Mensal |
|---------|---------------|--------------|
| **Vercel** | Frontend + CDN | $0 (hobby) |
| **Cloud Run Backend** | 4 vCPU, 16GB, 100h | ~$80 |
| **Cloud Run Workers** | GPU T4, 50h processamento | ~$120 |
| **Cloud SQL** | db-f1-micro, 20GB | ~$25 |
| **Cloud Storage** | 500GB storage | ~$15 |
| **Redis** | 1GB instance | ~$30 |
| **Load Balancer** | HTTPS + certificados | ~$20 |
| **Total Estimado** | | **~$290/mês** |

### **Otimizações de Custo**

```bash
# 1. Preemptible instances para workers
gcloud run jobs replace worker.yaml \
  --add-cloudsql-instances=$PROJECT_ID:southamerica-east1:legenda-db \
  --execution-environment=gen2 \
  --task-timeout=3600 \
  --max-retries=3

# 2. Lifecycle policies para storage
gsutil lifecycle set lifecycle.json gs://legenda-archive

# 3. Scheduled scaling para desenvolvimento
gcloud run services update legenda-backend \
  --min-instances=0 \
  --max-instances=10
```

---

## 📊 Monitoramento e Logs

### **Cloud Monitoring Setup**

```yaml
# monitoring.yaml
resources:
  - name: legenda-uptime-check
    type: monitoring.v1.uptimeCheckConfig
    properties:
      displayName: "Legenda API Health"
      httpCheck:
        path: "/health"
        port: 443
        useSsl: true
      monitoredResource:
        type: "uptime_url"
        labels:
          host: "api.legenda.iaforte.com.br"
      timeout: "10s"
      period: "60s"

  - name: legenda-alert-policy
    type: monitoring.v1.alertPolicy
    properties:
      displayName: "High Error Rate"
      conditions:
        - displayName: "Error rate > 5%"
          conditionThreshold:
            filter: 'resource.type="cloud_run_revision"'
            comparison: COMPARISON_GREATER_THAN
            thresholdValue: 0.05
```

### **Structured Logging**

```python
# logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    logHandler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logHandler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
    
    return logger

# Usage em FastAPI
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        "Request processed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": process_time,
            "user_agent": request.headers.get("user-agent")
        }
    )
    
    return response
```

---

## 🔒 Segurança

### **IAM Roles e Permissions**

```bash
# Service account para Cloud Run
gcloud iam service-accounts create legenda-backend \
  --display-name="Legenda Backend Service Account"

# Permissions mínimas necessárias
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:legenda-backend@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:legenda-backend@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:legenda-backend@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudtasks.enqueuer"
```

### **Secret Manager**

```bash
# Armazenar credenciais sensíveis
echo -n "sua_database_url" | gcloud secrets create database-url --data-file=-
echo -n "sua_redis_url" | gcloud secrets create redis-url --data-file=-
echo -n "seu_hf_token" | gcloud secrets create huggingface-token --data-file=-

# Dar acesso ao service account
gcloud secrets add-iam-policy-binding database-url \
  --member="serviceAccount:legenda-backend@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 🚀 Deploy Commands

### **Deploy Completo**

```bash
#!/bin/bash
# deploy.sh

# 1. Build e push das imagens
docker build -f Dockerfile.backend -t gcr.io/$PROJECT_ID/legenda-backend .
docker push gcr.io/$PROJECT_ID/legenda-backend

docker build -f Dockerfile.worker -t gcr.io/$PROJECT_ID/legenda-worker .
docker push gcr.io/$PROJECT_ID/legenda-worker

# 2. Deploy backend
gcloud run deploy legenda-backend \
  --image gcr.io/$PROJECT_ID/legenda-backend \
  --region southamerica-east1 \
  --platform managed \
  --allow-unauthenticated \
  --service-account legenda-backend@$PROJECT_ID.iam.gserviceaccount.com \
  --add-cloudsql-instances $PROJECT_ID:southamerica-east1:legenda-db \
  --set-env-vars "ENVIRONMENT=production" \
  --memory 16Gi \
  --cpu 4 \
  --concurrency 100 \
  --timeout 3600

# 3. Configurar domínio customizado
gcloud run domain-mappings create \
  --service legenda-backend \
  --domain api.legenda.iaforte.com.br \
  --region southamerica-east1

# 4. Deploy frontend
cd frontend/
vercel --prod

echo "✅ Deploy completo finalizado!"
echo "🌐 Frontend: https://legenda.iaforte.com.br"
echo "🔗 API: https://api.legenda.iaforte.com.br"
```

Esta arquitetura fornece uma base sólida, escalável e cost-effective para o projeto `legenda.iaforte.com.br`, aproveitando o melhor de cada plataforma!