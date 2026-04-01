from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'gamestore_secret_key_2026'

# ─────────────────────────────────────────────
# DADOS SIMULADOS
# ─────────────────────────────────────────────

usuarios = [
    {'id': 1, 'nome': 'Alice Gamer',  'email': 'alice@email.com',  'senha': '123456', 'perfil': 'Admin'},
    {'id': 2, 'nome': 'Bruno Silva',  'email': 'bruno@email.com',  'senha': '123456', 'perfil': 'Colecionador'},
    {'id': 3, 'nome': 'Carla Nunes',  'email': 'carla@email.com',  'senha': '123456', 'perfil': 'Colecionador'},
    {'id': 4, 'nome': 'Diego Torres', 'email': 'diego@email.com',  'senha': '123456', 'perfil': 'Moderador'},
    {'id': 5, 'nome': 'Elisa Rocha',  'email': 'elisa@email.com',  'senha': '123456', 'perfil': 'Colecionador'},
]

jogos = [
    {'id': 1, 'titulo': 'The Legend of Zelda: BotW', 'genero': 'Aventura',     'ano': 2017, 'plataforma': 'Nintendo Switch', 'nota': 10},
    {'id': 2, 'titulo': 'God of War',                'genero': 'Acao',         'ano': 2018, 'plataforma': 'PlayStation 4',   'nota': 10},
    {'id': 3, 'titulo': 'Halo Infinite',             'genero': 'FPS',          'ano': 2021, 'plataforma': 'Xbox Series X',   'nota': 8},
    {'id': 4, 'titulo': 'Cyberpunk 2077',            'genero': 'RPG',          'ano': 2020, 'plataforma': 'PC',              'nota': 9},
    {'id': 5, 'titulo': 'Hollow Knight',             'genero': 'Metroidvania', 'ano': 2017, 'plataforma': 'PC',              'nota': 10},
    {'id': 6, 'titulo': 'Elden Ring',                'genero': 'RPG',          'ano': 2022, 'plataforma': 'PlayStation 5',   'nota': 10},
]

plataformas = [
    {'id': 1, 'nome': 'PlayStation 5',   'fabricante': 'Sony',      'ano_lancamento': 2020, 'tipo': 'Console',    'jogos_disponiveis': 500},
    {'id': 2, 'nome': 'Nintendo Switch', 'fabricante': 'Nintendo',  'ano_lancamento': 2017, 'tipo': 'Hibrido',    'jogos_disponiveis': 4000},
    {'id': 3, 'nome': 'Xbox Series X',   'fabricante': 'Microsoft', 'ano_lancamento': 2020, 'tipo': 'Console',    'jogos_disponiveis': 600},
    {'id': 4, 'nome': 'PC',              'fabricante': 'Varios',    'ano_lancamento': 1970, 'tipo': 'Computador', 'jogos_disponiveis': 50000},
    {'id': 5, 'nome': 'PlayStation 4',   'fabricante': 'Sony',      'ano_lancamento': 2013, 'tipo': 'Console',    'jogos_disponiveis': 4000},
]

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def proximo_id(lista):
    return max((item['id'] for item in lista), default=0) + 1

def login_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Voce precisa estar logado para acessar esta pagina.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def usuario_logado():
    uid = session.get('usuario_id')
    if uid is None:
        return None
    return next((u for u in usuarios if u['id'] == uid), None)

@app.context_processor
def contexto_global():
    return {'usuario_atual': usuario_logado()}

