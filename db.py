# db.py — Módulo central de acesso ao banco de dados.
# Qualquer arquivo que precise do banco importa apenas este módulo.
# Padrão seguido do projeto CasaGestor (pi-01-26).

import mysql.connector
from mysql.connector import Error, pooling
import os

# Dicionário com todos os parâmetros de conexão com o banco de dados.
# Centralizamos aqui para que qualquer mudança (ex: senha) seja feita em um único lugar.
_DB_PARAMS = {
    # Endereço do servidor MySQL. 'localhost' significa que está na própria máquina.
    'host':               'localhost',

    # Usuário do MySQL criado durante a instalação.
    'user':               'root',

    # Senha do usuário root. Deixe vazio ('') se não definiu senha na instalação.
    'password':           '',

    # Nome do banco de dados que será usado pela aplicação.
    'database':           'gamestore',

    # Codificação de caracteres. Necessária para acentos funcionarem corretamente.
    'charset':            'utf8mb4',

    # Conjunto de regras do MySQL para validação de dados.
    'sql_mode':           (
        'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,'
        'ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'
    ),

    # use_pure=True usa a implementação em Python puro, compatível com todos os ambientes.
    'use_pure':           True,

    # Tempo máximo em segundos para tentar se conectar antes de desistir.
    'connection_timeout': 10,

    # autocommit=False significa que alterações no banco (INSERT, UPDATE, DELETE)
    # só são confirmadas quando o código chamar commit() explicitamente.
    'autocommit':         False,
}

# Variável que vai guardar o pool de conexões.
# Começa como None e é preenchida na primeira chamada de criar_pool().
_pool = None


def criar_pool():
    # 'global' permite que esta função modifique a variável _pool
    # que foi definida fora dela (no escopo do módulo).
    global _pool

    # Só cria o pool se ele ainda não existir.
    # Isso garante que apenas um pool seja criado durante toda a execução da aplicação.
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            # Nome interno do pool, usado para identificação.
            pool_name='webapp_pool',

            # Número de conexões abertas permanentemente.
            pool_size=5,

            # Limpa o estado da sessão ao devolver a conexão ao pool.
            pool_reset_session=True,

            # O ** "desempacota" o dicionário _DB_PARAMS,
            # passando cada chave como um argumento separado para a função.
            **_DB_PARAMS
        )


def get_connection():
    """Retorna uma conexão do pool. Levanta Exception em caso de falha."""
    try:
        # Garante que o pool foi criado antes de tentar pegar uma conexão.
        if _pool is None:
            criar_pool()

        # Pega uma conexão disponível do pool e a retorna para o chamador.
        return _pool.get_connection()

    except Error as e:
        raise Exception(f'Não foi possível obter conexão do pool: {e}')


def execute_query(sql, params=None, fetch=False):
    """
    Executa qualquer comando SQL de forma segura.

    Como usar:
        sql    -> string SQL com %s como marcadores de posição para os valores.
        params -> tupla com os valores que substituirão os %s no SQL.
        fetch  -> True para SELECT (retorna lista); False para INSERT/UPDATE/DELETE.

    Retorna:
        fetch=True  -> lista de dicionários, onde cada item é uma linha do resultado.
        fetch=False -> número inteiro com a quantidade de linhas afetadas.
    """
    # Pega uma conexão disponível do pool.
    conn = get_connection()

    try:
        # dictionary=True faz cada linha retornar como dicionário.
        # Assim acessamos jogo['titulo'] em vez de jogo[0], muito mais legível.
        cursor = conn.cursor(dictionary=True)

        # Executa o SQL passando os parâmetros separados da string SQL.
        # Isso evita SQL Injection: o MySQL trata os valores como dados,
        # nunca como parte do comando SQL.
        cursor.execute(sql, params or ())

        if fetch:
            # Para SELECT: retorna todas as linhas como uma lista de dicionários.
            return cursor.fetchall()
        else:
            # Para INSERT/UPDATE/DELETE: confirma a alteração no banco de dados.
            conn.commit()
            # Retorna quantas linhas foram afetadas pelo comando.
            return cursor.rowcount

    except Error as e:
        # Em caso de erro, desfaz qualquer alteração parcial.
        conn.rollback()
        raise Exception(f'Erro ao executar query: {e}')

    finally:
        # O bloco 'finally' sempre é executado, mesmo que ocorra um erro.
        cursor.close()
        # conn.close() não encerra a conexão fisicamente.
        # Ele apenas a devolve ao pool para ser reutilizada pela próxima requisição.
        conn.close()


def execute_one(sql, params=None):
    """
    Executa um SELECT e retorna apenas a primeira linha encontrada (ou None).
    Útil para buscar um único registro, como: SELECT * FROM jogos WHERE id_jogo = 5.
    """
    # Reutiliza execute_query com fetch=True para obter a lista de resultados.
    resultados = execute_query(sql, params, fetch=True)

    # Se encontrou resultados, retorna apenas o primeiro item da lista.
    # Se não encontrou nada, retorna None.
    return resultados[0] if resultados else None


def iniciar_bd():
    """
    Lê o arquivo schema.sql e executa cada comando para criar
    o banco de dados e as tabelas caso ainda não existam.
    Esta função é chamada uma vez ao iniciar a aplicação.
    """
    try:
        # Conecta ao MySQL SEM especificar o banco de dados.
        # Fazemos isso porque o banco 'gamestore' pode ainda não existir,
        # e o CREATE DATABASE no schema.sql vai criá-lo.
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password=''
        )
        cursor = conn.cursor()

        # Monta o caminho completo até o arquivo schema.sql.
        # os.path.dirname(__file__) retorna a pasta onde o db.py está salvo.
        arquivo_sql = os.path.join(os.path.dirname(__file__), 'schema.sql')

        # Abre e lê todo o conteúdo do schema.sql como texto.
        with open(arquivo_sql, 'r', encoding='utf-8') as f:
            script_sql = f.read()

        # Divide o script inteiro em comandos individuais usando o ';' como separador.
        # O mysql.connector não consegue executar múltiplos comandos de uma vez,
        # então precisamos executar um por um.
        for stmt in script_sql.split(';'):
            # Remove espaços e quebras de linha desnecessários.
            stmt = stmt.strip()
            # Ignora partes vazias que surgem após o último ';'.
            if stmt:
                cursor.execute(stmt)

        # Confirma todas as operações executadas.
        conn.commit()
        cursor.close()
        conn.close()
        print('Banco e tabelas inicializados com sucesso!')

    except Exception as e:
        print(f'Erro ao inicializar o banco de dados: {e}')