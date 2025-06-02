from langgraph.graph import END, StateGraph
from .graph_state import AgentState
from .retrieve_node import graph_search, vector_search
from .generate_node import cypher_agent, generate_prompt
from .conditional_edge import check_cypher_query

workflow = StateGraph(AgentState)
workflow.add_node("cypher_agent", cypher_agent)
workflow.add_node("graph_search", graph_search)
workflow.add_node("generate", generate_prompt)
workflow.add_node("vector_search", vector_search)
workflow.set_entry_point("cypher_agent")

workflow.add_conditional_edges(
    "graph_search",
    check_cypher_query,
    {
        "success": "generate",
        "error": "vector_search",
    }
)
workflow.add_edge("cypher_agent", "graph_search")
workflow.add_edge("vector_search", "generate")
workflow.set_finish_point("generate")

# langgraph의 workflow를 컴파일
app = workflow.compile()