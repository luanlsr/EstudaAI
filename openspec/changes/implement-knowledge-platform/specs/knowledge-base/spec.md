## Purpose
Gerenciamento de documentos oficiais, versões, páginas, seções e embeddings na base de conhecimento.

## ADDED Requirements

### Requirement: O sistema deve versionar a base de conhecimento e os documentos
The system SHALL keep track of versions of the knowledge base and individual documents. A document can have multiple versions and the knowledge base has a globally active version.

#### Scenario: Ativar uma nova versão da base de conhecimento
- **WHEN** a nova versão é validada e marcada como ativa
- **THEN** todas as requisições subsequentes utilizarão os embeddings e metadados desta nova versão ativa

### Requirement: Rastreabilidade por páginas e seções
The system SHALL store document contents fragmented by pages and sections for precise traceability.

#### Scenario: Recuperação de um chunk
- **WHEN** o sistema recupera um chunk do PostgreSQL
- **THEN** ele deve retornar metadados contendo o `document_id`, `page_start`, `page_end` e (se disponível) `section` e `chapter`
