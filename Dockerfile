# Dockerfile para Transcritor com Diarização
# Suporte para GPU (NVIDIA CUDA) e CPU

# Base image com Python e CUDA
FROM nvidia/cuda:11.8-devel-ubuntu22.04

# Evitar prompts interativos durante instalação
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    ffmpeg \
    git \
    wget \
    curl \
    build-essential \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 transcriptor && \
    mkdir -p /app /input /output && \
    chown -R transcriptor:transcriptor /app /input /output

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cu118 && \
    pip3 install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY . .

# Ajustar permissões
RUN chown -R transcriptor:transcriptor /app

# Mudar para usuário não-root
USER transcriptor

# Criar diretórios de trabalho
RUN mkdir -p /app/output /app/temp

# Definir volumes
VOLUME ["/input", "/output"]

# Variáveis de ambiente padrão
ENV INPUT_DIR=/input
ENV OUTPUT_DIR=/output
ENV TEMP_DIR=/app/temp
ENV HF_HOME=/app/.cache/huggingface
ENV TORCH_HOME=/app/.cache/torch

# Expor porta (para futuras funcionalidades web)
EXPOSE 8000

# Comando padrão
ENTRYPOINT ["python3", "transcrever.py"]
CMD ["--help"]

# Labels para metadata
LABEL maintainer="Transcritor Team"
LABEL version="1.0"
LABEL description="Transcritor com Diarização otimizado para Português Brasileiro"
LABEL gpu.required="false"
LABEL gpu.recommended="true"