"""
Screen capture utility.
Multiple backends: PIL/mss (fast), pyautogui (fallback).
Saves to a temp file so the AI vision model can read it.
"""
import os
import tempfile
from pathlib import Path

SCREENSHOT_PATH = Path(tempfile.gettempdir()) / "game_buddy_screenshot.png"

def capture_screen() -> str | None:
    """Capture the full screen. Returns file path or None on failure."""
    # Try mss first (fastest, no display issues)
    try:
        import mss
        import mss.tools
        with mss.mss() as sct:
            monitor = sct.monitors[0]  # all monitors combined
            img = sct.grab(monitor)
            mss.tools.to_png(img.rgb, img.size, output=str(SCREENSHOT_PATH))
        return str(SCREENSHOT_PATH)
    except Exception:
        pass

    # Fallback: PIL ImageGrab
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        img.save(str(SCREENSHOT_PATH), "PNG")
        return str(SCREENSHOT_PATH)
    except Exception:
        pass

    # Fallback: pyautogui
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        screenshot.save(str(SCREENSHOT_PATH))
        return str(SCREENSHOT_PATH)
    except Exception as e:
        print(f"[BuddyServer] All screenshot methods failed: {e}")
        return None

def capture_region(x: int, y: int, width: int, height: int) -> str | None:
    """Capture a specific screen region."""
    try:
        import mss
        import mss.tools
        with mss.mss() as sct:
            region = {"top": y, "left": x, "width": width, "height": height}
            img = sct.grab(region)
            mss.tools.to_png(img.rgb, img.size, output=str(SCREENSHOT_PATH))
        return str(SCREENSHOT_PATH)
    except Exception:
        pass
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        img.save(str(SCREENSHOT_PATH), "PNG")
        return str(SCREENSHOT_PATH)
    except Exception as e:
        print(f"[BuddyServer] Region screenshot failed: {e}")
        return None

def load_image_from_bytes(data: bytes) -> str:
    """Save raw image bytes sent from a plugin (e.g. Blender viewport render)."""
    SCREENSHOT_PATH.write_bytes(data)
    return str(SCREENSHOT_PATH)
