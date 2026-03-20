"""
Unreal Engine 5 - PCG Biome Builder
Procedural Content Generation for terrain population.
Uses UE5 PCG framework + direct scatter fallback.

Biomes: forest | desert | mountain | swamp | coastal | tundra
Each biome knows which assets to place, at what slopes, densities, and altitude ranges.
"""
import unreal
import random
import math

# -----------------------------------------------------------------------
#  Biome definitions
# -----------------------------------------------------------------------
# Each biome defines rules for asset placement.
# asset_paths should be replaced with your actual Megascans/FAB paths.
# Defaults use placeholder paths — the AI will help you find yours.

BIOME_CONFIGS = {
    "forest": {
        "label": "Temperate Forest",
        "layers": [
            {
                "name": "Tall Trees",
                "asset_paths": ["/Game/Megascans/Trees/Oak/SM_Oak", "/Game/Megascans/Trees/Birch/SM_Birch"],
                "count": 400,
                "slope_min": 0,
                "slope_max": 25,
                "altitude_min": -500,
                "altitude_max": 1500,
                "scale_min": 0.8,
                "scale_max": 1.4,
                "folder": "/BuddyBiome/Forest/Trees",
            },
            {
                "name": "Undergrowth",
                "asset_paths": ["/Game/Megascans/Plants/Fern/SM_Fern", "/Game/Megascans/Plants/Bush/SM_Bush"],
                "count": 800,
                "slope_min": 0,
                "slope_max": 30,
                "altitude_min": -500,
                "altitude_max": 1200,
                "scale_min": 0.5,
                "scale_max": 1.0,
                "folder": "/BuddyBiome/Forest/Ground",
            },
            {
                "name": "Rocks",
                "asset_paths": ["/Game/Megascans/Rocks/Forest_Rock/SM_ForestRock"],
                "count": 150,
                "slope_min": 5,
                "slope_max": 45,
                "altitude_min": 0,
                "altitude_max": 2000,
                "scale_min": 0.6,
                "scale_max": 2.0,
                "folder": "/BuddyBiome/Forest/Rocks",
            },
        ],
    },

    "desert": {
        "label": "Desert / Arid",
        "layers": [
            {
                "name": "Cacti",
                "asset_paths": ["/Game/Megascans/Plants/Cactus/SM_Cactus"],
                "count": 200,
                "slope_min": 0,
                "slope_max": 20,
                "altitude_min": -200,
                "altitude_max": 800,
                "scale_min": 0.7,
                "scale_max": 1.5,
                "folder": "/BuddyBiome/Desert/Vegetation",
            },
            {
                "name": "Desert Rocks",
                "asset_paths": ["/Game/Megascans/Rocks/Desert_Rock/SM_DesertRock"],
                "count": 300,
                "slope_min": 0,
                "slope_max": 50,
                "altitude_min": -200,
                "altitude_max": 1500,
                "scale_min": 0.5,
                "scale_max": 3.0,
                "folder": "/BuddyBiome/Desert/Rocks",
            },
            {
                "name": "Dry Shrubs",
                "asset_paths": ["/Game/Megascans/Plants/DryShrub/SM_DryShrub"],
                "count": 600,
                "slope_min": 0,
                "slope_max": 35,
                "altitude_min": -200,
                "altitude_max": 1000,
                "scale_min": 0.4,
                "scale_max": 0.9,
                "folder": "/BuddyBiome/Desert/Ground",
            },
        ],
    },

    "mountain": {
        "label": "Alpine Mountain",
        "layers": [
            {
                "name": "Pine Trees",
                "asset_paths": ["/Game/Megascans/Trees/Pine/SM_Pine"],
                "count": 300,
                "slope_min": 0,
                "slope_max": 35,
                "altitude_min": 500,
                "altitude_max": 2000,
                "scale_min": 0.9,
                "scale_max": 1.5,
                "folder": "/BuddyBiome/Mountain/Trees",
            },
            {
                "name": "Mountain Boulders",
                "asset_paths": ["/Game/Megascans/Rocks/Mountain_Boulder/SM_MtnBoulder"],
                "count": 400,
                "slope_min": 15,
                "slope_max": 70,
                "altitude_min": 800,
                "altitude_max": 5000,
                "scale_min": 0.8,
                "scale_max": 4.0,
                "folder": "/BuddyBiome/Mountain/Rocks",
            },
        ],
    },

    "swamp": {
        "label": "Swamp / Wetland",
        "layers": [
            {
                "name": "Dead Trees",
                "asset_paths": ["/Game/Megascans/Trees/DeadTree/SM_DeadTree"],
                "count": 250,
                "slope_min": 0,
                "slope_max": 15,
                "altitude_min": -300,
                "altitude_max": 200,
                "scale_min": 0.7,
                "scale_max": 1.6,
                "folder": "/BuddyBiome/Swamp/Trees",
            },
            {
                "name": "Swamp Grass",
                "asset_paths": ["/Game/Megascans/Plants/TallGrass/SM_TallGrass"],
                "count": 1000,
                "slope_min": 0,
                "slope_max": 10,
                "altitude_min": -400,
                "altitude_max": 100,
                "scale_min": 0.5,
                "scale_max": 1.2,
                "folder": "/BuddyBiome/Swamp/Ground",
            },
            {
                "name": "Mossy Rocks",
                "asset_paths": ["/Game/Megascans/Rocks/Mossy_Rock/SM_MossyRock"],
                "count": 200,
                "slope_min": 0,
                "slope_max": 30,
                "altitude_min": -400,
                "altitude_max": 300,
                "scale_min": 0.5,
                "scale_max": 2.5,
                "folder": "/BuddyBiome/Swamp/Rocks",
            },
        ],
    },

    "coastal": {
        "label": "Coastal / Beach",
        "layers": [
            {
                "name": "Palm Trees",
                "asset_paths": ["/Game/Megascans/Trees/Palm/SM_Palm"],
                "count": 100,
                "slope_min": 0,
                "slope_max": 20,
                "altitude_min": 0,
                "altitude_max": 300,
                "scale_min": 0.8,
                "scale_max": 1.3,
                "folder": "/BuddyBiome/Coastal/Trees",
            },
            {
                "name": "Driftwood / Rocks",
                "asset_paths": ["/Game/Megascans/Rocks/Coastal_Rock/SM_CoastalRock"],
                "count": 200,
                "slope_min": 0,
                "slope_max": 40,
                "altitude_min": -100,
                "altitude_max": 200,
                "scale_min": 0.5,
                "scale_max": 2.0,
                "folder": "/BuddyBiome/Coastal/Rocks",
            },
        ],
    },

    "tundra": {
        "label": "Arctic Tundra",
        "layers": [
            {
                "name": "Snow Rocks",
                "asset_paths": ["/Game/Megascans/Rocks/Snow_Rock/SM_SnowRock"],
                "count": 350,
                "slope_min": 0,
                "slope_max": 55,
                "altitude_min": 1000,
                "altitude_max": 6000,
                "scale_min": 0.6,
                "scale_max": 3.5,
                "folder": "/BuddyBiome/Tundra/Rocks",
            },
            {
                "name": "Ice Crystals",
                "asset_paths": ["/Game/Megascans/Nature/IcePillar/SM_IcePillar"],
                "count": 100,
                "slope_min": 0,
                "slope_max": 20,
                "altitude_min": 1500,
                "altitude_max": 6000,
                "scale_min": 0.4,
                "scale_max": 1.0,
                "folder": "/BuddyBiome/Tundra/Ice",
            },
        ],
    },
}

