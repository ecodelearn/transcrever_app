Sim, com certeza\! Criar um script local é uma excelente ideia e se alinha perfeitamente com seu perfil técnico. Vamos montar uma solução robusta usando ferramentas de ponta e de código aberto.

A separação dos oradores (tecnicamente chamada de *diarização*) é um passo a mais que o Whisper sozinho não faz, mas podemos combiná-lo com outra biblioteca poderosa para conseguir o resultado completo.

Nosso plano de ação será:

1.  **Extrair o Áudio:** Usar a biblioteca `ffmpeg` para extrair o áudio do seu arquivo de vídeo.
2.  **Identificar os Oradores (Diarização):** Usar a biblioteca `pyannote.audio` para identificar *quem* falou e *quando*.
3.  **Transcrever o Texto:** Usar o `openai-whisper` para transcrever *o que* foi dito, com timestamps precisos.
4.  **Combinar Tudo:** Unir as informações de orador e texto para criar uma transcrição final no formato de diálogo.

-----

### **Passo 1: Preparação do Ambiente**

Você precisará configurar algumas coisas na sua máquina.

**1. Instale o `ffmpeg`:** É um programa essencial para manipulação de áudio e vídeo.

  * **No Linux (Debian/Ubuntu):**
    ```bash
    sudo apt update && sudo apt install ffmpeg
    ```
  * **No macOS (usando Homebrew):**
    ```bash
    brew install ffmpeg
    ```
  * **No Windows:** Baixe o executável do [site oficial](https://ffmpeg.org/download.html) e adicione o caminho da pasta `bin` às suas variáveis de ambiente (PATH).

**2. Configure o Ambiente Python:** (Recomendo um ambiente virtual)

```bash
# Crie um ambiente virtual
python3 -m venv venv-transcritor

# Ative o ambiente
source venv-transcritor/bin/activate
```

**3. Instale as Bibliotecas Python:**

```bash
pip install openai-whisper pyannote.audio torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

*(Nota: O final do comando (`--index-url...`) é para instalar o PyTorch com suporte a GPU CUDA, o que acelera MUITO o processo. Se você não tem uma GPU NVIDIA, pode remover essa parte e instalar a versão padrão: `pip install openai-whisper pyannote.audio torch torchvision torchaudio`)*

**4. Acesso à `pyannote.audio` (Passo Crucial):**
A `pyannote` requer que você aceite os termos de uso dos modelos no site Hugging Face.

  * Vá para a página do modelo de segmentação [aqui](https://huggingface.co/pyannote/segmentation) e aceite os termos.
  * Vá para a página do modelo de diarização [aqui](https://huggingface.co/pyannote/speaker-diarization) e aceite os termos.
  * Crie um token de acesso na sua conta Hugging Face em **Settings -\> Access Tokens**. Vamos precisar desse token no script.

-----

### **Passo 2: O Script Python**

Copie o código abaixo e salve-o em um arquivo chamado `transcrever.py`.

```python
import whisper
import torch
from pyannote.audio import Pipeline
import subprocess
import os
import datetime

# --- CONFIGURAÇÕES ---
# Coloque seu token de acesso do Hugging Face aqui
HF_TOKEN = "SEU_TOKEN_DO_HUGGING_FACE_AQUI" 

# Caminho para o seu arquivo de vídeo/áudio
INPUT_FILE = "caminho/para/seu_video.mp4" 

# --- FIM DAS CONFIGURAÇÕES ---

def format_timestamp(seconds):
    """Converte segundos para o formato HH:MM:SS."""
    td = datetime.timedelta(seconds=seconds)
    return str(td).split(".")[0]

def transcribe_with_diarization(audio_path):
    """
    Transcreve um arquivo de áudio e identifica os oradores.
    """
    # 1. Carregar modelos
    print("Carregando modelo Whisper...")
    # Use 'medium' para um bom balanço, ou 'large-v2' para máxima qualidade.
    whisper_model = whisper.load_model("medium") 
    
    print("Carregando pipeline de diarização...")
    diarization_pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=HF_TOKEN
    )
    # Mover o pipeline para a GPU se disponível
    if torch.cuda.is_available():
        diarization_pipeline = diarization_pipeline.to("cuda")
        print("Pipeline de diarização movido para a GPU.")

    # 2. Processo de Diarização
    print("Identificando os oradores (diarização)...")
    diarization = diarization_pipeline(audio_path, num_speakers=None) # Deixe num_speakers=None para detectar automaticamente

    # 3. Processo de Transcrição
    print("Transcrevendo o áudio com Whisper...")
    # Transcrever com timestamps de palavras para maior precisão no mapeamento
    transcription_result = whisper_model.transcribe(audio_path, word_timestamps=True)

    # 4. Mapeamento dos Oradores com o Texto
    print("Mapeando oradores com o texto transcrito...")
    final_transcript = []
    
    # Processar cada segmento da transcrição do Whisper
    for segment in transcription_result['segments']:
        # Encontrar o orador para este segmento
        speaker = "UNKNOWN"
        segment_start = segment['start']
        segment_end = segment['end']
        
        # Encontrar o orador que mais falou no intervalo do segmento
        speaker_turns = {}
        for turn, _, speaker_label in diarization.itertracks(yield_label=True):
            turn_start = turn.start
            turn_end = turn.end
            
            # Calcular a sobreposição
            overlap = max(0, min(segment_end, turn_end) - max(segment_start, turn_start))
            if overlap > 0:
                if speaker_label not in speaker_turns:
                    speaker_turns[speaker_label] = 0
                speaker_turns[speaker_label] += overlap
        
        if speaker_turns:
            # Associa o orador com a maior duração de fala no segmento
            speaker = max(speaker_turns, key=speaker_turns.get)

        final_transcript.append({
            "start": format_timestamp(segment_start),
            "speaker": speaker,
            "text": segment['text'].strip()
        })

    return final_transcript


