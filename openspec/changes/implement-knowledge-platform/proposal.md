## Why

Implementar a plataforma de inteligência baseada em documentação oficial (Knowledge Platform + RAG + Agents) descrita no draft arquitetural, visando transformar PDFs oficiais em uma base de conhecimento versionada, pesquisável e auditável, garantindo que as respostas geradas por IA sejam estritamente baseadas nas fontes documentais (groundedness) e com alta rastreabilidade.

## What Changes

- Estabelecimento de infraestrutura local via Docker Compose (PostgreSQL com `pgvector` e Redis).
- Criação da camada Backend com FastAPI.
- Implementação do Worker e Ingestion Pipeline (usando PyMuPDF para parsing, extração de páginas e geração de chunks estruturados e embeddings).
- Setup do Knowledge Service com RAG Híbrido (Vector Search + Full Text Search no Postgres).
- Implementação do `ResearchAgent` e das Skills fundamentais para recuperar e validar evidências e citar fontes rigorosamente.
- Organização do repositório orientada a domínios (infrastructure, core, worker).

## Capabilities

### New Capabilities
- `knowledge-base`: Gerenciamento de documentos oficiais, versões, rastreabilidade de páginas, seções, e chunks persistidos no Postgres.
- `ingestion`: Pipeline de ingestão assíncrona de PDFs (parsing, chunking hierárquico, embeddings via Redis e worker).
- `rag-search`: Serviço de busca híbrida e reranking utilizando PostgreSQL FTS e `pgvector`.
- `research-agent`: Agente e Tools focadas em recuperar evidências e apresentar respostas fundamentadas.

### Modified Capabilities

## Impact

- Todo o projeto nascerá a partir desta fundação: configuração de ambiente (Docker, `.env.example`), criação da API (FastAPI) e do Worker (processamento assíncrono).
- Definição do schema relacional do PostgreSQL (tabelas `documents`, `pages`, `chunks`).
