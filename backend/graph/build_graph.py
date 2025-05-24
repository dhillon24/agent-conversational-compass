
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .nodes import ingest_node, sentiment_node, action_node, policy_node, memory_node


def should_continue(state: Dict[str, Any]) -> str:
    """Determine if the workflow should continue or end."""
    if state.get("is_final", False):
        return "memory"
    return "continue"


def build_customer_service_graph():
    """Build the LangGraph workflow for customer service."""
    
    # Create the state graph
    workflow = StateGraph(dict)
    
    # Add nodes
    workflow.add_node("ingest", ingest_node)
    workflow.add_node("sentiment", sentiment_node)
    workflow.add_node("action", action_node)
    workflow.add_node("policy", policy_node)
    workflow.add_node("memory", memory_node)
    
    # Set entry point
    workflow.set_entry_point("ingest")
    
    # Add edges
    workflow.add_edge("ingest", "sentiment")
    workflow.add_edge("sentiment", "action")
    workflow.add_edge("action", "policy")
    
    # Add conditional edge for the policy node
    workflow.add_conditional_edges(
        "policy",
        should_continue,
        {
            "memory": "memory",
            "continue": "policy",  # Loop back if not final
        }
    )
    
    # Add final edge
    workflow.add_edge("memory", END)
    
    # Add memory for conversation persistence
    memory = MemorySaver()
    
    # Compile the graph
    graph = workflow.compile(checkpointer=memory)
    
    return graph
