"""
Game AI Buddy - Unreal Engine 5 Plugin (Python)
Place this folder in your project's Content/Python/ directory.

To auto-load on startup, add to Project Settings > Plugins > Python:
  Additional Paths: [Content/Python/game_ai_buddy]
  Startup Scripts:  [game_ai_buddy/buddy_init.py]
"""
import unreal
import importlib

# Register a menu entry in Unreal's toolbar
@unreal.uclass()
class BuddyMenuEntry(unreal.ToolMenuEntryScript):
    @unreal.ufunction(override=True)
    def execute(self, context):
        from buddy_panel import show_buddy_panel
        show_buddy_panel()

def register_menu():
    menus = unreal.ToolMenus.get()
    main_menu = menus.find_menu("LevelEditor.MainMenu")
    if main_menu:
        section = main_menu.add_section("BuddySection", unreal.Text("AI Buddy"))
        entry = unreal.ToolMenuEntry(
            name="OpenBuddy",
            type=unreal.MultiBlockType.MENU_ENTRY,
        )
        entry.set_label(unreal.Text("Open AI Buddy"))
        entry.set_tool_tip(unreal.Text("Open the Game AI Buddy panel"))
        section.add_entry(entry)
        menus.refresh_all_widgets()
    unreal.log("[BuddyInit] Game AI Buddy menu registered.")

try:
    register_menu()
except Exception as e:
    unreal.log_warning(f"[BuddyInit] Menu registration failed (may be headless): {e}")

unreal.log("[BuddyInit] Game AI Buddy loaded. Run buddy_panel.show_buddy_panel() to open.")
