# 🌐 API REST - Transcritor com Diarização

## 📋 Visão Geral

A API REST do Transcritor oferece endpoints completos para integração programática com o sistema de transcrição. Desenvolvida com FastAPI, oferece documentação automática, validação de dados e performance otimizada.

### **Base URL**
```
https://api.transcritor.com.br/api/v1
```

### **Documentação Interativa**
- **Swagger UI**: `https://api.transcritor.com.br/docs`
- **ReDoc**: `https://api.transcritor.com.br/redoc`
- **OpenAPI JSON**: `https://api.transcritor.com.br/openapi.json`

---

## 🔐 Autenticação

### **Bearer Token (JWT)**
```http
Authorization: Bearer <seu_jwt_token>
```

### **API Key (Header)**
```http
X-API-Key: <sua_api_key>
```

### **Obter Token**
```http
POST /auth/token
Content-Type: application/json

{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

**Resposta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "def502005a8..."
}
```

---

## 📁 Upload de Arquivos

### **POST /upload**
Faz upload de arquivo de áudio ou vídeo para transcrição.

**Parâmetros:**
- `file` (obrigatório): Arquivo multipart/form-data
- `filename` (opcional): Nome personalizado para o arquivo
- `metadata` (opcional): JSON com metadados adicionais

**Exemplo:**
```bash
curl -X POST "https://api.transcritor.com.br/api/v1/upload" \
  -H "Authorization: Bearer <token>" \
  -F "file=@reuniao.mp4" \
  -F "filename=reuniao_diretoria_2024.mp4" \
  -F "metadata={\"tipo\":\"reuniao\",\"participantes\":3}"
```

**Resposta (201 Created):**
```json
{
  "file_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "filename": "reuniao_diretoria_2024.mp4",
  "size": 157286400,
  "duration": 3600,
  "mime_type": "video/mp4",
  "upload_url": "/files/f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "created_at": "2024-01-15T10:30:00Z",
  "metadata": {
    "tipo": "reuniao",
    "participantes": 3
  }
}
```

### **Limitações de Upload**
- **Tamanho máximo**: 2GB por arquivo
- **Formatos suportados**: MP3, WAV, M4A, FLAC, OGG, MP4, MKV, MOV, AVI, WebM
- **Taxa de upload**: 10 arquivos por minuto (free), 100 por minuto (premium)

---

## 🎙️ Transcrição

### **POST /transcribe**
Inicia o processo de transcrição de um arquivo.

**Body:**
```json
{
  "file_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "config": {
    "model": "medium",
    "language": "pt",
    "num_speakers": "auto",
    "output_formats": ["txt", "json", "srt"],
    "speaker_detection": {
      "min_speakers": 1,
      "max_speakers": 10
    },
    "quality": {
      "enhance_audio": true,
      "noise_reduction": true,
      "normalize_volume": true
    },
    "preprocessing": {
      "remove_silence": false,
      "split_long_audio": true,
      "chunk_duration": 600
    }
  },
  "callback_url": "https://webhook.exemplo.com/transcription_complete",
  "priority": "normal"
}
```

**Resposta (202 Accepted):**
```json
{
  "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
  "status": "queued",
  "file_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "estimated_duration": 1800,
  "position_in_queue": 3,
  "created_at": "2024-01-15T10:35:00Z",
  "config": { /* configuração aplicada */ }
}
```

### **Configurações Disponíveis**

#### **Modelos Whisper**
```json
{
  "models": [
    {
      "name": "tiny",
      "size": "39 MB",
      "vram": "~1 GB",
      "speed": "very_fast",
      "quality": "basic",
      "languages": ["pt", "en", "es"]
    },
    {
      "name": "base",
      "size": "74 MB",
      "vram": "~1 GB", 
      "speed": "fast",
      "quality": "good",
      "languages": ["pt", "en", "es"]
    },
    {
      "name": "small",
      "size": "244 MB",
      "vram": "~2 GB",
      "speed": "medium",
      "quality": "very_good",
      "languages": ["pt", "en", "es"]
    },
    {
      "name": "medium",
      "size": "769 MB",
      "vram": "~5 GB",
      "speed": "slow",
      "quality": "excellent",
      "languages": ["pt", "en", "es"],
      "recommended": true
    },
    {
      "name": "large",
      "size": "1550 MB",
      "vram": "~10 GB",
      "speed": "very_slow",
      "quality": "superior",
      "languages": ["multilingual"]
    },
    {
      "name": "large-v3",
      "size": "1550 MB",
      "vram": "~10 GB",
      "speed": "very_slow", 
      "quality": "maximum",
      "languages": ["multilingual"],
      "latest": true
    }
  ]
}
```

