from abc import ABC, abstractmethod
from typing import List
from langchain_openai import OpenAIEmbeddings

class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        pass

class MockEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * self.dimension for _ in texts]

    async def embed_query(self, text: str) -> List[float]:
        return [0.1] * self.dimension

class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self):
        # Utiliza a chave OPENAI_API_KEY do ambiente automaticamente
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return await self.embeddings.aembed_documents(texts)

    async def embed_query(self, text: str) -> List[float]:
        return await self.embeddings.aembed_query(text)
