"""
Game AI Buddy - Local Server
Serves all three app plugins: Blender, Unity, Unreal Engine.
Run: python main.py  (or double-click start_server.bat / start_server.sh)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal
import uvicorn

from ai_client import ask, get_asset_prompt
from screen_capture import capture_screen, load_image_from_bytes
from config import load_config, is_gemini_configured, get_ai_config

app = FastAPI(title="Game AI Buddy Server", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------
#  Models
# -----------------------------------------------------------------------

class AskRequest(BaseModel):
    prompt: str
    app: str = "general"
    mode: Literal["do", "teach"] = "do"
    include_screenshot: bool = False

class AskResponse(BaseModel):
    reply: str
    provider: str
    had_screenshot: bool
    mode: str

class AssetRequest(BaseModel):
    asset_type: str          # rock | tree | sword | building | character_base | mountain | chest | crystal
    custom_prompt: Optional[str] = None   # override or extend the preset prompt

# -----------------------------------------------------------------------
#  Routes
# -----------------------------------------------------------------------

@app.get("/")
def root():
    cfg = get_ai_config()
    return {
        "status": "running",
        "version": "2.0",
        "provider": cfg.get("provider"),
        "gemini_ready": is_gemini_configured(),
        "endpoints": ["/ask", "/ask-with-image", "/generate-asset", "/screenshot", "/status"],
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
    """
    Main endpoint for Blender, Unity, Unreal plugins.
    mode='do'    → AI generates and explains code.
    mode='teach' → AI gives step-by-step tutorial.
    """
    image_path = None
    had_screenshot = False

    if req.include_screenshot:
        image_path = capture_screen()
        had_screenshot = image_path is not None

    reply = await ask(req.prompt, req.app, req.mode, image_path)
    provider = get_ai_config().get("provider", "gemini")
    return AskResponse(reply=reply, provider=provider, had_screenshot=had_screenshot, mode=req.mode)

@app.post("/ask-with-image", response_model=AskResponse)
async def ask_with_image(
    prompt: str = Form(...),
    app: str = Form("general"),
    mode: str = Form("do"),
    image: Optional[UploadFile] = File(None),
):
    """
    Plugins that capture their own viewport (e.g. Blender render) send the image here.
    """
    image_path = None
    had_screenshot = False

    if image:
        data = await image.read()
        image_path = load_image_from_bytes(data)
        had_screenshot = True

    reply = await ask(prompt, app, mode, image_path)
    provider = get_ai_config().get("provider", "gemini")
    return AskResponse(reply=reply, provider=provider, had_screenshot=had_screenshot, mode=mode)

@app.post("/generate-asset", response_model=AskResponse)
async def generate_asset(req: AssetRequest):
    """
    Blender asset generation endpoint.
    Sends a curated prompt to generate a specific 3D asset type.
    """
    base_prompt = get_asset_prompt(req.asset_type)
    prompt = req.custom_prompt if req.custom_prompt else base_prompt
    if req.custom_prompt and req.asset_type in ["rock", "tree", "sword", "building", "character_base", "mountain", "chest", "crystal"]:
        # combine preset context with user customisation
        prompt = f"{base_prompt}\n\nAdditional requirements: {req.custom_prompt}"

    reply = await ask(prompt, "blender", "do", None)
    provider = get_ai_config().get("provider", "gemini")
    return AskResponse(reply=reply, provider=provider, had_screenshot=False, mode="do")

@app.post("/screenshot")
def take_screenshot():
    """Capture a screenshot (for debugging the vision pipeline)."""
    path = capture_screen()
    return {"path": path, "success": path is not None}

if __name__ == "__main__":
    cfg = load_config()
    host = cfg["server"]["host"]
    port = cfg["server"]["port"]
    print(f"\n  Game AI Buddy Server v2.0")
    print(f"  http://{host}:{port}")
    print(f"  Provider : {cfg['ai']['provider']}")
    print(f"  Gemini   : {'Ready' if is_gemini_configured() else 'KEY NOT SET - edit config.json'}")
    print(f"  Modes    : do (generate code) | teach (step-by-step)\n")
    uvicorn.run("main:app", host=host, port=port, reload=True)
