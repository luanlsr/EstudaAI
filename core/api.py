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
import hashlib
import base64

import bcrypt
from core.auth import auth_router, get_current_user, get_current_user_optional, SECRET_KEY, ALGORITHM
from jose import jwt
from datetime import timedelta, datetime
from fastapi import Response

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:password@db:5432/knowledge")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session

from fastapi.middleware.cors import CORSMiddleware
from infrastructure.database.models import Base, UserScore
from sqlalchemy import text, select

app = FastAPI(title="Knowledge Platform API", version="1.0")

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(text("ALTER TABLE user_scores ADD COLUMN password_hash VARCHAR"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE user_scores ADD COLUMN rank VARCHAR"))
        except Exception:
            pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas de autenticação
app.include_router(auth_router)



class RegisterPayload(BaseModel):
    name: str
    email: str
    password: str

class LoginPayload(BaseModel):
    email: str
    password: str

def get_safe_password(pwd: str) -> str:
    # Use SHA-256 to hash the password first, which always returns 32 bytes.
    # Base64 encode it so it fits nicely within bcrypt's 72 byte limit.
    # This securely supports passwords of infinite length and with any multibyte (emoji) characters.
    digest = hashlib.sha256(pwd.encode('utf-8')).digest()
    return base64.b64encode(digest).decode('utf-8')


@app.post("/api/auth/register")
async def register_user(payload: RegisterPayload, db_session: AsyncSession = Depends(get_db_session)):
    try:
        query = select(UserScore).where(UserScore.user_email == payload.email)
        result = await db_session.execute(query)
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Email já cadastrado.")
            
        pwd_bytes = get_safe_password(payload.password).encode('utf-8')
        hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode('utf-8')
        new_user = UserScore(
            user_email=payload.email,
            user_name=payload.name,
            password_hash=hashed,
            score=0,
            games_played=0
        )
        db_session.add(new_user)
        await db_session.commit()
        return {"message": "Conta criada com sucesso!"}
    except Exception as e:
        print(f"Registration Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor ao criar a conta. Tente novamente mais tarde.")

@app.post("/api/auth/login")
async def login_user(payload: LoginPayload, response: Response, db_session: AsyncSession = Depends(get_db_session)):
    query = select(UserScore).where(UserScore.user_email == payload.email)
    result = await db_session.execute(query)
    user = result.scalars().first()
    
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos.")
        
    pwd_bytes = get_safe_password(payload.password).encode('utf-8')
    hash_bytes = user.password_hash.encode('utf-8')
    if not bcrypt.checkpw(pwd_bytes, hash_bytes):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos.")
        
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = {
        "sub": user.user_email,
        "name": user.user_name,
        "picture": user.user_picture,
        "exp": expire
    }
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    response.set_cookie(key="access_token", value=token, httponly=True, secure=True, samesite="lax", max_age=7*24*3600)
    return {"message": "Login realizado com sucesso!"}

@app.get("/api/user/me")
async def get_my_user(db_session: AsyncSession = Depends(get_db_session), current_user: dict = Depends(get_current_user_optional)):
    if not current_user:
        return {"authenticated": False}
        
    query = select(UserScore).where(UserScore.user_email == current_user["sub"])
    result = await db_session.execute(query)
    user = result.scalars().first()
    if not user:
        # User logged in via Google but hasn't played/saved yet
        return {"email": current_user["sub"], "name": current_user.get("name", "Aluno"), "rank": None, "picture": current_user.get("picture"), "is_admin": current_user["sub"] in ADMIN_EMAILS}
    return {"email": user.user_email, "name": user.user_name, "rank": user.rank, "picture": user.user_picture, "is_admin": user.user_email in ADMIN_EMAILS}

ADMIN_EMAILS = ["luanlsr@gmail.com", "luan@email.com", "luanlsr@hotmail.com"]

def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user["sub"] not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores.")
    return current_user

@app.get("/admin")
async def admin_page():
    return FileResponse("frontend/admin.html")

@app.get("/api/admin/users")
async def get_all_users(db_session: AsyncSession = Depends(get_db_session), admin: dict = Depends(get_admin_user)):
    query = select(UserScore).order_by(UserScore.score.desc())
    result = await db_session.execute(query)
    users = result.scalars().all()
    return [{"email": u.user_email, "name": u.user_name, "score": u.score, "games": u.games_played, "created_at": u.updated_at} for u in users]

@app.delete("/api/admin/users/{email}")
async def delete_user(email: str, db_session: AsyncSession = Depends(get_db_session), admin: dict = Depends(get_admin_user)):
    query = select(UserScore).where(UserScore.user_email == email)
    result = await db_session.execute(query)
    user = result.scalars().first()
    if user:
        await db_session.delete(user)
        await db_session.commit()
    return {"message": "Usuário deletado."}

@app.post("/api/admin/users/{email}/reset")
async def reset_user_score(email: str, db_session: AsyncSession = Depends(get_db_session), admin: dict = Depends(get_admin_user)):
    query = select(UserScore).where(UserScore.user_email == email)
    result = await db_session.execute(query)
    user = result.scalars().first()
    if user:
        user.score = 0
        user.games_played = 0
        await db_session.commit()
    return {"message": "Pontuação resetada."}

embedding_provider = OpenAIEmbeddingProvider()
research_agent = create_research_agent()

os.makedirs("frontend", exist_ok=True)
@app.get("/sw.js")
async def serve_sw():
    return FileResponse("frontend/sw.js", media_type="application/javascript")

@app.get("/manifest.json")
async def serve_manifest():
    return FileResponse("frontend/manifest.json", media_type="application/manifest+json")

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

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
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3).with_structured_output(QuizResponse)
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    return response

class ScorePayload(BaseModel):
    points: int



@app.post("/api/score")
async def add_score(req: ScorePayload, db_session: AsyncSession = Depends(get_db_session), user: dict = Depends(get_current_user)):
    """Atualiza a pontuação do usuário e registra o jogo."""
    query = select(UserScore).where(UserScore.user_email == user["sub"])
    result = await db_session.execute(query)
    user_score = result.scalars().first()
    
    if not user_score:
        user_score = UserScore(
            user_email=user["sub"],
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
