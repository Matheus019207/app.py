# Importa as bibliotecas que vamos usar
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db' # O nome do arquivo do banco de dados mudou
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Permissão de Acesso (CORS) - Essencial para o GitHub Pages
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# --- Estrutura da Tabela de Usuários ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False) # Nome de usuário único
    senha = db.Column(db.String(120), nullable=False) # Armazenar a senha
    
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
    
    if not nome_usuario or not senha_usuario:
        return jsonify({'mensagem': 'Nome de usuário e senha são obrigatórios'}), 400

    # Verifica se o usuário já existe no banco de dados
    usuario_existente = Usuario.query.filter_by(nome=nome_usuario).first()
    if usuario_existente:
        return jsonify({'mensagem': 'Nome de usuário já existe'}), 409

    novo_usuario = Usuario(nome=nome_usuario, senha=senha_usuario)
    db.session.add(novo_usuario)
    db.session.commit()
    
    return jsonify({'mensagem': 'Usuário cadastrado com sucesso!'}), 201

# Rota para login de um usuário (método POST)
@app.route('/login', methods=['POST'])
def fazer_login():
    dados = request.get_json()
    nome_usuario = dados.get('nome')
    senha_usuario = dados.get('senha')
    
    if not nome_usuario or not senha_usuario:
        return jsonify({'mensagem': 'Nome de usuário e senha são obrigatórios'}), 400

    # Busca o usuário no banco de dados
    usuario = Usuario.query.filter_by(nome=nome_usuario).first()

    # Verifica se o usuário existe e se a senha está correta
    if usuario and usuario.senha == senha_usuario:
        return jsonify({'mensagem': 'Login bem-sucedido!'}), 200
    else:
        return jsonify({'mensagem': 'Nome de usuário ou senha inválidos'}), 401

if __name__ == '__main__':
    app.run(debug=True)

# Rota de Depuração (remova isso em produção!)
@app.route('/debug/usuarios')
def ver_usuarios_debug():
    try:
        usuarios = Usuario.query.all()
        lista_usuarios = []
        for usuario in usuarios:
            lista_usuarios.append({
                'id': usuario.id,
                'nome': usuario.nome,
                'senha_hash': usuario.senha  # Lembre-se, em produção, NUNCA mostre a senha real
            })
        return jsonify(lista_usuarios), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500