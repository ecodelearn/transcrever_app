# 🏠 Desenvolvimento Local com RTX 3060

## 🎯 Configuração Ideal: EndeavourOS + RTX 3060

**Excelente!** Com RTX 3060 você pode rodar **tudo localmente** com performance real:
- ✅ **Whisper medium/large** com performance excelente
- ✅ **PyAnnote diarization** funcionando perfeitamente  
- ✅ **Desenvolvimento completo** sem mocks
- ✅ **Testing real** antes de deploy

---

## 🐧 Setup EndeavourOS + NVIDIA

### **1. Drivers NVIDIA**
```bash
# Verificar se drivers estão instalados
nvidia-smi

# Se não estiver instalado:
sudo pacman -S nvidia nvidia-utils nvidia-settings
# ou para LTS kernel:
sudo pacman -S nvidia-lts

# Reboot após instalação
sudo reboot
```

### **2. Docker com GPU Support**
```bash
# Instalar Docker
sudo pacman -S docker docker-compose

# Instalar NVIDIA Container Toolkit
yay -S nvidia-container-toolkit

# Configurar Docker para usar GPU
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Testar GPU no Docker
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi
```

### **3. Python + CUDA**
```bash
# Python environment
python -m venv venv
source venv/bin/activate

# PyTorch com CUDA (importante!)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verificar CUDA
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name())"
# Deve retornar: True e "NVIDIA GeForce RTX 3060"
```

---

## 🐳 Docker Compose com GPU

### **docker-compose.dev.yml**
```yaml
version: '3.8'

services:
  # PostgreSQL
  postgres:
    image: postgres:15
    container_name: transcritor-db
    environment:
      POSTGRES_DB: transcritor
      POSTGRES_USER: transcritor
      POSTGRES_PASSWORD: transcritor123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql

  # Redis
  redis:
    image: redis:7-alpine
    container_name: transcritor-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # API Backend (sem GPU - apenas coordena)
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: transcritor-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://transcritor:transcritor123@postgres:5432/transcritor
      - REDIS_URL=redis://redis:6379
      - HUGGINGFACE_TOKEN=${HUGGINGFACE_TOKEN}
      - ENVIRONMENT=development
      - GPU_ENABLED=true
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
      - ./results:/app/results
    depends_on:
      - postgres
      - redis
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # Worker com GPU (aqui é onde a mágica acontece!)
  worker-gpu:
    build:
      context: .
      dockerfile: Dockerfile.gpu
    container_name: transcritor-worker-gpu
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - DATABASE_URL=postgresql://transcritor:transcritor123@postgres:5432/transcritor
      - REDIS_URL=redis://redis:6379
      - HUGGINGFACE_TOKEN=${HUGGINGFACE_TOKEN}
      - WHISPER_MODEL=medium  # Pode usar medium/large!
      - ENABLE_DIARIZATION=true
      - CUDA_VISIBLE_DEVICES=0
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
      - ./results:/app/results
    depends_on:
      - postgres
      - redis
    command: celery -A worker worker --loglevel=info --concurrency=2

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: transcritor-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

volumes:
  postgres_data:
  redis_data:
```

### **Dockerfile.gpu**
```dockerfile
FROM nvidia/cuda:11.8-devel-ubuntu20.04

# Evitar prompt durante instalação
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Instalar Python e dependências do sistema
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    python3-dev \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements-gpu.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements-gpu.txt

# Copiar código
COPY backend/ .

# Expor porta
EXPOSE 8000

# Comando padrão
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **requirements-gpu.txt**
```
# Core FastAPI
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# Machine Learning com CUDA
torch==2.1.0+cu118 --index-url https://download.pytorch.org/whl/cu118
torchaudio==2.1.0+cu118 --index-url https://download.pytorch.org/whl/cu118
transformers==4.35.2
openai-whisper==20231117
pyannote.audio==3.1.1

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1

# Queue/Cache
celery==5.3.4
redis==5.0.1

# Utils
python-multipart==0.0.6
python-jose==3.3.0
passlib==1.7.4
python-dotenv==1.0.0
librosa==0.10.1
scipy==1.11.4
numpy==1.24.4
```

---

## ⚡ Performance Esperada RTX 3060

### **Benchmarks Estimados**
| Modelo | Áudio 1h | Tempo Processamento | RAM GPU |
|--------|----------|-------------------|---------|
| **Whisper tiny** | 60 min | ~3 min | 1GB |
| **Whisper base** | 60 min | ~5 min | 1.5GB |
| **Whisper small** | 60 min | ~8 min | 2GB |
| **Whisper medium** | 60 min | ~15 min | 4GB |
| **Whisper large** | 60 min | ~25 min | 8GB |

### **Configuração Recomendada RTX 3060**
```python
# backend/app/config.py
class DevelopmentConfig:
    # RTX 3060 tem 12GB VRAM - pode usar medium confortavelmente
    WHISPER_MODEL = "medium"  # Ideal para RTX 3060
    ENABLE_DIARIZATION = True
    BATCH_SIZE = 16  # Pode processar batches maiores
    MAX_WORKERS = 2  # 2 jobs simultâneos
    GPU_MEMORY_FRACTION = 0.8  # Usar 80% da VRAM
