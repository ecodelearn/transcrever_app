import whisper
import torch
from pyannote.audio import Pipeline
import subprocess
import os
import datetime
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

# Carregar variáveis de ambiente
load_dotenv()

console = Console()

# --- CONFIGURAÇÕES A PARTIR DO .ENV ---
HF_TOKEN = os.getenv("HF_TOKEN")
INPUT_FILE = os.getenv("INPUT_FILE", "exemplo.mp4")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "medium")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "pt")
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "txt")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
USE_GPU = os.getenv("USE_GPU", "true").lower() == "true"
NUM_SPEAKERS = os.getenv("NUM_SPEAKERS", "auto")
AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
AUDIO_CHANNELS = int(os.getenv("AUDIO_CHANNELS", "1"))

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


def save_transcript(transcript, output_path, format_type="txt"):
    """
    Salva a transcrição em diferentes formatos.
    """
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    
    if format_type.lower() == "txt":
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=== TRANSCRIÇÃO COM DIARIZAÇÃO ===\n\n")
            for entry in transcript:
                f.write(f"[{entry['start']}] {entry['speaker']}: {entry['text']}\n")
    
    elif format_type.lower() == "json":
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2)
    
    elif format_type.lower() == "srt":
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, entry in enumerate(transcript, 1):
                start_time = entry['start']
                # Calcular tempo de fim (aproximado)
                if i < len(transcript):
                    end_time = transcript[i]['start']
                else:
                    # Para o último segmento, adicionar 3 segundos
                    end_time = format_timestamp(
                        sum(int(x) * 60**j for j, x in enumerate(reversed(start_time.split(':')))) + 3
                    )
                
                f.write(f"{i}\n")
                f.write(f"{start_time.replace(':', ',')} --> {end_time.replace(':', ',')}\n")
                f.write(f"{entry['speaker']}: {entry['text']}\n\n")

def process_single_file(input_file, output_dir=None):
    """
    Processa um único arquivo de áudio/vídeo.
    """
    if not os.path.exists(input_file):
        console.print(f"[red]❌ Arquivo não encontrado: {input_file}[/red]")
        return None
    
    console.print(f"[blue]🎵 Processando: {input_file}[/blue]")
    
    # Configurar diretório de saída
    if output_dir is None:
        output_dir = OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    # Verificar se o arquivo de entrada é um vídeo
    filename = Path(input_file).stem
    file_extension = Path(input_file).suffix
    
    audio_file_path = input_file
    if file_extension.lower() in ['.mp4', '.mkv', '.mov', '.avi', '.webm']:
        console.print(f"[yellow]🎬 Arquivo de vídeo detectado. Extraindo áudio...[/yellow]")
        audio_file_path = os.path.join(output_dir, f"{filename}.wav")
        
        try:
            subprocess.run([
                'ffmpeg', '-i', input_file, '-vn', '-acodec', 'pcm_s16le',
                '-ar', str(AUDIO_SAMPLE_RATE), '-ac', str(AUDIO_CHANNELS),
                audio_file_path, '-y'
            ], check=True, capture_output=True)
            console.print("[green]✅ Extração de áudio concluída.[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Erro na extração de áudio: {e}[/red]")
            return None

    # Executar a transcrição com diarização
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Transcrevendo e identificando oradores...", total=None)
        transcript = transcribe_with_diarization(audio_file_path)
        progress.remove_task(task)

    # Salvar em diferentes formatos
    base_output_path = os.path.join(output_dir, filename)
    
    formats = OUTPUT_FORMAT.split(',') if ',' in OUTPUT_FORMAT else [OUTPUT_FORMAT]
    
    for fmt in formats:
        fmt = fmt.strip().lower()
        output_file = f"{base_output_path}.{fmt}"
        save_transcript(transcript, output_file, fmt)
        console.print(f"[green]💾 Salvo: {output_file}[/green]")
    
    return transcript

def main():
    """
    Função principal com interface CLI melhorada.
    """
    parser = argparse.ArgumentParser(
        description="🎙️ Transcritor com Diarização - Português Brasil",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python transcrever.py                           # Usa arquivo padrão do .env
  python transcrever.py arquivo.mp4               # Transcreve arquivo específico
  python transcrever.py -i pasta/               # Processa todos arquivos da pasta
  python transcrever.py arquivo.wav -f json,srt  # Múltiplos formatos de saída
        """
    )
    
    parser.add_argument("input", nargs="?", help="Arquivo de entrada ou diretório")
    parser.add_argument("-i", "--input", dest="input_path", help="Arquivo de entrada ou diretório")
    parser.add_argument("-o", "--output", help="Diretório de saída")
    parser.add_argument("-f", "--format", choices=["txt", "json", "srt"],
                       help="Formato de saída")
    parser.add_argument("-m", "--model", help="Modelo Whisper (tiny, base, small, medium, large)")
    parser.add_argument("--batch", action="store_true", help="Processar múltiplos arquivos")
    
    args = parser.parse_args()
    
    # Mostrar banner
    console.print(Panel.fit(
        "[bold blue]🎙️ TRANSCRITOR COM DIARIZAÇÃO[/bold blue]\n"
        "[dim]Otimizado para Português Brasileiro[/dim]",
        border_style="blue"
    ))
    
    # Verificar token
    if not HF_TOKEN:
        console.print(Panel(
            "[red]❌ ERRO: Token do Hugging Face não encontrado![/red]\n\n"
            "Por favor, configure seu token no arquivo .env:\n"
            "[bold]HF_TOKEN=seu_token_aqui[/bold]",
            border_style="red",
            title="Configuração Necessária"
        ))
        return
    
    # Determinar arquivo de entrada
    input_file = args.input or args.input_path or INPUT_FILE
    output_dir = args.output or OUTPUT_DIR
    
    # Configurar formato de saída
    global OUTPUT_FORMAT
    if args.format:
        OUTPUT_FORMAT = args.format
    
    # Configurar modelo Whisper
    global WHISPER_MODEL
    if args.model:
        WHISPER_MODEL = args.model
    
    # Processar arquivo(s)
    if os.path.isdir(input_file):
        # Processar diretório
        audio_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.mp4', '.mkv', '.mov', '.avi', '.webm']
        files = [f for f in os.listdir(input_file)
                if any(f.lower().endswith(ext) for ext in audio_extensions)]
        
        if not files:
            console.print(f"[red]❌ Nenhum arquivo de áudio/vídeo encontrado em: {input_file}[/red]")
            return
        
        console.print(f"[blue]📁 Processando {len(files)} arquivo(s)...[/blue]")
        
        for file in files:
            file_path = os.path.join(input_file, file)
            process_single_file(file_path, output_dir)
    else:
        # Processar arquivo único
        transcript = process_single_file(input_file, output_dir)
        
        if transcript:
            # Mostrar estatísticas
            table = Table(title="📊 Estatísticas da Transcrição")
            table.add_column("Métrica", style="cyan")
            table.add_column("Valor", style="magenta")
            
            speakers = set(entry['speaker'] for entry in transcript)
            total_segments = len(transcript)
            
            table.add_row("Total de Segmentos", str(total_segments))
            table.add_row("Oradores Identificados", str(len(speakers)))
            table.add_row("Lista de Oradores", ", ".join(sorted(speakers)))
            
            console.print(table)

# --- Bloco Principal de Execução ---
if __name__ == "__main__":
    main()