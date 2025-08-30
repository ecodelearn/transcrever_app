# 🗄️ Schema do Banco de Dados - legenda.iaforte.com.br

## 📋 Visão Geral

O banco de dados PostgreSQL armazena metadados dos jobs, usuários, resultados e configurações. Otimizado para alta performance e escalabilidade.

---

## 🏗️ Estrutura das Tabelas

### **1. Users (Usuários)**

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    company VARCHAR(255),
    plan_type VARCHAR(50) DEFAULT 'free' CHECK (plan_type IN ('free', 'premium', 'enterprise')),
    api_key VARCHAR(255) UNIQUE,
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    
    -- Limites por plano
    monthly_upload_limit INTEGER DEFAULT 10,
    concurrent_jobs_limit INTEGER DEFAULT 2,
    storage_limit_gb INTEGER DEFAULT 5,
    
    -- Métricas de uso
    current_storage_usage BIGINT DEFAULT 0,
    total_jobs_created INTEGER DEFAULT 0,
    total_processing_time INTEGER DEFAULT 0, -- em segundos
    
    -- Configurações
    default_language VARCHAR(10) DEFAULT 'pt',
    notification_preferences JSONB DEFAULT '{"email": true, "webhook": false}'::jsonb
);

-- Índices
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_api_key ON users(api_key);
CREATE INDEX idx_users_plan_type ON users(plan_type);
CREATE INDEX idx_users_created_at ON users(created_at);
```

### **2. Files (Arquivos)**

```sql
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Metadados do arquivo
    filename VARCHAR(500) NOT NULL,
    original_filename VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_hash VARCHAR(128) UNIQUE, -- SHA-256 para deduplicação
    
    -- Metadados de mídia
    duration NUMERIC(10,2), -- duração em segundos
    sample_rate INTEGER,
    channels INTEGER,
    codec VARCHAR(50),
    
    -- Storage
    storage_bucket VARCHAR(100) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    storage_class VARCHAR(50) DEFAULT 'STANDARD',
    
    -- Status e controle
    status VARCHAR(50) DEFAULT 'uploaded' CHECK (status IN ('uploading', 'uploaded', 'processing', 'archived', 'deleted')),
    upload_completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE, -- auto-delete
    
    -- Metadados customizados
    metadata JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_files_user_id ON files(user_id);
CREATE INDEX idx_files_status ON files(status);
CREATE INDEX idx_files_created_at ON files(created_at);
CREATE INDEX idx_files_expires_at ON files(expires_at);
CREATE INDEX idx_files_file_hash ON files(file_hash);
CREATE INDEX idx_files_metadata ON files USING GIN(metadata);
```

### **3. Jobs (Trabalhos de Transcrição)**

```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    
    -- Configuração da transcrição
    config JSONB NOT NULL,
    preset_used VARCHAR(100),
    
    -- Status e controle
    status VARCHAR(50) DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'completed', 'failed', 'cancelled')),
    priority INTEGER DEFAULT 1, -- 1=low, 2=normal, 3=high, 4=urgent
    
    -- Progresso
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    current_stage VARCHAR(100),
    estimated_completion TIMESTAMP WITH TIME ZONE,
    
    -- Tempos
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_time INTEGER, -- segundos de processamento real
    
    -- Resultados
    speakers_detected INTEGER,
    segments_count INTEGER,
    confidence_avg NUMERIC(3,2), -- 0.00 a 1.00
    word_count INTEGER,
    
    -- Arquivos de resultado
    output_files JSONB DEFAULT '[]'::jsonb,
    
    -- Erros e logs
    error_code VARCHAR(100),
    error_message TEXT,
    error_details JSONB,
    
    -- Worker info
    worker_instance VARCHAR(200),
    gpu_used BOOLEAN DEFAULT false,
    model_used VARCHAR(50),
    
    -- Webhook
    callback_url VARCHAR(500),
    callback_attempts INTEGER DEFAULT 0,
    callback_success BOOLEAN DEFAULT false,
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_file_id ON jobs(file_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_jobs_priority_created ON jobs(priority DESC, created_at ASC); -- para fila
CREATE INDEX idx_jobs_status_priority ON jobs(status, priority DESC);
CREATE INDEX idx_jobs_config ON jobs USING GIN(config);
```

### **4. Speakers (Oradores)**

```sql
CREATE TABLE speakers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    
    -- Identificação
    speaker_id VARCHAR(50) NOT NULL, -- SPEAKER_00, SPEAKER_01, etc.
    custom_name VARCHAR(255),
    
    -- Estatísticas
    segments_count INTEGER DEFAULT 0,
    total_duration NUMERIC(10,2) DEFAULT 0, -- segundos
    first_appearance NUMERIC(10,2), -- timestamp em segundos
    last_appearance NUMERIC(10,2), -- timestamp em segundos
    confidence_avg NUMERIC(3,2), -- 0.00 a 1.00
    
    -- Metadados customizados
    metadata JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(job_id, speaker_id)
);

