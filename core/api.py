from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.retrieval import HybridRetriever
from infrastructure.embeddings.provider import OpenAIEmbeddingProvider
from core.skills import set_retriever
from core.agent import create_research_agent
from langchain_core.messages import HumanMessage
import os

from core.auth import auth_router, get_current_user

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:password@db:5432/knowledge")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session

from fastapi.middleware.cors import CORSMiddleware
from infrastructure.database.models import Base
from sqlalchemy import text

app = FastAPI(title="Knowledge Platform API", version="1.0")

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas de autenticação
app.include_router(auth_router)

embedding_provider = OpenAIEmbeddingProvider()
research_agent = create_research_agent()

os.makedirs("frontend", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")

class SearchQuery(BaseModel):
    query: str
    top_k: Optional[int] = 5

@app.post("/api/search")
async def search_knowledge_base(
    req: SearchQuery, 
    db_session = Depends(get_db_session),
    user: dict = Depends(get_current_user) # Exige login!
):
    """Retorna a resposta do LLM via Server-Sent Events (SSE) para efeito de digitação."""
    retriever = HybridRetriever(db_session=db_session, embedding_provider=embedding_provider)
    
    async def event_generator():
        try:
            set_retriever(retriever)
            initial_state = {"messages": [HumanMessage(content=req.query)]}
            
            # Usando astream_events do LangGraph para capturar o streaming do modelo
            async for event in research_agent.astream_events(initial_state, version="v2"):
                kind = event["event"]
                # Filtra apenas o stream de texto gerado pelo chat model (ignorando chamadas de tool)
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if chunk.content:
                        # Substitui quebras de linha para o formato SSE (Server-Sent Events)
                        # Em SSE, dados são mandados como "data: conteúdo\n\n"
                        # Mas como o conteúdo pode ter \n, nós encodamos para mandar seguro
                        import json
                        yield f"data: {json.dumps({'chunk': chunk.content})}\n\n"
            
            # Envia um evento finalizando a stream
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            import json
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

class QuizQuery(BaseModel):
    num_questions: int = 5
    topics: Optional[str] = None

class QuizOption(BaseModel):
    text: str

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_option_index: int
    justification: str

class QuizResponse(BaseModel):
    questions: List[QuizQuestion]

@app.post("/api/quiz", response_model=QuizResponse)
async def generate_quiz(
    req: QuizQuery,
    db_session = Depends(get_db_session),
    user: dict = Depends(get_current_user)
):
    """Gera um simulado automaticamente em formato JSON estruturado."""
    retriever = HybridRetriever(db_session=db_session, embedding_provider=embedding_provider)
    
    # 1. Busca contexto baseado nos tópicos
    query = req.topics if req.topics else "CEFS 2026 Resumo Geral"
    docs = await retriever.search(query, top_k=15)
    context = "\n\n".join([d["content"] for d in docs])
    
    # 2. Usa o modelo com saída estruturada
    from langchain_openai import ChatOpenAI
    topic_str = f" sobre: {req.topics}" if req.topics else ""
    prompt = f"""Você é o examinador oficial do CEFS.
Baseado **estritamente** nos fragmentos da apostila abaixo, crie um simulado com {req.num_questions} questões de múltipla escolha inéditas{topic_str}.
Para cada questão, forneça o enunciado, exatamente 4 opções de resposta, o índice da opção correta (0 a 3) e uma justificativa detalhada citando a regra no texto.

FRAGMENTOS DA APOSTILA:
{context}
"""
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3).with_structured_output(QuizResponse)
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    return response

class ScorePayload(BaseModel):
    points: int

from sqlalchemy import select
from infrastructure.database.models import UserScore

@app.post("/api/score")
async def add_score(req: ScorePayload, db_session: AsyncSession = Depends(get_db_session), user: dict = Depends(get_current_user)):
    """Atualiza a pontuação do usuário e registra o jogo."""
    query = select(UserScore).where(UserScore.user_email == user["email"])
    result = await db_session.execute(query)
    user_score = result.scalars().first()
    
    if not user_score:
        user_score = UserScore(
            user_email=user["email"],
            user_name=user.get("name", "Aluno"),
            user_picture=user.get("picture", ""),
            score=req.points,
            games_played=1
        )
        db_session.add(user_score)
    else:
        user_score.score += req.points
        user_score.games_played += 1
        
    await db_session.commit()
    return {"message": "Pontuação salva com sucesso!", "score": user_score.score}

@app.get("/api/ranking")
async def get_ranking(db_session: AsyncSession = Depends(get_db_session)):
    """Retorna o Top 10 usuários."""
    query = select(UserScore).order_by(UserScore.score.desc()).limit(10)
    result = await db_session.execute(query)
    scores = result.scalars().all()
    
    return [
        {
            "name": s.user_name,
            "picture": s.user_picture,
            "score": s.score,
            "games_played": s.games_played
        }
        for s in scores
    ]

from fastapi import BackgroundTasks

@app.post("/api/admin/ingest")
async def trigger_ingestion(background_tasks: BackgroundTasks, db_session = Depends(get_db_session)):
    """Rota para iniciar a ingestão dos PDFs em background no servidor."""
    from worker.ingestion import run_worker
    
    async def run_ingest():
        await run_worker()
        
    background_tasks.add_task(run_ingest)
    return {"message": "Ingestão iniciada em background no servidor."}

@app.get("/api/knowledge/documents")
async def list_documents(db_session = Depends(get_db_session)):
    return [{"id": "doc1", "title": "Manual Principal", "version": "v1"}]
