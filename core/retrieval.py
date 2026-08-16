from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func
from infrastructure.database.models import Chunk
from infrastructure.embeddings.provider import EmbeddingProvider

class HybridRetriever:
    def __init__(self, db_session: AsyncSession, embedding_provider: EmbeddingProvider):
        self.db = db_session
        self.embedder = embedding_provider

    async def search(self, query: str, top_k: int = 5, active_kb_version: str = "v1") -> List[Dict[str, Any]]:
        # 1. Full-Text Search (FTS)
        fts_query = select(Chunk).where(
            Chunk.knowledge_base_version == active_kb_version
        ).where(
            func.to_tsvector('portuguese', Chunk.content).bool_op('@@')(func.plainto_tsquery('portuguese', query))
        ).limit(top_k * 2) # Buscamos mais para fazer o merge
        
        fts_results = (await self.db.execute(fts_query)).scalars().all()

        # 2. Vector Search
        query_embedding = await self.embedder.embed_query(query)
        # SQLAlchemy pgvector syntax para cosine distance
        vector_query = select(Chunk).where(
            Chunk.knowledge_base_version == active_kb_version
        ).order_by(
            Chunk.embedding.cosine_distance(query_embedding)
        ).limit(top_k * 2)
        
        vector_results = (await self.db.execute(vector_query)).scalars().all()

        # 3. RRF (Reciprocal Rank Fusion)
        k = 60 # constante padrão para RRF
        scores = {}
        chunks_map = {}

        def add_to_scores(results, weight=1.0):
            for rank, chunk in enumerate(results):
                chunk_id = str(chunk.id)
                if chunk_id not in scores:
                    scores[chunk_id] = 0
                    chunks_map[chunk_id] = chunk
                scores[chunk_id] += weight * (1.0 / (k + rank + 1))

        add_to_scores(fts_results)
        add_to_scores(vector_results)

        # Ordenar os resultados baseados no RRF score
        sorted_chunk_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        # Pega o Top-K
        final_results = []
        for cid in sorted_chunk_ids[:top_k]:
            chunk = chunks_map[cid]
            final_results.append({
                "id": str(chunk.id),
                "document_id": chunk.document_id,
                "document_version": chunk.document_version,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "section": chunk.section,
                "content": chunk.content,
                "score": scores[cid]
            })

        return final_results