-- Índices
CREATE INDEX idx_speakers_job_id ON speakers(job_id);
CREATE INDEX idx_speakers_speaker_id ON speakers(speaker_id);
CREATE INDEX idx_speakers_custom_name ON speakers(custom_name);
```

### **5. Transcription_Segments (Segmentos de Transcrição)**

```sql
CREATE TABLE transcription_segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    speaker_id UUID REFERENCES speakers(id) ON DELETE SET NULL,
    
    -- Timing
    start_time NUMERIC(10,3) NOT NULL, -- segundos com precisão de milissegundos
    end_time NUMERIC(10,3) NOT NULL,
    duration NUMERIC(10,3) GENERATED ALWAYS AS (end_time - start_time) STORED,
    
    -- Conteúdo
    text TEXT NOT NULL,
    confidence NUMERIC(3,2), -- 0.00 a 1.00
    language VARCHAR(10),
    
    -- Metadados
    word_count INTEGER,
    no_speech_prob NUMERIC(3,2), -- probabilidade de não ser fala
    
    -- Controle de qualidade
    is_edited BOOLEAN DEFAULT false,
    editor_user_id UUID REFERENCES users(id),
    edited_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_segments_job_id ON transcription_segments(job_id);
CREATE INDEX idx_segments_speaker_id ON transcription_segments(speaker_id);
CREATE INDEX idx_segments_start_time ON transcription_segments(start_time);
CREATE INDEX idx_segments_text_search ON transcription_segments USING GIN(to_tsvector('portuguese', text));
```

### **6. Job_Logs (Logs de Processamento)**

```sql
CREATE TABLE job_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    
    -- Log details
    level VARCHAR(20) NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    message TEXT NOT NULL,
    details JSONB,
    
    -- Context
    stage VARCHAR(100),
    worker_instance VARCHAR(200),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_job_logs_job_id ON job_logs(job_id);
CREATE INDEX idx_job_logs_level ON job_logs(level);
CREATE INDEX idx_job_logs_created_at ON job_logs(created_at);
CREATE INDEX idx_job_logs_stage ON job_logs(stage);

-- Particionamento por mês para performance
CREATE TABLE job_logs_y2024m01 PARTITION OF job_logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### **7. API_Keys (Chaves de API)**

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Key details
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL, -- hash da chave
    key_prefix VARCHAR(20) NOT NULL, -- primeiros caracteres para identificação
    
    -- Permissions
    permissions JSONB DEFAULT '["read", "write"]'::jsonb,
    allowed_ips INET[],
    
    -- Usage limits
    rate_limit_per_minute INTEGER DEFAULT 60,
    rate_limit_per_hour INTEGER DEFAULT 1000,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Usage stats
    total_requests INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);
