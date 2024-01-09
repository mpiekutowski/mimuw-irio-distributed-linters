import os
import re

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

request_count = 0

language = os.getenv("LANGUAGE")
version = "2.0"

pattern = r"\S=|=\S"
success_message = "The code is linted properly."
failure_message = "Linting detected issues in the code."


class LintRequest(BaseModel):
    code: str


@app.post("/lint")
async def lint(request: LintRequest):
    global request_count
    request_count += 1

    has_linted_assignments = re.search(pattern, request.code) is None
    has_empty_last_line = request.code == "" or request.code.endswith("\n")
    lint_result = has_linted_assignments and has_empty_last_line

    return {
        "result": lint_result,
        "details": success_message if lint_result else failure_message
    }


@app.get("/health")
async def health():
    return {
        "version": version,
        "language": language,
        "requestCount": request_count
    }
