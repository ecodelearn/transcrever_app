# 🐧 Setup Manual - Arch Linux + RTX 3060

## 🎯 Setup Passo a Passo (Sem Docker)

Vamos configurar o ambiente de desenvolvimento Python local primeiro, antes de partir para Docker.

---

## 1. 🔧 Verificar Sistema

```bash
# Verificar GPU NVIDIA
nvidia-smi

# Verificar Python
python --version
# Deve ser 3.8+

# Verificar pip
pip --version

# Verificar ffmpeg
ffmpeg -version
# Se não tiver: sudo pacman -S ffmpeg
```

---

## 2. 🐍 Ativar Ambiente Virtual

```bash
# Se o venv já existe na pasta atual
source venv/bin/activate

# OU se está em outra pasta
source ./venv/bin/activate

# Verificar se está ativo (deve mostrar (venv) no prompt)
which python
which pip

# Atualizar pip
pip install --upgrade pip
```

---

## 3. 🔥 Instalar PyTorch com CUDA (RTX 3060)

```bash
# IMPORTANTE: PyTorch com suporte CUDA para RTX 3060
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verificar se CUDA está funcionando
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"Not available\"}')"

# Deve retornar:
# CUDA available: True
# GPU: NVIDIA GeForce RTX 3060
```

---

## 4. 📦 Instalar Dependências ML

```bash
# Transformers e Whisper
pip install transformers==4.35.2
pip install openai-whisper==20231117

# PyAnnote para diarização
pip install pyannote.audio==3.1.1

# Bibliotecas de áudio
pip install librosa==0.10.1
pip install scipy==1.11.4
pip install numpy==1.24.4
pip install soundfile

# Para desenvolvimento web (FastAPI)
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install python-multipart
pip install python-dotenv
pip install aiofiles
```

---

## 5. 🧪 Testar Configuração

### **Teste 1: GPU e PyTorch**
```bash
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
"
```

### **Teste 2: Whisper**
```bash
python -c "
import whisper
print('Whisper models available:')
print(whisper.available_models())
"
```

### **Teste 3: PyAnnote** 
```bash
python -c "
from pyannote.audio import Pipeline
print('PyAnnote importado com sucesso!')
"
```

---

## 6. 🔐 Configurar Token Hugging Face

```bash
# Verificar se .env existe
cat .env

# Se não tiver HUGGINGFACE_TOKEN, adicionar:
echo "HUGGINGFACE_TOKEN=seu_token_aqui" >> .env

# Testar login
python -c "
from huggingface_hub import login
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('HUGGINGFACE_TOKEN')
if token:
    login(token)
    print('✅ Token Hugging Face funcionando!')
else:
    print('❌ Token não encontrado no .env')
"
```

---

## 7. 🎵 Testar Script CLI Atual

```bash
# Ativar ambiente se não estiver ativo
source venv/bin/activate

# Testar o script atual com um arquivo pequeno
python transcrever.py --help

# Se tiver um arquivo de áudio de teste:
python transcrever.py caminho/para/audio_teste.mp3 --modelo tiny

# Verificar outputs gerados
ls -la *.txt *.json *.srt 2>/dev/null || echo "Nenhum output encontrado"
```

---

## 8. 📂 Criar Estrutura para Web Development

```bash
# Criar estrutura de pastas
mkdir -p backend/{app/{api,models,services,core},tests}
mkdir -p frontend/{src/{app,components,hooks,utils},public}
mkdir -p uploads results

# Verificar estrutura
tree -L 3 . 2>/dev/null || find . -type d -name "*" | head -20
```

---

## 9. 🔧 Configurar VSCode

### **Selecionar Interpretador Python**
1. `Ctrl+Shift+P` → "Python: Select Interpreter"
2. Escolher o caminho: `./venv/bin/python`
3. Verificar no canto inferior direito se mostra `Python 3.x.x ('venv': venv)`

### **Configurar Terminal Integrado**
```bash
# No terminal do VSCode, ativar o venv automaticamente
echo 'source venv/bin/activate' >> ~/.bashrc

# OU criar script de ativação local
echo '#!/bin/bash
source venv/bin/activate
echo "✅ Ambiente virtual ativado!"
echo "Python: $(which python)"
echo "GPU: $(python -c "import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"Not available\")")"
' > activate.sh

chmod +x activate.sh

# Usar com: ./activate.sh
```

---

## 10. 🚀 Próximo: FastAPI Backend

```bash
# Criar arquivo principal do backend
touch backend/main.py

# Instalar dependências do backend
pip install sqlalchemy psycopg2-binary alembic

# Testar FastAPI
cat > backend/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.responses import JSONResponse
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Testar API
cd backend
python main.py
# Abrir http://localhost:8000 no browser
```

---

## 11. 🔍 Troubleshooting Comum

### **CUDA não funciona**
```bash
# Verificar drivers NVIDIA
nvidia-smi

# Reinstalar PyTorch se necessário
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### **Problema com PyAnnote**
```bash
# Pode precisar de dependências específicas
pip install torch-audio
pip install speechbrain
```

### **Erro de memória GPU**
```bash
# Verificar uso de memória
nvidia-smi

# Reduzir batch size ou usar modelo menor
python transcrever.py arquivo.mp3 --modelo tiny  # Ao invés de medium
```

---

## 12. 📋 Checklist Final

- [ ] ✅ GPU NVIDIA funcionando (`nvidia-smi`)
- [ ] ✅ Ambiente virtual ativo (`(venv)` no prompt)
- [ ] ✅ PyTorch com CUDA funcionando
- [ ] ✅ Whisper instalado e testado
- [ ] ✅ PyAnnote funcionando
- [ ] ✅ Token Hugging Face configurado
- [ ] ✅ Script CLI testado
- [ ] ✅ VSCode com interpretador correto
- [ ] ✅ FastAPI básico funcionando

---

## 🎯 Status Atual

Quando tudo estiver funcionando, você terá:

✅ **Ambiente Python** com GPU funcionando  
✅ **CLI script** operacional  
✅ **Base para web development** pronta  
✅ **FastAPI** iniciado  

**Próximo passo**: Implementar backend web completo!

---

## 💡 Comandos Úteis

```bash
# Ativar ambiente rapidamente
source venv/bin/activate

# Ver packages instalados
pip list | grep -E "(torch|whisper|pyannote|fastapi)"

# Monitorar GPU durante desenvolvimento
watch -n 1 nvidia-smi

# Rodar API em desenvolvimento
cd backend && uvicorn main:app --reload

# Ver logs detalhados
python transcrever.py arquivo.mp3 --verbose