#!/bin/bash
# Script de instalação automática do Transcritor com Diarização
# Otimizado para sistemas Linux (Ubuntu/Debian)

set -e  # Parar em caso de erro

echo "🎙️ INSTALAÇÃO DO TRANSCRITOR COM DIARIZAÇÃO"
echo "============================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# Verificar se está executando no diretório correto
if [ ! -f "transcrever.py" ]; then
    print_error "Execute este script a partir do diretório raiz do projeto"
    exit 1
fi

# Verificar sistema operacional
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_status "Sistema Linux detectado"
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "Sistema macOS detectado"
    OS="macos"
else
    print_warning "Sistema não testado: $OSTYPE"
    OS="unknown"
fi

# Atualizar sistema (apenas Linux)
if [ "$OS" = "linux" ]; then
    print_status "Atualizando lista de pacotes..."
    sudo apt update
fi

# Instalar dependências do sistema
print_status "Instalando dependências do sistema..."

if [ "$OS" = "linux" ]; then
    sudo apt install -y python3 python3-pip python3-venv ffmpeg git wget curl
elif [ "$OS" = "macos" ]; then
    # Verificar se Homebrew está instalado
    if ! command -v brew &> /dev/null; then
        print_error "Homebrew não encontrado. Instale em: https://brew.sh"
        exit 1
    fi
    brew install python ffmpeg git wget
fi

print_success "Dependências do sistema instaladas"

# Verificar versão do Python
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_status "Versão do Python: $PYTHON_VERSION"

# Criar ambiente virtual
print_status "Criando ambiente virtual..."
python3 -m venv venv-transcritor
print_success "Ambiente virtual criado"

# Ativar ambiente virtual
print_status "Ativando ambiente virtual..."
source venv-transcritor/bin/activate
print_success "Ambiente virtual ativado"

# Atualizar pip
print_status "Atualizando pip..."
pip install --upgrade pip

# Instalar PyTorch (detectar CUDA)
print_status "Detectando suporte a GPU..."
if command -v nvidia-smi &> /dev/null; then
    print_success "NVIDIA GPU detectada - instalando PyTorch com CUDA"
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
else
    print_warning "GPU não detectada - instalando PyTorch CPU"
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Instalar dependências Python
print_status "Instalando dependências Python..."
pip install -r requirements.txt
print_success "Dependências Python instaladas"

# Configurar arquivo .env
if [ ! -f ".env" ]; then
    print_status "Criando arquivo .env..."
    cp .env.example .env
    print_warning "Configure seu token do Hugging Face no arquivo .env"
    print_warning "Edite o arquivo .env com: nano .env"
else
    print_success "Arquivo .env já existe"
fi

# Criar diretórios necessários
print_status "Criando diretórios..."
mkdir -p input output temp logs
print_success "Diretórios criados"

# Tornar scripts executáveis
print_status "Configurando permissões..."
chmod +x scripts/*.py
chmod +x scripts/*.sh
print_success "Permissões configuradas"

# Teste básico
print_status "Testando instalação..."
python3 transcrever.py --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Instalação testada com sucesso"
else
    print_error "Erro no teste de instalação"
    exit 1
fi

# Informações finais
echo ""
echo "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "===================================="
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Configure seu token do Hugging Face:"
echo "   nano .env"
echo ""
echo "2. Ative o ambiente virtual:"
echo "   source venv-transcritor/bin/activate"
echo ""
echo "3. Teste com um arquivo:"
echo "   python3 transcrever.py arquivo.mp4"
echo ""
echo "4. Ou use scripts especializados:"
echo "   python3 scripts/reuniao_corporativa.py arquivo.mp4"
echo "   python3 scripts/entrevista_jornalistica.py arquivo.wav"
echo "   python3 scripts/podcast_brasileiro.py arquivo.mp3"
echo ""
echo "📚 DOCUMENTAÇÃO:"
echo "   Consulte o README.md para informações completas"
echo ""
echo "🆘 SUPORTE:"
echo "   Em caso de problemas, consulte a seção de troubleshooting"
echo ""
print_success "Instalação finalizada!"