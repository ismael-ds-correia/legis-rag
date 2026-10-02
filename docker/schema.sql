-- 1. Tabela de Proposições
CREATE TABLE proposicoes (
    id BIGINT PRIMARY KEY,                  -- Identificador único da API
    sigla_tipo VARCHAR(10) NOT NULL,        -- Ex: PL, PEC, PLP
    cod_tipo INTEGER,                       -- Código interno do tipo
    numero INTEGER NOT NULL,                -- Número da proposição
    ano INTEGER NOT NULL,                   -- Ano de apresentação
    ementa TEXT,                            -- Texto da ementa oficial
    data_apresentacao TIMESTAMP,            -- Data e hora da apresentação
    temas TEXT[]                            -- Atributo multivalorado (Array de temas)
);

-- 2. Tabela de Autores
CREATE TABLE autores (
    id BIGINT PRIMARY KEY,                  -- ID do autor fornecido pela API
    nome_civil VARCHAR(255) NOT NULL,       -- Nome completo do autor
    sigla_partido VARCHAR(20),              -- Sigla do partido
    sigla_uf CHAR(2),                       -- UF do autor
    redes_sociais TEXT[]                    -- Atributo multivalorado
);

-- 3. Tabela Associativa (Proposição <-> Autor)
CREATE TABLE proposicao_autores (
    proposicao_id BIGINT REFERENCES proposicoes(id) ON DELETE CASCADE,
    autor_id BIGINT REFERENCES autores(id) ON DELETE CASCADE,
    PRIMARY KEY (proposicao_id, autor_id)
);

-- 4. Índices para Otimização de Consultas e Buscas no RAG
CREATE INDEX idx_proposicoes_ano ON proposicoes(ano);
CREATE INDEX idx_proposicoes_sigla ON proposicoes(sigla_tipo);
CREATE INDEX idx_autores_partido ON autores(sigla_partido);
CREATE INDEX idx_autores_uf ON autores(sigla_uf);