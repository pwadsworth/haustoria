# Entity Spec — Haustoria

## 1. Purpose

This document defines the entities used in Haustoria and the data fields an AI agent should implement for each.

This spec supports:
- Python Arcade
- Tiled `.tmx` maps
- `arcade.PhysicsEnginePlatformer`
- Modular entity and system design

The goal is to make all gameplay objects data-driven, readable, and easy to expand.

---

# 2. Entity Categories

Haustoria uses the following entity categories:

```text
Player
Interactable Objects
Enemies
Bosses
Environmental Creatures
Hazards
Breakable Terrain
Save Points
Resource Sources
Level Exits
Triggers
```

AI NOTE:
Each category should map to a clear Python class or data structure. Avoid hardcoding entity behavior directly into `game_window.py`.

---

# 3. Base Entity

All active gameplay entities should inherit from or follow a shared base entity structure.

Recommended file:

```text
entities/base_entity.py
```

## Required Fields

```python
class BaseEntity:
    id: str
    entity_type: str
    sprite: arcade.Sprite
    position_x: float
    position_y: float
    velocity_x: float
    velocity_y: float
    is_active: bool
    is_visible: bool
    collision_enabled: bool
```

## Optional Fields

```python
health: int
max_health: int
facing_direction: int
state: str
tags: list[str]
```

AI NOTE:
Not every entity needs health or state behavior. Keep the base entity simple.

---

# 4. Player Entity

Recommended file:

```text
game/player.py
```

The player is the daikon character controlled by the user.

## Required Fields

```python
class Player(arcade.Sprite):
    health: int
    max_health: int

    water: float
    max_water: float

    chlorophyll: float
    max_chlorophyll: float

    velocity_x: float
    velocity_y: float

    facing_direction: int
    movement_vector: tuple[float, float]

    current_state: str
    previous_state: str

    held_object: object | None

    is_grounded: bool
    is_touching_wall: bool
    is_climbing: bool
    is_dashing: bool
    is_sliding: bool
    is_rolling: bool
    is_using_haustoria: bool
    is_stunned: bool
    is_dead: bool
```

## Timers

```python
jump_buffer_timer: float
coyote_timer: float
dash_timer: float
dash_cooldown_timer: float
slide_timer: float
roll_timer: float
wall_bounce_timer: float
attack_cooldown_timer: float
haustoria_timer: float
```

## Design Notes

The player entity should store state and values.

The player controller should handle behavior.

AI NOTE:
Keep `Player` and `PlayerController` separate. The sprite should not contain all movement logic.

---

# 5. Interactable Object Entity

Recommended file:

```text
entities/interactable_object.py
```

Objects are central to gameplay. They can be picked up, dropped, thrown, used as platforms, used as weapons, or used to break terrain.

## Required Fields

```python
class InteractableObject(arcade.Sprite):
    object_id: str
    object_type: str

    is_grabbable: bool
    is_held: bool
    is_throwable: bool
    is_platform: bool
    is_breakable: bool

    mass: float
    damage: int
    stun_power: float

    velocity_x: float
    velocity_y: float

    held_by: object | None
    ignore_player_collision_timer: float
```

## Object Type Tags

```text
LIGHT_OBJECT
HEAVY_OBJECT
WEAPON_OBJECT
PLATFORM_OBJECT
BREAKABLE_OBJECT
BOUNCE_OBJECT
```

Objects may have more than one tag.

Examples:

```text
spear = LIGHT_OBJECT + WEAPON_OBJECT + BOUNCE_OBJECT
rock = HEAVY_OBJECT + WEAPON_OBJECT
crate = HEAVY_OBJECT + PLATFORM_OBJECT
weak_pod = BREAKABLE_OBJECT + LIGHT_OBJECT
```

## Tiled Properties

For objects placed in Tiled:

```text
object_type
mass
damage
stun_power
is_grabbable
is_throwable
is_platform
can_bounce
```

AI NOTE:
Use Tiled object properties to configure object behavior instead of making a separate class for every small object.

---

# 6. Enemy Entity

Recommended file:

```text
entities/enemy.py
```

Enemies are active hostile entities that can patrol, chase, attack, be stunned, die, and be used for Haustoria.

## Required Fields

