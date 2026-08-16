import hashlib
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

class Chunker:
    """
    Responsável por quebrar páginas de texto em chunks semânticos
    e de tamanho fixo, mantendo metadados das páginas originais.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def generate_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def chunk_pages(self, pages: List[Dict[str, Any]], toc: List[List] = None) -> List[Dict[str, Any]]:
        """
        Gera chunks a partir das páginas extraídas.
        O TOC (Table of Contents) pode ser usado futuramente para enriquecer 
        chapter/section, mas como fallback usa o RecursiveCharacterTextSplitter.
        """
        chunks = []
        
        # Agrupa conteúdo por proximidade (na fase 1 simplificamos fazendo chunking por página
        # ou unindo textos contínuos. Aqui unimos o texto e rastreamos as páginas).
        
        # Abordagem simples inicial: chunking pagina a pagina para não perder a referência exata
        # Numa abordagem avançada, uniríamos tudo mantendo um mapa de offset -> pagina.
        for page in pages:
            if not page.get("has_text", False):
                continue
                
            page_text = page["content"]
            page_num = page["page_number"]
            
            # Quebra o texto da página
            page_chunks = self.text_splitter.split_text(page_text)
            
            for chunk_text in page_chunks:
                chunks.append({
                    "page_start": page_num,
                    "page_end": page_num,
                    "chapter": None,  # TODO: integrar com TOC
                    "section": None,
                    "subsection": None,
                    "content": chunk_text,
                    "token_count": len(chunk_text.split()), # estimativa simples
                    "content_hash": self.generate_hash(chunk_text)
                })
                
        return chunks
