## 1. Setup da Infraestrutura

- [x] 1.1 Criar o arquivo `docker-compose.yml` para rodar PostgreSQL (com imagem que suporta pgvector) e Redis.
- [x] 1.2 Configurar o arquivo `.env.example` e estrutura básica do projeto Python (`core/`, `infrastructure/`, `worker/`).

## 2. Modelagem do Banco de Dados

- [x] 2.1 Criar modelos SQLAlchemy para `documents`, `pages` e `chunks`.
- [x] 2.2 Configurar o Alembic para gerenciar as migrações e criar a migração inicial ativando `pgvector`.

## 3. Ingestion Pipeline (Worker)

- [x] 3.1 Implementar a classe de Parsing utilizando PyMuPDF para extrair texto e estrutura básica (TOC) das páginas.
- [x] 3.2 Implementar a lógica de chunking hierárquico e fallback de tamanho (com metadados).
- [x] 3.3 Implementar a integração com um `EmbeddingProvider` abstrato (mock inicial ou OpenAI) para gerar embeddings.
- [x] 3.4 Configurar o job de worker (usando Redis Queue/Celery ou asyncio puro em script background) para coordenar a ingestão dos PDFs.

## 4. Busca Híbrida e RAG

- [x] 4.1 Implementar queries SQL ou via SQLAlchemy de Full-Text Search no PostgreSQL.
- [x] 4.2 Implementar queries vector-based utilizando o tipo `vector` do PostgreSQL.
- [x] 4.3 Implementar o merge via RRF (Reciprocal Rank Fusion) para a busca híbrida.
- [x] 4.4 Expor endpoints na API FastAPI (ex: `POST /api/search` e `GET /api/knowledge/documents`).

## 5. Agentes e Skills

- [x] 5.1 Criar as Skills fundamentais (`search_knowledge`, `get_document`).
- [x] 5.2 Implementar o fluxo do `ResearchAgent` (via LangGraph) para processar perguntas e buscar informações na Knowledge Base.
- [x] 5.3 Assegurar que as respostas incluam referências obrigatórias (`Citations`), testando o cenário onde nenhuma evidência existe.
