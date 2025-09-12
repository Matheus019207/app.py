# # Importa as bibliotecas que vamos usar
# from flask import Flask, jsonify, request
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db' # O nome do arquivo do banco de dados mudou
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# # Permissão de Acesso (CORS) - Essencial para o GitHub Pages
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
#     return response

# # --- Estrutura da Tabela de Usuários ---
# class Usuario(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     nome = db.Column(db.String(80), unique=True, nullable=False) # Nome de usuário único
#     senha = db.Column(db.String(120), nullable=False) # Armazenar a senha
#     email = db.Column(db.String(120), nullable=False) # Email opcional
    
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

#     # Verifica se o usuário já existe no banco de dados
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

#     # Busca o usuário no banco de dados
#     usuario = Usuario.query.filter_by(email=email_usuario).first()

#     # Verifica se o usuário existe e se a senha está correta
#     if usuario and usuario.senha == senha_usuario:
#         return jsonify({
#             'mensagem': 'Login bem-sucedido!',
#             'usuario_logado': {
#                 'nome': usuario.nome,
#                 'email': usuario.email,
#             }
#         }), 200
#     else:
#         return jsonify({'mensagem': 'E-mail ou senha inválidos'}), 401
# # Rota de Depuração (remova isso em produção!)
# @app.route('/debug/usuarios')
# def ver_usuarios_debug():
#     try:
#         usuarios = Usuario.query.all()
#         lista_usuarios = []
#         for usuario in usuarios:
#             lista_usuarios.append({
#                 'id': usuario.id,
#                 'nome': usuario.nome,
#                 'senha_hash': usuario.senha,
#                 'email': usuario.email,
#             })
#         return jsonify(lista_usuarios), 200
#     except Exception as e:
#         return jsonify({'erro': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)





# Importa as bibliotecas que vamos usar
from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS # Adicionei esta biblioteca

# AQUI! A variável 'app' é criada aqui.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Adicionei esta linha para habilitar o CORS com cookies
CORS(app, supports_credentials=True, origins='*') 

db = SQLAlchemy(app)

# --- Estrutura da Tabela de Usuários ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'

# Cria a tabela de usuários se ela não existir
with app.app_context():
    db.create_all()

# --- Rotas da API para Login e Cadastro ---

# Rota para cadastrar um novo usuário (método POST)
@app.route('/cadastrar', methods=['POST'])
def cadastrar_usuario():
    dados = request.get_json()
    nome_usuario = dados.get('nome')
    senha_usuario = dados.get('senha')
    email_usuario = dados.get('email')

    # Verifica se o usuário já existe no banco de dados
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
        response = make_response(jsonify({
            'mensagem': 'Login bem-sucedido!',
            'usuario_logado': {
                'nome': usuario.nome,
                'email': usuario.email,
            }
        }))
        # Configuração do cookie para funcionar entre domínios diferentes
        response.set_cookie('user_session', email_usuario, max_age=60 * 60 * 24 * 7, secure=True, samesite='None') 
        return response
    else:
        return jsonify({'mensagem': 'E-mail ou senha inválidos'}), 401

# Nova rota para verificar se o usuário já está logado via cookie
@app.route('/status', methods=['GET'])
def check_login_status():
    email_do_cookie = request.cookies.get('user_session')
    if email_do_cookie:
        usuario = Usuario.query.filter_by(email=email_do_cookie).first()
        if usuario:
            return jsonify({
                'logado': True,
                'nome': usuario.nome
            }), 200
    return jsonify({'logado': False}), 200
        
# Rota de Depuração
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
            })
        return jsonify(lista_usuarios), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)