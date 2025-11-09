"""FastAPI wrapper exposing vLLM for Paligemma."""

import asyncio

from fastapi import FastAPI
from pydantic import BaseModel

from src.inference.model_loader import get_model

app = FastAPI(title="Paligemma vLLM Server")


class CompletionRequest(BaseModel):
    prompt: str


class CompletionResponse(BaseModel):
    text: str


class VisionCompletionRequest(BaseModel):
    payload: dict
    image_base64: str


@app.post("/completions", response_model=CompletionResponse)
async def completions(request: CompletionRequest) -> CompletionResponse:
    loop = asyncio.get_running_loop()
    model = get_model()
    text = await loop.run_in_executor(None, model.generate, request.prompt)
    return CompletionResponse(text=text)


@app.post("/vision/completions")
async def vision_completions(request: VisionCompletionRequest):
    # Real implementation would feed multimodal content to Paligemma. Placeholder returns structured mock.
    return {
        "choices": [
            {
                "message": {
                    "content": "{\"asset_name\": \"Placeholder Pump\", \"service\": \"Mock\"}"
                }
            }
        ]
    }