```

---

## 🚀 Comandos de Desenvolvimento

### **Setup Inicial**
```bash
# 1. Verificar GPU
nvidia-smi

# 2. Configurar projeto
git init
git add .
git commit -m "feat: initial project setup with CLI transcription"

# 3. Criar branch de desenvolvimento
git checkout -b dev/web-interface

# 4. Configurar ambiente
cp .env.example .env
# Editar .env com seu HUGGINGFACE_TOKEN

# 5. Build e start
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d

# 6. Verificar logs
docker-compose -f docker-compose.dev.yml logs -f worker-gpu
```

### **Desenvolvimento Ativo**
```bash
# Terminal 1: Logs do worker GPU
docker-compose -f docker-compose.dev.yml logs -f worker-gpu

# Terminal 2: Logs da API
docker-compose -f docker-compose.dev.yml logs -f api

# Terminal 3: Desenvolvimento frontend (opcional local)
cd frontend/
npm run dev

# Terminal 4: Monitorar GPU
watch -n 1 nvidia-smi
```

### **Teste Rápido**
```bash
# Testar upload via API
curl -X POST "http://localhost:8000/jobs/" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_audio.mp3" \
  -F "model=medium" \
  -F "enable_diarization=true"
```

---

## 🔧 Estrutura do Projeto

```
transcritor/
├── 📄 docker-compose.dev.yml    # Docker com GPU
├── 📄 Dockerfile.gpu           # Container com CUDA
├── 📄 requirements-gpu.txt     # Deps com PyTorch+CUDA
├── 📁 backend/                 # FastAPI backend
│   ├── 📄 main.py
│   ├── 📄 worker.py           # Celery worker
│   ├── 📁 app/
│   │   ├── 📁 api/            # Routes
│   │   ├── 📁 models/         # Database models
│   │   ├── 📁 services/       # Business logic
│   │   │   ├── transcription_service.py
│   │   │   └── diarization_service.py
│   │   └── 📁 core/           # Config
│   └── 📁 tests/
├── 📁 frontend/               # Next.js frontend
│   ├── 📄 package.json
│   ├── 📁 src/
│   │   ├── 📁 app/
│   │   ├── 📁 components/
│   │   └── 📁 hooks/
├── 📁 database/               # SQL scripts
├── 📁 uploads/                # Arquivos temporários
└── 📁 results/                # Resultados processados
```

---

## 🎯 Workflow Desenvolvimento

### **Ciclo Completo Local**
```bash
# 1. Desenvolver feature
git checkout -b feature/upload-progress

# 2. Testar localmente (com GPU real!)
docker-compose -f docker-compose.dev.yml up --build

# 3. Upload arquivo de teste
# Assistir processamento em tempo real com WebSocket

# 4. Validar resultado
# Download TXT/JSON/SRT gerados

# 5. Commit
git add .
git commit -m "feat: add upload progress with real-time updates"

# 6. Merge quando pronto
git checkout dev/web-interface
git merge feature/upload-progress
```

### **Performance Monitoring Local**
```bash
# Terminal dedicado para monitorar recursos
htop
nvidia-smi -l 1
docker stats

# Logs estruturados
docker-compose -f docker-compose.dev.yml logs -f | grep "processing_time"
```

---

## 🔄 Migrate para Produção

### **Quando Estiver Pronto**
```bash
# 1. Testar build produção
docker build -f Dockerfile.prod -t transcritor-api .

# 2. Deploy staging
# Escolher entre: Railway, Render, Google Cloud

# 3. Deploy produção
# legenda.iaforte.com.br
```

### **Vantagens do Desenvolvimento com GPU Local**
✅ **Performance real** - testar com arquivos grandes  
✅ **Debug completo** - ver toda pipeline funcionando  
✅ **Custo zero** - usar sua própria GPU  
✅ **Offline** - desenvolver sem internet  
✅ **Iteração rápida** - mudanças instantâneas  

---

## 🎉 Próximos Passos

1. **Setup Docker + GPU** no EndeavourOS
2. **Implementar backend** FastAPI com workers
3. **Criar frontend** Next.js com upload
4. **Testar pipeline completo** localmente
5. **Deploy quando satisfeito** com resultado

**Resultado**: Sistema completo funcionando localmente com performance de produção!