# 🔌 WebSocket Guide - Atualizações em Tempo Real

## 📋 Visão Geral

O sistema de WebSocket fornece atualizações em tempo real sobre o progresso da transcrição, permitindo que interfaces de usuário exibam informações atualizadas sem polling constante.

---

## 🌐 Endpoints WebSocket

### **Conexão Principal**
```
wss://api.legenda.iaforte.com.br/ws/jobs/{job_id}?token={jwt_token}
```

### **Conexão de Usuário (todos os jobs)**
```
wss://api.legenda.iaforte.com.br/ws/user?token={jwt_token}
```

### **Conexão de Sistema (admin)**
```
wss://api.legenda.iaforte.com.br/ws/system?token={admin_token}
```

---

## 🔐 Autenticação

### **JWT Token via Query Parameter**
```javascript
const token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...";
const ws = new WebSocket(`wss://api.legenda.iaforte.com.br/ws/jobs/job_123?token=${token}`);
```

### **Autenticação via Header (Node.js)**
```javascript
const WebSocket = require('ws');

const ws = new WebSocket('wss://api.legenda.iaforte.com.br/ws/jobs/job_123', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
```

---

## 📨 Tipos de Eventos

### **1. Eventos de Status do Job**

#### **job_status_changed**
Disparado quando o status do job muda.

```json
{
    "event": "job_status_changed",
    "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
    "status": "processing",
    "previous_status": "queued",
    "timestamp": "2024-01-15T10:40:00Z",
    "estimated_completion": "2024-01-15T10:55:00Z"
}
```

#### **job_completed**
Disparado quando o job é concluído com sucesso.

```json
{
    "event": "job_completed",
    "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
    "status": "completed",
    "completed_at": "2024-01-15T10:47:00Z",
    "processing_time": 720,
    "results": {
        "speakers_detected": 4,
        "segments_count": 892,
        "total_duration": 3600,
        "confidence_avg": 0.89,
        "word_count": 12547,
        "download_urls": {
            "txt": "/jobs/job_8f7ac10b.../download/txt",
            "json": "/jobs/job_8f7ac10b.../download/json",
            "srt": "/jobs/job_8f7ac10b.../download/srt"
        }
    },
    "timestamp": "2024-01-15T10:47:00Z"
}
```

#### **job_failed**
Disparado quando o job falha.

```json
{
    "event": "job_failed",
    "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
    "status": "failed",
    "failed_at": "2024-01-15T10:38:00Z",
    "error": {
        "code": "AUDIO_EXTRACTION_FAILED",
        "message": "Falha na extração do áudio do arquivo de vídeo",
        "details": "Formato de vídeo corrompido ou não suportado",
        "retry_possible": true,
        "suggested_action": "Verificar integridade do arquivo e tentar novamente"
    },
    "timestamp": "2024-01-15T10:38:00Z"
}
```

### **2. Eventos de Progresso**

#### **progress_update**
Atualização geral do progresso.

```json
{
    "event": "progress_update",
    "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
    "progress": {
        "percentage": 45,
        "current_stage": "diarization",
        "stage_progress": 80,
        "estimated_remaining": 900,
        "stages": [
            {
                "name": "audio_extraction",
                "status": "completed",
                "duration": 45,
                "progress": 100
            },
            {
                "name": "model_loading", 
                "status": "completed",
                "duration": 30,
                "progress": 100
            },
            {
                "name": "diarization",
                "status": "processing",
                "duration": 180,
                "progress": 80
            },
            {
                "name": "transcription",
                "status": "pending",
                "progress": 0
            },
            {
                "name": "post_processing",
                "status": "pending",
                "progress": 0
            }
        ]
    },
    "timestamp": "2024-01-15T10:42:30Z"
}
```

#### **stage_started**
Início de uma nova etapa do processamento.

```json
{
    "event": "stage_started",
    "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
    "stage": {
        "name": "transcription",
        "display_name": "Transcrição de Áudio",
        "description": "Convertendo áudio em texto usando Whisper",
        "estimated_duration": 600,
        "model_used": "medium"
    },
    "overall_progress": 35,
    "timestamp": "2024-01-15T10:43:00Z"
}
```

### **3. Eventos de Transcrição em Tempo Real**

#### **transcription_segment**
Segmento de transcrição processado em tempo real.

```json
{
    "event": "transcription_segment",
    "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
    "segment": {
        "id": "segment_001",
        "start": "00:15:32.450",
        "end": "00:15:38.920",
        "duration": 6.47,
        "speaker": "SPEAKER_00",
        "text": "Vamos discutir o orçamento para o próximo trimestre.",
        "confidence": 0.89,
        "words": [
            {"word": "Vamos", "start": 932.45, "end": 932.78, "confidence": 0.95},
            {"word": "discutir", "start": 932.78, "end": 933.45, "confidence": 0.92},
            {"word": "o", "start": 933.45, "end": 933.52, "confidence": 0.88},
            {"word": "orçamento", "start": 933.52, "end": 934.12, "confidence": 0.91}
        ],
        "language": "pt",
        "no_speech_prob": 0.02
    },
    "progress": {
        "segments_processed": 234,
        "total_estimated_segments": 890,
        "percentage": 26
    },
    "timestamp": "2024-01-15T10:45:15Z"
}
```

#### **speaker_detected**
Novo orador identificado.

```json
{
    "event": "speaker_detected",
    "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
    "speaker": {
        "speaker_id": "SPEAKER_03",
        "first_appearance": "00:28:15.230",
        "confidence": 0.87,
        "suggested_names": ["Pessoa 4", "Participante D", "Orador 4"],
        "voice_characteristics": {
            "pitch": "medium",
            "gender_guess": "male",
            "age_estimate": "adult"
        }
    },
    "total_speakers": 4,
    "timestamp": "2024-01-15T10:46:00Z"
}
```

### **4. Eventos de Sistema**

#### **worker_assigned**
Worker atribuído ao job.

```json
{
    "event": "worker_assigned",
    "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
    "worker": {
        "instance_id": "worker-gpu-001",
        "region": "southamerica-east1",
        "gpu_type": "nvidia-tesla-t4",
        "cpu_cores": 8,
        "memory_gb": 32
    },
    "queue_position": 0,
    "timestamp": "2024-01-15T10:35:30Z"
}
```

#### **resource_usage**
Informações de uso de recursos durante processamento.

```json
{
    "event": "resource_usage",
    "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
    "resources": {
        "cpu_usage": 85.5,
        "memory_usage": 68.2,
        "gpu_usage": 92.1,
        "gpu_memory_usage": 78.9,
        "disk_io": 45.3
    },
    "timestamp": "2024-01-15T10:44:00Z"
}
```

### **5. Eventos de Erro**

#### **error_occurred**
Erro durante processamento.

```json
{
    "event": "error_occurred",
    "job_id": "job_8f7ac10b-58cc-4372-a567-0e02b2c3d480",
    "error": {
        "level": "warning",
        "code": "LOW_AUDIO_QUALITY",
        "message": "Qualidade do áudio baixa detectada",
        "details": "SNR baixo pode afetar a precisão da transcrição",
        "stage": "audio_analysis",
        "suggestions": [
            "Verificar qualidade do arquivo original",
            "Considerar usar preprocessing de áudio",
            "Modelo 'large' pode ter melhor performance"
        ],
        "recoverable": true
    },
    "timestamp": "2024-01-15T10:41:00Z"
}
```

---

## 💻 Implementações por Linguagem

### **JavaScript (Browser)**

```javascript
class TranscritorWebSocket {
    constructor(jobId, token) {
        this.jobId = jobId;
        this.token = token;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.eventHandlers = {};
    }

    connect() {
        const wsUrl = `wss://api.legenda.iaforte.com.br/ws/jobs/${this.jobId}?token=${this.token}`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = (event) => {
            console.log('🔌 WebSocket conectado');
            this.reconnectAttempts = 0;
            this.emit('connected', event);
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('❌ Erro ao processar mensagem WebSocket:', error);
            }
        };

        this.ws.onclose = (event) => {
            console.log('🔌 WebSocket desconectado:', event.code, event.reason);
            this.emit('disconnected', event);
            this.handleReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('❌ Erro WebSocket:', error);
            this.emit('error', error);
        };
    }

    handleMessage(data) {
        const { event } = data;
        
        // Log para debugging
        console.log(`📨 WebSocket event: ${event}`, data);
        
        // Emitir evento específico
        this.emit(event, data);
        
        // Emitir evento genérico
        this.emit('message', data);
    }

    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            
            console.log(`🔄 Tentando reconectar em ${delay}ms (tentativa ${this.reconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, delay);
        } else {
            console.error('❌ Máximo de tentativas de reconexão atingido');
            this.emit('max_reconnect_attempts');
        }
    }

    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }

    off(event, handler) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event] = this.eventHandlers[event].filter(h => h !== handler);
        }
    }

    emit(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`❌ Erro no handler do evento ${event}:`, error);
                }
            });
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    getConnectionState() {
        if (!this.ws) return 'disconnected';
        
        switch (this.ws.readyState) {
            case WebSocket.CONNECTING: return 'connecting';
            case WebSocket.OPEN: return 'connected';
            case WebSocket.CLOSING: return 'closing';
            case WebSocket.CLOSED: return 'disconnected';
            default: return 'unknown';
        }
    }
}

// Exemplo de uso
const ws = new TranscritorWebSocket('job_12345', 'seu_jwt_token');

// Event handlers
ws.on('connected', () => {
    console.log('✅ Conectado ao WebSocket');
    updateUI('Conectado - aguardando atualizações...');
});

ws.on('progress_update', (data) => {
    const { progress } = data;
    updateProgressBar(progress.percentage);
    updateStageInfo(progress.current_stage, progress.stage_progress);
});

ws.on('transcription_segment', (data) => {
    const { segment } = data;
    addTranscriptionSegment(segment);
    updateProgress(data.progress.percentage);
});

ws.on('job_completed', (data) => {
    console.log('🎉 Transcrição concluída!');
    showCompletionNotification(data.results);
    enableDownloadButtons(data.results.download_urls);
});

ws.on('error_occurred', (data) => {
    const { error } = data;
    if (error.level === 'warning') {
        showWarning(error.message, error.suggestions);
    } else {
        showError(error.message);
    }
});

// Conectar
ws.connect();

// Cleanup ao sair da página
window.addEventListener('beforeunload', () => {
    ws.disconnect();
});
```

### **React Hook**

```typescript
// useTranscriptionWebSocket.ts
import { useEffect, useState, useCallback, useRef } from 'react';

interface TranscriptionProgress {
    percentage: number;
    currentStage: string;
    estimatedRemaining: number;
}

interface TranscriptionSegment {
    id: string;
    start: string;
    end: string;
    speaker: string;
    text: string;
    confidence: number;
}

interface UseTranscriptionWebSocketProps {
    jobId: string;
    token: string;
    autoConnect?: boolean;
}

interface WebSocketState {
    connectionState: 'connecting' | 'connected' | 'disconnected' | 'error';
    progress: TranscriptionProgress | null;
    segments: TranscriptionSegment[];
    error: string | null;
    isCompleted: boolean;
}

export const useTranscriptionWebSocket = ({
    jobId,
    token,
    autoConnect = true
}: UseTranscriptionWebSocketProps) => {
    const [state, setState] = useState<WebSocketState>({
        connectionState: 'disconnected',
        progress: null,
        segments: [],
        error: null,
        isCompleted: false
    });

    const wsRef = useRef<TranscritorWebSocket | null>(null);

    const connect = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.disconnect();
        }

        const ws = new TranscritorWebSocket(jobId, token);
        wsRef.current = ws;

        ws.on('connected', () => {
            setState(prev => ({ ...prev, connectionState: 'connected', error: null }));
        });

        ws.on('disconnected', () => {
            setState(prev => ({ ...prev, connectionState: 'disconnected' }));
        });

        ws.on('error', (error) => {
            setState(prev => ({ 
                ...prev, 
                connectionState: 'error', 
                error: error.message || 'WebSocket error' 
            }));
        });

        ws.on('progress_update', (data) => {
            setState(prev => ({
                ...prev,
                progress: {
                    percentage: data.progress.percentage,
                    currentStage: data.progress.current_stage,
                    estimatedRemaining: data.progress.estimated_remaining
                }
            }));
        });

        ws.on('transcription_segment', (data) => {
            setState(prev => ({
                ...prev,
                segments: [...prev.segments, data.segment]
            }));
        });

        ws.on('job_completed', (data) => {
            setState(prev => ({
                ...prev,
                isCompleted: true,
                progress: { ...prev.progress!, percentage: 100 }
            }));
        });

        ws.on('error_occurred', (data) => {
            if (data.error.level === 'error') {
                setState(prev => ({ ...prev, error: data.error.message }));
            }
        });

        setState(prev => ({ ...prev, connectionState: 'connecting' }));
        ws.connect();
    }, [jobId, token]);

    const disconnect = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.disconnect();
            wsRef.current = null;
        }
        setState(prev => ({ ...prev, connectionState: 'disconnected' }));
    }, []);

    const clearSegments = useCallback(() => {
        setState(prev => ({ ...prev, segments: [] }));
    }, []);

    useEffect(() => {
        if (autoConnect) {
            connect();
        }

        return () => {
            disconnect();
        };
    }, [connect, disconnect, autoConnect]);

    return {
        ...state,
        connect,
        disconnect,
        clearSegments
    };
};

// Componente de exemplo
export const TranscriptionMonitor: React.FC<{ jobId: string; token: string }> = ({ 
    jobId, 
    token 
}) => {
    const {
        connectionState,
        progress,
        segments,
        error,
        isCompleted
    } = useTranscriptionWebSocket({ jobId, token });

    return (
        <div className="transcription-monitor">
            <div className="connection-status">
                Status: {connectionState}
                {error && <div className="error">{error}</div>}
            </div>

            {progress && (
                <div className="progress">
                    <div className="progress-bar">
                        <div 
                            className="progress-fill" 
                            style={{ width: `${progress.percentage}%` }}
                        />
                    </div>
                    <div className="progress-info">
                        {progress.currentStage} - {progress.percentage}%
                        {progress.estimatedRemaining > 0 && (
                            <span> (aprox. {Math.round(progress.estimatedRemaining / 60)} min restantes)</span>
                        )}
                    </div>
                </div>
            )}

            <div className="segments">
                {segments.map((segment) => (
                    <div key={segment.id} className="segment">
                        <span className="speaker">{segment.speaker}:</span>
                        <span className="text">{segment.text}</span>
                        <span className="confidence">({(segment.confidence * 100).toFixed(1)}%)</span>
                    </div>
                ))}
            </div>

            {isCompleted && (
                <div className="completion-message">
                    🎉 Transcrição concluída!
                </div>
            )}
        </div>
    );
};
```

### **Python Client**

```python
import asyncio
import websockets
import json
import logging
from typing import Callable, Dict, Any, Optional

logger = logging.getLogger(__name__)

class TranscritorWebSocketClient:
    def __init__(self, job_id: str, token: str, base_url: str = "wss://api.legenda.iaforte.com.br"):
        self.job_id = job_id
        self.token = token
        self.base_url = base_url
        self.websocket = None
        self.event_handlers: Dict[str, list] = {}
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

    async def connect(self):
        """Conecta ao WebSocket."""
        uri = f"{self.base_url}/ws/jobs/{self.job_id}?token={self.token}"
        
        try:
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            self.reconnect_attempts = 0
            
            logger.info(f"🔌 Conectado ao WebSocket para job {self.job_id}")
            await self._emit('connected', {'job_id': self.job_id})
            
            # Iniciar loop de mensagens
            await self._message_loop()
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar WebSocket: {e}")
            await self._emit('error', {'error': str(e)})
            await self._handle_reconnect()

    async def _message_loop(self):
        """Loop principal para receber mensagens."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Erro ao decodificar mensagem JSON: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 Conexão WebSocket fechada")
            self.is_connected = False
            await self._emit('disconnected', {'job_id': self.job_id})
            await self._handle_reconnect()
            
        except Exception as e:
            logger.error(f"❌ Erro no loop de mensagens: {e}")
            await self._emit('error', {'error': str(e)})

    async def _handle_message(self, data: Dict[str, Any]):
        """Processa mensagem recebida."""
        event = data.get('event')
        
        if event:
            logger.debug(f"📨 WebSocket event: {event}")
            await self._emit(event, data)
            await self._emit('message', data)

    async def _handle_reconnect(self):
        """Tenta reconectar automaticamente."""
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            delay = min(2 ** self.reconnect_attempts, 30)  # Max 30s
            
            logger.info(f"🔄 Tentando reconectar em {delay}s (tentativa {self.reconnect_attempts})")
            await asyncio.sleep(delay)
            await self.connect()
        else:
            logger.error("❌ Máximo de tentativas de reconexão atingido")
            await self._emit('max_reconnect_attempts', {'job_id': self.job_id})

    def on(self, event: str, handler: Callable):
        """Registra handler para evento."""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)

    def off(self, event: str, handler: Callable):
        """Remove handler de evento."""
        if event in self.event_handlers:
            self.event_handlers[event] = [h for h in self.event_handlers[event] if h != handler]

    async def _emit(self, event: str, data: Dict[str, Any]):
        """Emite evento para handlers registrados."""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"❌ Erro no handler do evento {event}: {e}")

    async def disconnect(self):
        """Desconecta do WebSocket."""
        self.is_connected = False
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

# Exemplo de uso
async def main():
    client = TranscritorWebSocketClient('job_12345', 'seu_jwt_token')
    
    # Event handlers
    @client.on('connected')
    async def on_connected(data):
        print(f"✅ Conectado ao job {data['job_id']}")

    @client.on('progress_update')
    async def on_progress(data):
        progress = data['progress']
        print(f"📊 Progresso: {progress['percentage']}% - {progress['current_stage']}")

    @client.on('transcription_segment')
    async def on_segment(data):
        segment = data['segment']
        print(f"🎙️ [{segment['speaker']}]: {segment['text']}")

    @client.on('job_completed')
    async def on_completed(data):
        print("🎉 Transcrição concluída!")
        results = data['results']
        print(f"👥 {results['speakers_detected']} oradores detectados")
        
        # Desconectar após conclusão
        await client.disconnect()

    @client.on('error_occurred')
    async def on_error(data):
        error = data['error']
        print(f"⚠️ {error['level'].upper()}: {error['message']}")

    # Conectar e aguardar
    try:
        await client.connect()
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔧 Configuração do Servidor

### **FastAPI WebSocket Implementation**

```python
# websocket_manager.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Any
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Conexões por job
        self.job_connections: Dict[str, List[WebSocket]] = {}
        # Conexões por usuário
        self.user_connections: Dict[str, List[WebSocket]] = {}
        # Conexões de sistema
        self.system_connections: List[WebSocket] = []

    async def connect_job(self, websocket: WebSocket, job_id: str):
        """Conecta WebSocket a um job específico."""
        await websocket.accept()
        
        if job_id not in self.job_connections:
            self.job_connections[job_id] = []
        
        self.job_connections[job_id].append(websocket)
        logger.info(f"🔌 Nova conexão para job {job_id}")

    async def connect_user(self, websocket: WebSocket, user_id: str):
        """Conecta WebSocket a todos os jobs de um usuário."""
        await websocket.accept()
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        
        self.user_connections[user_id].append(websocket)
        logger.info(f"🔌 Nova conexão para usuário {user_id}")

    async def disconnect_job(self, websocket: WebSocket, job_id: str):
        """Desconecta WebSocket de um job."""
        if job_id in self.job_connections:
            self.job_connections[job_id].remove(websocket)
            
            if not self.job_connections[job_id]:
                del self.job_connections[job_id]
        
        logger.info(f"🔌 Conexão removida do job {job_id}")

    async def disconnect_user(self, websocket: WebSocket, user_id: str):
        """Desconecta WebSocket de um usuário."""
        if user_id in self.user_connections:
            self.user_connections[user_id].remove(websocket)
            
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"🔌 Conexão removida do usuário {user_id}")

    async def broadcast_to_job(self, job_id: str, message: Dict[str, Any]):
        """Envia mensagem para todas as conexões de um job."""
        if job_id in self.job_connections:
            message_json = json.dumps(message)
            
            # Lista de conexões a serem removidas (conexões mortas)
            dead_connections = []
            
            for websocket in self.job_connections[job_id]:
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    logger.warning(f"❌ Erro ao enviar mensagem para job {job_id}: {e}")
                    dead_connections.append(websocket)
            
            # Remover conexões mortas
            for websocket in dead_connections:
                await self.disconnect_job(websocket, job_id)

    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]):
        """Envia mensagem para todas as conexões de um usuário."""
        if user_id in self.user_connections:
            message_json = json.dumps(message)
            
            dead_connections = []
            
            for websocket in self.user_connections[user_id]:
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    logger.warning(f"❌ Erro ao enviar mensagem para usuário {user_id}: {e}")
                    dead_connections.append(websocket)
            
            # Remover conexões mortas
            for websocket in dead_connections:
                await self.disconnect_user(websocket, user_id)