#### **Templates de Configuração**
```json
{
  "presets": {
    "reuniao_corporativa": {
      "model": "medium",
      "num_speakers": "auto",
      "min_speakers": 2,
      "max_speakers": 8,
      "enhance_audio": true,
      "output_formats": ["txt", "json"],
      "description": "Otimizado para reuniões empresariais"
    },
    "entrevista_jornalistica": {
      "model": "large",
      "num_speakers": 2,
      "enhance_audio": true,
      "noise_reduction": true,
      "output_formats": ["txt", "json", "srt"],
      "description": "Máxima qualidade para entrevistas"
    },
    "podcast": {
      "model": "medium",
      "num_speakers": "auto",
      "min_speakers": 2,
      "max_speakers": 5,
      "split_long_audio": true,
      "output_formats": ["txt", "srt", "json"],
      "description": "Otimizado para conteúdo longo"
    },
    "palestra": {
      "model": "medium",
      "num_speakers": 1,
      "enhance_audio": true,
      "remove_silence": true,
      "output_formats": ["txt", "srt"],
      "description": "Uma pessoa falando"
    }
  }
}
```

---

## 📊 Gerenciamento de Jobs

### **GET /jobs**
Lista todos os jobs de transcrição do usuário.

**Parâmetros de Query:**
- `status` (opcional): `queued`, `processing`, `completed`, `failed`
- `limit` (opcional): Número de resultados (padrão: 20, máximo: 100)
- `offset` (opcional): Paginação (padrão: 0)
- `sort` (opcional): `created_at`, `updated_at`, `duration`
- `order` (opcional): `asc`, `desc`

**Exemplo:**
```bash
GET /jobs?status=completed&limit=10&sort=created_at&order=desc
```

**Resposta:**
```json
{
  "jobs": [
    {
      "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
      "status": "completed",
      "file_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "filename": "reuniao_diretoria_2024.mp4",
      "duration": 3600,
      "processing_time": 720,
      "created_at": "2024-01-15T10:35:00Z",
      "completed_at": "2024-01-15T10:47:00Z",
      "config": {
        "model": "medium",
        "language": "pt"
      },
      "results": {
        "speakers_detected": 4,
        "segments_count": 892,
        "confidence_avg": 0.89,
        "output_files": ["txt", "json", "srt"]
      }
    }
  ],
  "total": 45,
  "limit": 10,
  "offset": 0,
  "has_next": true
}
```

### **GET /jobs/{job_id}**
Obtém detalhes específicos de um job.

**Resposta:**
```json
{
  "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
  "status": "processing",
  "file_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "filename": "reuniao_diretoria_2024.mp4",
  "progress": {
    "percentage": 65,
    "current_stage": "transcription",
    "stages": [
      {"name": "audio_extraction", "status": "completed", "duration": 45},
      {"name": "model_loading", "status": "completed", "duration": 30},
      {"name": "diarization", "status": "completed", "duration": 180},
      {"name": "transcription", "status": "processing", "progress": 65},
      {"name": "post_processing", "status": "pending"}
    ]
  },
  "estimated_completion": "2024-01-15T10:50:00Z",
  "created_at": "2024-01-15T10:35:00Z",
  "config": { /* configuração completa */ },
  "logs": [
    {
      "timestamp": "2024-01-15T10:35:15Z",
      "level": "info",
      "message": "Iniciando extração de áudio"
    },
    {
      "timestamp": "2024-01-15T10:36:00Z", 
      "level": "info",
      "message": "Áudio extraído com sucesso (16kHz, mono)"
    }
  ]
}
```

### **DELETE /jobs/{job_id}**
Cancela um job em andamento ou remove um job completo.

**Resposta (204 No Content):**
```json
{
  "message": "Job cancelado com sucesso",
  "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
  "status": "cancelled"
}
```

---

## 👥 Gerenciamento de Oradores

### **GET /jobs/{job_id}/speakers**
Lista oradores identificados em uma transcrição.

