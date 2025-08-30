#!/usr/bin/env python3
"""
Script otimizado para transcrição de reuniões corporativas brasileiras.
Configurado para detectar múltiplos oradores e gerar relatórios estruturados.
"""

import os
import sys
import subprocess
from pathlib import Path

# Configurações específicas para reuniões corporativas
REUNIAO_CONFIG = {
    'WHISPER_MODEL': 'medium',
    'OUTPUT_FORMAT': 'txt,json,srt',
    'NUM_SPEAKERS': 'auto',
    'MIN_SPEAKERS': '2',
    'MAX_SPEAKERS': '8',
    'CORPORATE_MODE': 'true',
    'VERBOSE_LOGGING': 'true',
    'CONFIDENCE_THRESHOLD': '0.7',
    'AUTO_NORMALIZE_VOLUME': 'true',
    'PORTUGUESE_POSTPROCESSING': 'true'
}

def processar_reuniao(arquivo_entrada, pasta_saida=None):
    """
    Processa um arquivo de reunião com configurações otimizadas.
    
    Args:
        arquivo_entrada (str): Caminho para o arquivo de áudio/vídeo
        pasta_saida (str): Pasta de destino para os resultados
    """
    
    if not os.path.exists(arquivo_entrada):
        print(f"❌ Arquivo não encontrado: {arquivo_entrada}")
        return False
    
    # Configurar pasta de saída
    if pasta_saida is None:
        nome_arquivo = Path(arquivo_entrada).stem
        pasta_saida = f"output/reuniao_{nome_arquivo}"
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Aplicar configurações
    env = os.environ.copy()
    env.update(REUNIAO_CONFIG)
    env['OUTPUT_DIR'] = pasta_saida
    
    print(f"🎙️ Processando reunião: {arquivo_entrada}")
    print(f"📁 Resultado será salvo em: {pasta_saida}")
    print("⚙️ Configurações: Reunião Corporativa")
    print("👥 Detectando múltiplos oradores automaticamente...")
    
    # Executar transcrição
    comando = [sys.executable, 'transcrever.py', arquivo_entrada]
    
    try:
        resultado = subprocess.run(comando, env=env, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            print("✅ Reunião processada com sucesso!")
            print(f"📊 Verifique os resultados em: {pasta_saida}")
            return True
        else:
            print(f"❌ Erro no processamento: {resultado.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    """Função principal para execução via linha de comando."""
    
    if len(sys.argv) < 2:
        print("📋 Uso: python reuniao_corporativa.py <arquivo> [pasta_saida]")
        print("📋 Exemplo: python reuniao_corporativa.py reuniao_diretoria.mp4")
        print("📋 Exemplo: python reuniao_corporativa.py reuniao.wav resultados/")
        sys.exit(1)
    
    arquivo = sys.argv[1]
    pasta_saida = sys.argv[2] if len(sys.argv) > 2 else None
    
    sucesso = processar_reuniao(arquivo, pasta_saida)
    sys.exit(0 if sucesso else 1)

if __name__ == "__main__":
    main()