# 📋 Especificação OpenAPI - Transcritor API

## Especificação OpenAPI 3.0.3

```yaml
openapi: 3.0.3
info:
  title: Transcritor com Diarização API
  description: |
    API REST completa para transcrição de áudio e vídeo com identificação automática de oradores.
    Otimizada para português brasileiro com suporte a múltiplos formatos e configurações avançadas.
    
    ## Funcionalidades Principais
    - Upload de arquivos de áudio/vídeo
    - Transcrição com Whisper (OpenAI)
    - Diarização de oradores com PyAnnote
    - Edição de nomes de oradores
    - WebSocket para atualizações em tempo real
    - Múltiplos formatos de saída
    - Templates otimizados para casos de uso brasileiros
    
    ## Autenticação
    A API utiliza JWT Bearer tokens ou API Keys para autenticação.
    
    ## Rate Limiting
    - Free: 1000 requests/hora, 10 uploads/minuto
    - Premium: 10000 requests/hora, 100 uploads/minuto
    
  version: 1.0.0
  contact:
    name: Suporte Transcritor
    email: support@transcritor.com.br
    url: https://docs.transcritor.com.br
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT
  termsOfService: https://transcritor.com.br/terms

servers:
  - url: https://api.transcritor.com.br/api/v1
    description: Servidor de Produção
  - url: https://api-staging.transcritor.com.br/api/v1
    description: Servidor de Staging
  - url: http://localhost:8000/api/v1
    description: Desenvolvimento Local

paths:
  /upload:
    post:
      summary: Upload de arquivo
      description: |
        Faz upload de arquivo de áudio ou vídeo para posterior transcrição.
        
        ### Formatos Suportados
        **Áudio:** MP3, WAV, M4A, FLAC, OGG, OPUS
        **Vídeo:** MP4, MKV, MOV, AVI, WebM, FLV
        
        ### Limitações
        - Tamanho máximo: 2GB
        - Duração máxima: 6 horas
        - Rate limit: 10 uploads/minuto (free), 100/minuto (premium)
        
      operationId: uploadFile
      tags:
        - Upload
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              required:
                - file
              properties:
                file:
                  type: string
                  format: binary
                  description: Arquivo de áudio ou vídeo
                filename:
                  type: string
                  description: Nome personalizado para o arquivo
                  example: "reuniao_diretoria_2024.mp4"
                metadata:
                  type: object
                  description: Metadados adicionais do arquivo
                  example:
                    tipo: "reuniao"
                    participantes: 4
                    departamento: "vendas"
      responses:
        '201':
          description: Arquivo carregado com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FileUploadResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '413':
          $ref: '#/components/responses/PayloadTooLarge'
        '422':
          $ref: '#/components/responses/UnprocessableEntity'
        '429':
          $ref: '#/components/responses/TooManyRequests'

  /transcribe:
    post:
      summary: Iniciar transcrição
      description: |
        Inicia o processo de transcrição de um arquivo previamente carregado.
        
        ### Configurações Disponíveis
        - **Modelos Whisper:** tiny, base, small, medium, large, large-v3
        - **Idiomas:** pt (português), en (inglês), es (espanhol), auto (detecção automática)
        - **Formatos de saída:** txt, json, srt, vtt, tsv
        - **Detecção de oradores:** automática ou número específico
        
      operationId: startTranscription
      tags:
        - Transcrição
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TranscriptionRequest'
      responses:
        '202':
          description: Transcrição iniciada com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/JobResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'
        '422':
          $ref: '#/components/responses/UnprocessableEntity'

  /jobs:
    get:
      summary: Listar jobs de transcrição
      description: |
        Lista todos os jobs de transcrição do usuário com opções de filtro e paginação.
        
      operationId: listJobs
      tags:
        - Jobs
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      parameters:
        - name: status
          in: query
          description: Filtrar por status do job
          schema:
            type: string
            enum: [queued, processing, completed, failed, cancelled]
        - name: limit
          in: query
          description: Número de resultados por página
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
        - name: offset
          in: query
          description: Número de registros a pular
          schema:
            type: integer
            minimum: 0
            default: 0
        - name: sort
          in: query
          description: Campo para ordenação
          schema:
            type: string
            enum: [created_at, updated_at, duration, filename]
            default: created_at
        - name: order
          in: query
          description: Direção da ordenação
          schema:
            type: string
            enum: [asc, desc]
            default: desc
        - name: search
          in: query
          description: Buscar por nome de arquivo
          schema:
            type: string
      responses:
        '200':
          description: Lista de jobs retornada com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/JobListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /jobs/{job_id}:
    get:
      summary: Obter detalhes do job
      description: |
        Retorna informações detalhadas sobre um job específico, incluindo progresso,
        logs e resultados (se disponíveis).
        
      operationId: getJob
      tags:
        - Jobs
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      parameters:
        - name: job_id
          in: path
          required: true
          description: ID único do job
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Detalhes do job retornados com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/JobDetailResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'
    
    delete:
      summary: Cancelar ou remover job
      description: |
        Cancela um job em andamento ou remove um job completo.
        Jobs em andamento são cancelados graciosamente.
        
      operationId: deleteJob
      tags:
        - Jobs
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      parameters:
        - name: job_id
          in: path
          required: true
          description: ID único do job
          schema:
            type: string
            format: uuid
      responses:
        '204':
          description: Job cancelado/removido com sucesso
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'
        '409':
          description: Job não pode ser cancelado no estado atual
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /jobs/{job_id}/speakers:
    get:
      summary: Listar oradores identificados
      description: |
        Lista todos os oradores identificados em uma transcrição com estatísticas
        de participação e sugestões de nomes.
        
      operationId: listSpeakers
      tags:
        - Oradores
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      parameters:
        - name: job_id
          in: path
          required: true
          description: ID do job de transcrição
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Lista de oradores retornada com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SpeakersResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  /jobs/{job_id}/speakers/{speaker_id}:
    put:
      summary: Editar nome do orador
      description: |
        Altera o nome de um orador específico e opcionalmente regenera
        os arquivos de saída com o novo nome.
        
      operationId: updateSpeaker
      tags:
        - Oradores
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      parameters:
        - name: job_id
          in: path
          required: true
          description: ID do job de transcrição
          schema:
            type: string
            format: uuid
        - name: speaker_id
          in: path
          required: true
          description: ID do orador (ex: SPEAKER_00)
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SpeakerUpdateRequest'
      responses:
        '200':
          description: Orador atualizado com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SpeakerUpdateResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  /jobs/{job_id}/speakers/batch:
    post:
      summary: Edição em lote de oradores
      description: |
        Permite editar múltiplos oradores simultaneamente e regenerar
        os arquivos de saída com os novos nomes.
        
      operationId: batchUpdateSpeakers
      tags:
        - Oradores
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      parameters:
        - name: job_id
          in: path
          required: true
          description: ID do job de transcrição
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BatchSpeakerUpdateRequest'
      responses:
        '200':
          description: Oradores atualizados com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BatchSpeakerUpdateResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  /jobs/{job_id}/results:
    get:
      summary: Listar arquivos de resultado
      description: |
        Lista todos os arquivos de resultado disponíveis para download,
        incluindo informações sobre formato, tamanho e data de criação.
        
      operationId: listResults
      tags:
        - Download
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      parameters:
        - name: job_id
          in: path
          required: true
          description: ID do job de transcrição
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Lista de resultados retornada com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResultsResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  /jobs/{job_id}/download/{format}:
    get:
      summary: Download de resultado
      description: |
        Faz download de um arquivo de resultado específico.
        
        ### Formatos Disponíveis
        - **txt**: Texto simples com timestamps e oradores
        - **json**: Dados estruturados com metadados completos
        - **srt**: Legendas no formato SubRip
        - **vtt**: Legendas no formato WebVTT
        - **original**: Arquivo original carregado
        
      operationId: downloadResult
      tags:
        - Download
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      parameters:
        - name: job_id
          in: path
          required: true
          description: ID do job de transcrição
          schema:
            type: string
            format: uuid
        - name: format
          in: path
          required: true
          description: Formato do arquivo
          schema:
            type: string
            enum: [txt, json, srt, vtt, original]
        - name: download
          in: query
          description: Forçar download (Content-Disposition: attachment)
          schema:
            type: boolean
            default: false
      responses:
        '200':
          description: Arquivo retornado com sucesso
          content:
            application/octet-stream:
              schema:
                type: string
                format: binary
            text/plain:
              schema:
                type: string
            application/json:
              schema:
                type: object
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  /models:
    get:
      summary: Listar modelos disponíveis
      description: |
        Lista todos os modelos Whisper disponíveis com suas características,
        requisitos de hardware e métricas de performance.
        
      operationId: listModels
      tags:
        - Configuração
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      responses:
        '200':
          description: Lista de modelos retornada com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ModelsResponse'

  /presets:
    get:
      summary: Listar templates de configuração
      description: |
        Lista templates pré-definidos e personalizados do usuário para
        diferentes casos de uso (reunião, entrevista, podcast, etc.).
        
      operationId: listPresets
      tags:
        - Configuração
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      responses:
        '200':
          description: Lista de presets retornada com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PresetsResponse'
    
    post:
      summary: Criar template personalizado
      description: |
        Cria um novo template de configuração personalizado que pode ser
        reutilizado em futuras transcrições.
        
      operationId: createPreset
      tags:
        - Configuração
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PresetCreateRequest'
      responses:
        '201':
          description: Preset criado com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PresetResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /stats/user:
    get:
      summary: Estatísticas do usuário
      description: |
        Retorna estatísticas detalhadas de uso da API pelo usuário atual,
        incluindo histórico de jobs, uso de recursos e métricas de performance.
        
      operationId: getUserStats
      tags:
        - Estatísticas
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      responses:
        '200':
          description: Estatísticas retornadas com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserStatsResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /auth/token:
    post:
      summary: Obter token de autenticação
      description: |
        Autentica usuário e retorna JWT token para acesso à API.
        
      operationId: getAuthToken
      tags:
        - Autenticação
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AuthRequest'
      responses:
        '200':
          description: Token gerado com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AuthResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          description: Credenciais inválidas
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /auth/refresh:
    post:
      summary: Renovar token
      description: |
        Renova um token JWT usando o refresh token.
        
      operationId: refreshToken
      tags:
        - Autenticação
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - refresh_token
              properties:
                refresh_token:
                  type: string
                  description: Refresh token obtido no login
      responses:
        '200':
          description: Token renovado com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AuthResponse'
        '401':
          description: Refresh token inválido
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: JWT token obtido através do endpoint /auth/token
    
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: API Key obtida no painel de usuário

  schemas:
    FileUploadResponse:
      type: object
      required:
        - file_id
        - filename
        - size
        - mime_type
        - created_at
      properties:
        file_id:
          type: string
          format: uuid
          description: ID único do arquivo
          example: "f47ac10b-58cc-4372-a567-0e02b2c3d479"
        filename:
          type: string
          description: Nome do arquivo
          example: "reuniao_diretoria_2024.mp4"
        size:
          type: integer
          description: Tamanho do arquivo em bytes
          example: 157286400
        duration:
          type: number
          description: Duração do áudio/vídeo em segundos
          example: 3600
        mime_type:
          type: string
          description: Tipo MIME do arquivo
          example: "video/mp4"
        upload_url:
          type: string
          description: URL para acesso ao arquivo
          example: "/files/f47ac10b-58cc-4372-a567-0e02b2c3d479"
        created_at:
          type: string
          format: date-time
          description: Data/hora do upload
        metadata:
          type: object
          description: Metadados adicionais fornecidos

    TranscriptionRequest:
      type: object
      required:
        - file_id
      properties:
        file_id:
          type: string
          format: uuid
          description: ID do arquivo previamente carregado
        config:
          $ref: '#/components/schemas/TranscriptionConfig'
        callback_url:
          type: string
          format: uri
          description: URL para webhook de notificação
        priority:
          type: string
          enum: [low, normal, high]
          default: normal
          description: Prioridade do job na fila

    TranscriptionConfig:
      type: object
      properties:
        model:
          type: string
          enum: [tiny, base, small, medium, large, large-v2, large-v3]
          default: medium
          description: Modelo Whisper a ser usado
        language:
          type: string
          default: pt
          description: Código do idioma (pt, en, es, auto)
        num_speakers:
          type: string
          default: auto
          description: Número de oradores (auto ou número específico)
        output_formats:
          type: array
          items:
            type: string
            enum: [txt, json, srt, vtt, tsv]
          default: [txt]
          description: Formatos de saída desejados
        speaker_detection:
          type: object
          properties:
            min_speakers:
              type: integer
              minimum: 1
              maximum: 50
              default: 1
            max_speakers:
              type: integer
              minimum: 1
              maximum: 50
              default: 10
        quality:
          type: object
          properties:
            enhance_audio:
              type: boolean
              default: true
              description: Melhorar qualidade do áudio
            noise_reduction:
              type: boolean
              default: false
              description: Redução de ruído
            normalize_volume:
              type: boolean
              default: true
              description: Normalizar volume
        preprocessing:
          type: object
          properties:
            remove_silence:
              type: boolean
              default: false
              description: Remover silêncios longos
            split_long_audio:
              type: boolean
              default: true
              description: Dividir áudios muito longos
            chunk_duration:
              type: integer
              default: 600
              description: Duração dos chunks em segundos

    JobResponse:
      type: object
      required:
        - job_id
        - status
        - file_id
        - created_at
      properties:
        job_id:
          type: string
          format: uuid
          description: ID único do job
        status:
          type: string
          enum: [queued, processing, completed, failed, cancelled]
          description: Status atual do job
        file_id:
          type: string
          format: uuid
          description: ID do arquivo sendo processado
        estimated_duration:
          type: integer
          description: Duração estimada em segundos
        position_in_queue:
          type: integer
          description: Posição na fila de processamento
        created_at:
          type: string
          format: date-time
          description: Data/hora de criação
        config:
          $ref: '#/components/schemas/TranscriptionConfig'

    JobListResponse:
      type: object
      required:
        - jobs
        - total
        - limit
        - offset
      properties:
        jobs:
          type: array
          items:
            $ref: '#/components/schemas/JobSummary'
        total:
          type: integer
          description: Total de jobs do usuário
        limit:
          type: integer
          description: Limite de resultados por página
        offset:
          type: integer
          description: Offset da paginação
        has_next:
          type: boolean
          description: Indica se há próxima página

    JobSummary:
      type: object
      properties:
        job_id:
          type: string
          format: uuid
        status:
          type: string
          enum: [queued, processing, completed, failed, cancelled]
        file_id:
          type: string
          format: uuid
        filename:
          type: string
        duration:
          type: number
        processing_time:
          type: number
        created_at:
          type: string
          format: date-time
        completed_at:
          type: string
          format: date-time
        config:
          type: object
        results:
          type: object
          properties:
            speakers_detected:
              type: integer
            segments_count:
              type: integer
            confidence_avg:
              type: number
            output_files:
              type: array
              items:
                type: string

    JobDetailResponse:
      allOf:
        - $ref: '#/components/schemas/JobSummary'
        - type: object
          properties:
            progress:
              $ref: '#/components/schemas/JobProgress'
            estimated_completion:
              type: string
              format: date-time
            logs:
              type: array
              items:
                $ref: '#/components/schemas/JobLog'

    JobProgress:
      type: object
      properties:
        percentage:
          type: integer
          minimum: 0
          maximum: 100
        current_stage:
          type: string
          enum: [audio_extraction, model_loading, diarization, transcription, post_processing]
        stages:
          type: array
          items:
            type: object
            properties:
              name:
                type: string
              status:
                type: string
                enum: [pending, processing, completed, failed]
              duration:
                type: number
              progress:
                type: integer

    JobLog:
      type: object
      properties:
        timestamp:
          type: string
          format: date-time
        level:
          type: string
          enum: [debug, info, warning, error]
        message:
          type: string
        details:
          type: object

    SpeakersResponse:
      type: object
      properties:
        job_id:
          type: string
          format: uuid
        speakers:
          type: array
          items:
            $ref: '#/components/schemas/Speaker'
        total_speakers:
          type: integer
        auto_suggestions:
          type: object
          additionalProperties:
            type: string

    Speaker:
      type: object
      properties:
        speaker_id:
          type: string
          description: ID do orador (ex: SPEAKER_00)
        custom_name:
          type: string
          description: Nome personalizado do orador
        segments_count:
          type: integer
          description: Número de segmentos falados
        total_duration:
          type: number
          description: Duração total de fala em segundos
        first_appearance:
          type: string
          description: Timestamp da primeira aparição
        last_appearance:
          type: string
          description: Timestamp da última aparição
        confidence_avg:
          type: number
          description: Confiança média da identificação
        suggested_names:
          type: array
          items:
            type: string
          description: Sugestões automáticas de nomes

    SpeakerUpdateRequest:
      type: object
      required:
        - custom_name
      properties:
        custom_name:
          type: string
          description: Novo nome para o orador
        metadata:
          type: object
          description: Metadados adicionais
        regenerate_outputs:
          type: boolean
          default: true
          description: Regenerar arquivos de saída

    SpeakerUpdateResponse:
      type: object
      properties:
        speaker_id:
          type: string
        custom_name:
          type: string
        previous_name:
          type: string
        metadata:
          type: object
        updated_at:
          type: string
          format: date-time

    BatchSpeakerUpdateRequest:
      type: object
      required:
        - speakers
      properties:
        speakers:
          type: object
          additionalProperties:
            type: object
            properties:
              custom_name:
                type: string
              metadata:
                type: object
        regenerate_outputs:
          type: boolean
          default: true

    BatchSpeakerUpdateResponse:
      type: object
      properties:
        updated_speakers:
          type: integer
        speakers:
          type: array
          items:
            $ref: '#/components/schemas/Speaker'
        regeneration_job_id:
          type: string
          format: uuid

    ResultsResponse:
      type: object
      properties:
        job_id:
          type: string
          format: uuid
        results:
          type: array
          items:
            type: object
            properties:
              format:
                type: string
              url:
                type: string
              size:
                type: integer
              created_at:
                type: string
                format: date-time
        original_file:
          type: object
          properties:
            url:
              type: string
            size:
              type: integer

    ModelsResponse:
      type: object
      properties:
        models:
          type: array
          items:
            type: object
            properties:
              name:
                type: string
              size:
                type: string
              vram:
                type: string
              speed:
                type: string
              quality:
                type: string
              languages:
                type: array
                items:
                  type: string
              recommended:
                type: boolean
              latest:
                type: boolean

    PresetsResponse:
      type: object
      properties:
        presets:
          type: object
          additionalProperties:
            $ref: '#/components/schemas/Preset'

    Preset:
      type: object
      properties:
        name:
          type: string
        description:
          type: string
        config:
          $ref: '#/components/schemas/TranscriptionConfig'
        is_public:
          type: boolean
        created_by:
          type: string

    PresetCreateRequest:
      type: object
      required:
        - name
        - config
      properties:
        name:
          type: string
        description:
          type: string
        config:
          $ref: '#/components/schemas/TranscriptionConfig'
        is_public:
          type: boolean
          default: false

    PresetResponse:
      type: object
      properties:
        preset_id:
          type: string
          format: uuid
        name:
          type: string
        description:
          type: string
        config:
          $ref: '#/components/schemas/TranscriptionConfig'
        is_public:
          type: boolean
        created_at:
          type: string
          format: date-time

    UserStatsResponse:
      type: object
      properties:
        user_id:
          type: string
        statistics:
          type: object
          properties:
            total_jobs:
              type: integer
            completed_jobs:
              type: integer
            failed_jobs:
              type: integer
            total_duration_processed:
              type: number
            total_hours_processed:
              type: number
            average_processing_time:
              type: number
            most_used_model:
              type: string
            preferred_language:
              type: string
            storage_used:
              type: integer
            api_calls_this_month:
              type: integer
        usage_by_period:
          type: object
        breakdown_by_type:
          type: object

    AuthRequest:
      type: object
      required:
        - username
        - password
      properties:
        username:
          type: string
          description: Nome de usuário ou email
        password:
          type: string
          format: password
          description: Senha do usuário

    AuthResponse:
      type: object
      properties:
        access_token:
          type: string
          description: JWT token de acesso
        token_type:
          type: string
          default: bearer
        expires_in:
          type: integer
          description: Tempo de expiração em segundos
        refresh_token:
          type: string
          description: Token para renovação

    ErrorResponse:
      type: object
      required:
        - detail
      properties:
        detail:
          type: string
          description: Descrição do erro
        error_code:
          type: string
          description: Código específico do erro
        timestamp:
          type: string
          format: date-time
        path:
          type: string
          description: Endpoint onde ocorreu o erro

  responses:
    BadRequest:
      description: Requisição inválida
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    
    Unauthorized:
      description: Não autorizado - token ausente ou inválido
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    
    NotFound:
      description: Recurso não encontrado
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    
    UnprocessableEntity:
      description: Dados válidos mas não processáveis
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    
    TooManyRequests:
      description: Rate limit excedido
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
      headers:
        X-RateLimit-Limit:
          description: Limite de requests por período
          schema:
            type: integer
        X-RateLimit-Remaining:
          description: Requests restantes no período
          schema:
            type: integer
        X-RateLimit-Reset:
          description: Timestamp do reset do limite
          schema:
            type: integer
        Retry-After:
          description: Segundos para próxima tentativa
          schema:
            type: integer
    
    PayloadTooLarge:
      description: Arquivo muito grande
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'

tags:
  - name: Upload
    description: Endpoints para upload de arquivos
  - name: Transcrição
    description: Endpoints para iniciar e gerenciar transcrições
  - name: Jobs
    description: Gerenciamento de jobs de processamento
  - name: Oradores
    description: Identificação e edição de oradores
  - name: Download
    description: Download de resultados e arquivos
  - name: Configuração
    description: Modelos, presets e configurações
  - name: Estatísticas
    description: Métricas e estatísticas de uso
  - name: Autenticação
    description: Autenticação e autorização

externalDocs:
  description: Documentação completa da API
  url: https://docs.transcritor.com.br
```

## 📊 Métricas de Endpoint

### **Performance Esperada**
- Upload: < 2s para arquivos até 100MB
- Início de transcrição: < 500ms
- Consulta de status: < 100ms
- Download de resultados: < 1s

### **Limites por Plano**

| Recurso | Free | Premium | Enterprise |
|---------|------|---------|------------|
| Uploads/minuto | 10 | 100 | 1000 |
| Jobs simultâneos | 2 | 10 | 50 |
| Duração máxima | 2h | 6h | 24h |
| Armazenamento | 5GB | 100GB | 1TB |
| Retenção | 30 dias | 1 ano | Ilimitado |

### **SLA Garantido**
- **Uptime**: 99.9% (Premium/Enterprise)
- **Latência**: < 200ms (95% das requisições)
- **Processamento**: Tempo real x 0.3 (modelo medium)

Esta especificação OpenAPI serve como base para geração automática de documentação interativa e SDKs para diferentes linguagens de programação.