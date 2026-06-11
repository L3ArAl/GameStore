from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import execute_one, execute_query, iniciar_bd

app = Flask(__name__)
app.secret_key = 'gamestore_secret_key_2026'

# Inicializa o banco de dados e cria as tabelas ao iniciar a aplicação.
iniciar_bd()


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def login_obrigatorio(f):
    """Bloqueia o acesso às rotas internas quando não há usuário logado."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.context_processor
def contexto_global():
    """Disponibiliza o usuário logado em todos os templates."""
    uid = session.get('usuario_id')
    if uid is None:
        return {'usuario_atual': None}
    usuario = execute_one('SELECT * FROM usuarios WHERE id_usuario = %s', (uid,))
    return {'usuario_atual': usuario}


# ─────────────────────────────────────────────
# ROTAS PÚBLICAS
# ─────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
@login_obrigatorio
def home():

    total_usuarios = execute_one(
        'SELECT COUNT(*) AS total FROM usuarios'
    )

    total_jogos = execute_one(
        'SELECT COUNT(*) AS total FROM jogos'
    )

    total_plataformas = execute_one(
        'SELECT COUNT(*) AS total FROM plataformas'
    )

    total_funcoes = execute_one(
        'SELECT COUNT(*) AS total FROM funcoes'
    )

    return render_template(
        'home.html',
        total_usuarios=total_usuarios['total'],
        total_jogos=total_jogos['total'],
        total_plataformas=total_plataformas['total'],
        total_funcoes=total_funcoes['total']
    )

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

        # Busca o usuário pelo e-mail no banco de dados.
        usuario = execute_one(
            'SELECT * FROM usuarios WHERE email = %s',
            (email,)
        )

        # Verifica se o usuário existe e se a senha está correta.
        # A senha no banco está em texto puro nesta versão inicial.
        # (Para adicionar hash, use werkzeug.security como no projeto CasaGestor.)
        if usuario is None or usuario['senha'] != senha:
            flash('E-mail ou senha incorretos.', 'danger')
            return render_template('login.html')

        session['usuario_id']   = usuario['id_usuario']
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
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('cadastro.html')

        if senha != confirmar:
            flash('As senhas não coincidem.', 'danger')
            return render_template('cadastro.html')

        # Verifica se o e-mail já está cadastrado no banco.
        existente = execute_one(
            'SELECT id_usuario FROM usuarios WHERE email = %s',
            (email,)
        )
        if existente:
            flash('Este e-mail já está cadastrado.', 'danger')
            return render_template('cadastro.html')

        try:
            execute_query(
                'INSERT INTO usuarios (nome, email, senha, perfil) VALUES (%s, %s, %s, %s)',
                (nome, email, senha, 'Colecionador')
            )
            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Erro ao cadastrar: {e}', 'danger')
            return render_template('cadastro.html')

    return render_template('cadastro.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))


# ─────────────────────────────────────────────
# USUÁRIOS
# ─────────────────────────────────────────────

@app.route('/usuarios/listar')
@login_obrigatorio
def listar_usuarios():
    # Busca todos os usuários do banco, ordenados pelo ID decrescente.
    lista = execute_query(
        'SELECT * FROM usuarios ORDER BY id_usuario DESC',
        fetch=True
    )
    # Os templates existentes esperam a lista como 'usuarios'
    # e cada item com 'id', então mapeamos id_usuario -> id.
    usuarios = [
        {**u, 'id': u['id_usuario']}
        for u in lista
    ]
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
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('usuarios/inserir_usuario.html')

        # Verifica se o e-mail já existe no banco.
        existente = execute_one(
            'SELECT id_usuario FROM usuarios WHERE email = %s',
            (email,)
        )
        if existente:
            flash('Este e-mail já está cadastrado.', 'danger')
            return render_template('usuarios/inserir_usuario.html')

        try:
            execute_query(
                'INSERT INTO usuarios (nome, email, senha, perfil) VALUES (%s, %s, %s, %s)',
                (nome, email, senha, perfil)
            )
            flash(f'Usuário "{nome}" cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_usuarios'))
        except Exception as e:
            flash(f'Erro ao cadastrar usuário: {e}', 'danger')
            return render_template('usuarios/inserir_usuario.html')

    return render_template('usuarios/inserir_usuario.html')


@app.route('/usuarios/editar/<int:uid>', methods=['GET', 'POST'])
@login_obrigatorio
def editar_usuario(uid):
    # Busca o usuário pelo ID no banco.
    usuario = execute_one(
        'SELECT * FROM usuarios WHERE id_usuario = %s',
        (uid,)
    )
    if usuario is None:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('home'))

    # O template espera o campo 'id', então adicionamos ao dicionário.
    usuario = {**usuario, 'id': usuario['id_usuario']}

    if request.method == 'POST':
        nome   = request.form.get('nome', '').strip()
        email  = request.form.get('email', '').strip()
        perfil = request.form.get('perfil', '').strip()

        if not nome or not email or not perfil:
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('usuarios/editar_usuario.html', usuario=usuario)

        # Verifica se o e-mail já pertence a OUTRO usuário.
        existente = execute_one(
            'SELECT id_usuario FROM usuarios WHERE email = %s AND id_usuario <> %s',
            (email, uid)
        )
        if existente:
            flash('Este e-mail já está em uso.', 'danger')
            return render_template('usuarios/editar_usuario.html', usuario=usuario)

        try:
            execute_query(
                'UPDATE usuarios SET nome=%s, email=%s, perfil=%s WHERE id_usuario=%s',
                (nome, email, perfil, uid)
            )
            flash(f'Usuário "{nome}" atualizado!', 'success')
            return redirect(url_for('listar_usuarios'))
        except Exception as e:
            flash(f'Erro ao atualizar usuário: {e}', 'danger')
            return render_template('usuarios/editar_usuario.html', usuario=usuario)

    return render_template('usuarios/editar_usuario.html', usuario=usuario)


@app.route('/usuarios/excluir/<int:uid>', methods=['POST'])
@login_obrigatorio
def excluir_usuario(uid):
    # Impede que o usuário logado exclua a si mesmo.
    if session.get('usuario_id') == uid:
        flash('Você não pode excluir seu próprio usuário.', 'danger')
        return redirect(url_for('listar_usuarios'))

    try:
        execute_query('DELETE FROM usuarios WHERE id_usuario = %s', (uid,))
        flash('Usuário excluído com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir usuário: {e}', 'danger')
    return redirect(url_for('listar_usuarios'))


# ─────────────────────────────────────────────
# JOGOS
# ─────────────────────────────────────────────

@app.route('/jogos/listar')
@login_obrigatorio
def listar_jogos():
    # Busca todos os jogos do banco, ordenados pelo ID decrescente.
    lista = execute_query(
        'SELECT * FROM jogos ORDER BY id_jogo DESC',
        fetch=True
    )
    # O template espera o campo 'id'.
    jogos = [
        {**j, 'id': j['id_jogo']}
        for j in lista
    ]
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
            flash('Todos os campos são obrigatórios.', 'danger')
            plataformas = execute_query('SELECT * FROM plataformas ORDER BY nome', fetch=True)
            return render_template('jogos/inserir_jogo.html', plataformas=plataformas)

        try:
            execute_query(
                'INSERT INTO jogos (titulo, genero, ano, plataforma, nota) VALUES (%s, %s, %s, %s, %s)',
                (titulo, genero, int(ano), plataforma, int(nota))
            )
            flash(f'Jogo "{titulo}" adicionado à coleção!', 'success')
            return redirect(url_for('listar_jogos'))
        except Exception as e:
            flash(f'Erro ao inserir jogo: {e}', 'danger')

    # GET: busca plataformas do banco para preencher o select.
    plataformas = execute_query('SELECT * FROM plataformas ORDER BY nome', fetch=True)
    return render_template('jogos/inserir_jogo.html', plataformas=plataformas)


@app.route('/jogos/editar/<int:jid>', methods=['GET', 'POST'])
@login_obrigatorio
def editar_jogo(jid):
    # Busca o jogo pelo ID no banco.
    jogo = execute_one('SELECT * FROM jogos WHERE id_jogo = %s', (jid,))
    if jogo is None:
        flash('Jogo não encontrado.', 'danger')
        return redirect(url_for('listar_jogos'))

    # O template espera o campo 'id'.
    jogo = {**jogo, 'id': jogo['id_jogo']}

    if request.method == 'POST':
        titulo     = request.form.get('titulo', '').strip()
        genero     = request.form.get('genero', '').strip()
        ano        = request.form.get('ano', '').strip()
        plataforma = request.form.get('plataforma', '').strip()
        nota       = request.form.get('nota', '').strip()

        if not titulo or not genero or not ano or not plataforma or not nota:
            flash('Todos os campos são obrigatórios.', 'danger')
            plataformas = execute_query('SELECT * FROM plataformas ORDER BY nome', fetch=True)
            return render_template('jogos/editar_jogo.html', jogo=jogo, plataformas=plataformas)

        try:
            execute_query(
                'UPDATE jogos SET titulo=%s, genero=%s, ano=%s, plataforma=%s, nota=%s WHERE id_jogo=%s',
                (titulo, genero, int(ano), plataforma, int(nota), jid)
            )
            flash(f'Jogo "{titulo}" atualizado!', 'success')
            return redirect(url_for('listar_jogos'))
        except Exception as e:
            flash(f'Erro ao atualizar jogo: {e}', 'danger')

    plataformas = execute_query('SELECT * FROM plataformas ORDER BY nome', fetch=True)
    return render_template('jogos/editar_jogo.html', jogo=jogo, plataformas=plataformas)


@app.route('/jogos/excluir/<int:jid>', methods=['POST'])
@login_obrigatorio
def excluir_jogo(jid):
    try:
        execute_query('DELETE FROM jogos WHERE id_jogo = %s', (jid,))
        flash('Jogo removido da coleção.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir jogo: {e}', 'danger')
    return redirect(url_for('listar_jogos'))


# ─────────────────────────────────────────────
# PLATAFORMAS
# ─────────────────────────────────────────────

@app.route('/funcoes/listar')
@login_obrigatorio
def listar_funcoes():

    lista = execute_query(
        'SELECT * FROM funcoes ORDER BY id_funcao DESC',
        fetch=True
    )

    funcoes = [
        {**f, 'id': f['id_funcao']}
        for f in lista
    ]

    return render_template(
        'funcoes/listar_funcoes.html',
        funcoes=funcoes
    )

@app.route('/funcoes/inserir', methods=['GET', 'POST'])
@login_obrigatorio
def inserir_funcao():

    if request.method == 'POST':

        nome = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()

        status = 'Ativo' if request.form.get('status') else 'Inativo'

        gerenciar_usuarios = 1 if request.form.get('gerenciar_usuarios') else 0
        gerenciar_funcoes = 1 if request.form.get('gerenciar_funcoes') else 0
        gerenciar_jogos = 1 if request.form.get('gerenciar_jogos') else 0
        gerenciar_plataformas = 1 if request.form.get('gerenciar_plataformas') else 0

        execute_query(
            '''
            INSERT INTO funcoes
            (
                nome,
                status,
                descricao,
                gerenciar_usuarios,
                gerenciar_funcoes,
                gerenciar_jogos,
                gerenciar_plataformas
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ''',
            (
                nome,
                status,
                descricao,
                gerenciar_usuarios,
                gerenciar_funcoes,
                gerenciar_jogos,
                gerenciar_plataformas
            )
        )

        flash('Função cadastrada com sucesso.', 'success')
        return redirect(url_for('listar_funcoes'))

    return render_template('funcoes/inserir_funcao.html')

@app.route('/funcoes/editar/<int:fid>', methods=['GET', 'POST'])
@login_obrigatorio
def editar_funcao(fid):

    funcao = execute_one(
        'SELECT * FROM funcoes WHERE id_funcao = %s',
        (fid,)
    )

    if funcao is None:
        flash('Função não encontrada.', 'danger')
        return redirect(url_for('listar_funcoes'))

    funcao = {**funcao, 'id': funcao['id_funcao']}

    if request.method == 'POST':

        nome = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()

        status = 'Ativo' if request.form.get('status') else 'Inativo'

        gerenciar_usuarios = 1 if request.form.get('gerenciar_usuarios') else 0
        gerenciar_funcoes = 1 if request.form.get('gerenciar_funcoes') else 0
        gerenciar_jogos = 1 if request.form.get('gerenciar_jogos') else 0
        gerenciar_plataformas = 1 if request.form.get('gerenciar_plataformas') else 0

        execute_query(
            '''
            UPDATE funcoes
            SET nome=%s,
                status=%s,
                descricao=%s,
                gerenciar_usuarios=%s,
                gerenciar_funcoes=%s,
                gerenciar_jogos=%s,
                gerenciar_plataformas=%s
            WHERE id_funcao=%s
            ''',
            (
                nome,
                status,
                descricao,
                gerenciar_usuarios,
                gerenciar_funcoes,
                gerenciar_jogos,
                gerenciar_plataformas,
                fid
            )
        )

        flash('Função atualizada.', 'success')
        return redirect(url_for('listar_funcoes'))

    return render_template(
        'funcoes/editar_funcao.html',
        funcao=funcao
    )


@app.route('/funcoes/excluir/<int:fid>', methods=['POST'])
@login_obrigatorio
def excluir_funcao(fid):

    execute_query(
        'DELETE FROM funcoes WHERE id_funcao = %s',
        (fid,)
    )

    flash('Função excluída.', 'success')

    return redirect(
        url_for('listar_funcoes')
    )


@app.route('/funcoes/visualizar/<int:fid>')
@login_obrigatorio
def visualizar_funcao(fid):

    funcao = execute_one(
        'SELECT * FROM funcoes WHERE id_funcao = %s',
        (fid,)
    )

    if funcao is None:
        flash('Função não encontrada.', 'danger')
        return redirect(url_for('listar_funcoes'))

    return render_template(
        'funcoes/visualizar_funcao.html',
        funcao=funcao
    )


@app.route('/plataformas/listar')
@login_obrigatorio
def listar_plataformas():
    # Busca todas as plataformas do banco, ordenadas pelo ID decrescente.
    lista = execute_query(
        'SELECT * FROM plataformas ORDER BY id_plataforma DESC',
        fetch=True
    )
    # O template espera o campo 'id'.
    plataformas = [
        {**p, 'id': p['id_plataforma']}
        for p in lista
    ]
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
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('plataformas/inserir_plataforma.html')

        try:
            execute_query(
                '''INSERT INTO plataformas (nome, fabricante, ano_lancamento, tipo, jogos_disponiveis)
                   VALUES (%s, %s, %s, %s, %s)''',
                (nome, fabricante, int(ano_lancamento), tipo,
                 int(jogos_disp) if jogos_disp.isdigit() else 0)
            )
            flash(f'Plataforma "{nome}" cadastrada com sucesso!', 'success')
            return redirect(url_for('listar_plataformas'))
        except Exception as e:
            flash(f'Erro ao inserir plataforma: {e}', 'danger')
            return render_template('plataformas/inserir_plataforma.html')

    return render_template('plataformas/inserir_plataforma.html')


@app.route('/plataformas/editar/<int:pid>', methods=['GET', 'POST'])
@login_obrigatorio
def editar_plataforma(pid):
    # Busca a plataforma pelo ID no banco.
    plataforma = execute_one(
        'SELECT * FROM plataformas WHERE id_plataforma = %s',
        (pid,)
    )
    if plataforma is None:
        flash('Plataforma não encontrada.', 'danger')
        return redirect(url_for('listar_plataformas'))

    # O template espera o campo 'id'.
    plataforma = {**plataforma, 'id': plataforma['id_plataforma']}

    if request.method == 'POST':
        nome           = request.form.get('nome', '').strip()
        fabricante     = request.form.get('fabricante', '').strip()
        ano_lancamento = request.form.get('ano_lancamento', '').strip()
        tipo           = request.form.get('tipo', '').strip()
        jogos_disp     = request.form.get('jogos_disponiveis', '0').strip()

        if not nome or not fabricante or not ano_lancamento or not tipo:
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('plataformas/editar_plataforma.html', plataforma=plataforma)

        try:
            execute_query(
                '''UPDATE plataformas SET nome=%s, fabricante=%s, ano_lancamento=%s,
                   tipo=%s, jogos_disponiveis=%s WHERE id_plataforma=%s''',
                (nome, fabricante, int(ano_lancamento), tipo,
                 int(jogos_disp) if jogos_disp.isdigit() else 0, pid)
            )
            flash(f'Plataforma "{nome}" atualizada!', 'success')
            return redirect(url_for('listar_plataformas'))
        except Exception as e:
            flash(f'Erro ao atualizar plataforma: {e}', 'danger')
            return render_template('plataformas/editar_plataforma.html', plataforma=plataforma)

    return render_template('plataformas/editar_plataforma.html', plataforma=plataforma)


@app.route('/plataformas/excluir/<int:pid>', methods=['POST'])
@login_obrigatorio
def excluir_plataforma(pid):
    try:
        execute_query('DELETE FROM plataformas WHERE id_plataforma = %s', (pid,))
        flash('Plataforma excluída com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir plataforma: {e}', 'danger')
    return redirect(url_for('listar_plataformas'))


# ─────────────────────────────────────────────
# EQUIPE
# ─────────────────────────────────────────────

@app.route('/equipe')
def equipe():
    return render_template('sobre_equipe.html')


if __name__ == '__main__':
    app.run(debug=True)