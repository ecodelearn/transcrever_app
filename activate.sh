#!/bin/bash

# 🚀 Script de Ativação - Ambiente Virtual + RTX 3060
# Para uso no terminal do VSCode

set -e

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Ativando ambiente de desenvolvimento...${NC}"

# Ativar ambiente virtual
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✅ Ambiente virtual ativado!${NC}"
else
    echo -e "${RED}❌ Ambiente virtual não encontrado. Execute: python -m venv venv${NC}"
    exit 1
fi

# Verificar Python
echo -e "${BLUE}🐍 Python:${NC} $(which python)"
echo -e "${BLUE}📦 Pip:${NC} $(which pip)"

# Verificar PyTorch e GPU
if python -c "import torch" 2>/dev/null; then
    GPU_STATUS=$(python -c "import torch; print('✅ Disponível' if torch.cuda.is_available() else '❌ Não disponível')")
    GPU_NAME=$(python -c "import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')")
    echo -e "${BLUE}🔥 GPU CUDA:${NC} $GPU_STATUS"
    echo -e "${BLUE}🎮 GPU:${NC} $GPU_NAME"
else
    echo -e "${YELLOW}⚠️  PyTorch não instalado ainda${NC}"
fi

# Verificar token Hugging Face
if python -c "
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('HUGGINGFACE_TOKEN')
print('ok' if token else 'missing')
" 2>/dev/null | grep -q "ok"; then
    echo -e "${GREEN}🔑 Token Hugging Face: Configurado${NC}"
else
    echo -e "${YELLOW}⚠️  Token Hugging Face: Não encontrado no .env${NC}"
fi

echo ""
echo -e "${BLUE}📋 Comandos úteis:${NC}"
echo "  🌐 Rodar API:    cd backend && uvicorn main:app --reload"
echo "  🎵 Testar CLI:   python transcrever.py --help"
echo "  📊 Monitor GPU:  watch -n 1 nvidia-smi"
echo "  📦 Install deps: pip install -r requirements-web.txt"
echo "  🧪 Test backend:  python backend/simple_main.py"
echo ""