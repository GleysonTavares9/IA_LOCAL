import sqlite3
from pathlib import Path

db_path = Path("databases/metadata.sqlite")

def verify():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- TABELA FILES ---")
    cursor.execute("SELECT id, file_name, file_type, status FROM files")
    for row in cursor.fetchall():
        print(row)
        
    print("\n--- TABELA CHUNKS (Primeiros 5) ---")
    cursor.execute("SELECT id, file_id, chunk_index, substr(content, 1, 50) FROM chunks LIMIT 5")
    for row in cursor.fetchall():
        print(row)
        
    conn.close()

if __name__ == "__main__":
    verify()
