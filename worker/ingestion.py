import asyncio
import os
import hashlib
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from worker.parser import PyMuPDFParser
from worker.chunker import Chunker
from infrastructure.embeddings.provider import OpenAIEmbeddingProvider
from infrastructure.database.models import Document, Page, Chunk

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/knowledge")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class IngestionPipeline:
    """
    Coordena a extração, chunking e indexação de PDFs oficiais no banco.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.chunker = Chunker()
        self.embedding_provider = OpenAIEmbeddingProvider()
        self.db_session = db_session

    def get_file_hash(self, file_path: str) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha256.update(block)
        return sha256.hexdigest()

    async def process_document(self, document_id: str, file_path: str, kb_version: str, document_version: str):
        print(f"[{datetime.now()}] Iniciando ingestão do documento {document_id}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        file_hash = self.get_file_hash(file_path)
        
        # Registrar Document
        doc_record = Document(
            id=document_id,
            title=os.path.basename(file_path),
            file_hash=file_hash,
            document_version=document_version,
            knowledge_base_version=kb_version,
            priority=1,
            authority="official"
        )
        # Ignorando conflitos para MVP ou podemos simplesmente adicionar
        # Em proc. ideal, faríamos um merge ou check
        self.db_session.add(doc_record)
        await self.db_session.commit()
        
        with PyMuPDFParser(file_path) as parser:
            metadata = parser.get_metadata()
            print(f"[{datetime.now()}] Total de páginas: {metadata['page_count']}")
            
            # Lotes para processamento incremental
            batch_size = 50
            for start_page in range(0, metadata['page_count'], batch_size):
                end_page = min(start_page + batch_size, metadata['page_count'])
                print(f"[{datetime.now()}] Processando páginas {start_page+1} a {end_page}...")
                
                # 1. Parse
                pages_data = parser.parse_pages(start_page, end_page)
                
                # 2. Chunking
                chunks_data = self.chunker.chunk_pages(pages_data, toc=metadata.get("toc"))
                
                # 3. Embeddings
                texts_to_embed = [c["content"] for c in chunks_data]
                if texts_to_embed:
                    embeddings = await self.embedding_provider.embed_documents(texts_to_embed)
                    
                    for i, chunk_dict in enumerate(chunks_data):
                        chunk_dict["embedding"] = embeddings[i]
                
                # 4. Salvar no banco (Chunks)
                # (Por enquanto pulamos salvar 'pages' inteiras para poupar código MVP)
                for c in chunks_data:
                    chunk_record = Chunk(
                        id=uuid.uuid4(),
                        document_id=document_id,
                        document_version=document_version,
                        knowledge_base_version=kb_version,
                        page_start=c["page_start"],
                        page_end=c["page_end"],
                        chapter=c["chapter"],
                        section=c["section"],
                        subsection=c["subsection"],
                        content=c["content"],
                        token_count=c["token_count"],
                        content_hash=c["content_hash"],
                        embedding=c["embedding"]
                    )
                    self.db_session.add(chunk_record)
                    
                await self.db_session.commit()
                print(f"[{datetime.now()}] Lote {start_page+1}-{end_page} salvo.")
                
        print(f"[{datetime.now()}] Ingestão concluída com sucesso para {document_id}")

async def run_worker():
    print("Iniciando Worker de Ingestão...")
    pdf_paths = [
        ("cefs-2026-p1", "docs/APOSTILA COMPLETA CEFS 2026.pdf"),
        ("cefs-2026-p2", "docs/ilovepdf_merged_compressed.pdf")
    ]

    async with AsyncSessionLocal() as session:
        pipeline = IngestionPipeline(session)
        for doc_id, pdf_path in pdf_paths:
            if not os.path.exists(pdf_path):
                print(f"Erro: Arquivo {pdf_path} não encontrado na pasta local.")
                continue

            await pipeline.process_document(
                document_id=doc_id,
                file_path=pdf_path,
                kb_version="v1",
                document_version="1.0"
            )

if __name__ == "__main__":
    asyncio.run(run_worker())
