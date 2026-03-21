"""
Game Mechanics prompt library.
Each entry is a curated prompt that produces complete, working Unity C# code
for a specific mechanic. Used by the /mechanics server endpoint.
"""

SYSTEM_PROMPT_MECHANICS = """You are an expert Unity game developer writing complete, production-ready C# code.

Rules:
- Write COMPLETE scripts, not fragments. Include all using statements and class definitions.
- Always use a ```csharp code block.
- Scripts must be drop-on-a-GameObject ready — no setup steps required unless unavoidable.
- Use [SerializeField] private instead of public for inspector fields.
- Add [Header("...")] attributes to group inspector fields clearly.
- Add brief // comments on non-obvious lines.
- After the code, write a short "How to use:" section (3-5 bullet points max).
- If the user is in Teach mode, explain the concepts before the code with numbered steps."""

MECHANICS = {

    # -----------------------------------------------------------------------
    #  PLAYER MOVEMENT
    # -----------------------------------------------------------------------
    "player.third_person": """Write a complete Unity C# ThirdPersonController script.
Features: WASD movement relative to camera, Shift to sprint, Space to jump, coyote time (0.15s),
jump buffer (0.1s), smooth rotation toward movement direction, slope handling, Animator integration
(Speed float, Jump trigger, Grounded bool). Use CharacterController component. Include [SerializeField]
fields for moveSpeed, sprintSpeed, jumpHeight, gravity. Add [Header] groups.""",

    "player.first_person": """Write a complete Unity C# FirstPersonController script.
Features: Mouse look (X=rotate player, Y=tilt camera, clamp vertical), WASD movement, Shift sprint,
Space jump, CharacterController-based. Lock/unlock cursor on Escape. Smooth head bob while walking.
[SerializeField] fields for sensitivity, speed, jumpHeight. No external dependencies.""",

    "player.top_down": """Write a complete Unity C# TopDownController script.
Features: WASD or click-to-move (Raycast to ground plane), smooth rotation toward move direction,
NavMeshAgent OR Rigidbody option (toggle via bool), sprint, Animator Speed float. Works for RPG
or twin-stick style. Include obstacle avoidance radius.""",

    "player.dash": """Write a complete Unity C# Dash ability script to add to an existing controller.
Features: Press LeftShift or custom key, dash in move direction (or forward if still),
dashDistance and dashDuration SerializeField, cooldown with UI-ready cooldownPercent property (0-1),
trail renderer toggle during dash, invincibility frames during dash,
layerMask to ignore enemies during dash. Works alongside CharacterController or Rigidbody.""",

    "player.wall_run": """Write a complete Unity C# WallRun script.
Features: detect walls via Raycast left/right, tilt camera during wall run,
wall jump off wall, max wall run time, gravity reduction while on wall,
cooldown before re-grabbing same wall. Requires CharacterController or Rigidbody.
Add camera tilt using Quaternion.Lerp.""",

    "player.swimming": """Write a complete Unity C# Swimming controller script.
Features: enter/exit water via trigger collider tagged 'Water', buoyancy force,
WASD swim direction + Space to surface + Ctrl to dive, reduced gravity in water,
breathing/oxygen timer with event OnDrown, swim speed vs walk speed.
Animator bool IsSwimming.""",

    # -----------------------------------------------------------------------
    #  COMBAT
    # -----------------------------------------------------------------------
    "combat.health": """Write a complete Unity C# HealthSystem script.
Features: maxHealth and currentHealth, TakeDamage(float amount, GameObject source),
Heal(float amount), Die() with UnityEvent OnDeath, OnDamaged(float amount, float currentHealth),
OnHealed events, invincibility frames after hit (iFrameDuration),
armor/damage reduction float (0-1), public HealthPercent property (0-1 for UI),
IsInvincible bool, IsDead bool. No UI — pure data, easy to subscribe to.""",

    "combat.melee": """Write a complete Unity C# MeleeAttack script.
Features: press Mouse0 to attack, attack combo system (up to 3 hits with timing window),
OverlapSphere hitbox on attack frame (use Animation Event OR coroutine timer),
damage falloff with distance from center, knockback force applied to Rigidbody targets,
hit stop (freeze frame 0.05s on hit), hit particle spawn at contact point,
cooldown between combos. Requires HealthSystem on target.""",

    "combat.ranged": """Write a complete Unity C# RangedWeapon script.
Features: Mouse1 to aim (FOV zoom), Mouse0 to shoot, Raycast OR Rigidbody projectile option,
ammo count (currentAmmo / maxAmmo), R to reload with reload time,
recoil (camera kick + recovery), bullet spread (accuracy degrades while moving),
muzzle flash particle spawn, hit decal spawn via Raycast,
empty click sound, full auto vs semi auto bool toggle. Animator Fire, Reload triggers.""",

    "combat.area_damage": """Write a complete Unity C# AreaOfEffect damage script.
Features: Explode(Vector3 position, float radius, float damage, float force) static method,
OverlapSphere to find all Rigidbodies and HealthSystems in radius,
damage falloff with distance (full at center, zero at edge),
AddExplosionForce to Rigidbodies, explosion particle effect spawn,
screen shake event (float intensity, float duration),
optional delay before explosion (for grenades). Self-contained, no MonoBehaviour needed.""",

    "combat.enemy_ai": """Write a complete Unity C# EnemyAI script using a state machine.
States: Idle (stand, look around), Patrol (move between waypoints array),
Detect (vision cone + hearing radius with SphereOverlap), Chase (NavMeshAgent follow player),
Attack (stop and attack when in range, cooldown between attacks),
Hurt (brief stagger), Dead (ragdoll or death anim).
Use NavMeshAgent for movement. [SerializeField] for detection radius, attack range,
patrol points Transform array. Gizmos for vision cone in editor.""",

    # -----------------------------------------------------------------------
    #  ANIMATION
    # -----------------------------------------------------------------------
    "animation.setup_controller": """Write Unity C# Editor code to create an Animator Controller asset at
'Assets/Animations/PlayerAnimator.controller' with the following setup:
Parameters: Speed (Float), IsGrounded (Bool), Jump (Trigger), Attack (Trigger), Die (Trigger), IsAiming (Bool).
States: Idle, Walk, Run, Jump, Fall, Land, Attack, Die.
Blend tree on Idle→Walk→Run driven by Speed parameter (0=Idle, 0.5=Walk, 1=Run).
Transitions: any→Jump on Jump trigger, Jump→Fall after 0.3s, Fall→Land on IsGrounded,
Land→Idle after 0.2s, any→Attack on Attack trigger (with exit time), any→Die on Die trigger.
Use UnityEditor.Animations namespace. Make it runnable as an Editor menu item.""",

    "animation.blend_tree": """Write Unity C# Editor code to create an Animator Controller with a 2D
directional blend tree for 8-directional movement.
Parameters: MoveX (Float), MoveZ (Float), Speed (Float).
Blend tree: 2D Simple Directional, motions for Forward/Back/Left/Right/ForwardLeft/ForwardRight/BackLeft/BackRight/Idle.
Add a locomotion layer and an upper body additive layer for aiming.
Create at 'Assets/Animations/CharacterAnimator.controller'.""",

    "animation.animator_script": """Write a complete Unity C# AnimatorController script to drive
character animations from a CharacterController or Rigidbody.
Reads velocity, grounded state, attack input, death. Updates all Animator parameters each frame.
Features: smooth Speed blending (Lerp, not instant),
predict landing for early Land transition,
AnimationEvent receiver methods (OnAttackHit, OnFootstep, OnReloadComplete),
IK look target (Animator.SetLookAtPosition toward enemy),
ragdoll enable on death (enable all Rigidbodies on death).""",

    # -----------------------------------------------------------------------
    #  PARTICLE EFFECTS  (code that creates/configures particle systems at runtime)
    # -----------------------------------------------------------------------
    "particles.fire": """Write a complete Unity C# script that creates a realistic fire particle system
entirely in code (no assets required).
Use ParticleSystem API to configure: main module (cone shape, 1-3s lifetime, 0.5-2 start size,
orange→yellow→transparent color over lifetime), emission (100 rate over time),
renderer (Additive blend), sub-emitter for sparks flying up,
light component that flickers (sin wave + noise),
heat distortion (second particle system with stretched billboard).
Create as a static CreateFire(Transform parent) method that returns the GameObject.""",

    "particles.explosion": """Write a complete Unity C# script that creates an explosion effect entirely in code.
Three layered particle systems:
1. Core flash (burst of 50, short lifetime, sphere shape, white→orange, additive)
2. Debris (burst of 30, high velocity outward, gravity affected, normal blend)
3. Smoke (continuous for 2s after, rising, grey→transparent, large particles)
Point light burst that fades over 0.3s.
Camera shake call (via static method or event).
Auto-destroy after all particles finish.
Static Explode(Vector3 position, float scale=1f) method.""",

    "particles.magic_aura": """Write a complete Unity C# script that creates a magical character aura in code.
Systems:
1. Orbiting particles (circle shape, particles orbit around character, emission additive, glow color)
2. Rising sparkles (cylinder shape, small bright particles float up and fade)
3. Ground rune circle (disc shape, flat emission)
Color configurable via gradient SerializeField, intensity pulsing over time via script.
SetColor(Color c) and SetIntensity(float t) public methods.
Attach to character root, auto-sizes to CharacterController bounds.""",

    "particles.blood_hit": """Write a complete Unity C# script for a blood/hit impact effect created in code.
Two modes: BloodHit (organic hit with blood splatter) and EnergyHit (sci-fi, no blood).
Features: burst of particles from hit point, oriented to surface normal,
blood decal projected onto surface (using ProjectionDecal or simple quad),
screen flash (Image overlay coroutine) on player hit,
hit number popup (instantiate TextMeshPro at world position, float up and fade),
camera impulse on heavy hits.
Static Hit(Vector3 position, Vector3 normal, float damage, HitType type) method.""",

    "particles.weather": """Write a complete Unity C# WeatherSystem script that creates weather effects in code.
Weather types: Clear, Rain, HeavyRain, Snow, Fog, Sandstorm.
For Rain: particle system falling from above camera (follows player),
raindrop ripple sprites on surfaces via Raycast, ambient rain audio volume blend.
For Snow: slower larger particles, accumulation (terrain paint over time).
For Fog: RenderSettings.fogDensity lerp.
SetWeather(WeatherType type, float transitionDuration) method.
Smooth transition between weather states.""",

    # -----------------------------------------------------------------------
    #  GAME SYSTEMS
    # -----------------------------------------------------------------------
    "systems.inventory": """Write a complete Unity C# Inventory system.
Classes: Item (ScriptableObject: id, name, icon, description, stackable, maxStack, weight),
Inventory (MonoBehaviour: List<ItemSlot>, capacity, AddItem, RemoveItem, HasItem, GetItem),
ItemSlot (struct: Item item, int count).
Events: OnItemAdded(Item, int), OnItemRemoved(Item, int), OnInventoryFull.
No UI code — pure data layer, fire events for UI to subscribe.
Singleton Inventory.Instance. Save/load via JSON to Application.persistentDataPath.""",

    "systems.save_load": """Write a complete Unity C# SaveSystem.
Features: SaveData class with all serialisable fields,
JsonUtility serialise to Application.persistentDataPath/save.json,
multiple save slots (slot index parameter),
encrypt/obfuscate with XOR key (anti-cheat for simple games),
SaveGame(int slot), LoadGame(int slot), DeleteSave(int slot), SaveExists(int slot) bool,
auto-save on application quit,
events: OnSaveComplete, OnLoadComplete, OnSaveNotFound.
Include example usage of saving player position, health, inventory count.""",

    "systems.dialogue": """Write a complete Unity C# Dialogue system (no external assets).
Classes: DialogueLine (speaker name, text, portrait Sprite, choices array),
DialogueTree (ScriptableObject containing DialogueLine array, branching via choice index),
DialogueManager (MonoBehaviour singleton, Display(DialogueTree tree), Next(), Choose(int index)),
TypewriterEffect (coroutine that reveals text char by char with configurable speed).
Events: OnDialogueStart, OnDialogueLine(DialogueLine), OnChoicePresented(string[]), OnDialogueEnd.
No UI — just data and events. Include a sample DialogueTree ScriptableObject creator.""",

    "systems.quest": """Write a complete Unity C# Quest system.
Classes: Quest (ScriptableObject: id, title, description, objectives array, rewards),
QuestObjective (description, type enum: KillCount/CollectItem/ReachLocation/TalkTo, required count, current count),
QuestManager (MonoBehaviour singleton, AcceptQuest, UpdateObjective, CompleteQuest, AbandonQuest),
Events: OnQuestAccepted, OnObjectiveUpdated, OnQuestCompleted, OnQuestFailed.
Auto-detect quest completion when all objectives met.
Save/load quest state to PlayerPrefs or JSON.
QuestGiver MonoBehaviour component for NPCs.""",

    "systems.object_pooling": """Write a complete Unity C# ObjectPool system.
Generic Pool<T> class and PoolManager MonoBehaviour singleton.
Features: pre-warm on Start (configurable count),
Get(string key) returns ready GameObject,
Return(GameObject) disables and returns to pool,
auto-expand if empty (configurable max size),
PooledObject component auto-returns after lifetime expires,
RegisterPool(string key, GameObject prefab, int initialSize) for setup,
works for bullets, particles, enemies, hit effects.""",

    # -----------------------------------------------------------------------
    #  UI
    # -----------------------------------------------------------------------
    "ui.health_bar": """Write a complete Unity C# HealthBar UI script using UI Toolkit or uGUI.
Features: smooth bar fill (Lerp with configurable speed),
separate front bar (instant) and back bar (delayed drain for visual feedback),
flash red on damage, flash green on heal,
show damage number that floats up then fades,
low health pulse animation (bar pulses red when below 25%),
boss health bar variant (wider, centered, with boss name),
subscribe to HealthSystem events (no polling).""",

    "ui.minimap": """Write a complete Unity C# Minimap system.
Approach: RenderTexture Camera pointing straight down, blitted to RawImage.
Features: zoom in/out scroll wheel, toggle between minimap and fullscreen map,
player arrow rotates with player,
POI markers (register/unregister MapMarker components),
map fog of war (render texture mask that reveals as player explores),
[SerializeField] for camera height, minimap size, zoom range.""",

    # -----------------------------------------------------------------------
    #  CAMERA
    # -----------------------------------------------------------------------
    "camera.shake": """Write a complete Unity C# CameraShake system (no Cinemachine required).
Trauma-based system: AddTrauma(float amount 0-1) accumulates,
shake magnitude = trauma^2,
Perlin noise drives offset X/Y and roll separately,
trauma decays over time (traumaDecayRate),
max offset and max roll [SerializeField],
static CameraShake.Instance.AddTrauma(0.5f) API,
screen flash (Image) on large trauma,
works by offsetting child camera relative to parent rig.""",

    "camera.third_person_follow": """Write a complete Unity C# ThirdPersonCamera script (no Cinemachine).
Features: orbit around player with mouse (X=horizontal, Y=vertical with clamp),
smooth follow (SmoothDamp for position),
collision detection (SphereCast toward player, pull camera in on hit),
camera zoom (scroll wheel, min/max distance),
lock-on target mode (Tab to cycle targets in range, camera interpolates),
shoulder offset (toggle left/right shoulder over-the-shoulder view),
[SerializeField] for all values.""",
}

def get_mechanic_prompt(key: str, custom: str | None = None, mode: str = "do") -> str:
    """
    Build the full prompt for a mechanic.
    key: dot-notation e.g. 'combat.melee', 'particles.fire'
    custom: additional user requirements
    mode: 'do' or 'teach'
    """
    base = MECHANICS.get(key)
    if not base:
        base = f"Write a complete Unity C# script for: {key}"

    if custom:
        base += f"\n\nAdditional requirements: {custom}"

    if mode == "teach":
        base = (
            f"TEACH MODE: First explain the concepts behind this mechanic in 4-5 sentences. "
            f"Then give numbered implementation steps the user can follow manually. "
            f"Then provide the complete code.\n\n" + base
        )

    return base

def list_categories() -> dict:
    cats: dict[str, list[str]] = {}
    for key in MECHANICS:
        cat, name = key.split(".", 1)
        cats.setdefault(cat, []).append(name)
    return cats
