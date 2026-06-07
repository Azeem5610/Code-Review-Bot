# TODO: Ask Codex to implement these three nodes
# Prompt: "Write agent/nodes.py — three LangGraph nodes: bug_detector_node,
# security_node, quality_node. Each receives state with a 'diff' key,
# calls OpenRouter using langchain-openai with the prompts from prompts.py,
# parses the JSON response, and returns findings merged into state."

from agent.prompts import BUG_DETECTOR_PROMPT, SECURITY_PROMPT, QUALITY_PROMPT

def bug_detector_node(state: dict) -> dict:
    pass

def security_node(state: dict) -> dict:
    pass

def quality_node(state: dict) -> dict:
    pass

def aggregator_node(state: dict) -> dict:
    pass