**Resposta:**
```json
{
  "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
  "speakers": [
    {
      "speaker_id": "SPEAKER_00",
      "custom_name": "João Silva",
      "segments_count": 234,
      "total_duration": 1420,
      "first_appearance": "00:00:05",
      "last_appearance": "00:58:43",
      "confidence_avg": 0.92,
      "suggested_names": ["João", "Sr. Silva", "Diretor"]
    },
    {
      "speaker_id": "SPEAKER_01", 
      "custom_name": "Maria Santos",
      "segments_count": 198,
      "total_duration": 1180,
      "first_appearance": "00:00:12",
      "last_appearance": "00:59:15",
      "confidence_avg": 0.88,
      "suggested_names": ["Maria", "Sra. Santos", "Gerente"]
    }
  ],
  "total_speakers": 4,
  "auto_suggestions": {
    "SPEAKER_00": "Pessoa Principal",
    "SPEAKER_01": "Entrevistado",
    "SPEAKER_02": "Moderador"
  }
}
```

### **PUT /jobs/{job_id}/speakers/{speaker_id}**
Edita o nome de um orador específico.

**Body:**
```json
{
  "custom_name": "Dr. João Silva",
  "metadata": {
    "cargo": "CEO",
    "empresa": "TechCorp"
  }
}
```

**Resposta:**
```json
{
  "speaker_id": "SPEAKER_00",
  "custom_name": "Dr. João Silva",
  "previous_name": "João Silva",
  "metadata": {
    "cargo": "CEO",
    "empresa": "TechCorp"
  },
  "updated_at": "2024-01-15T11:15:00Z"
}
```

### **POST /jobs/{job_id}/speakers/batch**
Edita múltiplos oradores simultaneamente.

**Body:**
```json
{
  "speakers": {
    "SPEAKER_00": {
      "custom_name": "Dr. João Silva",
      "metadata": {"cargo": "CEO"}
    },
    "SPEAKER_01": {
      "custom_name": "Maria Santos",
      "metadata": {"cargo": "CTO"}
    },
    "SPEAKER_02": {
      "custom_name": "Pedro Costa",
      "metadata": {"cargo": "CFO"}
    }
  },
  "regenerate_outputs": true
}
```

**Resposta:**
```json
{
  "updated_speakers": 3,
  "speakers": [ /* lista de oradores atualizados */ ],
  "regeneration_job_id": "job_9f8ac10b-58cc-4372-a567-0e02b2c3d481"
}
```

---

## 📥 Download de Resultados

### **GET /jobs/{job_id}/results**
Lista arquivos de resultado disponíveis.

**Resposta:**
```json
{
  "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
  "results": [
    {
      "format": "txt",
      "url": "/jobs/job_8f7ac10b.../download/txt",
      "size": 45672,
      "created_at": "2024-01-15T10:47:00Z"
    },
    {
      "format": "json",
      "url": "/jobs/job_8f7ac10b.../download/json",
      "size": 123456,
      "created_at": "2024-01-15T10:47:00Z"
    },
    {
      "format": "srt",
      "url": "/jobs/job_8f7ac10b.../download/srt", 
      "size": 67890,
      "created_at": "2024-01-15T10:47:00Z"
    }
  ],
  "original_file": {
    "url": "/files/f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "size": 157286400
  }
}
```

### **GET /jobs/{job_id}/download/{format}**
Download de arquivo específico.

**Parâmetros:**
- `format`: `txt`, `json`, `srt`, `vtt`, `original`
- `download` (query): `true` para forçar download

**Headers de Resposta:**
```
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="reuniao_diretoria_2024.txt"
Content-Length: 45672
```

### **POST /jobs/{job_id}/export**
Exportação avançada com opções personalizadas.

**Body:**
```json
{
  "formats": ["txt", "srt"],
  "options": {
    "include_timestamps": true,
    "include_confidence": false,
    "speaker_format": "custom_names",
    "text_formatting": "paragraphs",
    "srt_max_chars": 42
  },
  "delivery": {
    "method": "email",
    "email": "user@exemplo.com",
    "subject": "Transcrição - Reunião Diretoria"
  }
}
```

---

## 🔌 WebSocket - Atualizações em Tempo Real

### **Conectar ao WebSocket**
```javascript
const ws = new WebSocket('wss://api.transcritor.com.br/ws/jobs/job_8f7ac10b...');

ws.onopen = function() {
    console.log('Conectado ao job');
};

ws.onmessage = function(event) {
    const update = JSON.parse(event.data);
    console.log('Update:', update);
};
```

