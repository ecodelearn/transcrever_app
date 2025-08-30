#!/usr/bin/env python3
"""
Script otimizado para transcrição de entrevistas jornalísticas brasileiras.
Configurado para máxima qualidade e identificação precisa de entrevistador/entrevistado.
"""

import os
import sys
import subprocess
from pathlib import Path

# Configurações específicas para entrevistas jornalísticas
ENTREVISTA_CONFIG = {
    'WHISPER_MODEL': 'large',
    'OUTPUT_FORMAT': 'txt,json',
    'NUM_SPEAKERS': '2',  # Geralmente entrevistador + entrevistado
    'MIN_SPEAKERS': '2',
    'MAX_SPEAKERS': '3',
    'INTERVIEW_MODE': 'true',
    'VERBOSE_LOGGING': 'true',
    'CONFIDENCE_THRESHOLD': '0.8',
    'AUTO_NORMALIZE_VOLUME': 'true',
    'PORTUGUESE_POSTPROCESSING': 'true',
    'ENABLE_TEXT_CORRECTIONS': 'true',
    'AUDIO_SAMPLE_RATE': '22050'  # Maior qualidade para áudio jornalístico
}

def processar_entrevista(arquivo_entrada, pasta_saida=None, nome_entrevistado=None):
    """
    Processa uma entrevista com configurações otimizadas.
    
    Args:
        arquivo_entrada (str): Caminho para o arquivo de áudio/vídeo
        pasta_saida (str): Pasta de destino para os resultados
        nome_entrevistado (str): Nome do entrevistado para personalizar saída
    """
    
    if not os.path.exists(arquivo_entrada):
        print(f"❌ Arquivo não encontrado: {arquivo_entrada}")
        return False
    
    # Configurar pasta de saída
    if pasta_saida is None:
        nome_arquivo = Path(arquivo_entrada).stem
        if nome_entrevistado:
            pasta_saida = f"output/entrevista_{nome_entrevistado.replace(' ', '_')}"
        else:
            pasta_saida = f"output/entrevista_{nome_arquivo}"
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Aplicar configurações
    env = os.environ.copy()
    env.update(ENTREVISTA_CONFIG)
    env['OUTPUT_DIR'] = pasta_saida
    
    if nome_entrevistado:
        env['OUTPUT_PREFIX'] = f"entrevista_{nome_entrevistado.replace(' ', '_')}_"
    
    print(f"🎤 Processando entrevista: {arquivo_entrada}")
    if nome_entrevistado:
        print(f"👤 Entrevistado: {nome_entrevistado}")
    print(f"📁 Resultado será salvo em: {pasta_saida}")
    print("⚙️ Configurações: Entrevista Jornalística (Máxima Qualidade)")
    print("👥 Detectando 2 oradores (entrevistador/entrevistado)...")
    
    # Executar transcrição
    comando = [sys.executable, 'transcrever.py', arquivo_entrada]
    
    try:
        resultado = subprocess.run(comando, env=env, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            print("✅ Entrevista processada com sucesso!")
            print(f"📰 Material pronto para edição em: {pasta_saida}")
            
            # Gerar arquivo adicional com formatação jornalística
            gerar_formato_jornalistico(pasta_saida, nome_entrevistado)
            return True
        else:
            print(f"❌ Erro no processamento: {resultado.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def gerar_formato_jornalistico(pasta_saida, nome_entrevistado):
    """Gera um arquivo formatado especificamente para uso jornalístico."""
    
    try:
        # Buscar arquivo JSON gerado
        arquivos_json = list(Path(pasta_saida).glob("*.json"))
        if not arquivos_json:
            return
        
        import json
        
        with open(arquivos_json[0], 'r', encoding='utf-8') as f:
            transcricao = json.load(f)
        
        # Gerar formato jornalístico
        arquivo_jornalistico = Path(pasta_saida) / "formato_jornalistico.txt"
        
        with open(arquivo_jornalistico, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("TRANSCRIÇÃO PARA USO JORNALÍSTICO\n")
            f.write("=" * 60 + "\n\n")
            
            if nome_entrevistado:
                f.write(f"ENTREVISTADO: {nome_entrevistado}\n")
            f.write(f"DATA: {Path(arquivos_json[0]).stat().st_mtime}\n")
            f.write("OBSERVAÇÃO: Verificar citações antes da publicação\n\n")
            
            f.write("-" * 60 + "\n")
            f.write("TRANSCRIÇÃO COMPLETA\n")
            f.write("-" * 60 + "\n\n")
            
            orador_atual = None
            for entrada in transcricao:
                if entrada['speaker'] != orador_atual:
                    orador_atual = entrada['speaker']
                    f.write(f"\n[{entrada['speaker']}]: ")
                f.write(entrada['text'] + " ")
        
        print(f"📰 Formato jornalístico gerado: {arquivo_jornalistico}")
        
    except Exception as e:
        print(f"⚠️ Erro ao gerar formato jornalístico: {e}")

def main():
    """Função principal para execução via linha de comando."""
    
    if len(sys.argv) < 2:
        print("📋 Uso: python entrevista_jornalistica.py <arquivo> [pasta_saida] [nome_entrevistado]")
        print("📋 Exemplo: python entrevista_jornalistica.py entrevista.mp4")
        print("📋 Exemplo: python entrevista_jornalistica.py entrevista.wav resultados/ 'João Silva'")
        sys.exit(1)
    
    arquivo = sys.argv[1]
    pasta_saida = sys.argv[2] if len(sys.argv) > 2 else None
    nome_entrevistado = sys.argv[3] if len(sys.argv) > 3 else None
    
    sucesso = processar_entrevista(arquivo, pasta_saida, nome_entrevistado)
    sys.exit(0 if sucesso else 1)

if __name__ == "__main__":
    main()