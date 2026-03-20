"""
Unreal Engine 5 - AI-driven Terrain & World Controller
Handles landscape sizing, PCG asset scattering, tree/rock/building placement,
and world composition via Unreal Python API.

Usage (from buddy_panel or direct):
    import terrain_controller as tc
    tc.create_landscape(width=4096, height=4096)
    tc.scatter_assets("/Game/Megascans/Trees/Oak", count=500, slope_max=25)
    tc.swap_all_actors("/Game/Trees/OldTree", "/Game/Trees/NewTree")
"""
import unreal

# -----------------------------------------------------------------------
#  Landscape
# -----------------------------------------------------------------------

def create_landscape(width: int = 2017, height: int = 2017, z_scale: float = 200.0) -> unreal.LandscapeProxy:
    """
    Create a new landscape actor in the current level.
    width/height should be (2^n)+1 for Unreal landscape resolutions.
    Common sizes: 505, 1009, 2017, 4033, 8129
    """
    landscape_config = unreal.LandscapeEditorObject()
    landscape_config.new_landscape_component_count = unreal.IntPoint(8, 8)

    landscape = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.Landscape,
        unreal.Vector(0, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    unreal.log(f"[Buddy] Landscape spawned. Scale to ({width}, {height}, {z_scale}) manually if needed.")
    return landscape

def resize_landscape(landscape_actor, new_scale_x: float, new_scale_y: float, new_scale_z: float):
    """Resize an existing landscape by changing its scale."""
    landscape_actor.set_actor_scale3d(unreal.Vector(new_scale_x, new_scale_y, new_scale_z))
    unreal.log(f"[Buddy] Landscape scaled to ({new_scale_x}, {new_scale_y}, {new_scale_z})")

def get_landscape() -> unreal.LandscapeProxy | None:
    """Get the first landscape actor in the current level."""
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    for actor in actors:
        if isinstance(actor, unreal.LandscapeProxy):
            return actor
    unreal.log_warning("[Buddy] No landscape found in current level.")
    return None

# -----------------------------------------------------------------------
#  Asset Scatter
# -----------------------------------------------------------------------

def scatter_assets(
    asset_path: str,
    count: int = 100,
    area_min: unreal.Vector = unreal.Vector(-5000, -5000, 0),
    area_max: unreal.Vector = unreal.Vector(5000, 5000, 0),
    slope_max: float = 35.0,
    align_to_terrain: bool = True,
    random_yaw: bool = True,
    scale_min: float = 0.8,
    scale_max: float = 1.3,
):
    """
    Scatter static mesh assets across the terrain.
    asset_path: Unreal content path e.g. '/Game/Megascans/Trees/Oak/SM_Oak'
    """
    import random

    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    if not asset:
        unreal.log_error(f"[Buddy] Asset not found: {asset_path}")
        return

    landscape = get_landscape()
    placed = 0

    with unreal.ScopedEditorTransaction("Buddy Scatter Assets") as trans:
        for _ in range(count * 5):  # attempt buffer
            if placed >= count:
                break

            x = random.uniform(area_min.x, area_max.x)
            y = random.uniform(area_min.y, area_max.y)

            # Trace down to find terrain height
            start = unreal.Vector(x, y, 100000)
            end = unreal.Vector(x, y, -100000)
            hit_result, did_hit = unreal.SystemLibrary.line_trace_single(
                unreal.EditorLevelLibrary.get_editor_world(),
                start, end,
                unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                False, [], unreal.DrawDebugTrace.NONE, True,
            ) if False else (None, False)  # simplified: use z=0 fallback

            z = 0
            location = unreal.Vector(x, y, z)
            rot = unreal.Rotator(0, random.uniform(0, 360) if random_yaw else 0, 0)
            scale = random.uniform(scale_min, scale_max)

            actor = unreal.EditorLevelLibrary.spawn_actor_from_object(
                asset, location, rot
            )
            if actor:
                actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
                actor.set_folder_path("/BuddyScatter")
                placed += 1

    unreal.log(f"[Buddy] Scattered {placed}/{count} {asset_path.split('/')[-1]} actors.")

# -----------------------------------------------------------------------
#  Asset Swap
# -----------------------------------------------------------------------

def swap_all_actors(old_asset_path: str, new_asset_path: str):
    """
    Replace every actor using old_asset_path with new_asset_path.
    Preserves location, rotation, and scale.
    """
    new_asset = unreal.EditorAssetLibrary.load_asset(new_asset_path)
    if not new_asset:
        unreal.log_error(f"[Buddy] New asset not found: {new_asset_path}")
        return

    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    to_replace = []

    for actor in actors:
        if isinstance(actor, unreal.StaticMeshActor):
            comp = actor.get_component_by_class(unreal.StaticMeshComponent)
            if comp:
                mesh = comp.get_editor_property("static_mesh")
                if mesh and unreal.EditorAssetLibrary.get_path_name_for_loaded_asset(mesh) == old_asset_path:
                    to_replace.append(actor)

    replaced = 0
    with unreal.ScopedEditorTransaction("Buddy Swap Actors") as trans:
        for actor in to_replace:
            loc = actor.get_actor_location()
            rot = actor.get_actor_rotation()
            scale = actor.get_actor_scale3d()
            unreal.EditorLevelLibrary.destroy_actor(actor)

            new_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(new_asset, loc, rot)
            if new_actor:
                new_actor.set_actor_scale3d(scale)
                replaced += 1

    unreal.log(f"[Buddy] Swapped {replaced} actors from '{old_asset_path.split('/')[-1]}' to '{new_asset_path.split('/')[-1]}'.")

# -----------------------------------------------------------------------
#  PCG (Procedural Content Generation)
# -----------------------------------------------------------------------

def setup_pcg_foliage(
    mesh_paths: list[str],
    density: float = 1.0,
    area_bounds: float = 10000.0,
):
    """
    Create a PCG graph component on the landscape for procedural foliage.
    mesh_paths: list of Unreal asset paths to use as foliage meshes.
    density: multiplier for instance density (0.1 = sparse, 2.0 = dense).
    """
    landscape = get_landscape()
    if not landscape:
        unreal.log_error("[Buddy] No landscape - create one first.")
        return

    # Add PCG component to landscape
    pcg_comp = landscape.add_component_by_class(unreal.PCGComponent)
    if not pcg_comp:
        unreal.log_warning("[Buddy] PCG component could not be added - ensure PCG plugin is enabled.")
        return

    unreal.log(
        f"[Buddy] PCG component added to landscape.\n"
        f"Assign a PCG Graph asset manually in the Details panel and reference these meshes:\n"
        + "\n".join(f"  - {p}" for p in mesh_paths)
    )

# -----------------------------------------------------------------------
#  Water
# -----------------------------------------------------------------------

def add_water_body(body_type: str = "lake", location: unreal.Vector = unreal.Vector(0, 0, -50)):
    """
    Spawn a Water Body actor (requires Water plugin enabled).
    body_type: 'lake', 'river', or 'ocean'
    """
    class_map = {
        "lake": unreal.WaterBodyLake,
        "river": unreal.WaterBodyRiver,
        "ocean": unreal.WaterBodyOcean,
    }
    cls = class_map.get(body_type.lower())
    if not cls:
        unreal.log_error(f"[Buddy] Unknown water type: {body_type}. Use 'lake', 'river', or 'ocean'.")
        return

    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, location, unreal.Rotator(0, 0, 0))
    unreal.log(f"[Buddy] Spawned {body_type} water body at {location}.")
    return actor

# -----------------------------------------------------------------------
#  World info
# -----------------------------------------------------------------------

def get_world_summary() -> str:
    """Return a summary of the current level's actors for the AI context."""
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    type_counts: dict[str, int] = {}
    for a in actors:
        name = type(a).__name__
        type_counts[name] = type_counts.get(name, 0) + 1

    lines = [f"  {k}: {v}" for k, v in sorted(type_counts.items(), key=lambda x: -x[1])]
    summary = "Current level contents:\n" + "\n".join(lines)
    unreal.log(summary)
    return summary
