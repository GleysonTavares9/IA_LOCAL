import os
from pathlib import Path
from typing import List, Dict, Any
from app.config.settings import RAW_DATA_PATH, ALLOWED_EXTENSIONS
from app.storage.metadata_db import MetadataDB
from app.utils.hashes import calculate_file_hash
from app.utils.logger import logger

class DirectoryScanner:
    def __init__(self, db: MetadataDB, root_path: Path = RAW_DATA_PATH):
        self.db = db
        self.root_path = root_path
        self.root_path.mkdir(parents=True, exist_ok=True)

    def scan(self) -> List[int]:
        """Varre o diretório em busca de arquivos novos ou alterados."""
        logger.info(f"Iniciando varredura em: {self.root_path}")
        processed_ids = []
        
        for root, _, files in os.walk(self.root_path):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                    file_id = self._process_file_entry(file_path)
                    if file_id:
                        processed_ids.append(file_id)
        
        logger.info(f"Varredura concluída. {len(processed_ids)} arquivos identificados para processamento.")
        return processed_ids

    def _process_file_entry(self, file_path: Path) -> int:
        """Verifica se o arquivo precisa ser (re)indexado e o registra."""
        file_hash = calculate_file_hash(str(file_path))
        last_modified = file_path.stat().st_mtime
        
        existing_file = self.db.get_file_by_path(str(file_path))
        
        # Se o arquivo já existe e o hash não mudou, pula
        if existing_file and existing_file['file_hash'] == file_hash:
            # logger.debug(f"Arquivo ignorado (sem alterações): {file_path}")
            return None
            
        file_data = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_hash': file_hash,
            'file_type': file_path.suffix.lower(),
            'last_modified': last_modified
        }
        
        file_id = self.db.register_file(file_data)
        logger.info(f"Arquivo registrado para processamento: {file_path} (ID: {file_id})")
        return file_id
