"""
AI Client - supports Gemini (free API) and Ollama (local/free).
Add your Gemini API key to config.json to use Gemini.
Run Ollama locally (ollama.com) to use it for free with no key.
"""
import base64
import httpx
from pathlib import Path
from config import get_ai_config, is_gemini_configured

# App-specific system prompts so the AI knows what tools/API it's talking to
SYSTEM_PROMPTS = {
    "blender": """You are an expert Blender 4.x Python assistant.
When the user asks you to do something in Blender, respond with working bpy Python code.
Always wrap executable code in a ```python block.
Use bpy.ops, bpy.data, and bpy.context correctly.
After the code, briefly explain what it does.
If you see a screenshot, describe what you see in Blender before responding.""",

    "unity": """You are an expert Unity C# Editor scripting assistant.
When the user asks you to do something in Unity, respond with working C# Editor code.
Always wrap executable code in a ```csharp block.
Use UnityEditor, UnityEngine namespaces correctly.
For terrain tasks use Terrain, TerrainData APIs.
For asset placement use GameObject, PrefabUtility APIs.
After the code, briefly explain what it does.""",

    "unreal": """You are an expert Unreal Engine 5 Python scripting assistant.
When the user asks you to do something in Unreal, respond with working Python code using the unreal module.
Always wrap executable code in a ```python block.
Use unreal.EditorLevelLibrary, unreal.EditorAssetLibrary, unreal.LandscapeEditorObject correctly.
For PCG tasks use unreal.PCGComponent and unreal.PCGGraph APIs.
For asset swapping use unreal.EditorLevelLibrary.get_all_level_actors().
After the code, briefly explain what it does.""",

    "general": """You are a game development AI assistant that supports Blender, Unity, and Unreal Engine 5.
Help the user with their game development tasks. If they ask for code, provide working code examples.
If you see a screenshot, describe what you observe before answering.""",
}

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

async def ask_gemini(prompt: str, app: str, image_path: str | None = None) -> str:
    cfg = get_ai_config()
    api_key = cfg["gemini_api_key"]
    model = cfg.get("gemini_model", "gemini-1.5-flash")
    system = SYSTEM_PROMPTS.get(app, SYSTEM_PROMPTS["general"])
    full_prompt = f"{system}\n\nUser: {prompt}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    parts = []

    if image_path and Path(image_path).exists():
        img_data = encode_image(image_path)
        parts.append({"inline_data": {"mime_type": "image/png", "data": img_data}})

    parts.append({"text": full_prompt})

    payload = {"contents": [{"parts": parts}]}

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

async def ask_ollama(prompt: str, app: str, image_path: str | None = None) -> str:
    cfg = get_ai_config()
    base_url = cfg.get("ollama_url", "http://localhost:11434")
    model = cfg.get("ollama_model", "llava")
    system = SYSTEM_PROMPTS.get(app, SYSTEM_PROMPTS["general"])

    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
    }

    if image_path and Path(image_path).exists():
        payload["images"] = [encode_image(image_path)]

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(f"{base_url}/api/generate", json=payload)
        resp.raise_for_status()
        return resp.json()["response"]

async def ask(prompt: str, app: str = "general", image_path: str | None = None) -> str:
    cfg = get_ai_config()
    provider = cfg.get("provider", "gemini")

    if provider == "gemini":
        if not is_gemini_configured():
            return (
                "Gemini API key not set. Open config.json and paste your key into "
                "'gemini_api_key'. Get a free key at aistudio.google.com\n\n"
                "Alternatively set provider to 'ollama' in config.json and run Ollama locally."
            )
        return await ask_gemini(prompt, app, image_path)
    elif provider == "ollama":
        return await ask_ollama(prompt, app, image_path)
    else:
        return f"Unknown provider '{provider}'. Set to 'gemini' or 'ollama' in config.json."
