from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from core.skills import search_knowledge

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# Inicia o LLM com as tools vinculadas
# Se model_kwargs der erro, usamos bind_tools direto.
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools([search_knowledge])

def agent_node(state: AgentState):
    messages = state["messages"]
    sys_msg = SystemMessage(content="""Você é o Capitão Instrução, um instrutor virtual experiente e respeitado, focado no edital do CEFS da Polícia Militar.
Você deve responder às perguntas dos alunos de forma firme, clara, técnica e extremamente didática, baseando-se ESTRITAMENTE no conteúdo das apostilas fornecidas através da sua ferramenta de busca.
Seja direto ao ponto, mas sempre explique o porquê de cada resposta militar ou jurídica usando a doutrina oficial.
    
REGRAS IMPORTANTES:
1. Sempre utilize a tool 'search_knowledge' para buscar na documentação oficial antes de responder.
2. Se a documentação oficial não mencionar o tema, diga: "Não foi encontrada evidência suficiente na documentação oficial para responder sua pergunta." e não invente respostas.
3. Se a pergunta for uma questão (múltipla escolha, V/F ou direta), você DEVE responder EXATAMENTE neste formato Markdown:

### ✅ Resposta
**[Sua resposta direta ou a Alternativa Correta]**

### 🧠 Justificativa
[Explique detalhadamente o porquê, citando a regra oficial]

### 📚 Fonte Oficial
*[Página X e/ou Título do Capítulo]*

4. CITAÇÃO OBRIGATÓRIA: Nunca deixe a seção de Fonte Oficial em branco. Use o número da página que a tool retornar.""")
    
    # Se a primeira mensagem não for System, injetamos
    if not isinstance(messages[0], SystemMessage):
        messages = [sys_msg] + list(messages)
        
    response = llm.invoke(messages)
    return {"messages": [response]}

def create_research_agent():
    graph_builder = StateGraph(AgentState)
    
    # Adicionamos os nós
    graph_builder.add_node("agent", agent_node)
    
    # Criamos o nó de Tools (que vai rodar a search_knowledge)
    tools = [search_knowledge]
    tool_node = ToolNode(tools)
    graph_builder.add_node("tools", tool_node)
    
    # Definimos as arestas
    graph_builder.set_entry_point("agent")
    
    # Quando o agent rodar, ele pode decidir chamar uma tool (tools_condition -> "tools") ou terminar (END)
    graph_builder.add_conditional_edges(
        "agent",
        tools_condition,
    )
    # Depois que a tool rodar, volta para o agente ler o resultado
    graph_builder.add_edge("tools", "agent")
    
    return graph_builder.compile()
