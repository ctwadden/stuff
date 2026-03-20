"""
Screen capture utility.
Takes a screenshot and saves it to a temp file for sending to the AI vision model.
"""
import os
import tempfile
from pathlib import Path

SCREENSHOT_PATH = Path(tempfile.gettempdir()) / "game_buddy_screenshot.png"

def capture_screen() -> str | None:
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        screenshot.save(str(SCREENSHOT_PATH))
        return str(SCREENSHOT_PATH)
    except Exception as e:
        print(f"[BuddyServer] Screenshot failed: {e}")
        return None

def capture_region(x: int, y: int, width: int, height: int) -> str | None:
    try:
        import pyautogui
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot.save(str(SCREENSHOT_PATH))
        return str(SCREENSHOT_PATH)
    except Exception as e:
        print(f"[BuddyServer] Region screenshot failed: {e}")
        return None

def load_image_from_bytes(data: bytes) -> str:
    """Save image bytes sent from a plugin (e.g. Blender viewport render)."""
    SCREENSHOT_PATH.write_bytes(data)
    return str(SCREENSHOT_PATH)
