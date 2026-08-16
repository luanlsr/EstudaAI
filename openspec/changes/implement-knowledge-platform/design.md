## Context

O projeto atual está vazio. O design deste sistema visa construir uma plataforma RAG (Retrieval-Augmented Generation) voltada para o processamento de PDFs oficiais grandes (ex: 1600+ páginas) conforme descrito em `proposal.md`. A arquitetura será baseada em micro-serviços contendo uma API síncrona (FastAPI) e um worker assíncrono para processamento pesado dos PDFs.

## Goals / Non-Goals

**Goals:**
- Estabelecer as bases da arquitetura limpa (Clean Architecture).
- Implementar as tabelas base no PostgreSQL e habilitar `pgvector`.
- Criar a ingestão baseada em PyMuPDF para parsing de texto.
- Implementar vector search + full-text search (busca híbrida).
- Criar o primeiro agente (`ResearchAgent`) capaz de utilizar Skills para consultar o PostgreSQL e gerar citações precisas.

**Non-Goals:**
- Implementação completa do frontend Web (Next.js) não será foco da Fase 1, a menos que necessário para validar a API (será focado na estabilidade do core RAG primeiro).
- Não implementaremos agentes analíticos e de comparação na Fase 1.
- Não faremos fine-tuning de modelos.

## Decisions

- **Database único (PostgreSQL + pgvector)**: Para reduzir a complexidade operacional inicial, em vez de usar um banco relacional para metadados e um banco vetorial especializado (ex: Pinecone, Qdrant) separado, o PostgreSQL cuidará de tudo. Utilizaremos o FTS (Full Text Search) nativo do Postgres juntamente com o tipo `vector` para a busca híbrida.
- **Processamento Assíncrono com Redis Queue (RQ) ou Celery**: Devido a PDFs com centenas ou milhares de páginas, o parsing (PyMuPDF) e a geração de embeddings (via provedor de IA) demoram muito e podem causar timeout em requisições web síncronas. Uma arquitetura de Worker separada processará essas tarefas em background, marcando a nova versão da Knowledge Base como ativa somente após a conclusão (Atomic Activation).
- **Abstração de LLM/Embedding**: Será criado um `EmbeddingProvider` abstrato para não acoplar o sistema rigidamente à OpenAI ou Anthropic desde o dia 1.

## Risks / Trade-offs

- **[Risco] Falha no meio do processamento de grandes PDFs (Timeout / Limite de API)**
  → *Mitigação*: Implementar o Ingestion Pipeline processando e salvando chunks incrementalmente no banco ou gerenciando lotes. Se falhar no lote N, o worker retoma do lote N sem refazer de 1 a N-1.
- **[Risco] Excesso de chamadas na API de Embeddings**
  → *Mitigação*: Fazer batch das requisições para a API e realizar hash do conteúdo da página para reaproveitar embeddings (evitar reprocessamento de chunks idênticos em versões subsequentes, se aplicável, ou ao menos tratar erros temporários com exponential backoff).
- **[Risco] Adoção prematura de LangGraph para fluxo simples**
  → *Mitigação*: LangGraph será introduzido de forma restrita ao ciclo do `ResearchAgent` (Classify -> Retrieve -> Validate -> Answer), evitando abstrações excessivas enquanto não houver múltiplos agentes colaborando.
