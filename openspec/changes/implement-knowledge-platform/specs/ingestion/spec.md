## Purpose
Pipeline assíncrono para extração, chunking e enriquecimento de metadados a partir de PDFs oficiais.

## ADDED Requirements

### Requirement: Processamento incremental de PDFs longos
The system SHALL process documents incrementally so that a failure during the processing of a long PDF (e.g. 1600 pages) does not require reprocessing from the beginning.

#### Scenario: Falha no meio do processo
- **WHEN** o pipeline falha na página 900 de um PDF de 1600 páginas
- **THEN** uma retentativa deve retomar o processo da página 900 em diante sem processar as páginas 1 a 899 novamente

### Requirement: Chunking semântico e hierárquico
The system SHALL generate chunks using a hierarchical strategy based on document structure (chapters, sections, paragraphs) and fallback to fixed size/overlap.

#### Scenario: Documento com estrutura bem definida
- **WHEN** o PDF possui capítulos e seções identificáveis no TOC
- **THEN** os chunks gerados devem conter metadados referenciando essas seções e respeitar as fronteiras semânticas na quebra
