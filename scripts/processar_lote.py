#!/usr/bin/env python3
"""
Script para processamento em lote de múltiplos arquivos de áudio/vídeo.
Otimizado para processar grandes volumes de conteúdo brasileiro.
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configurações para processamento em lote
LOTE_CONFIG = {
    'WHISPER_MODEL': 'medium',
    'OUTPUT_FORMAT': 'txt,json',
    'NUM_SPEAKERS': 'auto',
    'VERBOSE_LOGGING': 'false',
    'BATCH_SIZE': '4',
    'USE_GPU': 'true',
    'KEEP_TEMP_FILES': 'false',
    'PORTUGUESE_POSTPROCESSING': 'true'
}

# Extensões de arquivo suportadas
EXTENSOES_SUPORTADAS = {
    '.mp3', '.wav', '.m4a', '.flac', '.ogg',  # Áudio
    '.mp4', '.mkv', '.mov', '.avi', '.webm'   # Vídeo
}

def encontrar_arquivos(diretorio):
    """Encontra todos os arquivos de áudio/vídeo em um diretório."""
    
    arquivos = []
    diretorio = Path(diretorio)
    
    if diretorio.is_file():
        if diretorio.suffix.lower() in EXTENSOES_SUPORTADAS:
            return [diretorio]
        else:
            print(f"❌ Extensão não suportada: {diretorio.suffix}")
            return []
    
    for arquivo in diretorio.rglob('*'):
        if arquivo.is_file() and arquivo.suffix.lower() in EXTENSOES_SUPORTADAS:
            arquivos.append(arquivo)
    
    return sorted(arquivos)

def processar_arquivo_unico(arquivo, pasta_saida, progresso_callback=None):
    """Processa um único arquivo."""
    
    nome_arquivo = arquivo.stem
    pasta_arquivo = Path(pasta_saida) / nome_arquivo
    pasta_arquivo.mkdir(parents=True, exist_ok=True)
    
    # Configurar ambiente
    env = os.environ.copy()
    env.update(LOTE_CONFIG)
    env['OUTPUT_DIR'] = str(pasta_arquivo)
    env['INPUT_FILE'] = str(arquivo)
    
    inicio = time.time()
    
    try:
        # Executar transcrição
        comando = [sys.executable, 'transcrever.py', str(arquivo)]
        resultado = subprocess.run(comando, env=env, capture_output=True, text=True)
        
        fim = time.time()
        duracao = fim - inicio
        
        if resultado.returncode == 0:
            status = "✅ SUCESSO"
            erro = None
        else:
            status = "❌ ERRO"
            erro = resultado.stderr
        
        if progresso_callback:
            progresso_callback(arquivo, status, duracao, erro)
        
        return {
            'arquivo': arquivo,
            'sucesso': resultado.returncode == 0,
            'duracao': duracao,
            'erro': erro,
            'pasta_saida': pasta_arquivo
        }
        
    except Exception as e:
        if progresso_callback:
            progresso_callback(arquivo, f"❌ EXCEÇÃO: {e}", time.time() - inicio, str(e))
        
        return {
            'arquivo': arquivo,
            'sucesso': False,
            'duracao': time.time() - inicio,
            'erro': str(e),
            'pasta_saida': pasta_arquivo
        }

def processar_lote(diretorio_entrada, pasta_saida, max_workers=2):
    """Processa múltiplos arquivos em paralelo."""
    
    arquivos = encontrar_arquivos(diretorio_entrada)
    
    if not arquivos:
        print(f"❌ Nenhum arquivo de áudio/vídeo encontrado em: {diretorio_entrada}")
        return []
    
    print(f"📁 Encontrados {len(arquivos)} arquivo(s) para processar")
    print(f"⚙️ Usando {max_workers} worker(s) paralelo(s)")
    print(f"📂 Resultados serão salvos em: {pasta_saida}")
    print("=" * 60)
    
    # Criar pasta de saída
    Path(pasta_saida).mkdir(parents=True, exist_ok=True)
    
    # Estatísticas
    estatisticas = {
        'total': len(arquivos),
        'processados': 0,
        'sucessos': 0,
        'erros': 0,
        'tempo_total': 0
    }
    
    def callback_progresso(arquivo, status, duracao, erro):
        estatisticas['processados'] += 1
        estatisticas['tempo_total'] += duracao
        
        if "SUCESSO" in status:
            estatisticas['sucessos'] += 1
        else:
            estatisticas['erros'] += 1
        
        print(f"[{estatisticas['processados']}/{estatisticas['total']}] "
              f"{arquivo.name} - {status} ({duracao:.1f}s)")
        
        if erro and "ERRO" in status:
            print(f"    💡 Erro: {erro[:100]}...")
    
    # Processamento paralelo
    resultados = []
    inicio_total = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submeter tarefas
        futures = {
            executor.submit(processar_arquivo_unico, arquivo, pasta_saida, callback_progresso): arquivo
            for arquivo in arquivos
        }
        
        # Coletar resultados
        for future in as_completed(futures):
            resultado = future.result()
            resultados.append(resultado)
    
    # Relatório final
    fim_total = time.time()
    duracao_total = fim_total - inicio_total
    
    print("=" * 60)
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    print(f"📁 Total de arquivos: {estatisticas['total']}")
    print(f"✅ Sucessos: {estatisticas['sucessos']}")
    print(f"❌ Erros: {estatisticas['erros']}")
    print(f"⏱️ Tempo total: {duracao_total:.1f}s")
    print(f"⚡ Tempo médio por arquivo: {duracao_total/len(arquivos):.1f}s")
    print(f"📂 Resultados em: {pasta_saida}")
    
    # Gerar relatório detalhado
    gerar_relatorio(resultados, pasta_saida)
    
    return resultados

def gerar_relatorio(resultados, pasta_saida):
    """Gera relatório detalhado do processamento em lote."""
    
    arquivo_relatorio = Path(pasta_saida) / "relatorio_processamento.txt"
    
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE PROCESSAMENTO EM LOTE\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Data: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total de arquivos: {len(resultados)}\n")
        f.write(f"Sucessos: {sum(1 for r in resultados if r['sucesso'])}\n")
        f.write(f"Erros: {sum(1 for r in resultados if not r['sucesso'])}\n\n")
        
        f.write("DETALHES POR ARQUIVO\n")
        f.write("-" * 50 + "\n")
        
        for resultado in resultados:
            status = "SUCESSO" if resultado['sucesso'] else "ERRO"
            f.write(f"\n📁 {resultado['arquivo'].name}\n")
            f.write(f"   Status: {status}\n")
            f.write(f"   Duração: {resultado['duracao']:.1f}s\n")
            f.write(f"   Pasta: {resultado['pasta_saida']}\n")
            
            if resultado['erro']:
                f.write(f"   Erro: {resultado['erro']}\n")
    
    print(f"📋 Relatório detalhado salvo: {arquivo_relatorio}")

def main():
    """Função principal para execução via linha de comando."""
    
    if len(sys.argv) < 2:
        print("📋 Uso: python processar_lote.py <diretorio_entrada> [pasta_saida] [workers]")
        print("📋 Exemplo: python processar_lote.py audios/")
        print("📋 Exemplo: python processar_lote.py videos/ resultados/ 4")
        print("📋 Exemplo: python processar_lote.py arquivo.mp4 resultados/")
        sys.exit(1)
    
    diretorio_entrada = sys.argv[1]
    pasta_saida = sys.argv[2] if len(sys.argv) > 2 else "output/lote"
    max_workers = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    
    if not os.path.exists(diretorio_entrada):
        print(f"❌ Diretório não encontrado: {diretorio_entrada}")
        sys.exit(1)
    
    resultados = processar_lote(diretorio_entrada, pasta_saida, max_workers)
    
    # Código de saída baseado nos resultados
    erros = sum(1 for r in resultados if not r['sucesso'])
    sys.exit(1 if erros > 0 else 0)

if __name__ == "__main__":
    main()