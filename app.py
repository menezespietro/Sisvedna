import sqlite3
import os

# --- FUNÇÕES DE BANCO DE DADOS ---
def conectar():
    return sqlite3.connect('database.db')

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()
    
    # Criar tabelas
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT UNIQUE,
                        senha TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT,
                        cpf TEXT UNIQUE)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT,
                        preco REAL,
                        estoque INTEGER)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS vendas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_produto INTEGER,
                        id_cliente INTEGER,
                        quantidade INTEGER,
                        total REAL,
                        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(id_produto) REFERENCES produtos(id),
                        FOREIGN KEY(id_cliente) REFERENCES clientes(id))''')
    
    # Criar um usuário padrão se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES ('admin', 'admin123')")
    
    conn.commit()
    conn.close()

# --- MÓDULOS DO SISTEMA ---

def tela_login():
    print("\n" + "="*30)
    print("      SISVENDA - LOGIN")
    print("="*30)
    usuario = input("Usuário: ")
    senha = input("Senha: ")
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
    usuario_logado = cursor.fetchone()
    conn.close()
    
    return usuario_logado

def modulo_clientes():
    print("\n--- CADASTRO DE CLIENTES ---")
    nome = input("Nome completo: ")
    cpf = input("CPF: ")
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nome, cpf) VALUES (?, ?)", (nome, cpf))
        conn.commit()
        print("✔ Cliente cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("✖ Erro: Este CPF já está cadastrado.")
    finally:
        conn.close()

def modulo_produtos():
    print("\n--- CADASTRO DE PRODUTOS ---")
    nome = input("Nome do produto: ")
    preco = float(input("Preço unitário: "))
    estoque = int(input("Quantidade em estoque: "))
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)", (nome, preco, estoque))
    conn.commit()
    conn.close()
    print("✔ Produto cadastrado!")

def modulo_vendas():
    print("\n--- NOVA VENDA ---")
    conn = conectar()
    cursor = conn.cursor()
    
    # Listar produtos disponíveis
    cursor.execute("SELECT id, nome, preco, estoque FROM produtos WHERE estoque > 0")
    produtos = cursor.fetchall()
    
    if not produtos:
        print("Não há produtos em estoque.")
        return

    print("Produtos Disponíveis:")
    for p in produtos:
        print(f"ID: {p[0]} | {p[1]} | R$ {p[2]:.22} | Estoque: {p[3]}")
    
    try:
        id_prod = int(input("\nDigite o ID do produto: "))
        id_cli = int(input("Digite o ID do cliente: "))
        qtd = int(input("Quantidade: "))
        
        # Verificar produto e estoque
        cursor.execute("SELECT preco, estoque FROM produtos WHERE id = ?", (id_prod,))
        prod_data = cursor.fetchone()
        
        if prod_data and prod_data[1] >= qtd:
            total = prod_data[0] * qtd
            cursor.execute("INSERT INTO vendas (id_produto, id_cliente, quantidade, total) VALUES (?, ?, ?, ?)",
                           (id_prod, id_cli, qtd, total))
            cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (qtd, id_prod))
            conn.commit()
            print(f"✔ Venda finalizada! Total: R$ {total:.2f}")
        else:
            print("✖ Venda cancelada: Produto não encontrado ou estoque insuficiente.")
    except ValueError:
        print("✖ Erro: Digite apenas números para IDs e Quantidade.")
    finally:
        conn.close()

# --- LOOP PRINCIPAL ---

def menu_principal():
    inicializar_banco()
    
    usuario = tela_login()
    if not usuario:
        print("Acesso Negado!")
        return

    while True:
        print("\n" + "-"*30)
        print(f" BEM-VINDO AO SISVENDA")
        print("-"*30)
        print("1. Cadastrar Cliente")
        print("2. Cadastrar Produto")
        print("3. Realizar Venda")
        print("4. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == '1':
            modulo_clientes()
        elif opcao == '2':
            modulo_produtos()
        elif opcao == '3':
            modulo_vendas()
        elif opcao == '4':
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    menu_principal()