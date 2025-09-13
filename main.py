from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Importe o Flask-CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Habilita o CORS para todas as rotas
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
    pontos_usuario = dados.get('pontos')

    usuario_existente = Usuario.query.filter_by(nome=nome_usuario).first()
    if usuario_existente:
        return jsonify({'mensagem': 'Nome de usuário já existe'}), 409

    novo_usuario = Usuario(nome=nome_usuario, senha=senha_usuario, email=email_usuario, pontos=pontos_usuario or 0)
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
            }
        }), 200
    else:
        return jsonify({'mensagem': 'E-mail ou senha inválidos'}), 401

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
                'pontos': usuario.pontos
            })
        return jsonify(lista_usuarios), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)