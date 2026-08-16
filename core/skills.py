from langchain_core.tools import tool
from typing import Dict, Any, List

# Dependência fictícia do retriever globalmente acessível para as tools
_global_retriever = None

def set_retriever(retriever):
    global _global_retriever
    _global_retriever = retriever

@tool
async def search_knowledge(query: str, top_k: int = 3) -> str:
    """
    Pesquisa na Base de Conhecimento oficial por informações relevantes para responder à pergunta do usuário.
    Use sempre esta tool para embasar fatos.
    """
    if _global_retriever is None:
        return "Erro: Retriever não configurado."
    
    results = await _global_retriever.search(query, top_k)
    
    if not results:
        return "Não foi encontrada evidência suficiente na documentação oficial."

    formatted_results = []
    for r in results:
        formatted_results.append(
            f"--- Fonte: Doc {r['document_id']} (Versão: {r['document_version']}) "
            f"| Páginas: {r['page_start']}-{r['page_end']} | Seção: {r['section']}\n"
            f"{r['content']}\n---"
        )
    return "\n\n".join(formatted_results)


@tool
async def get_document_summary(document_id: str) -> str:
    """
    Retorna o resumo ou metadados de um documento específico se ele existir na base.
    """
    # Exemplo simples, em produção buscaria do DB
    return f"Resumo do documento {document_id}: Um documento oficial sobre regras e procedimentos."
