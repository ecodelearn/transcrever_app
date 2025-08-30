#!/usr/bin/env python3
"""
🚀 Backend Simplificado - Transcritor API
Versão básica para testar antes de instalar todas as dependências
"""

import os
import sys
import json
import uuid
from datetime import datetime
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

print("🚀 Transcritor API - Backend Simplificado")
print("=" * 50)

def check_environment():
    """Verificar ambiente e dependências."""
    
    print("\n📋 Verificando ambiente...")
    
    # Python version
    print(f"🐍 Python: {sys.version}")
    
    # Verificar se venv está ativo
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Ambiente virtual ativo")
    else:
        print("⚠️  Ambiente virtual não detectado")
    
    # Verificar arquivo .env
    env_file = project_root / ".env"
    if env_file.exists():
        print("✅ Arquivo .env encontrado")
        
        # Verificar token
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if "HUGGINGFACE_TOKEN" in content:
                    print("✅ Token Hugging Face configurado")
                else:
                    print("⚠️  Token Hugging Face não encontrado")
        except Exception as e:
            print(f"❌ Erro ao ler .env: {e}")
    else:
        print("❌ Arquivo .env não encontrado")
    
    # Verificar script CLI
    cli_script = project_root / "transcrever.py"
    if cli_script.exists():
        print("✅ Script CLI encontrado")
    else:
        print("❌ Script CLI não encontrado")
    
    # Verificar GPU (se torch estiver disponível)
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU disponível: {gpu_name}")
        else:
            print("⚠️  GPU não disponível")
    except ImportError:
        print("⚠️  PyTorch não instalado")
    
    # Verificar dependências críticas
    missing_deps = []
    critical_deps = ['fastapi', 'uvicorn', 'pydantic', 'python-multipart']
    
    for dep in critical_deps:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep}")
        except ImportError:
            missing_deps.append(dep)
            print(f"❌ {dep} não instalado")
    
    if missing_deps:
        print(f"\n⚠️  Dependências faltando: {', '.join(missing_deps)}")
        print("💡 Execute: pip install -r requirements-web.txt")
        return False
    
    return True


def simulate_job_processing():
    """Simular processamento de job."""
    
    print("\n🧪 Simulando processamento de job...")
    
    # Criar job simulado
    job_id = str(uuid.uuid4())
    
    job_data = {
        "job_id": job_id,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
        "filename": "teste_audio.mp3",
        "model": "medium",
        "enable_diarization": True,
        "language": "pt",
        "progress": 0,
        "message": "Job criado"
    }
    
    print(f"📝 Job criado: {job_id}")
    print(f"📊 Status: {job_data['status']}")
    
    # Simular progresso
    stages = [
        (10, "Validando arquivo..."),
        (25, "Carregando modelo..."),
        (40, "Extraindo áudio..."),
        (65, "Processando transcrição..."),
        (85, "Identificando oradores..."),
        (100, "Concluído!")
    ]
    
    import time
    for progress, message in stages:
        job_data["progress"] = progress
        job_data["message"] = message
        print(f"⏳ {progress}% - {message}")
        time.sleep(0.5)
    
    job_data["status"] = "completed"
    job_data["completed_at"] = datetime.utcnow().isoformat()
    
    # Resultado simulado
    result = {
        "segments": [
            {
                "id": "segment_001",
                "start": "00:00:00.000",
                "end": "00:00:05.420",
                "speaker": "SPEAKER_00",
                "text": "Olá, bem-vindos à nossa reunião de hoje.",
                "confidence": 0.95
            },
            {
                "id": "segment_002",
                "start": "00:00:05.420",
                "end": "00:00:12.180",
                "speaker": "SPEAKER_01", 
                "text": "Obrigado. Vamos começar discutindo o orçamento.",
                "confidence": 0.92
            }
        ],
        "speakers": {
            "SPEAKER_00": {"speaker_id": "SPEAKER_00", "segment_count": 1},
            "SPEAKER_01": {"speaker_id": "SPEAKER_01", "segment_count": 1}
        },
        "metadata": {
            "total_duration": 12.18,
            "language": "pt",
            "model_used": "medium",
            "speakers_detected": 2,
            "word_count": 12
        }
    }
    
    job_data["result"] = result
    
    print("\n🎉 Job concluído com sucesso!")
    print(f"👥 Oradores detectados: {result['metadata']['speakers_detected']}")
    print(f"📝 Palavras: {result['metadata']['word_count']}")
    
    return job_data


def test_file_operations():
    """Testar operações de arquivo."""
    
    print("\n📁 Testando operações de arquivo...")
    
    # Criar diretórios necessários
    dirs = ["uploads", "results", "temp"]
    for dir_name in dirs:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Diretório criado/verificado: {dir_name}")
    
    # Testar escrita de arquivo de resultado
    test_job_id = "test_" + str(uuid.uuid4())[:8]
    
    result_data = {
        "job_id": test_job_id,
        "timestamp": datetime.utcnow().isoformat(),
        "result": "Teste de escrita de arquivo"
    }
    
    # Salvar como JSON
    result_file = project_root / "results" / f"{test_job_id}.json"
    try:
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Arquivo de resultado criado: {result_file.name}")
        
        # Verificar se pode ler
        with open(result_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        print(f"✅ Arquivo lido com sucesso: {loaded_data['job_id']}")
        
        # Limpar arquivo de teste
        result_file.unlink()
        print("✅ Arquivo de teste removido")
        
    except Exception as e:
        print(f"❌ Erro nas operações de arquivo: {e}")


def show_next_steps():
    """Mostrar próximos passos."""
    
    print("\n🎯 Próximos Passos")
    print("=" * 30)
    
    print("\n1. 🚀 Ativar ambiente virtual:")
    print("   ./activate.sh")
    print("   # ou")
    print("   source venv/bin/activate")
    
    print("\n2. 📦 Instalar dependências:")
    print("   pip install -r requirements-web.txt")
    
    print("\n3. 🧪 Testar script CLI atual:")
    print("   python transcrever.py --help")
    
    print("\n4. 🌐 Rodar API FastAPI:")
    print("   cd backend")
    print("   uvicorn main:app --reload")
    
    print("\n5. 🌍 Testar API no browser:")
    print("   http://localhost:8000")
    print("   http://localhost:8000/docs")
    
    print("\n6. 🔧 Configurar VSCode:")
    print("   Ctrl+Shift+P -> Python: Select Interpreter")
    print("   Escolher: ./venv/bin/python")
    
    print("\n💡 Dicas:")
    print("   - Use 'nvidia-smi' para monitorar GPU")
    print("   - Logs detalhados com --verbose no CLI")
    print("   - Swagger UI em /docs para testar API")


def main():
    """Função principal."""
    
    try:
        # Verificar ambiente
        env_ok = check_environment()
        
        # Testar operações básicas
        test_file_operations()
        
        # Simular processamento
        simulate_job_processing()
        
        # Mostrar próximos passos
        show_next_steps()
        
        if env_ok:
            print("\n🎉 Ambiente pronto para desenvolvimento!")
        else:
            print("\n⚠️  Configure as dependências antes de continuar")
            
    except KeyboardInterrupt:
        print("\n\n👋 Bye!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()