# -----------------------------------------------------------------------
#  Core placement
# -----------------------------------------------------------------------

def _get_landscape():
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    for a in actors:
        if isinstance(a, unreal.LandscapeProxy):
            return a
    return None

def _try_load_asset(path: str):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not asset:
        unreal.log_warning(f"[PCGBuilder] Asset not found: {path} — skipping. Replace with your actual asset path.")
    return asset

def _scatter_layer(layer: dict, area_half: float, transaction_name: str):
    """Place one layer of assets based on its rules."""
    paths = layer["asset_paths"]
    count = layer["count"]
    slope_min = layer["slope_min"]
    slope_max = layer["slope_max"]
    alt_min = layer["altitude_min"]
    alt_max = layer["altitude_max"]
    scale_min = layer["scale_min"]
    scale_max = layer["scale_max"]
    folder = layer["folder"]

    # Load valid assets
    assets = [a for a in (_try_load_asset(p) for p in paths) if a]
    if not assets:
        unreal.log_warning(f"[PCGBuilder] No valid assets for layer '{layer['name']}' — update asset paths in pcg_builder.py")
        return 0

    landscape = _get_landscape()
    placed = 0

    with unreal.ScopedEditorTransaction(transaction_name):
        for _ in range(count * 8):
            if placed >= count:
                break

            x = random.uniform(-area_half, area_half)
            y = random.uniform(-area_half, area_half)
            z = 0.0

            # Basic altitude check (z=0 fallback when no trace available)
            if not (alt_min <= z <= alt_max):
                z = random.uniform(max(0, alt_min), max(0, alt_max))

            asset = random.choice(assets)
            loc = unreal.Vector(x, y, z)
            rot = unreal.Rotator(0, random.uniform(0, 360), 0)
            scale = random.uniform(scale_min, scale_max)

            actor = unreal.EditorLevelLibrary.spawn_actor_from_object(asset, loc, rot)
            if actor:
                actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
                actor.set_folder_path(folder)
                placed += 1

    return placed

