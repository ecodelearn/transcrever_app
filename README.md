# 🎙️ Transcritor com Diarização - Português Brasil

Um sistema avançado de transcrição de áudio e vídeo com identificação automática de oradores, otimizado para português brasileiro. Utiliza Whisper da OpenAI para transcrição e PyAnnote para diarização de oradores.

## ✨ Funcionalidades

- 🎯 **Transcrição Precisa**: Utiliza modelos Whisper otimizados para português brasileiro
- 👥 **Identificação de Oradores**: Detecta automaticamente quem está falando
- 🎬 **Suporte Multimídia**: Processa arquivos de áudio (MP3, WAV, M4A, FLAC) e vídeo (MP4, MKV, MOV, AVI, WebM)
- 📝 **Múltiplos Formatos**: Exporta em TXT, JSON e SRT (legendas)
- 🚀 **Aceleração GPU**: Suporte completo para NVIDIA CUDA e Intel GPU
- 📦 **Docker Ready**: Containerização completa para deploy fácil
- 🔧 **Configuração Flexível**: Configurações avançadas via arquivo .env
- 📊 **Interface Rica**: CLI moderna com progresso visual e estatísticas

## 🛠️ Instalação

### Pré-requisitos

1. **Python 3.8+**
2. **FFmpeg** (para processamento de vídeo)
3. **Token do Hugging Face** (gratuito)

### Instalação do FFmpeg

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### CentOS/RHEL/Fedora
```bash
sudo dnf install ffmpeg
# ou
sudo yum install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

#### Windows
1. Baixe o FFmpeg de [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Adicione ao PATH do sistema

### Instalação do Projeto

#### Método 1: Instalação Local

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd transcritor

# Crie um ambiente virtual
python -m venv venv-transcritor

# Ative o ambiente virtual
# Linux/macOS:
source venv-transcritor/bin/activate
# Windows:
venv-transcritor\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

#### Método 2: Docker (Recomendado)

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd transcritor

# Configure o arquivo .env
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Build e execute com Docker Compose
docker-compose up --build
```

## ⚙️ Configuração

### 1. Token do Hugging Face

