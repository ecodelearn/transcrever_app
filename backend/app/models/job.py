"""
📊 Modelos de dados para jobs de transcrição
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class JobStatus(str, Enum):
    """Status possíveis de um job de transcrição."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TranscriptionSegment(BaseModel):
    """Segmento individual de transcrição."""
    id: str = Field(..., description="ID único do segmento")
    start: str = Field(..., description="Tempo de início (HH:MM:SS.mmm)")
    end: str = Field(..., description="Tempo de fim (HH:MM:SS.mmm)")
    duration: float = Field(..., description="Duração em segundos")
    speaker: str = Field(..., description="ID do orador (SPEAKER_00, SPEAKER_01, etc)")
    text: str = Field(..., description="Texto transcrito")
    confidence: float = Field(..., description="Confiança da transcrição (0-1)")
    words: Optional[List[Dict[str, Any]]] = Field(None, description="Palavras individuais com timestamps")
    language: str = Field("pt", description="Idioma detectado")


class SpeakerInfo(BaseModel):
    """Informações sobre um orador identificado."""
    speaker_id: str = Field(..., description="ID do orador")
    first_appearance: str = Field(..., description="Primeira aparição (timestamp)")
    total_duration: float = Field(..., description="Tempo total de fala em segundos")
    segment_count: int = Field(..., description="Número de segmentos")
    confidence: float = Field(..., description="Confiança média da diarização")


class TranscriptionMetadata(BaseModel):
    """Metadados da transcrição."""
    total_duration: float = Field(..., description="Duração total do áudio em segundos")
    language: str = Field(..., description="Idioma principal detectado")
    model_used: str = Field(..., description="Modelo Whisper utilizado")
    diarization_enabled: bool = Field(..., description="Se diarização foi habilitada")
    processing_time: float = Field(..., description="Tempo de processamento em segundos")
    file_size: int = Field(..., description="Tamanho do arquivo original em bytes")
    audio_quality: Optional[str] = Field(None, description="Qualidade do áudio detectada")
    speakers_detected: int = Field(0, description="Número de oradores detectados")
    word_count: int = Field(0, description="Número total de palavras")
    confidence_avg: float = Field(0.0, description="Confiança média geral")


class TranscriptionResult(BaseModel):
    """Resultado completo da transcrição."""
    segments: List[TranscriptionSegment] = Field(..., description="Segmentos de transcrição")
    speakers: Dict[str, SpeakerInfo] = Field(default_factory=dict, description="Informações dos oradores")
    metadata: TranscriptionMetadata = Field(..., description="Metadados da transcrição")
    
    @property
    def full_text(self) -> str:
        """Texto completo da transcrição."""
        return " ".join([segment.text for segment in self.segments])
    
    @property
    def speakers_list(self) -> List[str]:
        """Lista de IDs dos oradores."""
        return list(self.speakers.keys())


class JobRequest(BaseModel):
    """Request para criar um novo job."""
    model: str = Field("medium", description="Modelo Whisper (tiny, base, small, medium, large)")
    enable_diarization: bool = Field(True, description="Habilitar diarização de oradores")
    language: str = Field("pt", description="Idioma do áudio")
    
    class Config:
        schema_extra = {
            "example": {
                "model": "medium",
                "enable_diarization": True,
                "language": "pt"
            }
        }


