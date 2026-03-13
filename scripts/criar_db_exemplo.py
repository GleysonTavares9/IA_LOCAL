"""
scripts/criar_db_exemplo.py — Cria banco SQLite de exemplo para testes.
Use: python scripts/criar_db_exemplo.py
"""

import sqlite3
from pathlib import Path
from datetime import date, timedelta
import random

DB_PATH = Path(__file__).parent.parent / "dados_db" / "base.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def criar_banco():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS clientes (
        id            INTEGER PRIMARY KEY,
        nome          TEXT    NOT NULL,
        email         TEXT,
        cidade        TEXT,
        data_cadastro DATE
    );

    CREATE TABLE IF NOT EXISTS produtos (
        id        INTEGER PRIMARY KEY,
        nome      TEXT    NOT NULL,
        categoria TEXT,
        preco     REAL,
        estoque   INTEGER
    );

    CREATE TABLE IF NOT EXISTS pedidos (
        id           INTEGER PRIMARY KEY,
        cliente_id   INTEGER,
        produto_id   INTEGER,
        quantidade   INTEGER,
        valor_total  REAL,
        data_pedido  DATE,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
    );
    """)

    # Inserir clientes de exemplo
    clientes = [
        (1, "João Silva",      "joao@email.com",   "São Paulo",       "2024-01-15"),
        (2, "Maria Santos",    "maria@email.com",   "Rio de Janeiro",  "2024-02-20"),
        (3, "Pedro Oliveira",  "pedro@email.com",   "Belo Horizonte",  "2024-03-10"),
        (4, "Ana Ferreira",    "ana@email.com",     "Curitiba",        "2024-04-05"),
        (5, "Carlos Mendes",   "carlos@email.com",  "Fortaleza",       "2024-05-12"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO clientes VALUES (?,?,?,?,?)", clientes
    )

    # Inserir produtos de exemplo
    produtos = [
        (1, "Notebook Pro",       "Eletrônicos",  3500.00, 15),
        (2, "Mouse Wireless",     "Periféricos",   150.00, 50),
        (3, "Teclado Mecânico",   "Periféricos",   350.00, 30),
        (4, "Monitor 27\"",       "Eletrônicos",  1800.00, 10),
        (5, "Webcam Full HD",     "Periféricos",   280.00, 25),
        (6, "Headset Gamer",      "Periféricos",   420.00, 20),
        (7, "SSD 1TB",            "Armazenamento", 450.00, 40),
        (8, "Cadeira Ergonômica", "Móveis",       1200.00,  8),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO produtos VALUES (?,?,?,?,?)", produtos
    )

    # Gerar pedidos aleatórios
    pedidos = []
    for i in range(1, 31):
        cliente_id = random.randint(1, 5)
        produto = random.choice(produtos)
        quantidade = random.randint(1, 3)
        valor = produto[3] * quantidade
        data = (date(2024, 1, 1) + timedelta(days=random.randint(0, 364))).isoformat()
        pedidos.append((i, cliente_id, produto[0], quantidade, valor, data))

    cursor.executemany(
        "INSERT OR IGNORE INTO pedidos VALUES (?,?,?,?,?,?)", pedidos
    )

    conn.commit()
    conn.close()
    return len(pedidos)


if __name__ == "__main__":
    n = criar_banco()
    print(f"✅ Banco de dados criado em: {DB_PATH}")
    print(f"   • 5 clientes, 8 produtos, {n} pedidos aleatórios gerados.")
