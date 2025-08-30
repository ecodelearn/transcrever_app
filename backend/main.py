"""
🚀 Transcritor API - FastAPI Backend
Sistema de transcrição com diarização otimizado para RTX 3060
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import torch
import os
from pathlib import Path
import uuid
from datetime import datetime
from typing import Optional, List
import asyncio
import aiofiles

# Configurações
from app.core.config import get_settings
from app.models.job import JobStatus, JobResponse, TranscriptionResult
from app.services.transcription_service import TranscriptionService

settings = get_settings()

# Criar instância FastAPI
app = FastAPI(
    title="Transcritor API",
    description="Sistema de transcrição com diarização para Português Brasileiro",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar diretórios necessários
os.makedirs("uploads", exist_ok=True)
os.makedirs("results", exist_ok=True)

# Servir arquivos estáticos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/results", StaticFiles(directory="results"), name="results")

# Instância do serviço de transcrição
transcription_service = TranscriptionService()

# Jobs em memória (depois migrar para Redis/Database)
jobs_db = {}


@app.get("/")
async def root():
    """Endpoint raiz - informações da API."""
    return {
        "message": "Transcritor API - Sistema de Transcrição com Diarização",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check com informações do sistema."""
    gpu_available = torch.cuda.is_available()
    gpu_name = None
    gpu_memory = None
    
    if gpu_available:
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "gpu": {
            "available": gpu_available,
            "name": gpu_name,
            "memory_gb": round(gpu_memory, 1) if gpu_memory else None,
            "cuda_version": torch.version.cuda if gpu_available else None
        },
        "environment": settings.ENVIRONMENT,
        "models_available": ["tiny", "base", "small", "medium", "large"],
        "active_jobs": len([j for j in jobs_db.values() if j["status"] == "processing"])
    }


@app.post("/jobs/", response_model=JobResponse)
async def create_transcription_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model: str = "medium",
    enable_diarization: bool = True,
    language: str = "pt"
):
    """
    Criar novo job de transcrição.
    
    Args:
        file: Arquivo de áudio/vídeo para transcrever
        model: Modelo Whisper (tiny, base, small, medium, large)
        enable_diarization: Ativar identificação de oradores
        language: Idioma do áudio (pt para português)
    """
    
    # Validar arquivo
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome do arquivo é obrigatório")
    
    # Validar modelo
    available_models = ["tiny", "base", "small", "medium", "large"]
    if model not in available_models:
        raise HTTPException(
            status_code=400, 
            detail=f"Modelo '{model}' não disponível. Use: {available_models}"
        )
    
    # Gerar ID único para o job
    job_id = str(uuid.uuid4())
    
    # Salvar arquivo
    file_extension = Path(file.filename).suffix.lower()
    filename = f"{job_id}{file_extension}"
    file_path = f"uploads/{filename}"
    
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")
    
    # Criar job
    job_data = {
        "job_id": job_id,
        "status": JobStatus.QUEUED,
        "created_at": datetime.utcnow().isoformat(),
        "filename": file.filename,
        "file_path": file_path,
        "model": model,
        "enable_diarization": enable_diarization,
        "language": language,
        "progress": 0,
        "message": "Job criado, aguardando processamento"
    }
    
    jobs_db[job_id] = job_data
    
    # Adicionar task para processamento em background
    background_tasks.add_task(
        process_transcription_job, 
        job_id, 
        file_path, 
        model, 
        enable_diarization, 
        language
    )
    
    return JobResponse(**job_data)


@app.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """Obter status de um job específico."""
    
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    return JobResponse(**jobs_db[job_id])


@app.get("/jobs/", response_model=List[JobResponse])
async def list_jobs(limit: int = 50, status: Optional[JobStatus] = None):
    """Listar jobs com filtros opcionais."""
    
    jobs = list(jobs_db.values())
    
    # Filtrar por status se especificado
    if status:
        jobs = [job for job in jobs if job["status"] == status]
    
    # Ordenar por data de criação (mais recentes primeiro)
    jobs.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Limitar resultados
    jobs = jobs[:limit]
    
    return [JobResponse(**job) for job in jobs]


