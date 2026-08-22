# Code Review Pipeline

An AI-powered automated code review system that analyzes GitHub Pull Requests and provides structured feedback on bugs, security issues, and code quality.

## Overview

The pipeline integrates with GitHub to automatically process Pull Requests, analyze the code changes using an LLM, and post the review results directly back to the Pull Request.

It uses LangGraph to organize the review process into specialized analysis nodes and combines their findings into a final structured review.

## How It Works

```text
GitHub Pull Request
        ↓
    Get Code Diff
        ↓
┌───────────────────────────────┐
│       Review Pipeline         │
├───────────────────────────────┤
│  Bug Detection                │
│  Security Analysis            │
│  Code Quality Analysis        │
└───────────────────────────────┘
        ↓
   Result Aggregation
        ↓
  Structured Review
        ↓
GitHub Pull Request Comment
```

## Key Features

* **GitHub Pull Request Integration** — automatically receives and processes Pull Request code changes.
* **Automated Code Review** — analyzes code changes without manual intervention.
* **Bug Detection** — identifies potential bugs and logical issues.
* **Security Analysis** — detects potential security vulnerabilities and unsafe practices.
* **Code Quality Analysis** — evaluates readability, maintainability, and code structure.
* **AI-Powered Analysis** — uses an LLM to analyze the submitted code.
* **Result Aggregation** — combines findings from different review stages into a structured result.
* **Automatic GitHub Comments** — posts the generated review directly to the Pull Request.
* **LangGraph Workflow** — manages the review process using states, nodes, and a graph-based workflow.

## Architecture

The pipeline is built using LangGraph with specialized nodes for different review tasks:

```text
                    ┌── Bug Detector ──┐
                    │                  │
GitHub PR → Diff ───┼── Security ──────┼→ Aggregator → GitHub Comment
                    │                  │
                    └── Quality ───────┘
```

### Core Components

* **State** — stores the Pull Request diff and review results throughout the workflow.
* **Nodes** — perform individual tasks such as bug detection, security analysis, quality analysis, and result aggregation.
* **Graph** — controls the execution flow between the review nodes.

## Tech Stack

* Python
* LangGraph
* LLM / OpenRouter
* FastAPI
* GitHub API
* GitHub Webhooks
* TypedDict

## Setup

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and configure the required credentials:

```env
OPENROUTER_API_KEY=your_api_key
GITHUB_TOKEN=your_github_token
```

Configure the GitHub webhook according to the project's webhook settings and start the application using the project's entry point.

> **Note:** Never commit your `.env` file or expose API keys in the repository.

## Project Goal

The goal of this project is to demonstrate how **LLMs, LangGraph, GitHub APIs, and automated workflows** can be combined to build a practical AI-powered code review system that works directly within the software development workflow.
