"""
AI Client - supports Gemini (free API) and Ollama (local/free).
Supports two modes: 'do' (generates + executes code) and 'teach' (step-by-step learning).
Vision: pass an image_path to send a screenshot to the AI.
"""
import base64
import httpx
from pathlib import Path
from config import get_ai_config, is_gemini_configured

# -----------------------------------------------------------------------
#  System prompts per app per mode
# -----------------------------------------------------------------------

DO_PROMPTS = {
    "blender": """You are an expert Blender 4.x Python assistant embedded in the user's Blender sidebar.
Your job: generate working bpy Python code that accomplishes exactly what the user asks.

Rules:
- Always wrap executable code in a single ```python block.
- Use bpy.ops, bpy.data, bpy.context correctly for Blender 4.x.
- After the code block, write 2-3 sentences explaining what it does.
- If you see a screenshot, describe what you observe in Blender (viewport contents, selected objects, mode) before responding.
- For asset creation: use procedural geometry with modifiers (Subdivision, Displace, Solidify, etc).
- Never use external libraries not available in Blender's Python environment.""",

    "blender_teach": """You are a friendly Blender 4.x tutor embedded in the user's sidebar.
The user wants to LEARN how to do something, not just have it done for them.

Rules:
- Start by briefly explaining the concept/tool they're asking about (2-3 sentences).
- Then give numbered steps (Step 1, Step 2, etc.) — each step on its own line.
- Include keyboard shortcuts in brackets like [Tab], [G], [Ctrl+R].
- Include where to find things: "In the Properties panel > Material tab" or "Top menu > Object > Apply".
- After the steps, add a "Pro Tip:" with a useful shortcut or technique.
- If you see a screenshot, say "I can see your screen: ..." and tailor the steps to what's visible.
- At the end, add: "Stuck? Type 'do step X for me' and I'll execute it."
- Keep each step short (one action per step).""",

    "unity": """You are an expert Unity 2022+ C# Editor scripting assistant.
Your job: generate working C# code that accomplishes exactly what the user asks.

Rules:
- Always wrap executable code in a ```csharp block.
- Use UnityEditor and UnityEngine APIs correctly.
- For terrain: use Terrain, TerrainData, TerrainLayer APIs.
- For scatter/placement: use GameObject, PrefabUtility, Physics.Raycast.
- After the code, explain what it does in 2-3 sentences.
- If you see a screenshot, describe the Unity Editor state before responding.""",

    "unity_teach": """You are a friendly Unity tutor embedded in the Unity Editor.
The user wants to LEARN Unity, not just have things done for them.

Rules:
- Start with a brief concept explanation (2-3 sentences).
- Give numbered steps with exact menu paths: Edit > Project Settings > Physics.
- Include keyboard shortcuts like [Ctrl+D] to duplicate, [F] to frame selection.
- Mention which window/panel to look in for each step.
- Add a "Pro Tip:" at the end.
- If you see a screenshot, reference what's visible on screen.
- End with: "Stuck? Type 'do step X for me' and I'll generate the code.".""",

    "unreal": """You are an expert Unreal Engine 5 Python scripting assistant.
Your job: generate working Python code using the unreal module.

Rules:
- Always wrap executable code in a single ```python block.
- Use unreal.EditorLevelLibrary, unreal.EditorAssetLibrary, unreal.ScopedEditorTransaction.
- For PCG: use unreal.PCGComponent, PCG graph APIs.
- For landscape: use unreal.LandscapeEditorObject and landscape actor APIs.
- After the code, explain what it does in 2-3 sentences.
- If you see a screenshot, describe the Unreal Editor state before responding.""",

    "unreal_teach": """You are a friendly Unreal Engine 5 tutor embedded in the editor.
The user wants to LEARN UE5, not just have things done for them.

Rules:
- Explain the concept briefly first (2-3 sentences).
- Give numbered steps with exact menu paths: Window > World Settings > Lightmass.
- Note which panel/tab to look in.
- Include UE5 keyboard shortcuts like [G] to toggle game view, [F] to frame.
- Add a "Pro Tip:" about the feature.
- If you see a screenshot, reference what's visible.
- End with: "Stuck? Type 'do step X for me' and I'll generate the Python code.".""",

    "general": """You are a game development AI assistant supporting Blender, Unity, and Unreal Engine 5.
Help with any game dev task. Provide working code examples when relevant.
If you see a screenshot, describe what you observe before answering.""",
}

# -----------------------------------------------------------------------
#  Asset generation prompts for Blender
# -----------------------------------------------------------------------

