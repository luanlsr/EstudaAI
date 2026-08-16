# Ecossistema de Agentes - EstudaAI

A arquitetura do EstudaAI foi concebida para isolar responsabilidades e criar fluxos inteligentes usando **LangGraph**. A premissa central de segurança do projeto é que **os Agentes NÃO acessam o banco de dados diretamente**; eles obrigatoriamente utilizam *Tools (Skills)* expostas por uma camada restrita de serviços (`Knowledge Service`).

---

## 1. ResearchAgent (O Pesquisador Base)

O primeiro e mais importante agente da arquitetura, implementado na Fase 1. Ele resolve o desafio fundamental do projeto: localizar informações, garantir a fidelidade ao texto oficial e reportá-las de forma rastreável.

- **Responsabilidades Principais**: 
  - Pesquisar contexto utilizando a ferramenta `search_knowledge`.
  - Extrair cirurgicamente as páginas de evidência da base vetorial.
  - Formular respostas **exclusivamente** com os fatos recuperados (*Groundedness rigoroso*).
  - Nunca utilizar conhecimento generalista do LLM ("Alucinação controlada"). Se não houver contexto na base, ele é instruído a informar insuficiência de dados.
  - Citar rigidamente as fontes no formato `[Documento X, página Y]`.

---

## 2. Próximos Agentes da Topologia (Expansão)

Conforme a evolução do sistema simulador, a topologia multi-agent (StateGraph) se ramificará, incluindo:

### 🔍 AnalysisAgent
- **Propósito**: Interpretar as informações já localizadas pelo `ResearchAgent`. Ele explicará relações e destrinchará conceitos jurídicos e militares complexos encontrados nas apostilas. 
- **Regra**: Nunca deve apresentar como um "fato documental" algo que for apenas uma inferência ou analogia gerada por ele.

### ⚖️ ComparisonAgent
- **Propósito**: Comparar sistematicamente diferentes documentos, fluxos ou mudanças de legislação ao longo do tempo.
- **Exemplo**: "No manual de 2024 a regra X era A, no manual de 2026 a regra X é B".
- **Regra**: Ele normaliza as evidências enviadas pela tool de busca, mapeia os conflitos declarados pelas próprias fontes e expõe as disparidades ao usuário.

### 🛡️ ValidationAgent (Avaliador Interno)
- **Propósito**: Funciona como um guardião da integridade da resposta (*Evaluator*). 
- **Comportamento**: Ele é invisível para o usuário final. Ele apenas audita se a resposta redigida pelo `ResearchAgent` realmente utilizou citações válidas e se essas citações existem materialmente dentro dos "chunks" do banco de dados que foram resgatados na sessão atual. 
- **Feedback Loop**: Se detectar uma alucinação sutil, o `ValidationAgent` reprova o texto e engatilha um "retry loop" automático no LangGraph antes do texto chegar à tela do aluno.

---

## 🚦 O Cérebro do Fluxo: Agent Router

O **Agent Router** é o nó condicional do grafo encarregado da Classificação de Intenção (`Intent Classification`).

**Exemplo prático de como o fluxo orquestra os Agentes:**
1. **O Aluno digita:** "Quais são as diferenças nas exigências legais para a continência entre o documento de 2025 e a apostila mais nova?"
2. **Router**: Analisa a semântica da pergunta, nota que há um aspecto comparativo envolvendo múltiplas fontes e delega a tarefa ao `ComparisonAgent`.
3. **ComparisonAgent**: Invoca as skills de banco, recupera a Seção de Continências de ambos os PDFs correspondentes. Ele rascunha a explicação temporal.
4. **ValidationAgent**: Intercepta a resposta provisória e faz a auditoria. Ele lê a página do Doc de 2025 e do Doc Novo (2026). Confirma que a discrepância citada é textual e não uma alucinação criativa.
5. **Finalização**: A resposta aprovada retorna ao usuário pelo endpoint da API em tempo real.
