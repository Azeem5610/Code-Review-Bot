# TODO: Ask Codex to implement the FastAPI server
# Prompt: "Write server/main.py — a FastAPI app with a POST /review endpoint.
# It receives repo name, pr_number, and token. Use PyGithub to fetch the PR diff.
# Pass the diff to the LangGraph agent from agent/graph.py. Then loop through
# aggregated findings and post each as an inline GitHub PR review comment using
# PyGithub's create_review_comment(). Only post HIGH and MEDIUM severity."

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/review")
async def review(payload: dict):
    pass
