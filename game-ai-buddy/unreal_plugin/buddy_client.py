"""
HTTP client for Unreal Engine → Game AI Buddy server.
Supports do/teach modes and screenshot (vision).
"""
import urllib.request
import urllib.error
import json
import re

SERVER_URL = "http://127.0.0.1:8765"

def ask(prompt: str, include_screenshot: bool = False, mode: str = "do") -> dict:
    """
    Send prompt to buddy server.
    mode: 'do' (code generation) | 'teach' (step-by-step tutorial)
    Returns the full response dict: {reply, provider, had_screenshot, mode}
    """
    payload = json.dumps({
        "prompt": prompt,
        "app": "unreal",
        "mode": mode,
        "include_screenshot": include_screenshot,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{SERVER_URL}/ask",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as e:
        raise ConnectionError(
            f"Cannot reach Game AI Buddy server at {SERVER_URL}.\n"
            f"Start it with: start_server.bat (Windows) or bash start_server.sh (Mac/Linux)\n"
            f"Details: {e}"
        )

def check_online() -> bool:
    try:
        with urllib.request.urlopen(f"{SERVER_URL}/status", timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False

def extract_python_code(reply: str) -> str | None:
    match = re.search(r"```python\s*([\s\S]*?)```", reply)
    return match.group(1).strip() if match else None