```

### **8. Presets (Templates de Configuração)**

```sql
CREATE TABLE presets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE, -- NULL para presets públicos
    
    -- Preset details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    config JSONB NOT NULL,
    
    -- Visibility
    is_public BOOLEAN DEFAULT false,
    is_system BOOLEAN DEFAULT false, -- presets do sistema
    
    -- Usage stats
    usage_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, name) -- nome único por usuário
);

-- Índices
CREATE INDEX idx_presets_user_id ON presets(user_id);
CREATE INDEX idx_presets_is_public ON presets(is_public);
CREATE INDEX idx_presets_is_system ON presets(is_system);
CREATE INDEX idx_presets_config ON presets USING GIN(config);
```

### **9. Usage_Statistics (Estatísticas de Uso)**

```sql
CREATE TABLE usage_statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Período
    date DATE NOT NULL,
    hour INTEGER CHECK (hour >= 0 AND hour <= 23),
    
    -- Métricas
    api_requests INTEGER DEFAULT 0,
    files_uploaded INTEGER DEFAULT 0,
    jobs_created INTEGER DEFAULT 0,
    jobs_completed INTEGER DEFAULT 0,
    processing_time_seconds INTEGER DEFAULT 0,
    storage_used_bytes BIGINT DEFAULT 0,
    
    -- Breakdown por modelo
    model_usage JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, date, hour)
);

-- Índices
CREATE INDEX idx_usage_stats_user_date ON usage_statistics(user_id, date);
CREATE INDEX idx_usage_stats_date ON usage_statistics(date);

-- Particionamento por mês
CREATE TABLE usage_statistics_y2024m01 PARTITION OF usage_statistics
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

---

## 🔧 Functions e Triggers

### **1. Trigger para Updated_At**

```sql
-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar a todas as tabelas relevantes
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_files_updated_at BEFORE UPDATE ON files
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_speakers_updated_at BEFORE UPDATE ON speakers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON api_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_presets_updated_at BEFORE UPDATE ON presets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### **2. Função para Calcular Storage Usage**

```sql
-- Função para calcular uso de storage por usuário
CREATE OR REPLACE FUNCTION calculate_user_storage_usage(user_uuid UUID)
RETURNS BIGINT AS $$
DECLARE
    total_size BIGINT;
BEGIN
    SELECT COALESCE(SUM(file_size), 0) INTO total_size
    FROM files
    WHERE user_id = user_uuid AND status NOT IN ('deleted', 'archived');
    
    -- Atualizar na tabela users
    UPDATE users 
    SET current_storage_usage = total_size
    WHERE id = user_uuid;
    
    RETURN total_size;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar storage automaticamente
CREATE OR REPLACE FUNCTION update_user_storage_on_file_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Para INSERT
    IF TG_OP = 'INSERT' THEN
        PERFORM calculate_user_storage_usage(NEW.user_id);
        RETURN NEW;
    END IF;
    
    -- Para UPDATE
    IF TG_OP = 'UPDATE' THEN
        -- Se mudou o user_id ou file_size
        IF OLD.user_id != NEW.user_id OR OLD.file_size != NEW.file_size OR OLD.status != NEW.status THEN
            PERFORM calculate_user_storage_usage(OLD.user_id);
            PERFORM calculate_user_storage_usage(NEW.user_id);
        END IF;
        RETURN NEW;
    END IF;
    
    -- Para DELETE
    IF TG_OP = 'DELETE' THEN
        PERFORM calculate_user_storage_usage(OLD.user_id);
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_storage_usage_trigger
AFTER INSERT OR UPDATE OR DELETE ON files
FOR EACH ROW EXECUTE FUNCTION update_user_storage_on_file_change();
```

### **3. Função para Queue de Jobs**

```sql
-- Função para obter próximo job da fila
CREATE OR REPLACE FUNCTION get_next_job_from_queue()
RETURNS TABLE(job_id UUID, file_path TEXT, config JSONB) AS $$
BEGIN
    RETURN QUERY
    WITH next_job AS (
        SELECT j.id, f.storage_bucket || '/' || f.storage_path as file_path, j.config
        FROM jobs j
        JOIN files f ON j.file_id = f.id
        WHERE j.status = 'queued'
        ORDER BY j.priority DESC, j.created_at ASC
        LIMIT 1
        FOR UPDATE SKIP LOCKED
    )
    UPDATE jobs 
    SET status = 'processing', 
        started_at = NOW(),
        updated_at = NOW()
    FROM next_job
    WHERE jobs.id = next_job.id
    RETURNING next_job.id, next_job.file_path, next_job.config;
