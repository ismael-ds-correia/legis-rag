# Documentação de Testes — API de Dados Abertos da Câmara dos Deputados

Este documento registra os resultados práticos, endpoints validados, campos retornados e aprendizados operacionais obtidos durante testes realizados via navagador e script python.

## 1. Informações Gerais da Fonte
* **Fonte Oficial:** Portal de Dados Abertos da Câmara dos Deputados
* **Base URL da API REST:** `https://dadosabertos.camara.leg.br/api/v2`
* **Escopo Alvo:** Propostas legislativas dos tipos **PL, PEC e PLP** para o período de **2025–2026**.

---

## 2. Endpoints e Testes Validados

### 2.1. Referência de Tipos de Proposição
* **Endpoint:** `GET /referencias/proposicoes/siglaTipo`
* **Finalidade:** Listar todas as siglas válidas aceitas pela API da Câmara.
* **Comportamento Observado:** Retorna um catálogo completo contendo código, sigla e nome descritivo (ex: `PL` para Projeto de Lei, `PEC` para Proposta de Emenda à Constituição, `PLP` para Projeto de Lei Complementar, além de outros como `OF` para Ofício).

### 2.2. Listagem de Proposições com Filtros
* **Endpoint:** `GET /proposicoes`
* **Parâmetros de Teste:** `siglaTipo=PL&siglaTipo=PEC&siglaTipo=PLP&ano=2025&itens=5`
* **Comportamento Observado:** Retorna a listagem paginada correspondente. Nota-se que o comportamento de múltiplos filtros de tipo pode priorizar o tipo predominante dependendo do volume ativo no período, sendo recomendada a iteração individual ou controle refinado no pipeline.

### 2.3. Detalhes de uma Proposição Específica
* **Endpoint:** `GET /proposicoes/{id}`
* **Exemplo Testado:** `GET /proposicoes/2646600` (PL 3467/2025) e comparação com o ID `130138`.
* **Schema / Campos Retornados:**
  ```json
  {
    "dados": {
      "id": 2646600,
      "uri": "https://dadosabertos.camara.leg.br/api/v2/proposicoes/2646600",
      "siglaTipo": "PL",
      "codTipo": 139,
      "numero": 3467,
      "ano": 2025,
      "ementa": "Institui o Mapa de Vulnerabilidade Educacional...",
      "dataApresentacao": "2026-09-16T16:42",
      "statusProposicao": {
        "dataHora": "2026-09-16T16:42",
        "sequencia": 2,
        "siglaOrgao": "MESA",
        "uriOrgao": "...",
        "descricaoTramitacao": "Apresentação de Proposição",
        "codTipoTramitacao": 100,
        "descricaoSituacao": "Aguardando Autorização do Despacho",
        "codSituacao": 1200,
        "despacho": "Apresentação do PL n. 3467/2025...",
        "url": "...",
        "ambito": "Regimental",
        "apreciacao": "Indefinida"
      },
      "uriAutores": "https://dadosabertos.camara.leg.br/api/v2/proposicoes/2646600/autores",
      "descricaoTipo": "Projeto de Lei",
      "urlInteiroTeor": "https://www.camara.leg.br/proposicoesWeb/prop_mostrarintegra?codteor=3180876"
    }
  }
  ```
* **Consistência Estrutural:** A variação de IDs entre PL, PEC e PLP demonstrou que a estrutura do JSON é perfeitamente uniforme, facilitando a criação de um parser único no pipeline.

### 2.4. Arquivos Anuais (Carga Histórica)
* **URL:** `http://dadosabertos.camara.leg.br/arquivos/proposicoes/json/proposicoes-2025.json`
* **Comportamento Observado:** O arquivo consolida todas as proposições do ano em um único dump. Embora o arquivo seja grande e leve alguns segundos para carregar, mostrou-se altamente eficiente para a carga histórica inicial, evitando o custo de requisições paginadas em massa via API REST.

---

## 3. Desafios Operacionais e Soluções (Gotchas)

1. **Bloqueio HTTP 429 (Too Many Requests) no Download de PDFs:**
   * *Problema:* O acesso direto aos links de teor inteiro (`urlInteiroTeor`) hospedados no portal da Câmara (`www.camara.leg.br`) retorna erro `429` quando requisitado por scripts simples sem cabeçalhos de navegador.
   * *Solução:* Inclusão de cabeçalhos HTTP robustos simulando um navegador real (`User-Agent` de Chrome, `Referer`, `Accept-Language`) e espaçamento temporal (`time.sleep`) entre requisições.

2. **Estratégia Híbrida de Ingestão Definida:**
   * **Carga Inicial / Histórica:** Utilizar os arquivos JSON anuais consolidados.
   * **Atualização Incremental:** Utilizar os endpoints REST paginados da API para capturar atualizações diárias recentes.