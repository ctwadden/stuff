"""
Game AI Buddy - Local Server
Handles AI requests from Blender, Unity, and Unreal Engine plugins.

Run with: uvicorn main:app --host 127.0.0.1 --port 8765 --reload
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from ai_client import ask
from screen_capture import capture_screen, load_image_from_bytes
from config import load_config, is_gemini_configured, get_ai_config

app = FastAPI(title="Game AI Buddy Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    prompt: str
    app: str = "general"          # "blender" | "unity" | "unreal" | "general"
    include_screenshot: bool = False

class AskResponse(BaseModel):
    reply: str
    provider: str
    had_screenshot: bool

@app.get("/")
def root():
    cfg = get_ai_config()
    return {
        "status": "running",
        "provider": cfg.get("provider"),
        "gemini_ready": is_gemini_configured(),
        "message": "Game AI Buddy is online. Send requests from your plugin.",
    }

@app.get("/status")
def status():
    cfg = get_ai_config()
    return {
        "online": True,
        "provider": cfg.get("provider", "gemini"),
        "gemini_configured": is_gemini_configured(),
        "model": cfg.get("gemini_model") if cfg.get("provider") == "gemini" else cfg.get("ollama_model"),
    }

@app.post("/ask", response_model=AskResponse)
async def ask_endpoint(req: AskRequest):
    """Main endpoint for Blender, Unity, and Unreal plugins to send prompts."""
    image_path = None
    had_screenshot = False

    if req.include_screenshot:
        image_path = capture_screen()
        had_screenshot = image_path is not None

    reply = await ask(req.prompt, req.app, image_path)
    provider = get_ai_config().get("provider", "gemini")
    return AskResponse(reply=reply, provider=provider, had_screenshot=had_screenshot)

@app.post("/ask-with-image", response_model=AskResponse)
async def ask_with_image(
    prompt: str = Form(...),
    app: str = Form("general"),
    image: Optional[UploadFile] = File(None),
):
    """Endpoint for plugins that send their own viewport image (e.g. Blender render)."""
    image_path = None
    had_screenshot = False

    if image:
        data = await image.read()
        image_path = load_image_from_bytes(data)
        had_screenshot = True

    reply = await ask(prompt, app, image_path)
    provider = get_ai_config().get("provider", "gemini")
    return AskResponse(reply=reply, provider=provider, had_screenshot=had_screenshot)

@app.post("/screenshot")
def take_screenshot():
    """Take a screenshot and return the path (for debugging)."""
    path = capture_screen()
    return {"path": path, "success": path is not None}

if __name__ == "__main__":
    cfg = load_config()
    host = cfg["server"]["host"]
    port = cfg["server"]["port"]
    print(f"\n Game AI Buddy Server starting on http://{host}:{port}")
    print(f" Provider: {cfg['ai']['provider']}")
    print(f" Gemini ready: {is_gemini_configured()}")
    print(f" Open config.json to set your Gemini API key or switch to Ollama\n")
    uvicorn.run("main:app", host=host, port=port, reload=True)