### **Eventos WebSocket**

#### **job_status_changed**
```json
{
  "event": "job_status_changed",
  "job_id": "job_8f7ac10b...",
  "status": "processing",
  "previous_status": "queued",
  "timestamp": "2024-01-15T10:40:00Z"
}
```

#### **progress_update**
```json
{
  "event": "progress_update",
  "job_id": "job_8f7ac10b...",
  "progress": {
    "percentage": 45,
    "current_stage": "diarization",
    "estimated_remaining": 900
  },
  "timestamp": "2024-01-15T10:42:30Z"
}
```

#### **transcription_segment**
```json
{
  "event": "transcription_segment",
  "job_id": "job_8f7ac10b...",
  "segment": {
    "start": "00:15:32",
    "end": "00:15:38",
    "speaker": "SPEAKER_00",
    "text": "Vamos discutir o orçamento para o próximo trimestre.",
    "confidence": 0.89
  },
  "timestamp": "2024-01-15T10:45:15Z"
}
```

#### **job_completed**
```json
{
  "event": "job_completed",
  "job_id": "job_8f7ac10b...",
  "status": "completed",
  "results": {
    "speakers_detected": 4,
    "total_duration": 3600,
    "segments_count": 892,
    "download_urls": {
      "txt": "/jobs/job_8f7ac10b.../download/txt",
      "json": "/jobs/job_8f7ac10b.../download/json",
      "srt": "/jobs/job_8f7ac10b.../download/srt"
    }
  },
  "processing_time": 720,
  "timestamp": "2024-01-15T10:47:00Z"
}
```

#### **error_occurred**
```json
{
  "event": "error_occurred",
  "job_id": "job_8f7ac10b...",
  "error": {
    "code": "AUDIO_EXTRACTION_FAILED",
    "message": "Falha na extração do áudio",
    "details": "Formato de vídeo não suportado",
    "retry_possible": true
  },
  "timestamp": "2024-01-15T10:38:00Z"
}
```

---

## 📈 Estatísticas e Métricas

### **GET /stats/user**
Estatísticas do usuário atual.

**Resposta:**
```json
{
  "user_id": "user_123",
  "statistics": {
    "total_jobs": 127,
    "completed_jobs": 118,
    "failed_jobs": 9,
    "total_duration_processed": 145800,
    "total_hours_processed": 40.5,
    "average_processing_time": 892,
    "most_used_model": "medium",
    "preferred_language": "pt",
    "storage_used": 2147483648,
    "api_calls_this_month": 456
  },
  "usage_by_period": {
    "last_7_days": 12,
    "last_30_days": 45,
    "last_90_days": 127
  },
  "breakdown_by_type": {
    "reuniao": 45,
    "entrevista": 32,
    "podcast": 28,
    "outros": 22
  }
}
```

### **GET /stats/models**
Performance dos modelos disponíveis.

**Resposta:**
```json
{
  "models": [
    {
      "name": "medium",
      "usage_percentage": 65,
      "average_accuracy": 0.89,
      "average_processing_speed": 0.42,
      "recommended_for": ["reunioes", "entrevistas"]
    },
    {
      "name": "large",
      "usage_percentage": 25,
      "average_accuracy": 0.94,
      "average_processing_speed": 0.18,
      "recommended_for": ["entrevistas", "conteudo_profissional"]
    }
  ]
}
```

---

## ⚙️ Configurações e Presets

### **GET /presets**
Lista templates de configuração disponíveis.

### **POST /presets**
Cria template personalizado.

**Body:**
```json
{
  "name": "Minha Configuração",
  "description": "Para reuniões da minha empresa",
  "config": {
    "model": "medium",
    "language": "pt",
    "num_speakers": 4,
    "enhance_audio": true,
    "output_formats": ["txt", "json"]
  },
  "is_public": false
}
```

### **GET /models**
Lista modelos disponíveis e suas características.

---

## 🛡️ Segurança e Rate Limiting

### **Rate Limits**
- **Upload**: 10 arquivos/minuto (free), 100/minuto (premium)
- **API Calls**: 1000/hora (free), 10000/hora (premium) 
- **Concurrent Jobs**: 2 (free), 10 (premium)

