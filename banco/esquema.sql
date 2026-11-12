-- Banco SQLite do TomeOferta, separado do banco interno do n8n.
-- Esquema inicial para bancos novos; futuras alterações exigem migracoes.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY,
    nome_canonico TEXT NOT NULL,
    marca TEXT,
    modelo TEXT,
    gtin TEXT,
    variante_json TEXT NOT NULL DEFAULT '{}',
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS anuncios (
    id INTEGER PRIMARY KEY,
    produto_id INTEGER REFERENCES produtos(id),
    marketplace TEXT NOT NULL,
    id_produto_externo TEXT,
    id_anuncio_externo TEXT NOT NULL,
    titulo TEXT NOT NULL,
    url_produto TEXT,
    url_anuncio TEXT,
    id_vendedor TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(marketplace, id_anuncio_externo)
);

CREATE TABLE IF NOT EXISTS observacoes_preco (
    id INTEGER PRIMARY KEY,
    anuncio_id INTEGER NOT NULL REFERENCES anuncios(id),
    observado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    moeda TEXT NOT NULL DEFAULT 'BRL',
    preco_centavos INTEGER NOT NULL CHECK(preco_centavos >= 0),
    preco_original_centavos INTEGER CHECK(preco_original_centavos >= 0),
    frete_centavos INTEGER CHECK(frete_centavos >= 0),
    condicoes_json TEXT NOT NULL DEFAULT '{}',
    origem TEXT NOT NULL,
    id_observacao_origem TEXT UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_observacoes_anuncio_data ON observacoes_preco(anuncio_id, observado_em);

CREATE TABLE IF NOT EXISTS cupons (
    id INTEGER PRIMARY KEY,
    marketplace TEXT NOT NULL,
    codigo TEXT,
    regras_json TEXT NOT NULL DEFAULT '{}',
    valido_de TEXT,
    valido_ate TEXT,
    situacao_validacao TEXT NOT NULL DEFAULT 'nao_verificado'
        CHECK(situacao_validacao IN ('nao_verificado', 'verificado', 'invalido', 'expirado')),
    verificado_em TEXT
);

CREATE TABLE IF NOT EXISTS ofertas_candidatas (
    id INTEGER PRIMARY KEY,
    anuncio_id INTEGER NOT NULL REFERENCES anuncios(id),
    observacao_id INTEGER NOT NULL REFERENCES observacoes_preco(id),
    pontuacao REAL,
    justificativas_json TEXT NOT NULL DEFAULT '[]',
    situacao_revisao TEXT NOT NULL DEFAULT 'pendente'
        CHECK(situacao_revisao IN ('pendente', 'aprovada', 'rejeitada')),
    url_afiliado TEXT,
    afiliado_verificado_em TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revisado_em TEXT
);

CREATE TABLE IF NOT EXISTS publicacoes (
    id INTEGER PRIMARY KEY,
    oferta_candidata_id INTEGER NOT NULL REFERENCES ofertas_candidatas(id),
    numero_operador TEXT NOT NULL,
    texto_mensagem TEXT NOT NULL,
    id_mensagem_meta TEXT,
    situacao TEXT NOT NULL DEFAULT 'rascunho'
        CHECK(situacao IN ('rascunho', 'aprovada', 'submetida', 'enviada', 'entregue', 'lida', 'falha')),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    submetido_em TEXT
);
