"""
Game AI Buddy - Blender Addon
Installs as a standard Blender addon. Adds an "AI Buddy" panel in the N-panel (sidebar).

Install: Edit > Preferences > Add-ons > Install > select this folder as a zip
"""
bl_info = {
    "name": "Game AI Buddy",
    "author": "Game AI Buddy",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > AI Buddy",
    "description": "AI assistant for Blender - ask anything, execute AI-generated code",
    "category": "Interface",
}

import bpy
from . import buddy_panel, ai_operator

def register():
    ai_operator.register()
    buddy_panel.register()

def unregister():
    buddy_panel.unregister()
    ai_operator.unregister()