END;
$$ LANGUAGE plpgsql;
```

---

## 📊 Views para Analytics

### **1. User Dashboard Stats**

```sql
CREATE VIEW user_dashboard_stats AS
SELECT 
    u.id as user_id,
    u.email,
    u.plan_type,
    
    -- Estatísticas de jobs
    COUNT(j.id) as total_jobs,
    COUNT(CASE WHEN j.status = 'completed' THEN 1 END) as completed_jobs,
    COUNT(CASE WHEN j.status = 'failed' THEN 1 END) as failed_jobs,
    COUNT(CASE WHEN j.status IN ('queued', 'processing') THEN 1 END) as active_jobs,
    
    -- Tempo de processamento
    COALESCE(SUM(j.processing_time), 0) as total_processing_time,
    COALESCE(AVG(j.processing_time), 0) as avg_processing_time,
    
    -- Storage
    u.current_storage_usage,
    u.storage_limit_gb * 1024 * 1024 * 1024 as storage_limit_bytes,
    
    -- Atividade recente
    COUNT(CASE WHEN j.created_at > NOW() - INTERVAL '7 days' THEN 1 END) as jobs_last_7_days,
    COUNT(CASE WHEN j.created_at > NOW() - INTERVAL '30 days' THEN 1 END) as jobs_last_30_days,
    
    -- Modelos mais usados
    (
        SELECT jsonb_object_agg(model_used, count)
        FROM (
            SELECT j2.model_used, COUNT(*) as count
            FROM jobs j2 
            WHERE j2.user_id = u.id AND j2.model_used IS NOT NULL
            GROUP BY j2.model_used
            ORDER BY count DESC
            LIMIT 5
        ) model_stats
    ) as top_models_used

FROM users u
LEFT JOIN jobs j ON u.id = j.user_id
WHERE u.is_active = true
GROUP BY u.id, u.email, u.plan_type, u.current_storage_usage, u.storage_limit_gb;
```

### **2. System Performance Stats**

```sql
CREATE VIEW system_performance_stats AS
WITH daily_stats AS (
    SELECT 
        DATE(created_at) as date,
        COUNT(*) as total_jobs,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
        AVG(processing_time) as avg_processing_time,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY processing_time) as p95_processing_time,
        AVG(confidence_avg) as avg_confidence,
        SUM(CASE WHEN gpu_used THEN 1 ELSE 0 END) as gpu_jobs_count
    FROM jobs
    WHERE created_at > NOW() - INTERVAL '30 days'
    GROUP BY DATE(created_at)
)
SELECT 
    date,
    total_jobs,
    completed_jobs,
    failed_jobs,
    ROUND((completed_jobs::numeric / NULLIF(total_jobs, 0) * 100), 2) as success_rate,
    ROUND(avg_processing_time, 2) as avg_processing_time,
    ROUND(p95_processing_time, 2) as p95_processing_time,
    ROUND(avg_confidence, 3) as avg_confidence,
    gpu_jobs_count,
    ROUND((gpu_jobs_count::numeric / NULLIF(total_jobs, 0) * 100), 2) as gpu_usage_percentage