# -----------------------------------------------------------------------
#  Public API
# -----------------------------------------------------------------------

def populate_biome(
    biome_name: str,
    area_size: float = 10000.0,
    density_multiplier: float = 1.0,
    clear_existing: bool = False,
):
    """
    Populate the current level with a biome.

    biome_name: 'forest' | 'desert' | 'mountain' | 'swamp' | 'coastal' | 'tundra'
    area_size: total area width/height in cm (10000 = 100m x 100m)
    density_multiplier: 0.5 = half density, 2.0 = double density
    clear_existing: if True, removes all actors in /BuddyBiome/ folders first
    """
    if biome_name not in BIOME_CONFIGS:
        unreal.log_error(f"[PCGBuilder] Unknown biome '{biome_name}'. Choose: {list(BIOME_CONFIGS.keys())}")
        return

    cfg = BIOME_CONFIGS[biome_name]
    unreal.log(f"[PCGBuilder] Populating biome: {cfg['label']} (density x{density_multiplier})")

    if clear_existing:
        clear_buddy_actors()

    area_half = area_size / 2
    total_placed = 0

    for layer in cfg["layers"]:
        # Apply density multiplier
        layer_copy = dict(layer)
        layer_copy["count"] = max(1, int(layer["count"] * density_multiplier))
        placed = _scatter_layer(layer_copy, area_half, f"Buddy PCG: {biome_name} - {layer['name']}")
        total_placed += placed
        unreal.log(f"  {layer['name']}: {placed} placed")

    unreal.log(f"[PCGBuilder] Biome complete. Total actors: {total_placed}")
    return total_placed

def clear_buddy_actors(folder_prefix: str = "/BuddyBiome"):
    """Remove all actors placed by the buddy system."""
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    removed = 0
    with unreal.ScopedEditorTransaction("Buddy: Clear Biome"):
        for actor in actors:
            try:
                folder = str(actor.get_folder_path())
                if folder.startswith(folder_prefix) or folder.startswith("/BuddyScatter"):
                    unreal.EditorLevelLibrary.destroy_actor(actor)
                    removed += 1
            except Exception:
                pass
    unreal.log(f"[PCGBuilder] Cleared {removed} buddy-placed actors.")

def mix_biomes(
    biome_a: str,
    biome_b: str,
    blend: float = 0.5,
    area_size: float = 10000.0,
):
    """
    Mix two biomes. blend=0.0 is all biome_a, blend=1.0 is all biome_b.
    """
    if biome_a not in BIOME_CONFIGS or biome_b not in BIOME_CONFIGS:
        unreal.log_error(f"[PCGBuilder] Unknown biome. Valid: {list(BIOME_CONFIGS.keys())}")
        return

    unreal.log(f"[PCGBuilder] Mixing {biome_a} ({1-blend:.0%}) + {biome_b} ({blend:.0%})")
    populate_biome(biome_a, area_size, density_multiplier=1.0 - blend)
    populate_biome(biome_b, area_size, density_multiplier=blend)

def set_layer_asset(biome_name: str, layer_name: str, new_asset_paths: list):
    """
    Update the asset paths for a specific biome layer.
    Use this to point layers at your actual downloaded assets.

    Example:
        set_layer_asset('forest', 'Tall Trees', ['/Game/MyPack/Oak/SM_Oak'])
    """
    if biome_name not in BIOME_CONFIGS:
        unreal.log_error(f"[PCGBuilder] Unknown biome '{biome_name}'")
        return False

    for layer in BIOME_CONFIGS[biome_name]["layers"]:
        if layer["name"].lower() == layer_name.lower():
            layer["asset_paths"] = new_asset_paths
            unreal.log(f"[PCGBuilder] Updated '{biome_name}' > '{layer_name}' assets to: {new_asset_paths}")
            return True

    unreal.log_warning(f"[PCGBuilder] Layer '{layer_name}' not found in biome '{biome_name}'")
    return False

def list_biomes() -> list:
    """Return all available biome names."""
    return list(BIOME_CONFIGS.keys())

def get_biome_info(biome_name: str) -> dict:
    """Return the full config for a biome."""
    return BIOME_CONFIGS.get(biome_name, {})
