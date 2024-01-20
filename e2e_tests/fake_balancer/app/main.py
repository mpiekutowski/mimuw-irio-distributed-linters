from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

class AddRequest(BaseModel):
    lang: str
    version: str
    uri: str

@app.post("/add")
async def add(request: AddRequest):
    return "Addition completed"

class RemoveRequest(BaseModel):
    uri: str

@app.post("/remove")
async def remove(request: RemoveRequest):
    return "Removal completed"


class UpdateRatioRequest(BaseModel):
    lang: str
    versionRatio: Dict[str, int]

@app.post("/ratio")
async def remove(request: UpdateRatioRequest):
    return "Ratio updated"
