import hashlib
import hmac
import json
import os
from typing import Any

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from github import Github, GithubException

load_dotenv()

app = FastAPI(title="Code Review Bot")

COMMENTABLE_SEVERITIES = {"HIGH", "MEDIUM"}
REVIEWABLE_ACTIONS = {"opened", "reopened", "ready_for_review", "synchronize"}


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/review")
async def review(
    request: Request,
    x_github_event: str | None = Header(default=None),
    x_hub_signature_256: str | None = Header(default=None),
) -> dict[str, Any]:
    raw_body = await request.body()
    verify_github_signature(raw_body, x_hub_signature_256)

    payload = parse_json_body(raw_body)

    if x_github_event and x_github_event != "pull_request":
        return {"status": "ignored", "reason": f"unsupported event: {x_github_event}"}

    action = payload.get("action")
    if action and action not in REVIEWABLE_ACTIONS:
        return {"status": "ignored", "reason": f"unsupported action: {action}"}

    repo_name, pr_number = extract_pull_request_context(payload)
    token = payload.get("token") or get_github_token()
    diff = payload.get("diff") or fetch_pull_request_diff(repo_name, pr_number, token)

    agent_output = run_review_agent(diff)
    comment_summary = post_inline_comments(repo_name, pr_number, agent_output, token)

    return {
        "status": "reviewed",
        "repo": repo_name,
        "pr_number": pr_number,
        "diff_size": len(diff),
        "comments": comment_summary,
    }


def parse_json_body(raw_body: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON") from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Request body must be a JSON object")

    return payload


def verify_github_signature(raw_body: bytes, signature_header: str | None) -> None:
    secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    if not secret:
        return

    if not signature_header:
        raise HTTPException(status_code=401, detail="Missing GitHub webhook signature")

    expected_signature = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=401, detail="Invalid GitHub webhook signature")


def extract_pull_request_context(payload: dict[str, Any]) -> tuple[str, int]:
    repository = payload.get("repository") or payload.get("repo")
    pull_request = payload.get("pull_request") or {}

    repo_name = None
    if isinstance(repository, dict):
        repo_name = repository.get("full_name") or repository.get("name")
    elif isinstance(repository, str):
        repo_name = repository

    repo_name = repo_name or payload.get("repo_name")
    pr_number = (
        pull_request.get("number")
        or payload.get("pr_number")
        or payload.get("pull_request_number")
        or payload.get("number")
    )

    if not repo_name:
        raise HTTPException(status_code=400, detail="Missing repository full name")

    if not pr_number:
        raise HTTPException(status_code=400, detail="Missing pull request number")

    try:
        return repo_name, int(pr_number)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Pull request number must be an integer") from exc


def get_github_token() -> str:
    token = os.getenv("GIT_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="Missing GIT_TOKEN or GITHUB_TOKEN")
    return token


def fetch_pull_request_diff(repo_name: str, pr_number: int, token: str | None = None) -> str:
    token = token or get_github_token()
    url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"
    headers = {
        "Accept": "application/vnd.github.v3.diff",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Could not fetch PR diff: {exc}") from exc

    return response.text


def run_review_agent(diff: str) -> dict[str, Any]:
    try:
        from agent.graph import build_graph
    except ImportError as exc:
        raise HTTPException(status_code=500, detail=f"Could not import review graph: {exc}") from exc

    graph = build_graph()
    if graph is None or not hasattr(graph, "invoke"):
        raise HTTPException(status_code=501, detail="Review graph is not implemented yet")

    result = graph.invoke({"diff": diff, "findings": []})
    if not isinstance(result, dict):
        raise HTTPException(status_code=500, detail="Review graph must return a JSON object")

    return result


def post_inline_comments(
    repo_name: str,
    pr_number: int,
    agent_output: dict[str, Any] | list[dict[str, Any]],
    token: str | None = None,
) -> dict[str, Any]:
    token = token or get_github_token()
    findings = normalize_findings(agent_output)
    github = Github(token)

    try:
        repo = github.get_repo(repo_name)
        pull_request = repo.get_pull(pr_number)
    except GithubException as exc:
        raise HTTPException(status_code=502, detail=f"Could not load pull request: {exc.data}") from exc

    posted = 0
    skipped = 0
    errors: list[dict[str, Any]] = []

    for finding in findings:
        severity = str(finding.get("severity", "")).upper()
        if severity not in COMMENTABLE_SEVERITIES:
            skipped += 1
            continue

        path = finding.get("path") or finding.get("file") or finding.get("filename")
        line = finding.get("line") or finding.get("line_number") or finding.get("end_line")
        if not path or line is None:
            skipped += 1
            errors.append(
                {
                    "reason": "missing path or line",
                    "finding": finding,
                }
            )
            continue

        try:
            comment_kwargs = {
                "body": format_review_comment(finding),
                "commit": pull_request.head.sha,
                "path": str(path),
                "line": int(line),
                "side": str(finding.get("side") or "RIGHT").upper(),
            }

            start_line = finding.get("start_line")
            if start_line is not None:
                comment_kwargs["start_line"] = int(start_line)
                comment_kwargs["start_side"] = str(
                    finding.get("start_side") or comment_kwargs["side"]
                ).upper()

            pull_request.create_review_comment(**comment_kwargs)
            posted += 1
        except GithubException as exc:
            skipped += 1
            errors.append(
                {
                    "reason": "github rejected inline comment",
                    "path": str(path),
                    "line": line,
                    "details": exc.data,
                }
            )
        except (TypeError, ValueError) as exc:
            skipped += 1
            errors.append(
                {
                    "reason": "invalid inline comment fields",
                    "path": str(path),
                    "line": line,
                    "details": str(exc),
                }
            )

    return {
        "posted": posted,
        "skipped": skipped,
        "total_findings": len(findings),
        "errors": errors,
    }


def normalize_findings(agent_output: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(agent_output, list):
        return [finding for finding in agent_output if isinstance(finding, dict)]

    if not isinstance(agent_output, dict):
        return []

    if isinstance(agent_output.get("findings"), list):
        return [finding for finding in agent_output["findings"] if isinstance(finding, dict)]

    findings: list[dict[str, Any]] = []
    for key in (
        "bug_findings",
        "security_findings",
        "quality_findings",
        "bugs",
        "security",
        "quality",
        "results",
    ):
        value = agent_output.get(key)
        if isinstance(value, list):
            findings.extend(finding for finding in value if isinstance(finding, dict))

    return findings


def format_review_comment(finding: dict[str, Any]) -> str:
    severity = str(finding.get("severity", "INFO")).upper()
    category = finding.get("category") or finding.get("type") or "Review finding"
    message = (
        finding.get("message")
        or finding.get("comment")
        or finding.get("description")
        or finding.get("body")
        or "The review agent flagged this line."
    )
    suggestion = finding.get("suggestion") or finding.get("recommendation")

    body = f"**{severity} - {category}**\n\n{message}"
    if suggestion:
        body += f"\n\nSuggestion: {suggestion}"

    return body