# ─────────────────────────────────────────────
# ROTAS PUBLICAS
# ─────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_id' in session:
        return redirect(url_for('listar_usuarios'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        if not email or not senha:
            flash('Preencha e-mail e senha.', 'danger')
            return render_template('login.html')
        usuario = next((u for u in usuarios if u['email'] == email and u['senha'] == senha), None)
        if usuario is None:
            flash('E-mail ou senha incorretos.', 'danger')
            return render_template('login.html')
        session['usuario_id']   = usuario['id']
        session['usuario_nome'] = usuario['nome']
        flash(f'Bem-vindo, {usuario["nome"]}!', 'success')
        return redirect(url_for('listar_usuarios'))
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome      = request.form.get('nome', '').strip()
        email     = request.form.get('email', '').strip()
        senha     = request.form.get('senha', '').strip()
        confirmar = request.form.get('confirmar', '').strip()
        if not nome or not email or not senha or not confirmar:
            flash('Todos os campos sao obrigatorios.', 'danger')
            return render_template('cadastro.html')
        if senha != confirmar:
            flash('As senhas nao coincidem.', 'danger')
            return render_template('cadastro.html')
        if any(u['email'] == email for u in usuarios):
            flash('Este e-mail ja esta cadastrado.', 'danger')
            return render_template('cadastro.html')
        usuarios.append({'id': proximo_id(usuarios), 'nome': nome, 'email': email, 'senha': senha, 'perfil': 'Colecionador'})
        flash('Cadastro realizado com sucesso! Faca login.', 'success')
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Voce saiu do sistema.', 'info')
    return redirect(url_for('login'))

# ─────────────────────────────────────────────
# USUARIOS
# ─────────────────────────────────────────────

@app.route('/usuarios/listar')
@login_obrigatorio
def listar_usuarios():
    return render_template('usuarios/listar_usuarios.html', usuarios=usuarios)

@app.route('/usuarios/inserir', methods=['GET', 'POST'])
@login_obrigatorio
def inserir_usuario():
    if request.method == 'POST':
        nome   = request.form.get('nome', '').strip()
        email  = request.form.get('email', '').strip()
        perfil = request.form.get('perfil', '').strip()
        senha  = request.form.get('senha', '').strip()
        if not nome or not email or not perfil or not senha:
            flash('Todos os campos sao obrigatorios.', 'danger')
            return render_template('usuarios/inserir_usuario.html')
        if any(u['email'] == email for u in usuarios):
            flash('Este e-mail ja esta cadastrado.', 'danger')
            return render_template('usuarios/inserir_usuario.html')
        usuarios.append({'id': proximo_id(usuarios), 'nome': nome, 'email': email, 'senha': senha, 'perfil': perfil})
        flash(f'Usuario "{nome}" cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_usuarios'))
    return render_template('usuarios/inserir_usuario.html')

@app.route('/usuarios/editar/<int:uid>', methods=['GET', 'POST'])
@login_obrigatorio
def editar_usuario(uid):
    usuario = next((u for u in usuarios if u['id'] == uid), None)
    if usuario is None:
        flash('Usuario nao encontrado.', 'danger')
        return redirect(url_for('listar_usuarios'))
    if request.method == 'POST':
        nome   = request.form.get('nome', '').strip()
        email  = request.form.get('email', '').strip()
        perfil = request.form.get('perfil', '').strip()
        if not nome or not email or not perfil:
            flash('Todos os campos sao obrigatorios.', 'danger')
            return render_template('usuarios/editar_usuario.html', usuario=usuario)
        if any(u['email'] == email and u['id'] != uid for u in usuarios):
            flash('Este e-mail ja esta em uso.', 'danger')
            return render_template('usuarios/editar_usuario.html', usuario=usuario)
        usuario['nome']   = nome
        usuario['email']  = email
        usuario['perfil'] = perfil
        flash(f'Usuario "{nome}" atualizado!', 'success')
        return redirect(url_for('listar_usuarios'))
    return render_template('usuarios/editar_usuario.html', usuario=usuario)

@app.route('/usuarios/excluir/<int:uid>', methods=['POST'])
@login_obrigatorio
def excluir_usuario(uid):
    global usuarios
    if session.get('usuario_id') == uid:
        flash('Voce nao pode excluir seu proprio usuario.', 'danger')
        return redirect(url_for('listar_usuarios'))
    usuarios = [u for u in usuarios if u['id'] != uid]
    flash('Usuario excluido com sucesso.', 'success')
    return redirect(url_for('listar_usuarios'))

# ─────────────────────────────────────────────
# JOGOS
# ─────────────────────────────────────────────

@app.route('/jogos/listar')
@login_obrigatorio
def listar_jogos():
    return render_template('jogos/listar_jogos.html', jogos=jogos)

@app.route('/jogos/inserir', methods=['GET', 'POST'])
@login_obrigatorio
def inserir_jogo():
    if request.method == 'POST':
        titulo     = request.form.get('titulo', '').strip()
        genero     = request.form.get('genero', '').strip()
        ano        = request.form.get('ano', '').strip()
        plataforma = request.form.get('plataforma', '').strip()
        nota       = request.form.get('nota', '').strip()
        if not titulo or not genero or not ano or not plataforma or not nota:
            flash('Todos os campos sao obrigatorios.', 'danger')
            return render_template('jogos/inserir_jogo.html', plataformas=plataformas)
        jogos.append({'id': proximo_id(jogos), 'titulo': titulo, 'genero': genero,
                      'ano': int(ano), 'plataforma': plataforma, 'nota': int(nota)})
        flash(f'Jogo "{titulo}" adicionado a colecao!', 'success')
        return redirect(url_for('listar_jogos'))
    return render_template('jogos/inserir_jogo.html', plataformas=plataformas)

@app.route('/jogos/editar/<int:jid>', methods=['GET', 'POST'])
@login_obrigatorio
def editar_jogo(jid):
    jogo = next((j for j in jogos if j['id'] == jid), None)
    if jogo is None:
        flash('Jogo nao encontrado.', 'danger')
        return redirect(url_for('listar_jogos'))
    if request.method == 'POST':
        titulo     = request.form.get('titulo', '').strip()
        genero     = request.form.get('genero', '').strip()
        ano        = request.form.get('ano', '').strip()
        plataforma = request.form.get('plataforma', '').strip()
        nota       = request.form.get('nota', '').strip()
        if not titulo or not genero or not ano or not plataforma or not nota:
            flash('Todos os campos sao obrigatorios.', 'danger')
            return render_template('jogos/editar_jogo.html', jogo=jogo, plataformas=plataformas)
        jogo['titulo'] = titulo; jogo['genero'] = genero
        jogo['ano'] = int(ano); jogo['plataforma'] = plataforma; jogo['nota'] = int(nota)
        flash(f'Jogo "{titulo}" atualizado!', 'success')
        return redirect(url_for('listar_jogos'))
    return render_template('jogos/editar_jogo.html', jogo=jogo, plataformas=plataformas)

@app.route('/jogos/excluir/<int:jid>', methods=['POST'])
@login_obrigatorio
def excluir_jogo(jid):
    global jogos
    jogos = [j for j in jogos if j['id'] != jid]
    flash('Jogo removido da colecao.', 'success')
    return redirect(url_for('listar_jogos'))

# ─────────────────────────────────────────────
# PLATAFORMAS
# ─────────────────────────────────────────────

@app.route('/plataformas/listar')
@login_obrigatorio
def listar_plataformas():
    return render_template('plataformas/listar_plataformas.html', plataformas=plataformas)

@app.route('/plataformas/inserir', methods=['GET', 'POST'])
@login_obrigatorio
def inserir_plataforma():
    if request.method == 'POST':
        nome           = request.form.get('nome', '').strip()
        fabricante     = request.form.get('fabricante', '').strip()
        ano_lancamento = request.form.get('ano_lancamento', '').strip()
        tipo           = request.form.get('tipo', '').strip()
        jogos_disp     = request.form.get('jogos_disponiveis', '0').strip()
        if not nome or not fabricante or not ano_lancamento or not tipo:
            flash('Todos os campos sao obrigatorios.', 'danger')
            return render_template('plataformas/inserir_plataforma.html')
        plataformas.append({'id': proximo_id(plataformas), 'nome': nome, 'fabricante': fabricante,
                            'ano_lancamento': int(ano_lancamento), 'tipo': tipo,
                            'jogos_disponiveis': int(jogos_disp) if jogos_disp.isdigit() else 0})
        flash(f'Plataforma "{nome}" cadastrada com sucesso!', 'success')
        return redirect(url_for('listar_plataformas'))
    return render_template('plataformas/inserir_plataforma.html')

@app.route('/plataformas/editar/<int:pid>', methods=['GET', 'POST'])
@login_obrigatorio
def editar_plataforma(pid):
    plataforma = next((p for p in plataformas if p['id'] == pid), None)
    if plataforma is None:
        flash('Plataforma nao encontrada.', 'danger')
        return redirect(url_for('listar_plataformas'))
    if request.method == 'POST':
        nome           = request.form.get('nome', '').strip()
        fabricante     = request.form.get('fabricante', '').strip()
        ano_lancamento = request.form.get('ano_lancamento', '').strip()
        tipo           = request.form.get('tipo', '').strip()
        jogos_disp     = request.form.get('jogos_disponiveis', '0').strip()
        if not nome or not fabricante or not ano_lancamento or not tipo:
            flash('Todos os campos sao obrigatorios.', 'danger')
            return render_template('plataformas/editar_plataforma.html', plataforma=plataforma)
        plataforma['nome'] = nome; plataforma['fabricante'] = fabricante
        plataforma['ano_lancamento'] = int(ano_lancamento); plataforma['tipo'] = tipo
        plataforma['jogos_disponiveis'] = int(jogos_disp) if jogos_disp.isdigit() else 0
        flash(f'Plataforma "{nome}" atualizada!', 'success')
        return redirect(url_for('listar_plataformas'))
    return render_template('plataformas/editar_plataforma.html', plataforma=plataforma)

@app.route('/plataformas/excluir/<int:pid>', methods=['POST'])
@login_obrigatorio
def excluir_plataforma(pid):
    global plataformas
    plataformas = [p for p in plataformas if p['id'] != pid]
    flash('Plataforma excluida com sucesso.', 'success')
    return redirect(url_for('listar_plataformas'))

# ─────────────────────────────────────────────
# EQUIPE
# ─────────────────────────────────────────────

@app.route('/equipe')
def equipe():
    return render_template('sobre_equipe.html')

if __name__ == '__main__':
    app.run(debug=True)
