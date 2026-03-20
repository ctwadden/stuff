"""
Blender UI Panel for Game AI Buddy.
View3D sidebar > AI Buddy tab.
Sections: Mode toggle | Asset Generator | Chat | Vision | Code execution
"""
import bpy

# -----------------------------------------------------------------------
#  Helpers
# -----------------------------------------------------------------------

def wrap_text(layout, text: str, max_chars: int = 42):
    col = layout.column(align=True)
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            col.separator()
            continue
        if len(paragraph) <= max_chars:
            col.label(text=paragraph)
        else:
            words = paragraph.split(" ")
            line = ""
            for word in words:
                if len(line) + len(word) + 1 <= max_chars:
                    line = f"{line} {word}".strip()
                else:
                    if line:
                        col.label(text=line)
                    line = word
            if line:
                col.label(text=line)

# -----------------------------------------------------------------------
#  Panels
# -----------------------------------------------------------------------

class BUDDY_PT_Main(bpy.types.Panel):
    bl_label = "AI Buddy"
    bl_idname = "BUDDY_PT_Main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AI Buddy"

    def draw(self, context):
        layout = self.layout
        props = context.scene.buddy_props

        # Header
        box = layout.box()
        box.label(text="Game AI Buddy", icon="FUND")
        row = box.row(align=True)
        row.prop(props, "mode", expand=True)

class BUDDY_PT_Vision(bpy.types.Panel):
    bl_label = "See My Screen"
    bl_idname = "BUDDY_PT_Vision"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AI Buddy"
    bl_parent_id = "BUDDY_PT_Main"

    def draw(self, context):
        layout = self.layout
        props = context.scene.buddy_props

        col = layout.column(align=True)
        col.label(text="Stuck? Let Buddy see your screen:", icon="RESTRICT_VIEW_OFF")
        col.prop(props, "prompt", text="", placeholder="Optional: what to focus on...")

        btn = col.operator("buddy.see_screen", icon="CAMERA_DATA",
                           text="Take Screenshot + Ask Buddy")
        btn_row = col.row()
        btn_row.scale_y = 0.8
        btn_row.label(text="Buddy will describe what it sees", icon="INFO")

class BUDDY_PT_AssetGen(bpy.types.Panel):
    bl_label = "Asset Generator"
    bl_idname = "BUDDY_PT_AssetGen"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AI Buddy"
    bl_parent_id = "BUDDY_PT_Main"

    def draw(self, context):
        layout = self.layout
        props = context.scene.buddy_props

        layout.label(text="Generate a 3D asset with AI:", icon="MESH_MONKEY")
        layout.prop(props, "asset_type", text="")
        layout.prop(props, "asset_custom", text="", placeholder="Customise (optional)...")

        row = layout.row()
        row.scale_y = 1.5
        row.operator("buddy.generate_asset", icon="PLAY",
                     text=f"Generate {props.asset_type.replace('_', ' ').title()}")

        layout.separator()
        layout.label(text="Quick presets:", icon="PRESET")
        grid = layout.grid_flow(row_major=True, columns=2, align=True)

        presets = [
            ("rock", "Rock"),
            ("tree", "Tree"),
            ("sword", "Sword"),
            ("building", "Building"),
            ("character_base", "Character"),
            ("crystal", "Crystal"),
        ]
        for asset_id, label in presets:
            op = grid.operator("buddy.generate_asset", text=label)

class BUDDY_PT_Chat(bpy.types.Panel):
    bl_label = "Chat"
    bl_idname = "BUDDY_PT_Chat"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AI Buddy"
    bl_parent_id = "BUDDY_PT_Main"

    def draw(self, context):
        layout = self.layout
        props = context.scene.buddy_props

        mode_hint = "Ask anything — I'll teach you step by step" if props.mode == "teach" else "Tell me what to build or fix"
        layout.label(text=mode_hint + ":", icon="OUTLINER_OB_FONT")
        layout.prop(props, "prompt", text="")
        layout.prop(props, "include_screenshot")

        row = layout.row(align=True)
        row.scale_y = 1.4
        if props.is_loading:
            row.operator("buddy.ask", text="Thinking...", icon="SORTTIME")
        else:
            icon = "OUTLINER_OB_LIGHT" if props.mode == "teach" else "FUND"
            label = "Teach Me" if props.mode == "teach" else "Ask Buddy"
            row.operator("buddy.ask", text=label, icon=icon)
        row.operator("buddy.clear", text="", icon="X")

        # Reply
        if props.reply and props.reply not in ("Thinking...", ""):
            layout.separator()
            box = layout.box()

            if props.mode == "teach":
                box.label(text="Buddy's Tutorial:", icon="OUTLINER_OB_LIGHT")
            else:
                box.label(text="Buddy says:", icon="INFO")

            wrap_text(box, props.reply[:1200])  # cap display length

            # Show "do step X for me" buttons in teach mode
            if props.mode == "teach":
                import re
                steps = re.findall(r"Step\s+(\d+)", props.reply, re.IGNORECASE)
                if steps:
                    box.separator()
                    box.label(text="Do a step for me:", icon="PLAY")
                    row = box.row(align=True)
                    for n in steps[:6]:  # show up to 6 step buttons
                        op = row.operator("buddy.do_step", text=f"Step {n}")
                        op.step = int(n)

class BUDDY_PT_Code(bpy.types.Panel):
    bl_label = "Generated Code"
    bl_idname = "BUDDY_PT_Code"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AI Buddy"
    bl_parent_id = "BUDDY_PT_Main"

    @classmethod
    def poll(cls, context):
        return bool(context.scene.buddy_props.extracted_code)

    def draw(self, context):
        layout = self.layout
        props = context.scene.buddy_props

        layout.prop(props, "show_code", text="Show Python Code", icon="CONSOLE")
        if props.show_code:
            box = layout.box()
            wrap_text(box, props.extracted_code[:800])

        row = layout.row()
        row.scale_y = 1.5
        row.operator("buddy.execute_code", text="Execute in Blender", icon="PLAY")

        if props.last_exec_status:
            icon = "CHECKMARK" if "Success" in props.last_exec_status else "ERROR"
            layout.label(text=props.last_exec_status, icon=icon)

# -----------------------------------------------------------------------
#  Register
# -----------------------------------------------------------------------

_classes = [
    BUDDY_PT_Main,
    BUDDY_PT_Vision,
    BUDDY_PT_AssetGen,
    BUDDY_PT_Chat,
    BUDDY_PT_Code,
]

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
