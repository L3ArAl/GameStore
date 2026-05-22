# 🎮 GameStore

O GameStore é um sistema web desenvolvido com Flask que permite o gerenciamento de coleções de jogos digitais de forma simples, organizada e interativa.

## 📌 Objetivo

O objetivo do sistema é centralizar informações sobre jogos, plataformas e usuários, facilitando o controle e a visualização de uma coleção pessoal de jogos.

## 🚀 Funcionalidades

* Cadastro e login de usuários
* Gerenciamento de jogos (cadastrar, editar e excluir)
* Gerenciamento de plataformas
* Controle de usuários
* Associação de jogos a plataformas
* Sistema de autenticação com sessão
* Interface moderna com tema gamer

## 🛠️ Tecnologias utilizadas

* Python
* Flask
* HTML5
* CSS3
* Bootstrap
* Jinja2

## ▶️ Como executar o projeto

1. Clone o repositório:

```
git clone https://github.com/seu-usuario/GameStore.git
```

2. Acesse a pasta do projeto:

```
cd GameStore
```

3. Crie e ative um ambiente virtual:

```
python -m venv venv
venv\Scripts\activate
```

4. Instale as dependências:

```
pip install -r requirements.txt
```

5. Execute o projeto:

```
python app.py
```

6. Acesse no navegador:

```
http://127.0.0.1:5000
```

## 👥 Equipe

* Leandro — Desenvolvedor
* Heitor — Desenvolvedor

## 📚 Observações

Este projeto foi desenvolvido para fins acadêmicos, utilizando listas Python como armazenamento de dados, sem integração com banco de dados.

## 📄 Licença

Projeto de uso educacional.

#select* .funcoes
if
	nome = request.form.get('nome', '').strip()
	status = request.form.get('status', 'Ativo')
	descricao = request.for.get('descricao', '').strip()
	gerenciar-funcoes = 1 if request.form.get('gerenciar_funcoes') else 0
	gerenciar_usuarios = 1 if request.form.get('gerenciar_usuarios') else 0
	gerenciar_tarefas = 1 if request.form.get('gerenciar_tarefas') else 0

	if not nome:
		flash('O campo <b>NOME</b> é obrigatorio', 'danger')
		return redirect(url_for('funcoes_cadastrar')) 
