from flask import Flask, request, jsonify
from database import init_db
from models import Produto, Cliente, Venda

app = Flask(__name__)

# Inicializa o banco de dados
init_db()

# Rotas para Produtos
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    """Lista todos os produtos"""
    produtos = Produto.get_all()
    return jsonify([dict(produto) for produto in produtos])

@app.route('/produtos/<int:id>', methods=['GET'])
def obter_produto(id):
    """Obtém um produto específico"""
    produto = Produto.get_by_id(id)
    if produto:
        return jsonify(dict(produto))
    return jsonify({'erro': 'Produto não encontrado'}), 404

@app.route('/produtos', methods=['POST'])
def criar_produto():
    """Cria um novo produto"""
    data = request.json
    required_fields = ['nome', 'preco', 'estoque']
    
    if not all(field in data for field in required_fields):
        return jsonify({'erro': 'Campos obrigatórios faltando'}), 400
    
    produto_id = Produto.create(
        data['nome'],
        data.get('descricao', ''),
        float(data['preco']),
        int(data['estoque'])
    )
    
    return jsonify({'id': produto_id, 'mensagem': 'Produto criado com sucesso'}), 201

@app.route('/produtos/<int:id>', methods=['PUT'])
def atualizar_produto(id):
    """Atualiza um produto"""
    data = request.json
    sucesso = Produto.update(
        id,
        data['nome'],
        data.get('descricao', ''),
        float(data['preco']),
        int(data['estoque'])
    )
    
    if sucesso:
        return jsonify({'mensagem': 'Produto atualizado com sucesso'})
    return jsonify({'erro': 'Produto não encontrado'}), 404

@app.route('/produtos/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    """Deleta um produto"""
    sucesso = Produto.delete(id)
    if sucesso:
        return jsonify({'mensagem': 'Produto deletado com sucesso'})
    return jsonify({'erro': 'Produto não encontrado'}), 404

# Rotas para Clientes
@app.route('/clientes', methods=['GET'])
def listar_clientes():
    """Lista todos os clientes"""
    clientes = Cliente.get_all()
    return jsonify([dict(cliente) for cliente in clientes])

@app.route('/clientes/<int:id>', methods=['GET'])
def obter_cliente(id):
    """Obtém um cliente específico"""
    cliente = Cliente.get_by_id(id)
    if cliente:
        return jsonify(dict(cliente))
    return jsonify({'erro': 'Cliente não encontrado'}), 404

@app.route('/clientes', methods=['POST'])
def criar_cliente():
    """Cria um novo cliente"""
    data = request.json
    if 'nome' not in data:
        return jsonify({'erro': 'Campo nome é obrigatório'}), 400
    
    cliente_id = Cliente.create(
        data['nome'],
        data.get('email', ''),
        data.get('telefone', ''),
        data.get('endereco', '')
    )
    
    return jsonify({'id': cliente_id, 'mensagem': 'Cliente criado com sucesso'}), 201

@app.route('/clientes/<int:id>', methods=['PUT'])
def atualizar_cliente(id):
    """Atualiza um cliente"""
    data = request.json
    sucesso = Cliente.update(
        id,
        data['nome'],
        data.get('email', ''),
        data.get('telefone', ''),
        data.get('endereco', '')
    )
    
    if sucesso:
        return jsonify({'mensagem': 'Cliente atualizado com sucesso'})
    return jsonify({'erro': 'Cliente não encontrado'}), 404

@app.route('/clientes/<int:id>', methods=['DELETE'])
def deletar_cliente(id):
    """Deleta um cliente"""
    sucesso = Cliente.delete(id)
    if sucesso:
        return jsonify({'mensagem': 'Cliente deletado com sucesso'})
    return jsonify({'erro': 'Cliente não encontrado'}), 404

# Rotas para Vendas
@app.route('/vendas', methods=['GET'])
def listar_vendas():
    """Lista todas as vendas"""
    vendas = Venda.get_all()
    return jsonify([dict(venda) for venda in vendas])

@app.route('/vendas/<int:id>', methods=['GET'])
def obter_venda(id):
    """Obtém uma venda específica com seus itens"""
    venda = Venda.get_by_id(id)
    if not venda:
        return jsonify({'erro': 'Venda não encontrada'}), 404
    
    itens = Venda.get_itens(id)
    venda_dict = dict(venda)
    venda_dict['itens'] = [dict(item) for item in itens]
    
    return jsonify(venda_dict)

@app.route('/vendas', methods=['POST'])
def criar_venda():
    """Cria uma nova venda"""
    data = request.json
    
    if 'itens' not in data or not data['itens']:
        return jsonify({'erro': 'Lista de itens é obrigatória'}), 400
    
    # Valida e processa os itens
    itens = []
    for item in data['itens']:
        if 'produto_id' not in item or 'quantidade' not in item:
            return jsonify({'erro': 'Cada item deve ter produto_id e quantidade'}), 400
        
        # Obtém o produto para pegar o preço
        produto = Produto.get_by_id(item['produto_id'])
        if not produto:
            return jsonify({'erro': f'Produto {item["produto_id"]} não encontrado'}), 404
        
        itens.append({
            'produto_id': item['produto_id'],
            'quantidade': item['quantidade'],
            'preco_unitario': produto['preco']
        })
    
    try:
        venda_id = Venda.create(data.get('cliente_id'), itens)
        return jsonify({'id': venda_id, 'mensagem': 'Venda realizada com sucesso'}), 201
    except Exception as e:
        return jsonify({'erro': f'Erro ao processar venda: {str(e)}'}), 400

@app.route('/vendas/<int:id>/status', methods=['PATCH'])
def atualizar_status_venda(id):
    """Atualiza o status de uma venda"""
    data = request.json
    if 'status' not in data:
        return jsonify({'erro': 'Campo status é obrigatório'}), 400
    
    sucesso = Venda.update_status(id, data['status'])
    if sucesso:
        return jsonify({'mensagem': 'Status atualizado com sucesso'})
    return jsonify({'erro': 'Venda não encontrada'}), 404

# Rotas de relatório
@app.route('/relatorio/vendas', methods=['GET'])
def relatorio_vendas():
    """Gera um relatório simples de vendas"""
    vendas = Venda.get_all()
    
    total_vendas = len(vendas)
    valor_total = sum(venda['total'] for venda in vendas)
    
    return jsonify({
        'total_vendas': total_vendas,
        'valor_total': valor_total,
        'vendas': [dict(venda) for venda in vendas]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