class JobResponse(BaseModel):
    """Response com informações do job."""
    job_id: str = Field(..., description="ID único do job")
    status: JobStatus = Field(..., description="Status atual do job")
    created_at: str = Field(..., description="Data/hora de criação")
    started_at: Optional[str] = Field(None, description="Data/hora de início do processamento")
    completed_at: Optional[str] = Field(None, description="Data/hora de conclusão")
    failed_at: Optional[str] = Field(None, description="Data/hora de falha")
    
    filename: str = Field(..., description="Nome do arquivo original")
    file_path: str = Field(..., description="Caminho do arquivo no servidor")
    model: str = Field(..., description="Modelo Whisper utilizado")
    enable_diarization: bool = Field(..., description="Se diarização está habilitada")
    language: str = Field(..., description="Idioma configurado")
    
    progress: int = Field(0, description="Progresso do processamento (0-100)")
    message: str = Field("", description="Mensagem de status atual")
    
    result: Optional[TranscriptionResult] = Field(None, description="Resultado da transcrição (quando concluído)")
    error: Optional[str] = Field(None, description="Mensagem de erro (se falhou)")
    
    # URLs para download (quando concluído)
    download_urls: Optional[Dict[str, str]] = Field(None, description="URLs para download dos resultados")
    
    @property
    def is_completed(self) -> bool:
        """Verifica se o job foi concluído."""
        return self.status == JobStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Verifica se o job falhou."""
        return self.status == JobStatus.FAILED
    
    @property
    def is_processing(self) -> bool:
        """Verifica se o job está sendo processado."""
        return self.status == JobStatus.PROCESSING
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "created_at": "2024-01-15T10:30:00Z",
                "completed_at": "2024-01-15T10:35:00Z",
                "filename": "reuniao_empresa.mp3",
                "model": "medium",
                "enable_diarization": True,
                "language": "pt",
                "progress": 100,
                "message": "Transcrição concluída com sucesso!",
                "download_urls": {
                    "txt": "/jobs/550e8400-e29b-41d4-a716-446655440000/download/txt",
                    "json": "/jobs/550e8400-e29b-41d4-a716-446655440000/download/json",
                    "srt": "/jobs/550e8400-e29b-41d4-a716-446655440000/download/srt"
                }
            }
        }


class JobsList(BaseModel):
    """Lista de jobs com metadados."""
    jobs: List[JobResponse] = Field(..., description="Lista de jobs")
    total: int = Field(..., description="Total de jobs")
    limit: int = Field(..., description="Limite aplicado")
    offset: int = Field(0, description="Offset aplicado")
    
    class Config:
        schema_extra = {
            "example": {
                "jobs": [],
                "total": 5,
                "limit": 50,
                "offset": 0
            }
        }


class ProgressUpdate(BaseModel):
    """Atualização de progresso via WebSocket."""
    job_id: str = Field(..., description="ID do job")
    progress: int = Field(..., description="Progresso (0-100)")
    message: str = Field(..., description="Mensagem de status")
    stage: Optional[str] = Field(None, description="Etapa atual (audio_extraction, transcription, etc)")
    estimated_remaining: Optional[int] = Field(None, description="Tempo estimado restante em segundos")
    
    class Config:
        schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "progress": 45,
                "message": "Processando transcrição...",
                "stage": "transcription",
                "estimated_remaining": 120
            }
        }


class ErrorResponse(BaseModel):
    """Response padrão para erros."""
    error: str = Field(..., description="Tipo do erro")
    message: str = Field(..., description="Mensagem de erro")
    details: Optional[str] = Field(None, description="Detalhes adicionais")
    job_id: Optional[str] = Field(None, description="ID do job relacionado")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "PROCESSING_ERROR",
                "message": "Erro durante o processamento do áudio",
                "details": "Arquivo corrompido ou formato não suportado",
                "job_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class HealthResponse(BaseModel):
    """Response do health check."""
    status: str = Field(..., description="Status da API")
    timestamp: str = Field(..., description="Timestamp da verificação")
    gpu: Dict[str, Any] = Field(..., description="Informações da GPU")
    environment: str = Field(..., description="Ambiente atual")
    models_available: List[str] = Field(..., description="Modelos disponíveis")
    active_jobs: int = Field(..., description="Jobs ativos")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "gpu": {
                    "available": True,
                    "name": "NVIDIA GeForce RTX 3060",
                    "memory_gb": 12.0,
                    "cuda_version": "11.8"
                },
                "environment": "development",
                "models_available": ["tiny", "base", "small", "medium", "large"],
                "active_jobs": 2
            }
        }