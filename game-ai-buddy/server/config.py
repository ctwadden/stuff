import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"config.json not found at {CONFIG_PATH}")
    with open(CONFIG_PATH) as f:
        return json.load(f)

def get_ai_config() -> dict:
    return load_config()["ai"]

def get_server_config() -> dict:
    return load_config()["server"]

def get_features() -> dict:
    return load_config()["features"]

def is_gemini_configured() -> bool:
    key = get_ai_config().get("gemini_api_key", "")
    return key and key != "PASTE_YOUR_GEMINI_KEY_HERE"
