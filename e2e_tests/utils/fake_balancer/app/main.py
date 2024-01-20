from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

class AddRequest(BaseModel):
    lang: str
    version: str
    uri: str
    secretKey: str

@app.post("/add")
async def add(request: AddRequest):
    return "Addition completed"

class RemoveRequest(BaseModel):
    uri: str
    secretKey: str

@app.post("/remove")
async def remove(request: RemoveRequest):
    return "Removal completed"


class UpdateRatioRequest(BaseModel):
    lang: str
    versionRatio: Dict[str, int]
    secretKey: str

@app.post("/ratio")
async def remove(request: UpdateRatioRequest):
    return "Ratio updated"
