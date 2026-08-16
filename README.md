# EstudaAI - Plataforma de Conhecimento RAG

O **EstudaAI** é uma plataforma inteligente voltada para simulação, estudos e resolução de provas (como o CEFS), utilizando a arquitetura RAG (Retrieval-Augmented Generation). Ela responde perguntas do usuário **estritamente com base em documentos oficiais** (apostilas, manuais e legislações). A Inteligência Artificial do projeto tem travas para não "inventar" dados, garantindo rastreabilidade das respostas com citação da fonte e da página correspondente.

## 🚀 Tecnologias

- **Backend:** FastAPI (Python), SQLAlchemy, Alembic.
- **Banco de Dados:** PostgreSQL com extensão `pgvector` para busca semântica, Redis para mensageria.
- **IA e Agentes:** LangChain, LangGraph e OpenAI (extensível a outros provedores).
- **Processamento e Ingestão:** PyMuPDF para preservação exata da paginação dos PDFs.
- **Frontend:** Vanilla HTML, CSS e JS (Servido nativamente pela API).

## 📂 Estrutura do Projeto

- `core/`: Coração do sistema (Rotas da API, Definição do Grafo de Agentes, Tools e Skills).
- `infrastructure/`: Abstrações, modelos do SQLAlchemy e migrações do Alembic.
- `worker/`: Orquestração pesada de leitura de PDFs, chunking de texto e inserção vetorial no banco.
- `frontend/`: Interface de usuário final (o "Caderno de Provas").
- `docs/`: Documentos e PDFs brutos lidos pelo worker.
- `agents.md`: Arquitetura aprofundada dos Agentes e fluxo lógico.

## 🛠️ Como Rodar Localmente

1. **Suba os Contêineres de Infraestrutura (Banco + Redis):**
   ```bash
   docker-compose up -d
   ```
   *(Isso levanta o PostgreSQL na porta 5432 e o Redis na 6379)*

2. **Configure o Ambiente:**
   Copie o arquivo de exemplo e insira suas credenciais (ex: Chave da OpenAI).
   ```bash
   cp .env.example .env
   ```

3. **Crie a Estrutura do Banco de Dados:**
   Construa as tabelas baseando-se nas migrações.
   ```bash
   alembic upgrade head
   ```

4. **Rode a Aplicação:**
   Inicie a API com Uvicorn.
   ```bash
   uvicorn core.api:app --reload
   ```
   O sistema (API e site) estará disponível em `http://localhost:8000`.

## 🌍 Como Fazer Deploy

O repositório já está configurado para ambientes de produção. Escolha uma das arquiteturas:

### Opção 1: Tudo no Railway (Recomendado e Mais Simples)
O Railway vai rodar seu Banco de Dados, sua API e servir sua página estática da web ao mesmo tempo.
1. No [Railway](https://railway.app/), crie novos serviços: **PostgreSQL** (já possui `pgvector`) e **Redis**.
2. Conecte seu repositório do GitHub no Railway.
3. Configure as Variáveis de Ambiente (`DATABASE_URL`, `OPENAI_API_KEY`).
4. Para as migrações rodarem automaticamente, vá em *Settings* > *Deploy* > *Custom Release Command* e adicione: `alembic upgrade head`.

### Opção 2: Vercel (Frontend) + Railway (Backend/API)
Para máxima performance e CDN global para sua página de frontend.
1. Hospede a API no Railway seguindo os passos da "Opção 1".
2. Edite o arquivo `vercel.json` na raiz deste repositório, inserindo a URL de produção do Railway gerada.
3. Conecte o repositório no [Vercel](https://vercel.com). O arquivo JSON instruirá o Vercel a servir os arquivos visuais e criar um proxy automático direcionando rotas `/api/*` ao Railway.