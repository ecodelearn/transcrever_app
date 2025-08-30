"""
🎵 Serviço de Transcrição
Integra o script CLI atual com a API web
"""

import os
import sys
import asyncio
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, Any, Callable, Optional
from datetime import datetime

# Adicionar o diretório raiz ao path para importar o script CLI
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Serviço principal de transcrição."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.cli_script = self.project_root / "transcrever.py"
        
        # Verificar se o script CLI existe
        if not self.cli_script.exists():
            logger.warning(f"Script CLI não encontrado em: {self.cli_script}")
    
    async def transcribe_file(
        self,
        file_path: str,
        model: str = "medium",
        enable_diarization: bool = True,
        language: str = "pt",
        job_id: str = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Transcrever arquivo usando o script CLI atual.
        
        Args:
            file_path: Caminho para o arquivo de áudio
            model: Modelo Whisper a usar
            enable_diarization: Se deve usar diarização
            language: Idioma do áudio
            job_id: ID do job para tracking
            progress_callback: Função para atualizar progresso
        
        Returns:
            Resultado da transcrição em formato estruturado
        """
        
        try:
            start_time = datetime.now()
            
            if progress_callback:
                progress_callback(5, "Validando arquivo de entrada...")
            
            # Validar arquivo
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
            if progress_callback:
                progress_callback(10, "Preparando transcrição...")
            
            # Preparar argumentos para o script CLI
            cmd_args = self._build_cli_command(
                file_path, model, enable_diarization, language, job_id
            )
            
            if progress_callback:
                progress_callback(15, "Iniciando processamento...")
            
            # Executar script CLI
            result = await self._run_cli_transcription(cmd_args, progress_callback)
            
            if progress_callback:
                progress_callback(95, "Processando resultados...")
            
            # Processar resultados
            transcription_result = await self._process_cli_results(
                file_path, result, start_time
            )
            
            if progress_callback:
                progress_callback(100, "Transcrição concluída!")
            
            return transcription_result
            
        except Exception as e:
            logger.error(f"Erro na transcrição: {str(e)}")
            if progress_callback:
                progress_callback(0, f"Erro: {str(e)}")
            raise
    
    def _build_cli_command(
        self,
        file_path: str,
        model: str,
        enable_diarization: bool,
        language: str,
        job_id: str = None
    ) -> list:
        """Construir comando para executar o script CLI."""
        
        cmd = [
            sys.executable,  # python
            str(self.cli_script),
            file_path,
            "--modelo", model,
            "--idioma", language,
            "--formato", "json",  # Sempre gerar JSON para parsing
        ]
        
        if enable_diarization:
            cmd.append("--diarizacao")
        
        if job_id:
            # Usar job_id como prefixo para os arquivos de saída
            output_prefix = f"results/{job_id}"
            cmd.extend(["--output", output_prefix])
        
        # Sempre gerar verbose para capturar progresso
        cmd.append("--verbose")
        
        return cmd
    
    async def _run_cli_transcription(
        self,
        cmd_args: list,
        progress_callback: Optional[Callable] = None
    ) -> subprocess.CompletedProcess:
        """Executar o script CLI de forma assíncrona."""
        
        try:
            # Executar comando de forma assíncrona
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root
            )
            
            # Monitorar progresso se callback fornecido
            if progress_callback:
                asyncio.create_task(
                    self._monitor_progress(process, progress_callback)
                )
            
            # Aguardar conclusão
            stdout, stderr = await process.communicate()
            
            # Verificar se houve erro
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Erro desconhecido"
                raise RuntimeError(f"Script CLI falhou: {error_msg}")
            
            return subprocess.CompletedProcess(
                cmd_args, process.returncode, stdout, stderr
            )
            
        except Exception as e:
            logger.error(f"Erro ao executar CLI: {str(e)}")
            raise
    
    async def _monitor_progress(
        self,
        process: asyncio.subprocess.Process,
        progress_callback: Callable
    ):
        """Monitorar progresso do script CLI."""
        
        progress_stages = {
            "Carregando modelo": 20,
            "Processando áudio": 30,
            "Transcrevendo": 60,
            "Diarização": 80,
            "Salvando": 90
        }
        
        try:
            # Ler saída em tempo real
            while True:
                line = await process.stderr.readline()
                if not line:
                    break
                
                line_text = line.decode('utf-8').strip()
                
                # Procurar por indicadores de progresso
                for stage, progress in progress_stages.items():
                    if stage.lower() in line_text.lower():
                        progress_callback(progress, f"{stage}...")
                        break
                
        except Exception as e:
            logger.warning(f"Erro ao monitorar progresso: {str(e)}")
    
    async def _process_cli_results(
        self,
        original_file: str,
        cli_result: subprocess.CompletedProcess,
        start_time: datetime
    ) -> Dict[str, Any]:
        """Processar resultados do script CLI."""
        
        try:
            # Calcular tempo de processamento
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Procurar arquivos de resultado
            base_name = Path(original_file).stem
            result_files = {
                "json": None,
                "txt": None,
                "srt": None
            }
            
            # Procurar nos diretórios padrão
            search_dirs = [".", "results", str(Path(original_file).parent)]
            
            for search_dir in search_dirs:
                for ext in result_files.keys():
                    pattern = f"{base_name}*.{ext}"
                    matches = list(Path(search_dir).glob(pattern))
                    if matches:
                        result_files[ext] = str(matches[0])
                        break
            
            # Tentar carregar resultado JSON
            transcription_data = None
            if result_files["json"] and os.path.exists(result_files["json"]):
                try:
                    with open(result_files["json"], 'r', encoding='utf-8') as f:
                        transcription_data = json.load(f)
                except Exception as e:
                    logger.warning(f"Erro ao carregar JSON: {e}")
            
            # Se não tiver JSON, criar estrutura básica do TXT
            if not transcription_data and result_files["txt"]:
                transcription_data = await self._parse_txt_result(result_files["txt"])
            
            # Estruturar resultado final
            result = {
                "segments": transcription_data.get("segments", []) if transcription_data else [],
                "speakers": transcription_data.get("speakers", {}) if transcription_data else {},
                "metadata": {
                    "total_duration": transcription_data.get("duration", 0) if transcription_data else 0,
                    "language": transcription_data.get("language", "pt") if transcription_data else "pt",
                    "model_used": transcription_data.get("model", "unknown") if transcription_data else "unknown",
                    "diarization_enabled": bool(transcription_data.get("speakers")) if transcription_data else False,
                    "processing_time": processing_time,
                    "file_size": os.path.getsize(original_file),
                    "speakers_detected": len(transcription_data.get("speakers", {})) if transcription_data else 0,
                    "word_count": self._count_words(transcription_data) if transcription_data else 0,
                    "confidence_avg": self._calculate_avg_confidence(transcription_data) if transcription_data else 0.0
                },
                "files": result_files
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao processar resultados: {str(e)}")
            
            # Retornar resultado mínimo em caso de erro
            return {
                "segments": [],
                "speakers": {},
                "metadata": {
                    "total_duration": 0,
                    "language": "pt",
                    "model_used": "unknown",
                    "diarization_enabled": False,
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "file_size": os.path.getsize(original_file) if os.path.exists(original_file) else 0,
                    "speakers_detected": 0,
                    "word_count": 0,
                    "confidence_avg": 0.0
                },
                "files": {"json": None, "txt": None, "srt": None}
            }
    
    async def _parse_txt_result(self, txt_file: str) -> Dict[str, Any]:
        """Fazer parsing básico do arquivo TXT quando JSON não disponível."""
        
        try:
            segments = []
            speakers = set()
            
            with open(txt_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            segment_id = 1
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Formato esperado: [SPEAKER_XX]: texto
                if line.startswith('[') and ']:' in line:
                    speaker_end = line.find(']:')
                    speaker = line[1:speaker_end]
                    text = line[speaker_end + 2:].strip()
                    
                    speakers.add(speaker)
                    
                    segments.append({
                        "id": f"segment_{segment_id:03d}",
                        "start": "00:00:00.000",  # Não temos timestamps do TXT
                        "end": "00:00:00.000",
                        "duration": 0.0,
                        "speaker": speaker,
                        "text": text,
                        "confidence": 0.8  # Confiança padrão
                    })
                    
                    segment_id += 1
            
            # Criar estrutura de speakers
            speakers_dict = {}
            for speaker in speakers:
                speakers_dict[speaker] = {
                    "speaker_id": speaker,
                    "first_appearance": "00:00:00.000",
                    "total_duration": 0.0,
                    "segment_count": len([s for s in segments if s["speaker"] == speaker]),
                    "confidence": 0.8
                }
            
            return {
                "segments": segments,
                "speakers": speakers_dict,
                "language": "pt",
                "model": "unknown",
                "duration": 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao fazer parsing do TXT: {str(e)}")
            return {"segments": [], "speakers": {}}
    
    def _count_words(self, transcription_data: Dict[str, Any]) -> int:
        """Contar palavras na transcrição."""
        if not transcription_data or "segments" not in transcription_data:
            return 0
        
        total_words = 0
        for segment in transcription_data["segments"]:
            text = segment.get("text", "")
            words = text.split()
            total_words += len(words)
        
        return total_words
    
    def _calculate_avg_confidence(self, transcription_data: Dict[str, Any]) -> float:
        """Calcular confiança média."""
        if not transcription_data or "segments" not in transcription_data:
            return 0.0
        
        segments = transcription_data["segments"]
        if not segments:
            return 0.0
        
        total_confidence = sum(segment.get("confidence", 0.0) for segment in segments)
        return total_confidence / len(segments)
    
    async def get_available_models(self) -> list:
        """Obter lista de modelos disponíveis."""
        return ["tiny", "base", "small", "medium", "large"]
    
    async def validate_audio_file(self, file_path: str) -> Dict[str, Any]:
        """Validar arquivo de áudio."""
        
        try:
            # Verificar se arquivo existe
            if not os.path.exists(file_path):
                return {"valid": False, "error": "Arquivo não encontrado"}
            
            # Verificar extensão
            valid_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.mp4', '.avi', '.mkv']
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext not in valid_extensions:
                return {
                    "valid": False, 
                    "error": f"Extensão não suportada: {file_ext}"
                }
            
            # Verificar tamanho
            file_size = os.path.getsize(file_path)
            max_size = 500 * 1024 * 1024  # 500 MB
            
            if file_size > max_size:
                return {
                    "valid": False,
                    "error": f"Arquivo muito grande: {file_size / 1024 / 1024:.1f} MB (máximo: 500 MB)"
                }
            
            return {
                "valid": True,
                "file_size": file_size,
                "extension": file_ext,
                "estimated_duration": None  # Poderia usar ffprobe aqui
            }
            
        except Exception as e:
            return {"valid": False, "error": f"Erro ao validar arquivo: {str(e)}"}