1. Acesse [https://huggingface.co/](https://huggingface.co/)
2. Crie uma conta gratuita
3. Vá em Settings → Access Tokens
4. Crie um novo token com permissão de leitura
5. Adicione o token ao arquivo `.env`

### 2. Arquivo .env

```bash
# Token de acesso do Hugging Face
HF_TOKEN=seu_token_aqui

# Arquivo de entrada padrão
INPUT_FILE=exemplo.mp4

# Modelo Whisper (tiny, base, small, medium, large, large-v2, large-v3)
WHISPER_MODEL=medium

# Idioma principal (pt para português)
WHISPER_LANGUAGE=pt

# Formato de saída (txt, json, srt ou combinação: txt,json,srt)
OUTPUT_FORMAT=txt

# Diretório de saída
OUTPUT_DIR=output

# Usar GPU se disponível
USE_GPU=true

# Número de oradores (auto para detecção automática)
NUM_SPEAKERS=auto

# Configurações de áudio
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
```

## 🚀 Uso

### Exemplos Básicos

```bash
# Transcrever arquivo específico
python transcrever.py reuniao.mp4

# Usar arquivo configurado no .env
python transcrever.py

# Processar todos arquivos de uma pasta
python transcrever.py pasta-com-audios/

# Especificar formato de saída
python transcrever.py entrevista.wav -f json

# Múltiplos formatos
python transcrever.py podcast.mp3 -f txt,srt,json

# Especificar diretório de saída
python transcrever.py video.mp4 -o resultados/

# Usar modelo específico
python transcrever.py audio.wav -m large-v3
```

### Exemplos Avançados

```bash
# Processamento em lote
python transcrever.py pasta-audios/ -o resultados/ -f txt,srt

# Usar modelo maior para máxima qualidade
python transcrever.py reuniao-importante.mp4 -m large-v3 -f json,srt

# Pipeline completo para produção
python transcrever.py entrevista.mp4 -o producao/ -f txt,json,srt -m large
```

### Uso com Docker

```bash
# Processar arquivo específico
docker-compose run transcritor python transcrever.py /input/audio.mp4

# Processar pasta completa
docker-compose run transcritor python transcrever.py /input/ -o /output/
```

## 📋 Formatos de Saída

### TXT (Padrão)
```
=== TRANSCRIÇÃO COM DIARIZAÇÃO ===

[00:00:05] SPEAKER_00: Bom dia, pessoal. Vamos começar nossa reunião.
[00:00:12] SPEAKER_01: Bom dia! Estou pronto para discutir o projeto.
[00:00:18] SPEAKER_00: Perfeito. Hoje vamos revisar os resultados do último trimestre.
```

### JSON (Estruturado)
```json
[
  {
    "start": "00:00:05",
    "speaker": "SPEAKER_00",
    "text": "Bom dia, pessoal. Vamos começar nossa reunião."
  },
  {
    "start": "00:00:12",
    "speaker": "SPEAKER_01", 
    "text": "Bom dia! Estou pronto para discutir o projeto."
  }
]
```

### SRT (Legendas)
```
1
00:00:05,000 --> 00:00:12,000
SPEAKER_00: Bom dia, pessoal. Vamos começar nossa reunião.

2
00:00:12,000 --> 00:00:18,000
SPEAKER_01: Bom dia! Estou pronto para discutir o projeto.
```

## 🐳 Docker

### Dockerfile

O projeto inclui um Dockerfile otimizado para diferentes cenários:

```dockerfile
# Build para GPU (NVIDIA)
docker build -t transcritor:gpu -f Dockerfile.gpu .

# Build para CPU
docker build -t transcritor:cpu -f Dockerfile.cpu .

# Build universal (detecta automaticamente)
docker build -t transcritor .
```

### Docker Compose

```yaml
# Executar com suporte a GPU
docker-compose -f docker-compose.gpu.yml up

# Executar apenas CPU
docker-compose -f docker-compose.cpu.yml up

# Desenvolvimento
docker-compose -f docker-compose.dev.yml up
```

## 🔧 Configurações Avançadas

### Modelos Whisper Disponíveis

| Modelo | Tamanho | VRAM | Velocidade | Qualidade |
|--------|---------|------|-----------|-----------|
| tiny | 39 MB | ~1 GB | Muito Rápida | Básica |
| base | 74 MB | ~1 GB | Rápida | Boa |
| small | 244 MB | ~2 GB | Média | Muito Boa |
| medium | 769 MB | ~5 GB | Lenta | Excelente |
| large | 1550 MB | ~10 GB | Muito Lenta | Superior |
| large-v2 | 1550 MB | ~10 GB | Muito Lenta | Superior |
| large-v3 | 1550 MB | ~10 GB | Muito Lenta | Máxima |

### Otimizações para Português Brasileiro

1. **Modelo Recomendado**: `medium` ou `large` para melhor precisão
2. **Language Setting**: Sempre usar `WHISPER_LANGUAGE=pt`
3. **Sample Rate**: 16kHz é ideal para fala
4. **Canais**: Mono (1 canal) para economia de recursos

### Performance e Hardware

#### Requisitos Mínimos
- **CPU**: 4 cores, 2.5 GHz
- **RAM**: 8 GB
- **Armazenamento**: 5 GB livres

#### Configuração Recomendada
- **CPU**: 8+ cores, 3.0+ GHz
- **RAM**: 16+ GB
- **GPU**: NVIDIA RTX (qualquer) com 6+ GB VRAM
- **Armazenamento**: SSD com 10+ GB livres

#### Configuração Profissional
- **CPU**: 16+ cores, 3.5+ GHz
- **RAM**: 32+ GB
- **GPU**: NVIDIA RTX 4080/4090 com 12+ GB VRAM
- **Armazenamento**: NVMe SSD com 50+ GB livres

## 📁 Estrutura do Projeto

```
transcritor/
├── 📄 README.md                 # Este arquivo
├── 🐍 transcrever.py           # Script principal
├── ⚙️ .env                     # Configurações (não versionado)
├── 📋 requirements.txt         # Dependências Python
├── 🐳 Dockerfile              # Container principal
├── 🐳 docker-compose.yml      # Orquestração Docker
├── 📁 output/                 # Resultados (criado automaticamente)
├── 📁 examples/               # Arquivos de exemplo
│   ├── 🎵 reuniao-exemplo.mp4
│   ├── 🎵 entrevista-exemplo.wav
│   └── 📋 config-exemplo.yml
├── 📁 scripts/                # Scripts auxiliares
│   ├── 🔧 setup.sh           # Instalação automática
│   ├── 🧪 test.py            # Testes
│   └── 📊 benchmark.py       # Performance
└── 📁 docs/                   # Documentação adicional
    ├── 🇧🇷 INSTALL-PT.md      # Instalação detalhada
    ├── 🔧 ADVANCED.md         # Configurações avançadas
    └── 🐛 TROUBLESHOOTING.md  # Solução de problemas
```

## 🐛 Solução de Problemas

### Erros Comuns

#### 1. "Unable to import 'whisper'"
```bash
# Solução:
pip install --upgrade openai-whisper
```

#### 2. "CUDA out of memory"
```bash
# Solução 1: Usar modelo menor
WHISPER_MODEL=small

# Solução 2: Forçar CPU
USE_GPU=false
```

#### 3. "Token de acesso inválido"
```bash
# Verifique se o token está correto no .env
# Regenere o token no Hugging Face se necessário
```

#### 4. "FFmpeg not found"
```bash
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS:
brew install ffmpeg

# Verificar instalação:
ffmpeg -version
```

#### 5. "Arquivo muito grande"
```bash
# Para arquivos >2GB, use processamento em chunks:
python transcrever.py arquivo-grande.mp4 -m small
```

### Problemas de Performance

#### Áudio com Ruído
- Use ferramentas de pré-processamento como Audacity
- Configure `AUDIO_SAMPLE_RATE=22050` para áudio de baixa qualidade

#### Múltiplos Oradores Não Detectados
```bash
# Force o número de oradores
NUM_SPEAKERS=3  # Substitua pelo número esperado
```

#### Transcrição Imprecisa
1. Use modelo maior: `WHISPER_MODEL=large`
2. Verifique qualidade do áudio
3. Configure idioma: `WHISPER_LANGUAGE=pt`

### Suporte Técnico

Para problemas não listados aqui:

1. ✅ Verifique a seção [Issues](../../issues) do repositório
2. 📚 Consulte a [documentação avançada](docs/ADVANCED.md)
3. 🆘 Abra uma nova issue com:
   - Versão do Python
   - Sistema operacional
   - Comando executado
   - Mensagem de erro completa
   - Arquivo de log (se disponível)

## 📊 Casos de Uso Brasileiros

### 1. Reuniões Corporativas
```bash
# Configuração otimizada para reuniões
WHISPER_MODEL=medium
NUM_SPEAKERS=auto
OUTPUT_FORMAT=txt,srt
```

### 2. Entrevistas Jornalísticas
```bash
# Máxima qualidade para entrevistas
WHISPER_MODEL=large
OUTPUT_FORMAT=json,txt
AUDIO_SAMPLE_RATE=22050
```

### 3. Podcasts
```bash
# Balanceado para conteúdo longo
WHISPER_MODEL=medium
OUTPUT_FORMAT=srt,txt
USE_GPU=true
```

### 4. Aulas e Palestras
```bash
# Otimizado para uma pessoa falando
WHISPER_MODEL=large
NUM_SPEAKERS=1
OUTPUT_FORMAT=txt,srt
```

### 5. Audiências Jurídicas
```bash
# Máxima precisão para contexto legal
WHISPER_MODEL=large-v3
OUTPUT_FORMAT=json,txt,srt
AUDIO_SAMPLE_RATE=22050
```

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

### Diretrizes de Contribuição

- ✅ Mantenha o foco em português brasileiro
- ✅ Teste em diferentes sistemas operacionais
- ✅ Adicione documentação para novas funcionalidades
- ✅ Siga as convenções de código Python (PEP 8)
- ✅ Adicione testes para novas funcionalidades

## 📜 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **OpenAI** pelo modelo Whisper
- **Hugging Face** pelo PyAnnote e hospedagem de modelos
- **Comunidade Python Brasil** pelo feedback e contribuições
- **FFmpeg Team** pela excelente biblioteca de processamento multimídia

## 📈 Roadmap

### Versão 2.0 (Próxima)
- [ ] Interface web interativa
- [ ] API REST para integração
- [ ] Suporte a streaming em tempo real
- [ ] Modelos personalizados para setores específicos

### Versão 2.1
- [ ] Integração com serviços de nuvem (AWS, GCP, Azure)
- [ ] Análise de sentimento em português
- [ ] Detecção automática de idioma (português/espanhol)
- [ ] Exportação para formatos de vídeo com legendas

### Versão 3.0 (Futura)
- [ ] IA generativa para resumos automáticos
- [ ] Reconhecimento de emoções na fala
- [ ] Suporte a múltiplos idiomas simultâneos
- [ ] Dashboard de analytics avançado

---

**🔗 Links Úteis:**
- [Documentação Whisper](https://github.com/openai/whisper)
- [PyAnnote Audio](https://github.com/pyannote/pyannote-audio)
- [Hugging Face](https://huggingface.co/)
- [FFmpeg](https://ffmpeg.org/)

**📧 Contato:** [seu-email@exemplo.com](mailto:seu-email@exemplo.com)

---

<div align="center">

**🇧🇷 Feito com ❤️ para a comunidade brasileira**

</div>