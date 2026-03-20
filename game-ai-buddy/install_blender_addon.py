"""
Run this script to automatically zip the Blender addon and install it.
Usage:  python install_blender_addon.py [path-to-blender-executable]

Example Windows:  python install_blender_addon.py "C:/Program Files/Blender Foundation/Blender 4.3/blender.exe"
Example Mac:      python install_blender_addon.py /Applications/Blender.app/Contents/MacOS/Blender
"""
import zipfile
import shutil
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent
ADDON_DIR = ROOT / "blender_addon"
ZIP_PATH = ROOT / "game_ai_buddy_blender.zip"

def build_zip():
    print("Building Blender addon zip...")
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in ADDON_DIR.rglob("*.py"):
            arcname = f"game_ai_buddy/{f.relative_to(ADDON_DIR)}"
            zf.write(f, arcname)
    print(f"Created: {ZIP_PATH}")
    return ZIP_PATH

def install_to_blender(blender_exe: str, zip_path: Path):
    print(f"Installing addon to Blender: {blender_exe}")
    script = f"""
import bpy
bpy.ops.preferences.addon_install(filepath=r'{zip_path}', overwrite=True)
bpy.ops.preferences.addon_enable(module='game_ai_buddy')
bpy.ops.wm.save_userpref()
print('[BuddyInstall] Addon installed and enabled.')
"""
    tmp_script = ROOT / "_buddy_install_tmp.py"
    tmp_script.write_text(script)

    result = subprocess.run(
        [blender_exe, "--background", "--python", str(tmp_script)],
        capture_output=True, text=True
    )
    tmp_script.unlink()

    if "Addon installed and enabled" in result.stdout:
        print("Addon successfully installed in Blender!")
    else:
        print("Blender output:")
        print(result.stdout[-2000:])
        print(result.stderr[-1000:])
        print(f"\nIf auto-install failed, manually install the zip:\n  {zip_path}")
        print("In Blender: Edit > Preferences > Add-ons > Install > select the zip")

if __name__ == "__main__":
    zip_path = build_zip()

    if len(sys.argv) > 1:
        install_to_blender(sys.argv[1], zip_path)
    else:
        print(f"\nAddon zip built: {zip_path}")
        print("\nTo install manually in Blender:")
        print("  Edit > Preferences > Add-ons > Install > select the zip above")
        print("  Then enable 'Game AI Buddy' in the addon list")
        print("\nTo auto-install, run:")
        print(f"  python install_blender_addon.py /path/to/blender")
