import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.config.settings import SQLITE_DB_PATH
from app.utils.logger import logger

class MetadataDB:
    def __init__(self, db_path: Path = SQLITE_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Inicializa o banco de dados SQLite com as tabelas necessárias."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela de Arquivos (File Registry)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_name TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    last_modified REAL NOT NULL,
                    status TEXT DEFAULT 'pending', -- pending, processing, completed, error
                    department TEXT,
                    sensitivity TEXT,
                    language TEXT,
                    version INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de Chunks (Relação com arquivos)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT, -- Metadados específicos do chunk (página, aba, etc)
                    vector_id TEXT, -- ID no ChromaDB
                    FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
                )
            """)
            
            # Tabela de Auditoria
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    file_id INTEGER,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("Banco de dados SQLite inicializado com sucesso.")

    def register_file(self, file_data: Dict[str, Any]) -> int:
        """Registra ou atualiza um arquivo no banco de dados."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO files (file_path, file_name, file_hash, file_type, last_modified, status)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(file_path) DO UPDATE SET
                    file_hash=excluded.file_hash,
                    last_modified=excluded.last_modified,
                    status='pending',
                    updated_at=CURRENT_TIMESTAMP
                RETURNING id
            """, (
                file_data['file_path'],
                file_data['file_name'],
                file_data['file_hash'],
                file_data['file_type'],
                file_data['last_modified'],
                'pending'
            ))
            file_id = cursor.fetchone()[0]
            conn.commit()
            return file_id

    def get_file_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Busca um arquivo pelo caminho."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM files WHERE file_path = ?", (file_path,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_file_status(self, file_id: int, status: str, **kwargs):
        """Atualiza o status e metadados de um arquivo."""
        fields = [f"{k} = ?" for k in kwargs.keys()]
        values = list(kwargs.values())
        
        query = f"UPDATE files SET status = ?, updated_at = CURRENT_TIMESTAMP"
        if fields:
            query += ", " + ", ".join(fields)
        query += " WHERE id = ?"
        
        with self._get_connection() as conn:
            conn.execute(query, [status] + values + [file_id])
            conn.commit()

    def save_chunks(self, file_id: int, chunks: List[Dict[str, Any]]):
        """Salva os chunks de um arquivo."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Remove chunks antigos se existirem (reindexação)
            cursor.execute("DELETE FROM chunks WHERE file_id = ?", (file_id,))
            
            for i, chunk in enumerate(chunks):
                cursor.execute("""
                    INSERT INTO chunks (file_id, chunk_index, content, metadata_json, vector_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (file_id, i, chunk['content'], chunk.get('metadata_json'), chunk.get('vector_id')))
            conn.commit()