@app.get("/jobs/{job_id}/download/{format}")
async def download_result(job_id: str, format: str):
    """
    Download dos resultados da transcrição.
    
    Args:
        job_id: ID do job
        format: Formato do arquivo (txt, json, srt)
    """
    
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job = jobs_db[job_id]
    
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job ainda não foi concluído")
    
    # Validar formato
    if format not in ["txt", "json", "srt"]:
        raise HTTPException(status_code=400, detail="Formato deve ser: txt, json ou srt")
    
    # Caminho do arquivo de resultado
    result_file = f"results/{job_id}.{format}"
    
    if not os.path.exists(result_file):
        raise HTTPException(status_code=404, detail=f"Arquivo {format} não encontrado")
    
    return FileResponse(
        result_file,
        media_type="application/octet-stream",
        filename=f"{job['filename']}_transcricao.{format}"
    )


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Deletar job e arquivos associados."""
    
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job = jobs_db[job_id]
    
    # Remover arquivos
    try:
        if os.path.exists(job["file_path"]):
            os.remove(job["file_path"])
        
        # Remover resultados
        for ext in ["txt", "json", "srt"]:
            result_file = f"results/{job_id}.{ext}"
            if os.path.exists(result_file):
                os.remove(result_file)
    except Exception as e:
        # Log error but don't fail the request
        print(f"Erro ao remover arquivos: {e}")
    
    # Remover do banco em memória
    del jobs_db[job_id]
    
    return {"message": f"Job {job_id} removido com sucesso"}


async def process_transcription_job(
    job_id: str, 
    file_path: str, 
    model: str, 
    enable_diarization: bool, 
    language: str
):
    """
    Processar job de transcrição em background.
    
    Esta função roda em background e atualiza o status do job.
    """
    
    try:
        # Atualizar status para processando
        jobs_db[job_id]["status"] = JobStatus.PROCESSING
        jobs_db[job_id]["message"] = "Iniciando processamento..."
        jobs_db[job_id]["started_at"] = datetime.utcnow().isoformat()
        
        # Processar transcrição
        result = await transcription_service.transcribe_file(
            file_path=file_path,
            model=model,
            enable_diarization=enable_diarization,
            language=language,
            job_id=job_id,
            progress_callback=lambda progress, message: update_job_progress(job_id, progress, message)
        )
        
        # Salvar resultados
        await save_transcription_results(job_id, result)
        
        # Atualizar status para concluído
        jobs_db[job_id]["status"] = JobStatus.COMPLETED
        jobs_db[job_id]["progress"] = 100
        jobs_db[job_id]["message"] = "Transcrição concluída com sucesso!"
        jobs_db[job_id]["completed_at"] = datetime.utcnow().isoformat()
        jobs_db[job_id]["result"] = result
        
    except Exception as e:
        # Atualizar status para erro
        jobs_db[job_id]["status"] = JobStatus.FAILED
        jobs_db[job_id]["message"] = f"Erro durante processamento: {str(e)}"
        jobs_db[job_id]["failed_at"] = datetime.utcnow().isoformat()
        jobs_db[job_id]["error"] = str(e)


def update_job_progress(job_id: str, progress: int, message: str):
    """Atualizar progresso do job."""
    if job_id in jobs_db:
        jobs_db[job_id]["progress"] = progress
        jobs_db[job_id]["message"] = message


async def save_transcription_results(job_id: str, result: TranscriptionResult):
    """Salvar resultados em diferentes formatos."""
    
    # Salvar como JSON
    import json
    async with aiofiles.open(f"results/{job_id}.json", 'w', encoding='utf-8') as f:
        await f.write(json.dumps(result.dict(), ensure_ascii=False, indent=2))
    
    # Salvar como TXT
    async with aiofiles.open(f"results/{job_id}.txt", 'w', encoding='utf-8') as f:
        for segment in result.segments:
            speaker = segment.get("speaker", "SPEAKER_UNKNOWN")
            text = segment.get("text", "")
            await f.write(f"[{speaker}]: {text}\n")
    
    # Salvar como SRT
    async with aiofiles.open(f"results/{job_id}.srt", 'w', encoding='utf-8') as f:
        for i, segment in enumerate(result.segments, 1):
            start = segment.get("start", "00:00:00.000")
            end = segment.get("end", "00:00:00.000")
            text = segment.get("text", "")
            
            await f.write(f"{i}\n")
            await f.write(f"{start} --> {end}\n")
            await f.write(f"{text}\n\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )