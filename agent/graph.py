from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from agent.nodes import (
    aggregator_node,
    bug_detector_node,
    quality_node,
    security_node,
)


class ReviewState(TypedDict, total=False):
    diff: str
    bug_findings: list[dict[str, Any]]
    security_findings: list[dict[str, Any]]
    quality_findings: list[dict[str, Any]]
    findings: list[dict[str, Any]]


def build_graph():
    graph = StateGraph(ReviewState)

    graph.add_node("bug_detector", run_bug_detector)
    graph.add_node("security_scanner", run_security_scanner)
    graph.add_node("quality_checker", run_quality_checker)
    graph.add_node("aggregate", aggregate_results)

    graph.add_conditional_edges(START, fan_out_reviewers)
    graph.add_edge(
        ["bug_detector", "security_scanner", "quality_checker"],
        "aggregate",
    )
    graph.add_edge("aggregate", END)

    return graph.compile()


def fan_out_reviewers(state: ReviewState) -> list[Send]:
    diff = state.get("diff", "")
    return [
        Send("bug_detector", {"diff": diff}),
        Send("security_scanner", {"diff": diff}),
        Send("quality_checker", {"diff": diff}),
    ]


def run_bug_detector(state: ReviewState) -> dict[str, list[dict[str, Any]]]:
    result = bug_detector_node(state)
    return {"bug_findings": result.get("bug_findings", [])}


def run_security_scanner(state: ReviewState) -> dict[str, list[dict[str, Any]]]:
    result = security_node(state)
    return {"security_findings": result.get("security_findings", [])}


def run_quality_checker(state: ReviewState) -> dict[str, list[dict[str, Any]]]:
    result = quality_node(state)
    return {"quality_findings": result.get("quality_findings", [])}


def aggregate_results(state: ReviewState) -> dict[str, list[dict[str, Any]]]:
    result = aggregator_node(state)
    return {"findings": result.get("findings", [])}