```python
class Enemy(BaseEntity):
    enemy_type: str

    health: int
    max_health: int

    damage: int
    contact_damage: int

    move_speed: float
    patrol_range: float
    detection_range: float
    attack_range: float

    state: str
    facing_direction: int

    can_be_haustoria_target: bool
    water_value: float
    chlorophyll_value: float

    stun_timer: float
    attack_cooldown_timer: float
```

## Enemy States

```text
IDLE
PATROL
CHASE
ATTACK
STUNNED
DEAD
```

## Tiled Properties

```text
enemy_type
health
damage
move_speed
patrol_range
detection_range
attack_range
water_value
chlorophyll_value
```

AI NOTE:
Enemy behavior should be handled by an enemy AI system or enemy update method, not by the level loader.

---

# 7. Boss Entity

Recommended file:

```text
entities/boss.py
```

Bosses are larger enemy entities with more complex state patterns.

## Required Fields

```python
class Boss(Enemy):
    boss_id: str
    phase: int
    max_phase: int

    arena_id: str
    is_active: bool
    intro_played: bool
    defeated: bool

    attack_pattern_index: int
    phase_transition_health_thresholds: list[int]
```

## Boss States

```text
INACTIVE
INTRO
PHASE_1
PHASE_2
PHASE_3
STUNNED
DEFEATED
```

## Boss Arena Requirements

Bosses should be linked to:
- arena boundaries
- camera lock triggers
- entrance lock
- exit unlock
- optional save point nearby

## Tiled Properties

```text
boss_type
boss_id
arena_id
health
phase_count
```

---

# 8. Environmental Creature Entity

Recommended file:

```text
entities/environmental_creature.py`
```

Environmental creatures may be hostile, passive, decorative, or swarm-based.

They support atmosphere and movement pressure.

## Required Fields

```python
class EnvironmentalCreature(BaseEntity):
    creature_type: str
    behavior_type: str

    damage: int
    contact_damage_enabled: bool

    movement_pattern: str
    swarm_id: str | None

    can_be_killed: bool
    can_be_haustoria_target: bool
```

## Behavior Types

```text
PASSIVE
AMBIENT
HOSTILE_CONTACT
SWARM
OBSTACLE
```

## Examples

```text
crawl_bug
swarm_gnat
root_mite
tunnel_worm_small
flesh_fly
```

AI NOTE:
Not all environmental creatures need combat logic. Some can simply animate or move on a path.

---

# 9. Hazard Entity

Recommended file:

```text
entities/hazard.py
```

Hazards are non-enemy damage sources.

## Required Fields

```python
class Hazard(BaseEntity):
    hazard_type: str
    damage: int
    damage_interval: float
    is_instant_death: bool
    knockback_force: float
```

## Supported Hazard Types

```text
PIT
DARKNESS_ZONE
TOXIC_AREA
MOVING_CREATURE
CRUSHING_TERRAIN
```

AI NOTE:
Avoid heavy spike-trap design. Hazards should mostly support atmosphere, traversal, and swarm pressure.

---

# 10. Breakable Terrain Entity

Recommended file:

```text
entities/breakable_terrain.py
```

Breakable terrain supports hidden routes, optional shortcuts, and light secrets.

## Required Fields

```python
class BreakableTerrain(arcade.Sprite):
    breakable_id: str
    health: int
    break_method: str
    required_damage_type: str | None
    reveals_secret: bool
    target_layer_change: str | None
```

## Break Methods

```text
ANY_DAMAGE
THROWN_OBJECT
HEAVY_OBJECT
SPEAR
BOSS_ATTACK
```

## Tiled Properties

```text
breakable_id
health
break_method
reveals_secret
```

AI NOTE:
Breakable terrain should be visually hinted. It should not hide required progression unless clearly taught.

---

# 11. Save Point Entity

Recommended file:

```text
entities/save_point.py
```

Save points are bench-like checkpoints.

## Required Fields

```python
class SavePoint(BaseEntity):
    save_id: str
    is_activated: bool
    restore_resources: bool
    respawn_x: float
    respawn_y: float
```

## Tiled Properties

```text
save_id
restore_resources
```

## Behavior

When player interacts:

```python
save_position()
restore_water()
restore_chlorophyll()
set_respawn_point()
```

AI NOTE:
Save points should be sparse and meaningful.

---

# 12. Resource Source Entity

Recommended file:

```text
entities/resource_source.py
```

Resource sources restore water or chlorophyll.

## Required Fields

```python
class ResourceSource(BaseEntity):
    source_id: str
    resource_type: str
    amount: float
    respawns: bool
    respawn_timer: float
    is_available: bool
