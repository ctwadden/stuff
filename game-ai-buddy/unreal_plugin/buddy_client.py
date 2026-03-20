"""
HTTP client for Unreal Engine to communicate with the Game AI Buddy server.
Uses Python's urllib (built-in, no pip needed inside Unreal's Python env).
"""
import urllib.request
import urllib.error
import json

SERVER_URL = "http://127.0.0.1:8765"

def ask(prompt: str, include_screenshot: bool = False) -> dict:
    """
    Send a prompt to the buddy server and return the response dict.
    Raises ConnectionError if server is not running.
    """
    payload = json.dumps({
        "prompt": prompt,
        "app": "unreal",
        "include_screenshot": include_screenshot,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{SERVER_URL}/ask",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as e:
        raise ConnectionError(
            f"Cannot reach Game AI Buddy server at {SERVER_URL}.\n"
            f"Start it with: python server/main.py\nDetails: {e}"
        )

def check_online() -> bool:
    try:
        with urllib.request.urlopen(f"{SERVER_URL}/status", timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False

def extract_python_code(reply: str) -> str | None:
    """Extract the first ```python code block from the AI reply."""
    import re
    match = re.search(r"```python\s*([\s\S]*?)```", reply)
    return match.group(1).strip() if match else None
