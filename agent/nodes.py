import json
import os
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from agent.prompts import BUG_DETECTOR_PROMPT, QUALITY_PROMPT, SECURITY_PROMPT

load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-4o-mini"


def bug_detector_node(state: dict[str, Any]) -> dict[str, Any]:
    findings = run_reviewer(
        prompt_template=BUG_DETECTOR_PROMPT,
        diff=get_diff(state),
        category="bug",
    )
    return merge_findings(state, "bug_findings", findings)


def security_node(state: dict[str, Any]) -> dict[str, Any]:
    findings = run_reviewer(
        prompt_template=SECURITY_PROMPT,
        diff=get_diff(state),
        category="security",
    )
    return merge_findings(state, "security_findings", findings)


def quality_node(state: dict[str, Any]) -> dict[str, Any]:
    findings = run_reviewer(
        prompt_template=QUALITY_PROMPT,
        diff=get_diff(state),
        category="quality",
    )
    return merge_findings(state, "quality_findings", findings)


def aggregator_node(state: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for key in ("bug_findings", "security_findings", "quality_findings", "findings"):
        value = state.get(key, [])
        if isinstance(value, list):
            findings.extend(finding for finding in value if isinstance(finding, dict))

    deduped = dedupe_findings(findings)
    return {**state, "findings": deduped}


def get_diff(state: dict[str, Any]) -> str:
    diff = state.get("diff")
    if not isinstance(diff, str) or not diff.strip():
        raise ValueError("State must include a non-empty 'diff' string")
    return diff


def run_reviewer(
    prompt_template: str,
    diff: str,
    category: str,
) -> list[dict[str, Any]]:
    prompt = prompt_template.format(diff=diff)
    response = get_llm().invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)
    return normalize_findings(parse_json_array(content), category)


def get_llm() -> ChatOpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENROUTER_API_KEY")

    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL),
        api_key=api_key,
        base_url=os.getenv("OPENROUTER_BASE_URL", OPENROUTER_BASE_URL),
        temperature=0,
        max_retries=2,
        timeout=60,
        default_headers={
            "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost"),
            "X-Title": os.getenv("OPENROUTER_APP_NAME", "Code Review Bot"),
        },
    )


def parse_json_array(content: Any) -> list[dict[str, Any]]:
    if isinstance(content, list):
        return [item for item in content if isinstance(item, dict)]

    if not isinstance(content, str):
        raise ValueError("Reviewer response must be a JSON array string")

    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        cleaned = cleaned.removesuffix("```").strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("[")
        end = cleaned.rfind("]")
        if start == -1 or end == -1 or end < start:
            raise
        parsed = json.loads(cleaned[start : end + 1])

    if isinstance(parsed, dict) and isinstance(parsed.get("findings"), list):
        parsed = parsed["findings"]

    if not isinstance(parsed, list):
        raise ValueError("Reviewer response must be a JSON array")

    return [item for item in parsed if isinstance(item, dict)]


def normalize_findings(
    findings: list[dict[str, Any]],
    category: str,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []

    for finding in findings:
        file_name = finding.get("file") or finding.get("path") or finding.get("filename")
        line = finding.get("line") or finding.get("line_number") or finding.get("end_line")
        severity = str(finding.get("severity", "LOW")).upper()
        comment = finding.get("comment") or finding.get("message") or finding.get("description")

        if not file_name or line is None or not comment:
            continue

        try:
            line_number = int(line)
        except (TypeError, ValueError):
            continue

        normalized.append(
            {
                **finding,
                "file": str(file_name),
                "path": str(file_name),
                "line": line_number,
                "severity": severity if severity in {"HIGH", "MEDIUM", "LOW"} else "LOW",
                "comment": str(comment),
                "category": category,
            }
        )

    return normalized


def merge_findings(
    state: dict[str, Any],
    key: str,
    findings: list[dict[str, Any]],
) -> dict[str, Any]:
    existing = state.get("findings", [])
    merged = [*existing, *findings] if isinstance(existing, list) else findings
    return {**state, key: findings, "findings": merged}


def dedupe_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, int, str, str]] = set()
    deduped: list[dict[str, Any]] = []

    for finding in findings:
        key = (
            str(finding.get("file") or finding.get("path") or ""),
            int(finding.get("line") or 0),
            str(finding.get("category") or ""),
            str(finding.get("comment") or finding.get("message") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)

    return deduped


bug_detector = bug_detector_node
security_scanner = security_node
quality_checker = quality_node
