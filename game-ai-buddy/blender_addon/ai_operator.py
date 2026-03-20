"""
Blender operators for Game AI Buddy.
Handles: Ask (do mode), Teach mode, Asset generation, Vision (see screen), Step execution.
"""
import bpy
import urllib.request
import urllib.error
import json
import threading
import re

SERVER_URL = "http://127.0.0.1:8765"

# -----------------------------------------------------------------------
#  HTTP helpers
# -----------------------------------------------------------------------

def _post(endpoint: str, payload: dict, callback):
    """Non-blocking POST to buddy server, returns result via callback on main thread."""
    data = json.dumps(payload).encode("utf-8")

    def run():
        try:
            req = urllib.request.Request(
                f"{SERVER_URL}{endpoint}",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                result = json.loads(resp.read())
                bpy.app.timers.register(lambda: callback(result, None), first_interval=0.0)
        except urllib.error.URLError:
            err = (
                f"Cannot reach Buddy Server at {SERVER_URL}\n"
                "Start it: double-click start_server.bat (Win) or bash start_server.sh (Mac)"
            )
            bpy.app.timers.register(lambda: callback(None, err), first_interval=0.0)
        except Exception as e:
            bpy.app.timers.register(lambda: callback(None, str(e)), first_interval=0.0)

    threading.Thread(target=run, daemon=True).start()

def extract_python(text: str) -> str:
    match = re.search(r"```python\s*([\s\S]*?)```", text)
    return match.group(1).strip() if match else ""

def extract_steps(text: str) -> list[str]:
    """Parse numbered steps from teach-mode reply."""
    steps = re.findall(r"(?:Step\s+\d+[:\.]?\s*)(.*?)(?=Step\s+\d+[:\.]?|\Z)", text, re.IGNORECASE | re.DOTALL)
    return [s.strip() for s in steps if s.strip()]

# -----------------------------------------------------------------------
#  Properties
# -----------------------------------------------------------------------

class BuddyProperties(bpy.types.PropertyGroup):
    prompt: bpy.props.StringProperty(name="Prompt", default="")
    reply: bpy.props.StringProperty(name="Reply", default="")
    extracted_code: bpy.props.StringProperty(name="Code", default="")
    last_exec_status: bpy.props.StringProperty(default="")
    is_loading: bpy.props.BoolProperty(default=False)
    include_screenshot: bpy.props.BoolProperty(
        name="Show Buddy my screen",
        description="Send a screenshot so AI can see your current Blender state",
        default=False,
    )
    show_code: bpy.props.BoolProperty(name="Show Code", default=True)
    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("do",    "Do It",    "AI generates and executes code for you",          "PLAY",         0),
            ("teach", "Teach Me", "AI explains step-by-step how to do it yourself",  "OUTLINER_OB_LIGHT", 1),
        ],
        default="do",
    )
    asset_type: bpy.props.EnumProperty(
        name="Asset",
        items=[
            ("rock",           "Rock / Boulder",   "Procedural rock",       "MESH_ICOSPHERE",  0),
            ("tree",           "Tree",             "Low-poly tree",         "OUTLINER_OB_EMPTY", 1),
            ("sword",          "Sword",            "Fantasy sword",         "ORIENTATION_NORMAL", 2),
            ("building",       "Building",         "Modular building",      "HOME",            3),
            ("character_base", "Character Base",   "Humanoid base mesh",    "ARMATURE_DATA",   4),
            ("mountain",       "Mountain Chunk",   "Terrain chunk",         "RNDCURVE",        5),
            ("chest",          "Treasure Chest",   "Treasure chest",        "PACKAGE",         6),
            ("crystal",        "Crystal Cluster",  "Magical crystals",      "SHADING_RENDERED", 7),
        ],
        default="rock",
    )
    asset_custom: bpy.props.StringProperty(
        name="Customise",
        description="Optional: describe how you want the asset customised",
        default="",
    )

# -----------------------------------------------------------------------
#  Operators
# -----------------------------------------------------------------------

