-- DROP DATABASE IF EXISTS gamestore;

-- Cria o banco de dados chamado "gamestore".
-- IF NOT EXISTS garante que o comando não vai dar erro se o banco já existir.
-- utf8mb4 é a codificação que suporta acentos e caracteres especiais do português.
CREATE DATABASE IF NOT EXISTS gamestore
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Diz ao MySQL para usar este banco de dados nas próximas instruções.
USE gamestore;

-- ─────────────────────────────────────────────
-- TABELA: plataformas
-- ─────────────────────────────────────────────

-- DROP TABLE IF EXISTS plataformas;

-- Cria a tabela de plataformas (PS5, Xbox, PC, etc.)
-- Precisa ser criada antes de jogos pois jogos terão FK para plataformas.
CREATE TABLE IF NOT EXISTS plataformas (
    id_plataforma    BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome             VARCHAR(100) NOT NULL UNIQUE,
    fabricante       VARCHAR(100) NOT NULL,
    ano_lancamento   INT          NOT NULL,
    -- Console, Computador, Híbrido, Portátil
    tipo             VARCHAR(50)  NOT NULL,
    jogos_disponiveis INT         DEFAULT 0,

    -- Campos de log: preenchidos automaticamente pelo MySQL.
    criado_em    DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em  DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────
-- FUNÇÕES
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS funcoes (
    id_funcao BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    status VARCHAR(50) DEFAULT 'Ativo',
    descricao TEXT,

    gerenciar_usuarios TINYINT(1) DEFAULT 0,
    gerenciar_funcoes TINYINT(1) DEFAULT 0,
    gerenciar_jogos TINYINT(1) DEFAULT 0,
    gerenciar_plataformas TINYINT(1) DEFAULT 0,

    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);
-- ─────────────────────────────────────────────
-- TABELA: usuarios
-- ─────────────────────────────────────────────

-- DROP TABLE IF EXISTS usuarios;

-- Cria a tabela de usuários do sistema.
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario   BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome         VARCHAR(255) NOT NULL,

    -- UNIQUE no e-mail garante que cada e-mail pertence a um único usuário.
    email        VARCHAR(255) NOT NULL UNIQUE,

    -- Senha armazenada como hash (texto embaralhado), nunca em texto puro.
    senha        VARCHAR(255) NOT NULL,

    -- Admin, Moderador, Colecionador
    perfil       VARCHAR(50)  NOT NULL DEFAULT 'Colecionador',

    -- Campos de log.
    criado_em    DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em  DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────
-- TABELA: jogos
-- ─────────────────────────────────────────────

-- DROP TABLE IF EXISTS jogos;

-- Cria a tabela de jogos da coleção.
CREATE TABLE IF NOT EXISTS jogos (
    id_jogo      BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo       VARCHAR(255) NOT NULL,
    genero       VARCHAR(50)  NOT NULL,
    ano          INT          NOT NULL,

    -- Nome da plataforma armazenado como texto (desacoplado da tabela plataformas
    -- para manter compatibilidade com os templates existentes).
    plataforma   VARCHAR(100) NOT NULL,

    -- Nota de 1 a 10.
    nota         TINYINT UNSIGNED NOT NULL DEFAULT 5,

    -- Campos de log.
    criado_em    DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em  DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

-- INSERT INTO funcoes (nome, status, descricao)
-- VALUES
-- ('Administrador', 'Ativo', 'Acesso total'),
-- ('Gerente', 'Ativo', 'Gerencia o sistema'),
-- ('Colecionador', 'Ativo', 'Usuário comum');
