from langchain_core.tools import tool
from typing import Dict, Any, List
import contextvars

# Variável de contexto (async-safe) para lidar com milhares de requisições simultâneas sem misturar dados
_retriever_context = contextvars.ContextVar('retriever')

def set_retriever(retriever):
    _retriever_context.set(retriever)

@tool
async def search_knowledge(query: str, top_k: int = 3) -> str:
    """
    Pesquisa na Base de Conhecimento oficial por informações relevantes para responder à pergunta do usuário.
    Use sempre esta tool para embasar fatos.
    """
    retriever = _retriever_context.get(None)
    if retriever is None:
        return "Erro: Retriever não configurado."
    
    results = await retriever.search(query, top_k)
    
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
