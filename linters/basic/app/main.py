from fastapi import FastAPI
from pydantic import BaseModel

import re

app = FastAPI()

request_count = 0
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
    return {"message": success_message if lint_result else failure_message}


@app.get("/health")
async def health():
    return {"version": version, "requestCount": request_count}
