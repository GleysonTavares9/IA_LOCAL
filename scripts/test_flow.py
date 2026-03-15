import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.storage.metadata_db import MetadataDB
from app.ingestion.scanner import DirectoryScanner
from app.processors.text_processor import TextProcessor
from app.indexing.chunker import TextChunker
from app.utils.logger import logger

def run_test():
    logger.info("Iniciando teste de fluxo simplificado...")
    
    # 1. Inicializa Banco de Dados
    db = MetadataDB()
    logger.info("Banco de dados SQLite inicializado.")
    
    # 2. Varredura de Arquivos
    scanner = DirectoryScanner(db)
    file_ids = scanner.scan()
    
    if not file_ids:
        logger.error("Nenhum arquivo encontrado para indexar!")
        return

    logger.info(f"Arquivos encontrados: {len(file_ids)}")
    
    # 3. Processamento do primeiro arquivo encontrado
    file_id = file_ids[0]
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT file_path, file_type FROM files WHERE id = ?", (file_id,))
        file_path, file_type = cursor.fetchone()
    
    logger.info(f"Processando arquivo de teste: {file_path}")
    
    processor = TextProcessor()
    text = processor.extract_text(file_path)
    metadata = processor.extract_metadata(file_path)
    
    logger.info(f"Texto extraído (primeiros 50 caracteres): {text[:50]}...")
    
    # 4. Chunking
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk_text(text, metadata)
    
    logger.info(f"Número de chunks gerados: {len(chunks)}")
    
    # 5. Salva no Banco de Metadados (Simulando sucesso sem embeddings)
    db.save_chunks(file_id, chunks)
    db.update_file_status(file_id, 'completed')
    
    logger.info("Teste de fluxo concluído com sucesso!")
    
    # 6. Verificação Final
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM chunks WHERE file_id = ?", (file_id,))
        count = cursor.fetchone()[0]
        logger.info(f"Verificação: {count} chunks salvos no banco de dados.")

if __name__ == "__main__":
    run_test()