class BUDDY_OT_Ask(bpy.types.Operator):
    bl_idname = "buddy.ask"
    bl_label = "Ask AI Buddy"

    def execute(self, context):
        props = context.scene.buddy_props
        if not props.prompt.strip():
            self.report({"WARNING"}, "Enter a prompt first.")
            return {"CANCELLED"}

        props.is_loading = True
        props.reply = "Thinking..."
        props.extracted_code = ""

        def on_done(result, error):
            props.is_loading = False
            if error:
                props.reply = f"ERROR: {error}"
            else:
                props.reply = result["reply"]
                props.extracted_code = extract_python(result["reply"])
            return None

        _post("/ask", {
            "prompt": props.prompt,
            "app": "blender",
            "mode": props.mode,
            "include_screenshot": props.include_screenshot,
        }, on_done)
        return {"FINISHED"}

class BUDDY_OT_GenerateAsset(bpy.types.Operator):
    bl_idname = "buddy.generate_asset"
    bl_label = "Generate Asset"
    bl_description = "Ask AI to generate this 3D asset type in Blender"

    def execute(self, context):
        props = context.scene.buddy_props
        props.is_loading = True
        props.reply = f"Generating {props.asset_type}..."
        props.extracted_code = ""

        def on_done(result, error):
            props.is_loading = False
            if error:
                props.reply = f"ERROR: {error}"
            else:
                props.reply = result["reply"]
                props.extracted_code = extract_python(result["reply"])
            return None

        payload = {"asset_type": props.asset_type}
        if props.asset_custom.strip():
            payload["custom_prompt"] = props.asset_custom

        _post("/generate-asset", payload, on_done)
        return {"FINISHED"}

class BUDDY_OT_SeeScreen(bpy.types.Operator):
    bl_idname = "buddy.see_screen"
    bl_label = "See My Screen"
    bl_description = "Take a screenshot and ask Buddy what it sees - great for getting unstuck"

    def execute(self, context):
        props = context.scene.buddy_props
        props.is_loading = True
        props.reply = "Analysing your screen..."
        props.extracted_code = ""

        prompt = props.prompt.strip() or "Look at my Blender screen and tell me what you see. What am I working on and what should I do next?"

        def on_done(result, error):
            props.is_loading = False
            if error:
                props.reply = f"ERROR: {error}"
            else:
                props.reply = result["reply"]
                props.extracted_code = extract_python(result["reply"])
            return None

        _post("/ask", {
            "prompt": prompt,
            "app": "blender",
            "mode": props.mode,
            "include_screenshot": True,
        }, on_done)
        return {"FINISHED"}

class BUDDY_OT_Execute(bpy.types.Operator):
    bl_idname = "buddy.execute_code"
    bl_label = "Execute in Blender"
    bl_description = "Run the AI-generated Python code in Blender"

    def execute(self, context):
        props = context.scene.buddy_props
        code = props.extracted_code.strip()
        if not code:
            self.report({"WARNING"}, "No code to execute.")
            return {"CANCELLED"}

        try:
            exec(compile(code, "<buddy_ai>", "exec"), {"bpy": bpy})
            self.report({"INFO"}, "Executed successfully.")
            props.last_exec_status = "Success"
        except Exception as e:
            self.report({"ERROR"}, str(e))
            props.last_exec_status = f"Error: {e}"
        return {"FINISHED"}

class BUDDY_OT_DoStepForMe(bpy.types.Operator):
    """Send 'do step N for me' back to the AI - used in teach mode."""
    bl_idname = "buddy.do_step"
    bl_label = "Do This Step For Me"
    step: bpy.props.IntProperty(default=1)

    def execute(self, context):
        props = context.scene.buddy_props
        props.prompt = f"Do step {self.step} for me"
        bpy.ops.buddy.ask()
        return {"FINISHED"}

class BUDDY_OT_Clear(bpy.types.Operator):
    bl_idname = "buddy.clear"
    bl_label = "Clear"

    def execute(self, context):
        p = context.scene.buddy_props
        p.prompt = ""
        p.reply = ""
        p.extracted_code = ""
        p.last_exec_status = ""
        return {"FINISHED"}

# -----------------------------------------------------------------------
#  Register
# -----------------------------------------------------------------------

_classes = [
    BuddyProperties,
    BUDDY_OT_Ask,
    BUDDY_OT_GenerateAsset,
    BUDDY_OT_SeeScreen,
    BUDDY_OT_Execute,
    BUDDY_OT_DoStepForMe,
    BUDDY_OT_Clear,
]

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.buddy_props = bpy.props.PointerProperty(type=BuddyProperties)

def unregister():
    del bpy.types.Scene.buddy_props
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
