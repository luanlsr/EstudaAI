## Purpose
Agente especializado em encontrar evidências, validar citações e responder com base exclusiva no RAG.

## ADDED Requirements

### Requirement: Respostas restritas ao contexto documental
The system SHALL NOT generate answers using the LLM's general knowledge when asked about the domain of the official documentation; it MUST ground answers exclusively in the retrieved chunks.

#### Scenario: Informação não encontrada
- **WHEN** o contexto recuperado não contém a resposta para a pergunta
- **THEN** o agente deve responder explicitamente que não há evidência suficiente nos documentos oficiais e se recusar a inventar a informação

### Requirement: Citações obrigatórias nas respostas
The system SHALL provide citations for every grounded statement, including at least the document ID and the page numbers where the evidence was found.

#### Scenario: Resposta fundamentada com sucesso
- **WHEN** o agente elabora uma resposta baseada na seção 12.3 do documento X, páginas 817-819
- **THEN** a resposta final exibida ao usuário deve incluir a citação referenciando o documento X, as páginas 817-819 e a seção correspondente