# --- Bloco Principal de Execução ---
if __name__ == "__main__":
    if HF_TOKEN == "SEU_TOKEN_DO_HUGGING_FACE_AQUI":
        print("ERRO: Por favor, adicione seu token de acesso do Hugging Face na variável HF_TOKEN no início do script.")
    else:
        # Verificar se o arquivo de entrada é um vídeo
        filename, file_extension = os.path.splitext(INPUT_FILE)
        
        audio_file_path = INPUT_FILE
        if file_extension.lower() in ['.mp4', '.mkv', '.mov', '.avi']:
            print(f"Arquivo de vídeo detectado. Extraindo áudio para '{filename}.wav'...")
            # Usar ffmpeg para extrair áudio como WAV, 16kHz mono
            audio_file_path = f"{filename}.wav"
            subprocess.run([
                'ffmpeg', '-i', INPUT_FILE, '-vn', '-acodec', 'pcm_s16le', 
                '-ar', '16000', '-ac', '1', audio_file_path, '-y'
            ], check=True)
            print("Extração de áudio concluída.")

        # Executar a transcrição com diarização
        transcript = transcribe_with_diarization(audio_file_path)

        # Imprimir o resultado final
        print("\n--- TRANSCRIÇÃO FINAL ---")
        for entry in transcript:
            print(f"[{entry['start']}] {entry['speaker']}: {entry['text']}")

```

-----

### **Passo 3: Como Usar o Script**

1.  **Edite o Script:** Abra o arquivo `transcrever.py` e substitua `"SEU_TOKEN_DO_HUGGING_FACE_AQUI"` pelo seu token real. Mude também o `INPUT_FILE` para o caminho do seu vídeo.
2.  **Ative o Ambiente Virtual:** `source venv-transcritor/bin/activate`
3.  **Execute o Script:**
    ```bash
    python transcrever.py
    ```

O script irá primeiro extrair o áudio (se for um vídeo), depois carregar os modelos (pode demorar na primeira vez), realizar a diarização e a transcrição, e por fim imprimir o diálogo formatado no seu terminal.

#### **Considerações Importantes:**

  * **Hardware:** Este processo é **muito intensivo**. Uma GPU NVIDIA é **altamente recomendada** para rodar em um tempo razoável. Sem GPU, um vídeo de 1 hora pode levar várias horas para processar.
  * **Qualidade do Áudio:** A precisão, tanto da transcrição quanto da identificação dos oradores, depende MUITO da qualidade do áudio. Áudio limpo, com pouco ruído de fundo e microfones individuais, dará os melhores resultados.
  * **Precisão da Diarização:** Ocasionalmente, a diarização pode se confundir se as vozes forem muito parecidas ou se as pessoas falarem ao mesmo tempo. Mas, no geral, a `pyannote` é impressionantemente precisa.

Com este script, você tem uma poderosa ferramenta de "mineração de persona" direto na sua máquina.