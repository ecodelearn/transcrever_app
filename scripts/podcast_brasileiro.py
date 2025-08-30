#!/usr/bin/env python3
"""
Script otimizado para transcrição de podcasts brasileiros.
Configurado para conteúdo longo, múltiplos oradores e geração de legendas.
"""

import os
import sys
import subprocess
from pathlib import Path

# Configurações específicas para podcasts
PODCAST_CONFIG = {
    'WHISPER_MODEL': 'medium',
    'OUTPUT_FORMAT': 'txt,srt,json',
    'NUM_SPEAKERS': 'auto',
    'MIN_SPEAKERS': '2',
    'MAX_SPEAKERS': '5',
    'PODCAST_MODE': 'true',
    'VERBOSE_LOGGING': 'false',  # Menos verboso para conteúdo longo
    'CONFIDENCE_THRESHOLD': '0.6',
    'AUTO_NORMALIZE_VOLUME': 'true',
    'PORTUGUESE_POSTPROCESSING': 'true',
    'ENABLE_TEXT_CORRECTIONS': 'true',
    'PROCESSING_TIMEOUT': '7200',  # 2 horas timeout para podcasts longos
    'BATCH_SIZE': '8'  # Menor batch para economia de memória
}

def processar_podcast(arquivo_entrada, pasta_saida=None, nome_podcast=None, episodio=None):
    """
    Processa um podcast com configurações otimizadas.
    
    Args:
        arquivo_entrada (str): Caminho para o arquivo de áudio/vídeo
        pasta_saida (str): Pasta de destino para os resultados
        nome_podcast (str): Nome do podcast
        episodio (str): Número ou nome do episódio
    """
    
    if not os.path.exists(arquivo_entrada):
        print(f"❌ Arquivo não encontrado: {arquivo_entrada}")
        return False
    
    # Configurar pasta de saída
    if pasta_saida is None:
        nome_arquivo = Path(arquivo_entrada).stem
        if nome_podcast and episodio:
            pasta_saida = f"output/podcast_{nome_podcast.replace(' ', '_')}_ep{episodio}"
        elif nome_podcast:
            pasta_saida = f"output/podcast_{nome_podcast.replace(' ', '_')}"
        else:
            pasta_saida = f"output/podcast_{nome_arquivo}"
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Aplicar configurações
    env = os.environ.copy()
    env.update(PODCAST_CONFIG)
    env['OUTPUT_DIR'] = pasta_saida
    
    if nome_podcast:
        prefix = f"{nome_podcast.replace(' ', '_')}"
        if episodio:
            prefix += f"_ep{episodio}"
        env['OUTPUT_PREFIX'] = prefix + "_"
    
    print(f"🎧 Processando podcast: {arquivo_entrada}")
    if nome_podcast:
        print(f"📻 Podcast: {nome_podcast}")
    if episodio:
        print(f"📺 Episódio: {episodio}")
    print(f"📁 Resultado será salvo em: {pasta_saida}")
    print("⚙️ Configurações: Podcast (Otimizado para conteúdo longo)")
    print("👥 Detectando múltiplos oradores automaticamente...")
    print("⏱️ Processamento pode demorar para arquivos longos...")
    
    # Executar transcrição
    comando = [sys.executable, 'transcrever.py', arquivo_entrada]
    
    try:
        resultado = subprocess.run(comando, env=env, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            print("✅ Podcast processado com sucesso!")
            print(f"🎧 Material pronto para publicação em: {pasta_saida}")
            
            # Gerar arquivos adicionais para podcast
            gerar_arquivos_podcast(pasta_saida, nome_podcast, episodio)
            return True
        else:
            print(f"❌ Erro no processamento: {resultado.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def gerar_arquivos_podcast(pasta_saida, nome_podcast, episodio):
    """Gera arquivos adicionais específicos para podcasts."""
    
    try:
        # Buscar arquivos gerados
        pasta = Path(pasta_saida)
        arquivos_srt = list(pasta.glob("*.srt"))
        arquivos_json = list(pasta.glob("*.json"))
        
        if arquivos_json:
            import json
            
            with open(arquivos_json[0], 'r', encoding='utf-8') as f:
                transcricao = json.load(f)
            
            # Gerar show notes básicas
            arquivo_shownotes = pasta / "show_notes.md"
            
            with open(arquivo_shownotes, 'w', encoding='utf-8') as f:
                f.write("# Show Notes\n\n")
                if nome_podcast:
                    f.write(f"**Podcast:** {nome_podcast}\n")
                if episodio:
                    f.write(f"**Episódio:** {episodio}\n")
                f.write(f"**Duração:** Aprox. {calcular_duracao(transcricao)} minutos\n")
                f.write(f"**Oradores identificados:** {len(set(t['speaker'] for t in transcricao))}\n\n")
                
                f.write("## Transcrição Completa\n\n")
                f.write("*Gerada automaticamente - revisar antes da publicação*\n\n")
                
                for entrada in transcricao[:10]:  # Primeiros 10 segmentos como amostra
                    f.write(f"**{entrada['speaker']}:** {entrada['text']}\n\n")
                
                f.write("...\n\n*(Transcrição completa nos outros arquivos)*")
            
            print(f"📝 Show notes geradas: {arquivo_shownotes}")
        
        if arquivos_srt:
            # Converter SRT para WebVTT para web
            arquivo_vtt = pasta / f"{arquivos_srt[0].stem}.vtt"
            converter_srt_para_vtt(arquivos_srt[0], arquivo_vtt)
            print(f"🌐 Legendas WebVTT geradas: {arquivo_vtt}")
        
    except Exception as e:
        print(f"⚠️ Erro ao gerar arquivos adicionais: {e}")

def calcular_duracao(transcricao):
    """Calcula duração aproximada do podcast em minutos."""
    if not transcricao:
        return 0
    
    ultimo_timestamp = transcricao[-1]['start']
    # Converter timestamp para segundos
    partes = ultimo_timestamp.split(':')
    segundos = int(partes[0]) * 3600 + int(partes[1]) * 60 + int(partes[2])
    return round(segundos / 60)

def converter_srt_para_vtt(arquivo_srt, arquivo_vtt):
    """Converte arquivo SRT para WebVTT."""
    
    with open(arquivo_srt, 'r', encoding='utf-8') as f:
        conteudo_srt = f.read()
    
    # Converter formato
    conteudo_vtt = "WEBVTT\n\n" + conteudo_srt.replace(',', '.')
    
    with open(arquivo_vtt, 'w', encoding='utf-8') as f:
        f.write(conteudo_vtt)

def main():
    """Função principal para execução via linha de comando."""
    
    if len(sys.argv) < 2:
        print("📋 Uso: python podcast_brasileiro.py <arquivo> [pasta_saida] [nome_podcast] [episodio]")
        print("📋 Exemplo: python podcast_brasileiro.py podcast.mp3")
        print("📋 Exemplo: python podcast_brasileiro.py podcast.mp3 resultados/ 'Meu Podcast' '001'")
        sys.exit(1)
    
    arquivo = sys.argv[1]
    pasta_saida = sys.argv[2] if len(sys.argv) > 2 else None
    nome_podcast = sys.argv[3] if len(sys.argv) > 3 else None
    episodio = sys.argv[4] if len(sys.argv) > 4 else None
    
    sucesso = processar_podcast(arquivo, pasta_saida, nome_podcast, episodio)
    sys.exit(0 if sucesso else 1)

if __name__ == "__main__":
    main()