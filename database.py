import sqlite3
import os

DATABASE = 'sisvenda.db'

def get_db():
    """Conecta ao banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    return conn

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabela de produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT,
            telefone TEXT,
            endereco TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total REAL NOT NULL,
            status TEXT DEFAULT 'pendente',
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')
    
    # Tabela de itens da venda
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venda_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    ''')
    
    conn.commit()
    conn.close()
