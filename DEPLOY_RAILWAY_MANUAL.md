# 🚂 Manual Completo de Deploy no Railway

Este manual apresenta o passo a passo exato para você colocar o **EstudaIA** no ar gratuitamente usando a infraestrutura do Railway. 

Como o nosso projeto tem banco de dados vetorial (`pgvector`), cache (`Redis`) e uma API robusta (`FastAPI`), o Railway é a plataforma ideal, pois provisiona tudo no mesmo ambiente.

---

## Passo 1: Preparando a Conta e o Repositório
1. Certifique-se de que todo o seu código atualizado está em um repositório no seu **GitHub**.
2. Acesse [railway.app](https://railway.app/) e crie uma conta usando o seu login do GitHub.
3. No painel inicial (Dashboard), clique no botão **New Project** (ou `Ctrl+K` -> New Project).

---

## Passo 2: Criando o Banco de Dados (PostgreSQL + pgvector)
A Inteligência Artificial precisa salvar e buscar os documentos por similaridade semântica. O Postgres do Railway já tem essa função nativa.

1. Dentro do seu novo projeto em branco, clique em **Add a Plugin** ou **Provision PostgreSQL**.
2. Aguarde alguns segundos. O banco de dados aparecerá na tela do seu projeto.
3. *Atenção:* O Railway já cria e vincula as variáveis de ambiente automaticamente (como `DATABASE_URL`).

---

## Passo 3: Criando o Redis (Mensageria e Cache)
O projeto também usa Redis (presente no `docker-compose.yml`).
1. No mesmo painel do projeto, clique no botão superior direito **New** ou **+**.
2. Escolha **Database** -> **Add Redis** (ou Provision Redis).
3. O contêiner vermelho do Redis aparecerá ao lado do seu Postgres.

---

## Passo 4: Subindo o Nosso Código (A API)
Agora vamos subir o "cérebro" do projeto.
1. No mesmo painel do projeto, clique novamente em **New** ou **+**.
2. Escolha **GitHub Repo**.
3. Selecione o repositório do **EstudaIA** na lista. (Se não aparecer, clique em "Configure GitHub App" e dê permissão para o Railway ver seus repositórios).
4. Clique em **Deploy Now**. 
5. O contêiner da nossa API vai aparecer na tela. O Railway vai começar a compilar o nosso `Dockerfile` automaticamente.

---

## Passo 5: Configurando as Variáveis de Ambiente
A API precisa de senhas para falar com a OpenAI e com o banco de dados.
1. Clique no bloco do repositório (o bloco da sua API) que acabou de ser criado na tela do Railway.
2. No menu lateral ou superior, vá até a aba **Variables**.
3. Clique em **New Variable**. Adicione:
   - **Variável:** `OPENAI_API_KEY`
   - **Valor:** `sk-...` *(Cole aqui a sua chave secreta da OpenAI)*
4. Verifique se existe uma variável chamada `DATABASE_URL`. Se você subiu os bancos nos Passos 2 e 3 dentro do mesmo projeto, o Railway geralmente cria uma "Referência Mágica" (`${{Postgres.DATABASE_URL}}`) para injetar a URL do banco. Se não estiver lá, você pode adicionar e referenciar o banco.
5. Se você precisar do Redis na API, o Railway faz o mesmo criando uma variável `REDIS_URL`.

---

## Passo 6: Criação das Tabelas do Banco (Migrações)
Quando você criar a API pela primeira vez, o banco de dados estará vazio. Para criar as tabelas corretas, usamos o `alembic`.
Graças ao arquivo `railway.toml` que já está no repositório, **este passo ocorrerá automaticamente!** O Railway lerá o `railway.toml`, executará o comando `alembic upgrade head` e só então liberará o seu site para o público.

Se por algum motivo precisar fazer isso manualmente:
1. Clique no bloco da sua API.
2. Vá até a aba **Settings**.
3. Desça a página até encontrar a seção **Deploy**.
4. Procure por **Custom Release Command** e digite: `alembic upgrade head`.

---

## Passo 7: Gerando o Link Público (Acessando o Site)
Por fim, precisamos de um link de internet para acessar o site.
1. Ainda clicando no bloco da sua API, vá até a aba **Settings**.
2. Role até a seção **Networking**.
3. Clique no botão roxo **Generate Domain**.
4. O Railway criará uma URL parecida com `https://estudaia-production.up.railway.app`.

🎉 **Pronto!** Clique nesse link gerado. O seu frontend (Caderno de Provas) deverá abrir na tela, já se comunicando com o banco de dados do Railway em nuvem e pronto para uso!
