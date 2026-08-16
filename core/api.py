from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:password@db:5432/knowledge")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Knowledge Platform API", version="1.0")

# Permitir requisições de outros domínios (ex: Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, pode restringir para o domínio do Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embedding_provider = OpenAIEmbeddingProvider()

# Compila o agente do LangGraph
research_agent = create_research_agent()

os.makedirs("frontend", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")

class SearchQuery(BaseModel):
    query: str
    top_k: Optional[int] = 5

class AgentResponse(BaseModel):
    answer: str

@app.post("/api/search", response_model=AgentResponse)
async def search_knowledge_base(
    req: SearchQuery, 
    db_session = Depends(get_db_session)
):
    try:
        # Inicializa o retriever real para essa sessão de DB
        retriever = HybridRetriever(db_session=db_session, embedding_provider=embedding_provider)
        
        # Injeta globalmente para a tool conseguir usar
        set_retriever(retriever)
        
        # Invoca o LangGraph
        initial_state = {"messages": [HumanMessage(content=req.query)]}
        final_state = await research_agent.ainvoke(initial_state)
        
        # A última mensagem é a resposta do Agente (AI)
        ai_msg = final_state["messages"][-1].content
        
        return {"answer": ai_msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge/documents")
async def list_documents(db_session = Depends(get_db_session)):
    # Simulação da busca de documentos
    # docs = await db_session.execute(select(Document))
    return [
        {"id": "doc1", "title": "Manual Principal", "version": "v1"}
    ]

# Para rodar o servidor: uvicorn core.api:app --reload