### **Headers de Rate Limit**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1642276800
```

### **Códigos de Erro**
```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED", 
  "retry_after": 3600
}
```

---

## 🚨 Códigos de Status HTTP

| Código | Significado | Descrição |
|--------|-------------|-----------|
| 200 | OK | Requisição bem-sucedida |
| 201 | Created | Recurso criado com sucesso |
| 202 | Accepted | Requisição aceita para processamento |
| 204 | No Content | Sucesso sem conteúdo de resposta |
| 400 | Bad Request | Dados da requisição inválidos |
| 401 | Unauthorized | Token de autenticação necessário |
| 403 | Forbidden | Acesso negado |
| 404 | Not Found | Recurso não encontrado |
| 409 | Conflict | Conflito com estado atual |
| 422 | Unprocessable Entity | Dados válidos mas não processáveis |
| 429 | Too Many Requests | Rate limit excedido |
| 500 | Internal Server Error | Erro interno do servidor |
| 503 | Service Unavailable | Serviço temporariamente indisponível |

---

## 🔧 Webhooks

### **Configuração de Webhooks**
```json
{
  "url": "https://webhook.exemplo.com/transcription",
  "events": ["job_completed", "job_failed"],
  "secret": "webhook_secret_key",
  "retry_policy": {
    "max_attempts": 3,
    "backoff_factor": 2
  }
}
```

### **Payload do Webhook**
```json
{
  "event": "job_completed",
  "job_id": "job_8f7ac10b...",
  "timestamp": "2024-01-15T10:47:00Z",
  "data": {
    "status": "completed",
    "results": { /* dados do resultado */ }
  },
  "signature": "sha256=5d41402abc4b2a76b9719d911017c592"
}
```

---

## 📝 Exemplos de Integração

### **Python**
```python
import requests
import json

# Upload e transcrição
def transcribe_file(file_path, api_key):
    base_url = "https://api.transcritor.com.br/api/v1"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Upload
    with open(file_path, 'rb') as f:
        upload_response = requests.post(
            f"{base_url}/upload",
            files={"file": f},
            headers=headers
        )
    
    file_data = upload_response.json()
    
    # Transcrição
    transcribe_payload = {
        "file_id": file_data["file_id"],
        "config": {
            "model": "medium",
            "language": "pt",
            "output_formats": ["json"]
        }
    }
    
    job_response = requests.post(
        f"{base_url}/transcribe",
        json=transcribe_payload,
        headers=headers
    )
    
    return job_response.json()
```

### **JavaScript/Node.js**
```javascript
const axios = require('axios');
const FormData = require('form-data');

async function transcribeFile(filePath, apiKey) {
    const baseURL = 'https://api.transcritor.com.br/api/v1';
    const headers = { 'Authorization': `Bearer ${apiKey}` };
    
    // Upload
    const formData = new FormData();
    formData.append('file', fs.createReadStream(filePath));
    
    const uploadResponse = await axios.post(
        `${baseURL}/upload`,
        formData,
        { headers: { ...headers, ...formData.getHeaders() } }
    );
    
    // Transcrição  
    const transcribeResponse = await axios.post(
        `${baseURL}/transcribe`,
        {
            file_id: uploadResponse.data.file_id,
            config: {
                model: 'medium',
                language: 'pt',
                output_formats: ['json']
            }
        },
        { headers }
    );
    
    return transcribeResponse.data;
}
```

### **cURL**
```bash
#!/bin/bash

API_KEY="seu_api_key"
BASE_URL="https://api.transcritor.com.br/api/v1"
FILE_PATH="reuniao.mp4"

# Upload
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/upload" \
  -H "Authorization: Bearer $API_KEY" \
  -F "file=@$FILE_PATH")

FILE_ID=$(echo $UPLOAD_RESPONSE | jq -r '.file_id')

# Transcrição
curl -X POST "$BASE_URL/transcribe" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"file_id\": \"$FILE_ID\",
    \"config\": {
      \"model\": \"medium\",
      \"language\": \"pt\",
      \"output_formats\": [\"txt\", \"json\"]
    }
  }"
```

---

Esta documentação será mantida atualizada conforme novas funcionalidades forem implementadas. Para suporte técnico ou dúvidas sobre integração, consulte nossa [base de conhecimento](https://docs.transcritor.com.br) ou entre em contato através do [support@transcritor.com.br](mailto:support@transcritor.com.br).