# legis-rag — Assistente de Pesquisa Legislativa

Pipeline de Engenharia de Dados + RAG sobre proposições da Câmara dos Deputados, com ingestão histórica, atualização incremental e interface de consulta em Streamlit.

> **Status:** Fase 0 concluída (escopo definido). Implementação em andamento.

---

## 1. Problema

Proposições legislativas são publicadas em grande volume, em PDFs longos e com linguagem jurídica. Encontrar "o que um projeto propõe", "quais projetos tratam de um tema" ou "em que pé está uma tramitação" exige navegar por vários endpoints e documentos.

## 2. Objetivo

Construir um assistente que responda perguntas sobre proposições legislativas usando **dados estruturados** (metadados, autores, temas, tramitações, relações) e **texto dos documentos** (inteiro teor), sempre indicando as fontes (proposição e página).

## 3. Escopo

### Corpus inicial

| Item | Definição |
|---|---|
| Fonte | Dados Abertos da Câmara dos Deputados (API REST e arquivos anuais) |
| Tipos | `PL`, `PEC`, `PLP` (somente estes) |
| Período | 01/01/2025 → Data Atual |
| Atualização | Incremental e diária, a partir da ingestão histórica |

A coleta filtra exatamente pelos três tipos e pelo período acima. Não será baixado tudo o que a API retornar.

### Fora do escopo (nesta versão)

- Outros tipos de proposição (requerimentos, MPV, PDL etc.)
- Proposições anteriores a 2025
- Documentos do Senado

## 4. Decisões de arquitetura

| Componente | Escolha | Motivo |
|---|---|---|
| Orquestração | Apache Airflow | Pipeline agendado, com reprocessamento |
| Dados estruturados | PostgreSQL | Metadados, tramitações, relações, controle de execuções |
| Busca vetorial | FAISS | Biblioteca embutida, sem serviço extra rodando em Docker |
| LLM | Ollama (local) e Groq (API) | Provedor intercambiável via `LLMProvider` |
| Interface | Streamlit | Demonstração rápida e filtros |
| Containers | Docker Compose | Ambiente reprodutível |

Restrições de ambiente: máquina com 8 GB de RAM, então paralelismo baixo no Airflow e Ollama rodando fora do Compose.

```
Câmara dos Deputados (API + arquivos)
        │
        ▼
     Airflow
        │
        ├──► PostgreSQL (metadados)
        │
        └──► PDFs locais → extração → limpeza → chunks → embeddings → FAISS
                                                                        │
PostgreSQL ─────────────────────────────┬───────────────────────────────┘
                                        ▼
                                    Retriever
                                        │
                             ┌──────────┴──────────┐
                             ▼                     ▼
                          Ollama                 Groq
                             └──────────┬──────────┘
                                        ▼
                                    Streamlit
```

Regra de divisão:

- **Informação estruturada** (situação, autores, tramitação, relações) → PostgreSQL
- **Informação textual** (conteúdo dos documentos) → FAISS

## 5. Perguntas que o sistema deve responder

Este conjunto é o ponto de partida da avaliação do RAG.

1. O que o PL X propõe?
2. Qual é a justificativa do PL X?
3. Quais projetos tratam de inteligência artificial?
4. Quais proposições tratam de educação?
5. Quais propostas foram apresentadas por determinado deputado?
6. Qual é a situação atual da proposição X?
7. Qual foi a última tramitação da proposição X?
8. Quais proposições estão relacionadas à proposição X?
9. Quais documentos mencionam determinado assunto?
10. Compare o conteúdo de duas proposições.


## 6. Fonte dos dados

Dados Abertos da Câmara dos Deputados: https://dadosabertos.camara.leg.br