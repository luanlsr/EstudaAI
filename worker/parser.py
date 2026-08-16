import fitz  # PyMuPDF
from typing import List, Dict, Any

class PyMuPDFParser:
    """
    Parser para PDFs usando PyMuPDF (fitz).
    Extrai texto, estrutura de metadados e páginas.
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.doc = None

    def open(self):
        self.doc = fitz.open(self.file_path)
    
    def close(self):
        if self.doc:
            self.doc.close()

    def get_metadata(self) -> Dict[str, Any]:
        if not self.doc:
            self.open()
        
        toc = self.doc.get_toc()
        return {
            "page_count": len(self.doc),
            "toc": toc,
            "metadata": self.doc.metadata
        }

    def parse_pages(self, start_page: int = 0, end_page: int = None) -> List[Dict[str, Any]]:
        """
        Extrai texto e metadados das páginas, de forma paginada para grandes documentos.
        """
        if not self.doc:
            self.open()

        if end_page is None or end_page > len(self.doc):
            end_page = len(self.doc)

        pages_data = []
        for page_num in range(start_page, end_page):
            page = self.doc.load_page(page_num)
            text = page.get_text("text")
            
            pages_data.append({
                "page_number": page_num + 1,
                "content": text.strip(),
                "ocr_used": False, # PyMuPDF extract raw text
                "has_text": len(text.strip()) > 0
            })
            
        return pages_data

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