# Instance global
manager = ConnectionManager()

# Routes WebSocket
@app.websocket("/ws/jobs/{job_id}")
async def websocket_job_endpoint(websocket: WebSocket, job_id: str, token: str = None):
    """WebSocket endpoint para job específico."""
    
    # Validar token e permissões
    try:
        user = await authenticate_websocket_token(token)
        # Verificar se usuário tem acesso ao job
        job = await get_job_by_id(job_id)
        if job.user_id != user.id:
            await websocket.close(code=1008, reason="Unauthorized")
            return
    except Exception as e:
        await websocket.close(code=1008, reason="Authentication failed")
        return

    await manager.connect_job(websocket, job_id)
    
    try:
        while True:
            # Manter conexão viva
            await asyncio.sleep(30)
            await websocket.ping()
            
    except WebSocketDisconnect:
        await manager.disconnect_job(websocket, job_id)
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket job {job_id}: {e}")
        await manager.disconnect_job(websocket, job_id)

# Funções para emitir eventos
async def emit_job_event(job_id: str, event: str, data: Dict[str, Any]):
    """Emite evento para job específico."""
    message = {
        "event": event,
        "job_id": job_id,
        "timestamp": datetime.utcnow().isoformat(),
        **data
    }
    
    await manager.broadcast_to_job(job_id, message)

async def emit_progress_update(job_id: str, progress_data: Dict[str, Any]):
    """Emite atualização de progresso."""
    await emit_job_event(job_id, "progress_update", {
        "progress": progress_data
    })

async def emit_transcription_segment(job_id: str, segment_data: Dict[str, Any]):
    """Emite novo segmento de transcrição."""
    await emit_job_event(job_id, "transcription_segment", {
        "segment": segment_data
    })
```

Este guia completo de WebSocket fornece todas as ferramentas necessárias para implementar atualizações em tempo real robustas e user-friendly para o sistema de transcrição.