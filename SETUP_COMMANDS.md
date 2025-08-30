# ⚡ Comandos de Setup - Execute no Terminal do VSCode

## 🎯 Execute estes comandos em sequência

### **1. Tornar scripts executáveis**
```bash
chmod +x activate.sh
chmod +x scripts/setup.sh
```

### **2. Ativar ambiente virtual**
```bash
./activate.sh
# ou
source venv/bin/activate
```

### **3. Verificar ambiente atual**
```bash
python backend/simple_main.py
```

### **4. Instalar dependências web**
```bash
pip install -r requirements-web.txt
```

### **5. Testar script CLI atual**
```bash
python transcrever.py --help
```

### **6. Testar backend FastAPI**
```bash
cd backend
python main.py
# Em outro terminal: curl http://localhost:8000/health
```

### **7. Configurar Git**
```bash
git add .
git commit -m "feat: add web backend structure and setup scripts"
git checkout -b dev/web-interface
```

## 🔧 Comandos de desenvolvimento

### **Durante desenvolvimento:**
```bash
# Ativar ambiente
./activate.sh

# Rodar API
cd backend && uvicorn main:app --reload

# Monitorar GPU
watch -n 1 nvidia-smi

# Testar endpoints
curl http://localhost:8000/
curl http://localhost:8000/health
```

### **Estrutura criada:**
```
transcritor/
├── activate.sh              ⭐ Script de ativação
├── requirements-web.txt     ⭐ Dependências web
├── backend/
│   ├── main.py             ⭐ FastAPI principal
│   ├── simple_main.py      ⭐ Teste sem deps
│   └── app/
│       ├── core/config.py  ⭐ Configurações
│       ├── models/job.py   ⭐ Modelos de dados
│       └── services/transcription_service.py ⭐ Serviço ML
└── [arquitetura completa já criada]
```

## 🎉 Próximo passo

Quando tudo estiver funcionando:
- ✅ GPU detectada
- ✅ API rodando
- ✅ CLI funcionando

**Então**: Implementar frontend Next.js! 🚀