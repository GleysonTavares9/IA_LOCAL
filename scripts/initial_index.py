import sys
import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from typing import List

# Adiciona o diretório raiz ao path para importar o app
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.storage.metadata_db import MetadataDB
from app.ingestion.scanner import DirectoryScanner
from app.processors.pdf_processor import PDFProcessor
from app.processors.docx_processor import DOCXProcessor
from app.processors.excel_processor import ExcelProcessor
from app.processors.image_processor import ImageProcessor
from app.processors.video_processor import VideoProcessor
from app.processors.text_processor import TextProcessor
from app.indexing.chunker import TextChunker
from app.indexing.embedder import Embedder
from app.indexing.vector_store import VectorStore
from app.utils.logger import logger

def process_single_file(file_id: int):
    """Processa um único arquivo de forma isolada para permitir paralelismo."""
    db = MetadataDB()
    chunker = TextChunker()
    embedder = Embedder()
    vector_store = VectorStore()
    
    processors = {
        '.pdf': PDFProcessor(),
        '.docx': DOCXProcessor(),
        '.xlsx': ExcelProcessor(),
        '.xls': ExcelProcessor(),
        '.png': ImageProcessor(),
        '.jpg': ImageProcessor(),
        '.jpeg': ImageProcessor(),
        '.mp4': VideoProcessor(),
        '.avi': VideoProcessor(),
        '.mov': VideoProcessor(),
        '.txt': TextProcessor(),
        '.csv': TextProcessor(),
        '.json': TextProcessor()
    }
    
    # Busca o caminho do arquivo
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT file_path, file_type FROM files WHERE id = ?", (file_id,))
        res = cursor.fetchone()
        if not res: return
        file_path, file_type = res
            
    logger.info(f"Processando arquivo: {file_path}")
    
    processor = processors.get(file_type)
    if not processor:
        logger.warning(f"Nenhum processador para o tipo: {file_type}")
        return
        
    try:
        # 1. Extração de conteúdo
        text = processor.extract_text(file_path)
        metadata = processor.extract_metadata(file_path)
        
        # 2. Chunking
        chunks = chunker.chunk_text(text, metadata)
        if not chunks:
            logger.warning(f"Nenhum conteúdo extraído de: {file_path}")
            db.update_file_status(file_id, 'completed')
            return
            
        # 3. Embeddings
        texts_to_embed = [c['content'] for c in chunks]
        embeddings = embedder.get_embeddings(texts_to_embed)
        
        # 4. Armazenamento Vetorial
        ids = [f"{file_id}_{i}" for i in range(len(chunks))]
        metadatas = [{"file_id": str(file_id), "file_name": Path(file_path).name} for _ in chunks]
        vector_store.add_documents(ids, texts_to_embed, embeddings, metadatas)
        
        # 5. Atualização do Banco de Metadados
        db.save_chunks(file_id, chunks)
        db.update_file_status(file_id, 'completed')
        logger.info(f"Arquivo {file_path} indexado com sucesso.")
        
    except Exception as e:
        logger.error(f"Erro ao processar {file_path}: {e}")
        db.update_file_status(file_id, 'error')

def run_indexing():
    """Executa o pipeline incremental de indexação com paralelismo."""
    db = MetadataDB()
    scanner = DirectoryScanner(db)
    
    # 1. Varredura de arquivos novos ou alterados
    file_ids = scanner.scan()
    
    if not file_ids:
        logger.info("Nenhum arquivo novo para indexar.")
        return

    # 2. Processamento paralelo para escalabilidade
    max_workers = max(1, os.cpu_count() - 1)
    logger.info(f"Iniciando processamento paralelo com {max_workers} workers.")
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        executor.map(process_single_file, file_ids)

if __name__ == "__main__":
    run_indexing()
