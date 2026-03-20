"""
Blender UI Panel for Game AI Buddy.
Shows up in View3D sidebar under "AI Buddy" tab.
"""
import bpy

class BUDDY_PT_MainPanel(bpy.types.Panel):
    bl_label = "AI Buddy"
    bl_idname = "BUDDY_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AI Buddy"

    def draw(self, context):
        layout = self.layout
        props = context.scene.buddy_props

        # Header
        header = layout.box()
        header.label(text="Game AI Buddy", icon="FUND")
        header.label(text="Blender AI Assistant", icon="BLANK1")

        layout.separator()

        # Prompt input
        layout.label(text="Ask Buddy:")
        layout.prop(props, "prompt", text="")
        layout.prop(props, "include_screenshot")

        row = layout.row(align=True)
        ask_btn = row.operator("buddy.ask", text="Ask" if not props.is_loading else "Thinking...", icon="FUND")
        row.operator("buddy.clear", text="", icon="X")

        layout.separator()

        # Response
        if props.reply:
            box = layout.box()
            box.label(text="Buddy says:", icon="INFO")
            # Word-wrap the reply in the panel
            wrap_text(box, props.reply, context)

        # Code block
        if props.extracted_code:
            layout.separator()
            code_box = layout.box()
            row = code_box.row()
            row.prop(props, "show_code", text="Python Code", icon="CONSOLE", emboss=False)

            if props.show_code:
                wrap_text(code_box, props.extracted_code, context)

            execute_row = layout.row()
            execute_row.scale_y = 1.5
            execute_row.operator("buddy.execute_code", text="Execute in Blender", icon="PLAY")

            if props.last_exec_status:
                status_box = layout.box()
                icon = "CHECKMARK" if "Success" in props.last_exec_status else "ERROR"
                status_box.label(text=props.last_exec_status, icon=icon)

def wrap_text(layout, text: str, context, max_chars: int = 40):
    """Simple word-wrap for Blender UI panels."""
    col = layout.column(align=True)
    # Split on newlines first, then wrap long lines
    for paragraph in text.split("\n"):
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

def register():
    bpy.utils.register_class(BUDDY_PT_MainPanel)

def unregister():
    bpy.utils.unregister_class(BUDDY_PT_MainPanel)
