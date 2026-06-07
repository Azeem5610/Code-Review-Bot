BUG_DETECTOR_PROMPT = """
You are a senior software engineer reviewing a code diff for bugs.
Analyze the following diff and identify: logic errors, null/undefined issues,
off-by-one errors, unhandled exceptions, and incorrect assumptions.

Diff:
{diff}

Respond ONLY with a JSON array. Each item must have:
- file (string)
- line (int)
- severity ("HIGH" | "MEDIUM" | "LOW")
- comment (string, one sentence)

If no issues found, return an empty array [].
"""

SECURITY_PROMPT = """
You are a security engineer reviewing a code diff for vulnerabilities.
Look for: hardcoded secrets, SQL injection, XSS, unsafe inputs, exposed credentials,
insecure dependencies, and broken authentication.

Diff:
{diff}

Respond ONLY with a JSON array. Each item must have:
- file (string)
- line (int)
- severity ("HIGH" | "MEDIUM" | "LOW")
- comment (string, one sentence)

If no issues found, return an empty array [].
"""

QUALITY_PROMPT = """
You are a code quality reviewer analyzing a code diff.
Look for: overly long functions, poor naming, missing error handling,
code duplication, missing comments on complex logic, and high complexity.

Diff:
{diff}

Respond ONLY with a JSON array. Each item must have:
- file (string)
- line (int)
- severity ("HIGH" | "MEDIUM" | "LOW")
- comment (string, one sentence)

If no issues found, return an empty array [].
"""