ASSET_PROMPTS = {
    "rock": "Create a realistic procedural rock/boulder in Blender using bpy. Use a subdivided icosphere, add Displace modifier with cloud texture, Decimate modifier for low-poly feel, and apply a stone-like material with roughness 0.9.",
    "tree": "Create a low-poly stylized tree in Blender using bpy. Make a tapered cylinder trunk with bark texture, add 3 overlapping spheres for canopy scaled and positioned naturally, merge into one object, apply tree bark material to trunk and leaf green to canopy.",
    "sword": "Create a fantasy sword in Blender using bpy. Build from primitives: flat elongated box for blade with slight taper, smaller box for crossguard, cylinder for grip. Bevel edges, apply silver metallic material to blade, dark leather to grip.",
    "building": "Create a modular medieval building in Blender using bpy. Build a box base, extrude windows as indents, add a pitched roof using a scaled+positioned pyramid mesh. Add stone wall material with normal map roughness.",
    "character_base": "Create a low-poly humanoid character base mesh in Blender using bpy. Use box modeling: body cube, head cube scaled up, arm cylinders, leg cylinders, hand and foot boxes. Apply a base skin material. This will be used as a starting point for character sculpting.",
    "mountain": "Create a procedural mountain terrain chunk in Blender using bpy. Start with a highly subdivided plane (100x100), use vertex displacement via noise to create mountain shape, add cliff details. Apply a rock/terrain material.",
    "chest": "Create a treasure chest in Blender using bpy. Box base with slightly rounded top lid, metal hinge strips, lock plate on front, corner reinforcement strips. Apply wood material to body, metallic material to fittings.",
    "crystal": "Create a magical crystal cluster in Blender using bpy. Array of elongated hexagonal prisms at varied angles and scales, use Solidify and Bevel modifiers. Apply emission material with subsurface scattering in blue/purple.",
}

# -----------------------------------------------------------------------
#  Core functions
# -----------------------------------------------------------------------

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def get_system_prompt(app: str, mode: str) -> str:
    if mode == "teach":
        key = f"{app}_teach"
        return DO_PROMPTS.get(key, DO_PROMPTS["general"])
    return DO_PROMPTS.get(app, DO_PROMPTS["general"])

async def ask_gemini(prompt: str, app: str, mode: str = "do", image_path: str | None = None) -> str:
    cfg = get_ai_config()
    api_key = cfg["gemini_api_key"]
    model = cfg.get("gemini_model", "gemini-1.5-flash")
    system = get_system_prompt(app, mode)
    full_prompt = f"{system}\n\nUser: {prompt}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    parts = []

    if image_path and Path(image_path).exists():
        img_data = encode_image(image_path)
        # Detect actual image type
        mime = "image/png"
        if image_path.lower().endswith(".jpg") or image_path.lower().endswith(".jpeg"):
            mime = "image/jpeg"
        parts.append({"inline_data": {"mime_type": mime, "data": img_data}})

    parts.append({"text": full_prompt})
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 4096,
        },
    }

    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(url, json=payload)
        if resp.status_code != 200:
            body = resp.json()
            err = body.get("error", {}).get("message", resp.text)
            raise ValueError(f"Gemini API error {resp.status_code}: {err}")
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

async def ask_ollama(prompt: str, app: str, mode: str = "do", image_path: str | None = None) -> str:
    cfg = get_ai_config()
    base_url = cfg.get("ollama_url", "http://localhost:11434")
    model = cfg.get("ollama_model", "llava")
    system = get_system_prompt(app, mode)

    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 4096},
    }

    if image_path and Path(image_path).exists():
        payload["images"] = [encode_image(image_path)]

    async with httpx.AsyncClient(timeout=180) as client:
        resp = await client.post(f"{base_url}/api/generate", json=payload)
        resp.raise_for_status()
        return resp.json()["response"]

async def ask(prompt: str, app: str = "general", mode: str = "do", image_path: str | None = None) -> str:
    """
    Main entry point.
    app:  'blender' | 'unity' | 'unreal' | 'general'
    mode: 'do' (generate+execute code) | 'teach' (step-by-step learning)
    image_path: path to screenshot file (None = no vision)
    """
    cfg = get_ai_config()
    provider = cfg.get("provider", "gemini")

    if provider == "gemini":
        if not is_gemini_configured():
            return (
                "Gemini API key not set.\n\n"
                "1. Go to aistudio.google.com\n"
                "2. Sign in with Google\n"
                "3. Click 'Get API Key'\n"
                "4. Open config.json and paste it into 'gemini_api_key'\n\n"
                "Or set provider to 'ollama' in config.json and run Ollama locally (free, no key needed)."
            )
        return await ask_gemini(prompt, app, mode, image_path)
    elif provider == "ollama":
        return await ask_ollama(prompt, app, mode, image_path)
    else:
        return f"Unknown provider '{provider}'. Set to 'gemini' or 'ollama' in config.json."

def get_asset_prompt(asset_type: str) -> str:
    return ASSET_PROMPTS.get(asset_type, f"Create a {asset_type} 3D asset in Blender using bpy Python.")
