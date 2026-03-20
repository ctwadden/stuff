"""
Blender operators for Game AI Buddy.
Handles sending prompts to the local server and executing returned code.
"""
import bpy
import urllib.request
import urllib.error
import json
import threading
import tempfile
import os

SERVER_URL = "http://127.0.0.1:8765"

def get_server_url():
    return SERVER_URL

def send_to_server(prompt: str, include_screenshot: bool, callback):
    """Send request to buddy server in a background thread (non-blocking)."""
    payload = json.dumps({
        "prompt": prompt,
        "app": "blender",
        "include_screenshot": include_screenshot,
    }).encode("utf-8")

    def run():
        try:
            req = urllib.request.Request(
                f"{get_server_url()}/ask",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
                bpy.app.timers.register(lambda: callback(data["reply"], None), first_interval=0.0)
        except urllib.error.URLError as e:
            err = f"Cannot reach Buddy Server at {get_server_url()}.\nMake sure the server is running:\n  cd server && python main.py"
            bpy.app.timers.register(lambda: callback(None, err), first_interval=0.0)
        except Exception as e:
            bpy.app.timers.register(lambda: callback(None, str(e)), first_interval=0.0)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

def extract_code(reply: str) -> str | None:
    """Extract the first ```python code block from AI reply."""
    import re
    pattern = r"```python\s*([\s\S]*?)```"
    match = re.search(pattern, reply)
    if match:
        return match.group(1).strip()
    return None

class BUDDY_OT_Ask(bpy.types.Operator):
    """Send prompt to AI Buddy"""
    bl_idname = "buddy.ask"
    bl_label = "Ask AI Buddy"
    bl_description = "Send your prompt to the AI Buddy server"

    def execute(self, context):
        props = context.scene.buddy_props
        prompt = props.prompt.strip()

        if not prompt:
            self.report({"WARNING"}, "Please enter a prompt first.")
            return {"CANCELLED"}

        props.is_loading = True
        props.reply = "Thinking..."
        props.extracted_code = ""

        def on_response(reply, error):
            props.is_loading = False
            if error:
                props.reply = f"ERROR: {error}"
            else:
                props.reply = reply
                code = extract_code(reply)
                props.extracted_code = code if code else ""
            return None  # stop timer

        send_to_server(prompt, props.include_screenshot, on_response)
        return {"FINISHED"}

class BUDDY_OT_Execute(bpy.types.Operator):
    """Execute the AI-generated Blender Python code"""
    bl_idname = "buddy.execute_code"
    bl_label = "Execute Code"
    bl_description = "Run the AI-generated Python code in Blender"

    def execute(self, context):
        props = context.scene.buddy_props
        code = props.extracted_code.strip()

        if not code:
            self.report({"WARNING"}, "No code to execute.")
            return {"CANCELLED"}

        try:
            exec(compile(code, "<buddy_ai>", "exec"), {"bpy": bpy})
            self.report({"INFO"}, "AI code executed successfully.")
            props.last_exec_status = "Success"
        except Exception as e:
            self.report({"ERROR"}, f"Code error: {e}")
            props.last_exec_status = f"Error: {e}"

        return {"FINISHED"}

class BUDDY_OT_ClearHistory(bpy.types.Operator):
    """Clear the AI conversation"""
    bl_idname = "buddy.clear"
    bl_label = "Clear"
    bl_description = "Clear prompt and response"

    def execute(self, context):
        props = context.scene.buddy_props
        props.prompt = ""
        props.reply = ""
        props.extracted_code = ""
        props.last_exec_status = ""
        return {"FINISHED"}

class BuddyProperties(bpy.types.PropertyGroup):
    prompt: bpy.props.StringProperty(
        name="Prompt",
        description="Ask AI Buddy anything about Blender",
        default="",
    )
    reply: bpy.props.StringProperty(
        name="Reply",
        default="",
    )
    extracted_code: bpy.props.StringProperty(
        name="Extracted Code",
        default="",
    )
    last_exec_status: bpy.props.StringProperty(default="")
    is_loading: bpy.props.BoolProperty(default=False)
    include_screenshot: bpy.props.BoolProperty(
        name="Send Screenshot",
        description="Capture screen and send to AI so it can see your scene",
        default=False,
    )
    show_code: bpy.props.BoolProperty(
        name="Show Code",
        description="Show the extracted Python code",
        default=True,
    )

def register():
    bpy.utils.register_class(BuddyProperties)
    bpy.utils.register_class(BUDDY_OT_Ask)
    bpy.utils.register_class(BUDDY_OT_Execute)
    bpy.utils.register_class(BUDDY_OT_ClearHistory)
    bpy.types.Scene.buddy_props = bpy.props.PointerProperty(type=BuddyProperties)

def unregister():
    del bpy.types.Scene.buddy_props
    bpy.utils.unregister_class(BUDDY_OT_ClearHistory)
    bpy.utils.unregister_class(BUDDY_OT_Execute)
    bpy.utils.unregister_class(BUDDY_OT_Ask)
    bpy.utils.unregister_class(BuddyProperties)
