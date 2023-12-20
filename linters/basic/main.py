import os
import re

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

request_count = 0

language = os.getenv("LANGUAGE")
version = "1.0"

pattern = r"\S=|=\S"
success_message = "The code is linted properly."
failure_message = "Linting detected issues in the code."


class LintRequest(BaseModel):
    code: str


@app.post("/lint")
async def lint(request: LintRequest):
    global request_count
    request_count += 1
    lint_result = re.search(pattern, request.code) is None
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