FROM daily_stats
ORDER BY date DESC;
```

---

## 🔄 Procedures de Manutenção

### **1. Cleanup de Arquivos Expirados**

```sql
-- Procedure para limpar arquivos expirados
CREATE OR REPLACE FUNCTION cleanup_expired_files()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Marcar arquivos como deletados
    UPDATE files 
    SET status = 'deleted', updated_at = NOW()
    WHERE expires_at < NOW() AND status NOT IN ('deleted', 'archived');
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log da operação
    INSERT INTO job_logs (job_id, level, message, details, created_at)
    SELECT 
        NULL as job_id,
        'INFO' as level,
        'Cleanup expired files' as message,
        jsonb_build_object('deleted_count', deleted_count) as details,
        NOW() as created_at;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Executar diariamente via cron job
```

### **2. Aggregate Statistics**

```sql
-- Procedure para calcular estatísticas agregadas
CREATE OR REPLACE FUNCTION update_daily_statistics()
RETURNS VOID AS $$
BEGIN
    -- Inserir estatísticas do dia anterior
    INSERT INTO usage_statistics (user_id, date, api_requests, jobs_created, jobs_completed, processing_time_seconds)
    SELECT 
        j.user_id,
        DATE(j.created_at) as date,
        0 as api_requests, -- será preenchido por outra fonte
        COUNT(*) as jobs_created,
        COUNT(CASE WHEN j.status = 'completed' THEN 1 END) as jobs_completed,
        COALESCE(SUM(j.processing_time), 0) as processing_time_seconds
    FROM jobs j
    WHERE DATE(j.created_at) = CURRENT_DATE - INTERVAL '1 day'
    GROUP BY j.user_id, DATE(j.created_at)
    ON CONFLICT (user_id, date, hour) DO UPDATE SET
        jobs_created = EXCLUDED.jobs_created,
        jobs_completed = EXCLUDED.jobs_completed,
        processing_time_seconds = EXCLUDED.processing_time_seconds;
END;
$$ LANGUAGE plpgsql;
```

---

## 🚀 Comandos de Inicialização

### **1. Script de Criação do Schema**

```sql
-- init_database.sql
-- Execute this script to initialize the database

BEGIN;

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Criar todas as tabelas (execute os CREATEs acima)
-- ...

-- Inserir presets do sistema
INSERT INTO presets (id, name, description, config, is_public, is_system) VALUES
(gen_random_uuid(), 'Reunião Corporativa', 'Otimizado para reuniões empresariais brasileiras', '{
    "model": "medium",
    "language": "pt",
    "num_speakers": "auto",
    "speaker_detection": {"min_speakers": 2, "max_speakers": 8},
    "quality": {"enhance_audio": true, "normalize_volume": true},
    "output_formats": ["txt", "json", "srt"]
}', true, true),
(gen_random_uuid(), 'Entrevista Jornalística', 'Máxima qualidade para entrevistas', '{
    "model": "large",
    "language": "pt", 
    "num_speakers": 2,
    "quality": {"enhance_audio": true, "noise_reduction": true},
    "output_formats": ["txt", "json"]
}', true, true),
(gen_random_uuid(), 'Podcast Brasileiro', 'Otimizado para podcasts longos', '{
    "model": "medium",
    "language": "pt",
    "num_speakers": "auto",
    "speaker_detection": {"min_speakers": 2, "max_speakers": 5},
    "preprocessing": {"split_long_audio": true, "chunk_duration": 600},
    "output_formats": ["txt", "srt", "json"]
}', true, true);

-- Criar usuário admin padrão (alterar senha em produção)
INSERT INTO users (email, password_hash, full_name, plan_type, is_active, email_verified)
VALUES ('admin@legenda.iaforte.com.br', '$2b$12$example_hash', 'Administrador', 'enterprise', true, true);

COMMIT;
```

Este schema fornece uma base sólida e escalável para o sistema de transcrição, com foco em performance, auditoria e analytics detalhados.