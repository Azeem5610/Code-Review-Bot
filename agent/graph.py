# TODO: Ask Codex to implement the LangGraph StateGraph
# Prompt: "Write agent/graph.py — a LangGraph StateGraph that runs
# bug_detector_node, security_node, and quality_node in parallel using
# Send/fan-out, then routes all three into aggregator_node. Return a
# compiled graph."

from langgraph.graph import StateGraph
from agent.nodes import bug_detector_node, security_node, quality_node, aggregator_node

def build_graph():
    pass