```

## Resource Types

```text
WATER
CHLOROPHYLL
BOTH
```

## Level Rules

### Level 1
Common sources.

### Level 2
Rare sources.

### Level 3
No environmental sources.

AI NOTE:
In Level 3, resource recovery should come from Haustoria only.

---

# 13. Level Exit Entity

Recommended file:

```text
entities/level_exit.py
```

Level exits move the player between `.tmx` maps.

## Required Fields

```python
class LevelExit(BaseEntity):
    exit_id: str
    target_level: str
    target_spawn: str
    requires_condition: str | None
```

## Tiled Properties

```text
exit_id
target_level
target_spawn
requires_condition
```

---

# 14. Trigger Entity

Recommended file:

```text
entities/trigger.py
```

Triggers are invisible regions that cause scripted changes.

## Required Fields

```python
class Trigger(BaseEntity):
    trigger_id: str
    trigger_type: str
    one_shot: bool
    is_triggered: bool
```

## Trigger Types

```text
CAMERA_LOCK
BOSS_START
SWARM_START
CHECKPOINT_HINT
MUSIC_CHANGE
LEVEL_EVENT
```

AI NOTE:
Use triggers sparingly. Do not script basic movement or exploration through triggers.

---

# 15. Entity Loading From Tiled

The level loader should:
1. Read map layers
2. Detect object layer entries
3. Read object properties
4. Instantiate matching entity class
5. Add entity to the correct scene/system list

Example:

```python
if tiled_object.name == "EnemySpawn":
    create_enemy_from_properties(tiled_object.properties)
```

---

# 16. Recommended Entity Lists

The game window or level manager should maintain:

```python
self.enemy_list
self.object_list
self.breakable_list
self.resource_source_list
self.save_point_list
self.trigger_list
self.level_exit_list
self.environmental_creature_list
```

AI NOTE:
Do not search every sprite in the scene for every system. Keep specific lists for specific systems.

---

# 17. Collision Groups

Recommended collision group logic:

## Player Collides With

```text
Walls
Platforms
Ladders
Hazards
Enemies
Objects
BreakableTerrain
ResourceSources
SavePoints
LevelExits
Triggers
```

## Thrown Objects Collide With

```text
Walls
Platforms
Enemies
BreakableTerrain
Switches
Objects
```

## Enemies Collide With

```text
Walls
Platforms
Player
ThrownObjects
BreakableTerrain
```

AI NOTE:
Held objects should temporarily disable collision against the player.

---

# 18. Object Lifetime Rules

## Persistent While Level Loaded

- thrown objects
- moved objects
- stunned enemies
- broken breakable terrain

## Reset On Reload

- enemy positions
- object positions
- breakable wall state
- resource availability

AI NOTE:
Permanent persistence is not required for the first prototype.

---

# 19. Naming Conventions

Use lowercase snake_case for code values.

Examples:

```text
burrowyrm
dragonfly
aphid_swarm
heavy_rock
throwing_spear
garden_save_01
```

Use PascalCase for Tiled object names only when they represent entity classes.

Examples:

```text
EnemySpawn
SavePoint
LevelExit
BreakableWall
```

---

# 20. Required First Prototype Entities

The first playable prototype should include:

```text
Player
SavePoint
LevelExit
BasicEnemy
ThrowableRock
ThrowingSpear
BreakableWall
WaterSource
LightSource
Ladder
EnvironmentalCreature
```

## Prototype Success Criteria

The player can:
- move through a map
- pick up and throw objects
- damage an enemy
- break a wall
- restore resources
- save
- transition to another level
- encounter simple environmental creatures

---

# 21. AI Agent Rules

The AI agent must:

1. Keep entities modular
2. Avoid hardcoding specific level behavior
3. Load entity settings from Tiled properties where possible
4. Keep player behavior separate from enemy behavior
5. Keep combat separate from movement
6. Keep object interaction separate from resource survival
7. Use placeholder sprites when final art is missing
8. Keep the game runnable after each entity type is added
9. Add debug visuals for collision boxes and triggers
10. Avoid overengineering boss logic before basic enemies work

---

# 22. Recommended Next Document

After this Entity Spec, create:

```text
Enemy AI Spec
```

That document should define:
- patrol logic
- chase logic
- attack logic
- swarm behavior
- boss behavior templates
- Haustoria target behavior
