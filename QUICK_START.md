# ⚡ Quick Start - Comandos para VSCode Terminal

## 🎯 Execute estes comandos no terminal do VSCode

### **1. Ativar Ambiente Virtual**
```bash
# Ativar o venv que já existe
source venv/bin/activate

# Verificar se está ativo (deve mostrar (venv) no prompt)
echo "Ambiente ativo: $(which python)"
```

### **2. Instalar PyTorch com CUDA para RTX 3060**
```bash
# IMPORTANTE: Instalar PyTorch com suporte CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Testar GPU
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

### **3. Instalar Dependências ML**
```bash
# Whisper e Transformers
pip install openai-whisper==20231117 transformers==4.35.2

# PyAnnote para diarização
pip install pyannote.audio==3.1.1

# Bibliotecas de áudio
pip install librosa scipy numpy soundfile
```

### **4. Instalar FastAPI para Web Development**
```bash
# FastAPI e dependências web
pip install fastapi[all] uvicorn[standard] python-multipart aiofiles python-dotenv

# Database (para futuro)
pip install sqlalchemy psycopg2-binary alembic
```

### **5. Testar Configuração Atual**
```bash
# Testar script CLI atual
python transcrever.py --help

# Verificar token Hugging Face
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('HUGGINGFACE_TOKEN')
print('Token encontrado!' if token else 'Token não encontrado no .env')
"
```

### **6. Criar Estrutura Backend**
```bash
# Criar pastas
mkdir -p backend/{app/{api,models,services,core},tests}
mkdir -p uploads results

# Criar arquivo FastAPI básico
cat > backend/main.py << 'EOF'
from fastapi import FastAPI
import torch

app = FastAPI(title="Transcritor API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Transcritor API funcionando!"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    }
EOF
```

### **7. Testar API Backend**
```bash
# Rodar FastAPI
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Em outro terminal ou browser, testar:
# http://localhost:8000
# http://localhost:8000/health
# http://localhost:8000/docs (Swagger UI)
```

### **8. Script de Ativação Automática**
```bash
# Criar script para ativar ambiente facilmente
cat > activate.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
echo "✅ Ambiente virtual ativado!"
echo "Python: $(which python)"
if python -c "import torch" 2>/dev/null; then
    echo "GPU: $(python -c "import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'Not available')")"
else
    echo "PyTorch: Não instalado"
fi
echo ""
echo "Para rodar a API: cd backend && uvicorn main:app --reload"
echo "Para rodar CLI: python transcrever.py --help"
EOF

chmod +x activate.sh

# Usar com: ./activate.sh
```

### **9. Configurar VSCode**
```bash
# No VSCode:
# 1. Ctrl+Shift+P → "Python: Select Interpreter"
# 2. Escolher: ./venv/bin/python
# 3. Verificar no rodapé se mostra "Python 3.x.x ('venv': venv)"

# Testar no terminal integrado do VSCode
source venv/bin/activate
python --version
```

### **10. Git Setup**
```bash
# Se ainda não fez o commit inicial
git add .
git commit -m "feat: complete project architecture and documentation

- Add CLI transcription tool with environment variables  
- Create comprehensive documentation and guides
- Design web architecture with RTX 3060 support
- Include Arch Linux specific setup instructions"

# Criar branch de desenvolvimento
git checkout -b dev/web-interface
```

## 🎯 Checklist Rápido

Execute e marque conforme completa:

- [ ] `source venv/bin/activate` - Ambiente ativado
- [ ] `pip install torch...` - PyTorch com CUDA
- [ ] `python -c "import torch; print(torch.cuda.is_available())"` - GPU funcionando
- [ ] `pip install openai-whisper transformers pyannote.audio` - ML libs
- [ ] `pip install fastapi[all]` - Web framework
- [ ] `python transcrever.py --help` - CLI funcionando
- [ ] `mkdir backend && cat > backend/main.py` - Estrutura criada
- [ ] `cd backend && uvicorn main:app --reload` - API rodando
- [ ] VSCode com interpretador Python correto
- [ ] `git commit` - Código versionado

## 🚀 Próximo Passo

Quando tudo estiver funcionando, você terá:

✅ **Ambiente Python** com RTX 3060 ativo  
✅ **CLI atual** funcionando  
✅ **FastAPI** básico rodando  
✅ **Estrutura** para desenvolvimento web  

**Depois disso**: Implementar endpoints de upload e transcription!

## 💡 Comandos Úteis Durante Desenvolvimento

```bash
# Monitorar GPU
watch -n 1 nvidia-smi

# Ativar ambiente rapidamente
./activate.sh

# Rodar API em desenvolvimento
cd backend && uvicorn main:app --reload

# Ver logs detalhados do CLI
python transcrever.py arquivo.mp3 --verbose

# Listar packages instalados
pip list | grep -E "(torch|whisper|fastapi)"
```

## 🔧 Troubleshooting

### **Se PyTorch não reconhecer GPU:**
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### **Se erro com PyAnnote:**
```bash
pip install torch-audio speechbrain
```

### **Se VSCode não reconhecer interpretador:**
```bash
# Verificar caminho
ls -la venv/bin/python
# Usar caminho absoluto: /caminho/completo/para/projeto/venv/bin/python
```

---

**Status**: Pronto para setup manual no Arch Linux! 🎉