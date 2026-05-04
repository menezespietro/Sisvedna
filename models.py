from database import get_db
import sqlite3

class Produto:
    @staticmethod
    def create(nome, descricao, preco, estoque):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO produtos (nome, descricao, preco, estoque) VALUES (?, ?, ?, ?)',
            (nome, descricao, preco, estoque)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM produtos ORDER BY nome')
        return cursor.fetchall()
    
    @staticmethod
    def get_by_id(id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM produtos WHERE id = ?', (id,))
        return cursor.fetchone()
    
    @staticmethod
    def update(id, nome, descricao, preco, estoque):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ? WHERE id = ?',
            (nome, descricao, preco, estoque, id)
        )
        db.commit()
        return cursor.rowcount > 0
    
    @staticmethod
    def delete(id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM produtos WHERE id = ?', (id,))
        db.commit()
        return cursor.rowcount > 0
    
    @staticmethod
    def update_estoque(id, quantidade):
        """Atualiza o estoque do produto"""
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?',
            (quantidade, id, quantidade)
        )
        db.commit()
        return cursor.rowcount > 0

class Cliente:
    @staticmethod
    def create(nome, email, telefone, endereco):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO clientes (nome, email, telefone, endereco) VALUES (?, ?, ?, ?)',
            (nome, email, telefone, endereco)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM clientes ORDER BY nome')
        return cursor.fetchall()
    
    @staticmethod
    def get_by_id(id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM clientes WHERE id = ?', (id,))
        return cursor.fetchone()
    
    @staticmethod
    def update(id, nome, email, telefone, endereco):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'UPDATE clientes SET nome = ?, email = ?, telefone = ?, endereco = ? WHERE id = ?',
            (nome, email, telefone, endereco, id)
        )
        db.commit()
        return cursor.rowcount > 0
    
    @staticmethod
    def delete(id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM clientes WHERE id = ?', (id,))
        db.commit()
        return cursor.rowcount > 0

class Venda:
    @staticmethod
    def create(cliente_id, itens):
        """Cria uma nova venda com seus itens
        itens: lista de dicionários [{'produto_id': 1, 'quantidade': 2, 'preco_unitario': 10.00}]
        """
        db = get_db()
        cursor = db.cursor()
        
        # Calcula o total da venda
        total = sum(item['quantidade'] * item['preco_unitario'] for item in itens)
        
        try:
            # Inicia transação
            cursor.execute('BEGIN TRANSACTION')
            
            # Insere a venda
            cursor.execute(
                'INSERT INTO vendas (cliente_id, total) VALUES (?, ?)',
                (cliente_id, total)
            )
            venda_id = cursor.lastrowid
            
            # Insere os itens da venda
            for item in itens:
                subtotal = item['quantidade'] * item['preco_unitario']
                cursor.execute(
                    '''INSERT INTO venda_itens 
                       (venda_id, produto_id, quantidade, preco_unitario, subtotal) 
                       VALUES (?, ?, ?, ?, ?)''',
                    (venda_id, item['produto_id'], item['quantidade'], 
                     item['preco_unitario'], subtotal)
                )
                
                # Atualiza estoque
                Produto.update_estoque(item['produto_id'], item['quantidade'])
            
            db.commit()
            return venda_id
        except Exception as e:
            db.rollback()
            raise e
    
    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT v.*, c.nome as cliente_nome 
            FROM vendas v
            LEFT JOIN clientes c ON v.cliente_id = c.id
            ORDER BY v.data_venda DESC
        ''')
        return cursor.fetchall()
    
    @staticmethod
    def get_by_id(id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM vendas WHERE id = ?', (id,))
        return cursor.fetchone()
    
    @staticmethod
    def get_itens(venda_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT vi.*, p.nome as produto_nome 
            FROM venda_itens vi
            JOIN produtos p ON vi.produto_id = p.id
            WHERE vi.venda_id = ?
        ''', (venda_id,))
        return cursor.fetchall()
    
    @staticmethod
    def update_status(id, status):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'UPDATE vendas SET status = ? WHERE id = ?',
            (status, id)
        )
        db.commit()
        return cursor.rowcount > 0
