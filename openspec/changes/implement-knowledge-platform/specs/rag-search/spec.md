## Purpose
Serviço de busca híbrida e reranking utilizando PostgreSQL FTS e pgvector.

## ADDED Requirements

### Requirement: Busca híbrida fundindo vetores e palavras-chave
The system SHALL execute both vector search and full-text search against the chunks in PostgreSQL and merge the results using Reciprocal Rank Fusion (RRF) or a similar algorithm.

#### Scenario: Busca com termo exato e contexto semântico
- **WHEN** uma query é submetida ao `rag-search`
- **THEN** os resultados devem incluir tanto os chunks que possuem a palavra-chave exata quanto aqueles que têm alta similaridade semântica (vetor)

### Requirement: Tratamento do contexto da busca
The system SHALL retrieve contextual chunks around the matched chunk if needed to avoid isolated fragments.

#### Scenario: Necessidade de contexto estendido
- **WHEN** um chunk é recuperado e identificado como resposta primária
- **THEN** o sistema pode recuperar e concatenar o chunk adjacente (anterior/posterior) ou a seção pai para prover contexto completo à LLM
