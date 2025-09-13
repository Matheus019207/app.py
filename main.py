# from flask import Flask, jsonify, request
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS  # Importe o Flask-CORS

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # Habilita o CORS para todas as rotas
# CORS(app, origins='*')

# db = SQLAlchemy(app)

# # --- Estrutura da Tabela de Usuários ---
# class Usuario(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     nome = db.Column(db.String(80), unique=True, nullable=False)
#     senha = db.Column(db.String(120), nullable=False)
#     email = db.Column(db.String(120), nullable=False)
    
#     def __repr__(self):
#         return f'<Usuario {self.nome}>'

# # Cria a tabela de usuários se ela não existir
# with app.app_context():
#     db.create_all()

# # --- Rotas da API para Login e Cadastro ---

# # Rota para cadastrar um novo usuário (método POST)
# @app.route('/cadastrar', methods=['POST'])
# def cadastrar_usuario():
#     dados = request.get_json()
#     nome_usuario = dados.get('nome')
#     senha_usuario = dados.get('senha')
#     email_usuario = dados.get('email')

#     usuario_existente = Usuario.query.filter_by(nome=nome_usuario).first()
#     if usuario_existente:
#         return jsonify({'mensagem': 'Nome de usuário já existe'}), 409

#     novo_usuario = Usuario(nome=nome_usuario, senha=senha_usuario, email=email_usuario)
#     db.session.add(novo_usuario)
#     db.session.commit()
    
#     return jsonify({'mensagem': 'Usuário cadastrado com sucesso!'}), 201

# # Rota para login de um usuário (método POST)
# @app.route('/login', methods=['POST'])
# def fazer_login():
#     dados = request.get_json()
#     email_usuario = dados.get('email')
#     senha_usuario = dados.get('senha')
    
#     if not email_usuario or not senha_usuario:
#         return jsonify({'mensagem': 'Email e senha são obrigatórios'}), 400

#     usuario = Usuario.query.filter_by(email=email_usuario).first()

#     if usuario and usuario.senha == senha_usuario:
#         return jsonify({
#             'mensagem': 'Login bem-sucedido!',
#             'token': usuario.email,
#             'usuario_logado': {
#                 'nome': usuario.nome,
#                 'email': usuario.email,
#             }
#         }), 200
#     else:
#         return jsonify({'mensagem': 'E-mail ou senha inválidos'}), 401

# # Rota para verificar se o usuário já está logado via token
# @app.route('/status', methods=['GET'])
# def check_login_status():
#     auth_header = request.headers.get('Authorization')
#     if auth_header and auth_header.startswith('Bearer '):
#         token = auth_header.split(' ')[1]
#         usuario = Usuario.query.filter_by(email=token).first()
#         if usuario:
#             return jsonify({
#                 'logado': True,
#                 'nome': usuario.nome
#             }), 200
#     return jsonify({'logado': False}), 200
        
# # Rota de Depuração
# @app.route('/debug/usuarios')
# def ver_usuarios_debug():
#     try:
#         usuarios = Usuario.query.all()
#         lista_usuarios = []
#         for usuario in usuarios:
#             lista_usuarios.append({
#                 'id': usuario.id,
#                 'nome': usuario.nome,
#                 'senha': usuario.senha,
#                 'email': usuario.email
#             })
#         return jsonify(lista_usuarios), 200
#     except Exception as e:
#         return jsonify({'erro': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)








from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, origins='*')

db = SQLAlchemy(app)

# --- Estrutura da Tabela de Usuários ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    pontos = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'

# --- Estrutura da Tabela de Códigos Promocionais ---
class Codigo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(100), unique=True, nullable=False)
    usado = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Codigo {self.codigo}>'

# Cria as tabelas de usuários e códigos se elas não existirem
with app.app_context():
    db.create_all()

# --- Rotas da API ---

# Rota para cadastrar um novo usuário (método POST)
@app.route('/cadastrar', methods=['POST'])
def cadastrar_usuario():
    dados = request.get_json()
    nome_usuario = dados.get('nome')
    senha_usuario = dados.get('senha')
    email_usuario = dados.get('email')

    usuario_existente = Usuario.query.filter_by(nome=nome_usuario).first()
    if usuario_existente:
        return jsonify({'mensagem': 'Nome de usuário já existe'}), 409

    novo_usuario = Usuario(nome=nome_usuario, senha=senha_usuario, email=email_usuario)
    db.session.add(novo_usuario)
    db.session.commit()
    
    return jsonify({'mensagem': 'Usuário cadastrado com sucesso!'}), 201

# Rota para login de um usuário (método POST)
@app.route('/login', methods=['POST'])
def fazer_login():
    dados = request.get_json()
    email_usuario = dados.get('email')
    senha_usuario = dados.get('senha')
    
    if not email_usuario or not senha_usuario:
        return jsonify({'mensagem': 'Email e senha são obrigatórios'}), 400

    usuario = Usuario.query.filter_by(email=email_usuario).first()

    if usuario and usuario.senha == senha_usuario:
        return jsonify({
            'mensagem': 'Login bem-sucedido!',
            'token': usuario.email,
            'usuario_logado': {
                'nome': usuario.nome,
                'email': usuario.email,
                'pontos': usuario.pontos, # Retorna os pontos do usuário
            }
        }), 200
    else:
        return jsonify({'mensagem': 'E-mail ou senha inválidos'}), 401

# Rota para validar um código e adicionar pontos (método POST)
@app.route('/validar-codigo', methods=['POST'])
def validar_codigo():
    dados = request.get_json()
    codigo_recebido = dados.get('codigo')
    email_usuario = dados.get('email')

    # 1. Encontra o código no banco de dados
    codigo_existente = Codigo.query.filter_by(codigo=codigo_recebido).first()

    if not codigo_existente:
        return jsonify({'mensagem': 'Código inválido'}), 404

    if codigo_existente.usado:
        return jsonify({'mensagem': 'Este código já foi utilizado'}), 409
    
    # 2. Encontra o usuário pelo email
    usuario = Usuario.query.filter_by(email=email_usuario).first()
    if not usuario:
        return jsonify({'mensagem': 'Usuário não encontrado'}), 404

    # 3. Adiciona os pontos ao usuário e marca o código como usado
    usuario.pontos += 1000
    codigo_existente.usado = True
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Pontos adicionados com sucesso!', 
        'novos_pontos': usuario.pontos
    }), 200

# Rota para verificar se o usuário já está logado via token
@app.route('/status', methods=['GET'])
def check_login_status():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        usuario = Usuario.query.filter_by(email=token).first()
        if usuario:
            return jsonify({
                'logado': True,
                'nome': usuario.nome,
                'pontos': usuario.pontos # Retorna os pontos do usuário
            }), 200
    return jsonify({'logado': False}), 200
    
# Rota de Depuração (apenas para testar)
@app.route('/debug/usuarios')
def ver_usuarios_debug():
    try:
        usuarios = Usuario.query.all()
        lista_usuarios = []
        for usuario in usuarios:
            lista_usuarios.append({
                'id': usuario.id,
                'nome': usuario.nome,
                'senha': usuario.senha,
                'email': usuario.email,
                'pontos': usuario.pontos
            })
        return jsonify(lista_usuarios), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# Rota para adicionar um código de teste (apenas para depuração)
@app.route('/debug/adicionar-codigo-teste')
def adicionar_codigo_teste():
    try:
        novo_codigo = Codigo(codigo='CODIGO1000')
        db.session.add(novo_codigo)
        db.session.commit()
        return jsonify({'mensagem': 'Código de teste CODIGO1000 adicionado com sucesso!'}), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)