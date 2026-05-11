# Level Map Spec — Haustoria

## 1. Purpose

This document defines the map structure, `.tmx` workflow, level composition rules, and gameplay-space conventions for Haustoria.

This spec is intended for:
- AI implementation agents
- Human level designers
- Tiled map creators

The game uses:
- Python Arcade
- `arcade.PhysicsEnginePlatformer`
- Tiled `.tmx` maps

---

# 2. World Structure

Haustoria uses a hybrid world structure.

## Structure Goals

- Mostly linear progression
- Optional loops and shortcuts
- Some backtracking
- Region-based progression
- Minimal puzzle gating
- Traversal-focused exploration

The intended progression:

```text
Level 1 → Level 2 → Level 3
```

However:
- regions may reconnect internally
- shortcuts may unlock
- optional areas may exist

---

# 3. Map Organization Philosophy

Use chunked zone maps instead of:
- one giant world map
- many tiny room files

Recommended structure:

```text
levels/

level_1/
    garden_surface.tmx
    garden_lower.tmx
    garden_boss.tmx

level_2/
    underground_entry.tmx
    underground_depths.tmx
    underground_hive.tmx

level_3/
    flesh_entry.tmx
    flesh_depths.tmx
    flesh_core.tmx
```

## Why Chunked Zones

This approach:
- simplifies loading
- simplifies debugging
- works well with Arcade
- avoids massive single-map performance issues
- keeps AI generation manageable

---

# 4. Camera Rules

Camera style is hybrid.

## Standard Areas

Use:
- smooth scrolling camera
- Hollow Knight-like movement

## Locked Challenge Rooms

Use:
- temporary room lock
- fixed camera bounds

Recommended for:
- boss arenas
- swarm encounters
- traversal challenges

---

# 5. Save Point Philosophy

Save points are sparse and meaningful.

## Save Point Rules

### Level 1
- fairly common
- low punishment
- acts as onboarding

### Level 2
- sparse
- encourages careful movement
- resource pressure increases

### Level 3
- extremely rare
- survival tension high
- player mastery expected

---

# 6. Resource Placement Philosophy

## Level 1

Water/light sources:
- common
- visible
- low-stress

Purpose:
- teach mechanics
- reduce survival pressure

## Level 2

Water/light sources:
- rare
- intentionally spaced
- may require risk

Purpose:
- increase tension

## Level 3

No environmental resource support.

Player expected to:
- use Haustoria frequently
- hunt enemies for survival

---

# 7. Object Persistence Rules

Objects persist while a level remains loaded.

## Persistence Behavior

### Objects SHOULD Persist:
- moved crates
- thrown spears
- rocks
- movable platforms

### Objects SHOULD Reset:
- if level unloads
- if player dies and reloads save
- if object becomes unreachable

AI NOTE:
Do not implement permanent world persistence initially.

---

# 8. Hazard Philosophy

Primary hazards:

- environmental creatures
- enemy swarms

Secondary hazards may include:
- pits
- unstable terrain
- darkness pressure

Avoid excessive:
- spike traps
- instant-kill platforming

The game focus is:
- movement flow
- object interaction
- enemy pressure

NOT precision death traps.

---

# 9. Puzzle Philosophy

Puzzle density is intentionally minimal.

The game is:
- traversal-focused
- movement-tech-focused
- interaction-focused

NOT a dedicated puzzle platformer.

## Acceptable Puzzle Types

- move object to reach ledge
- throw object to trigger switch
- break weak terrain
- use bounce movement creatively

Avoid:
- long logic puzzles
- cryptic progression blockers
- inventory puzzle systems

---

# 10. Secrets and Breakable Terrain

The game supports hidden breakable terrain.

## Breakable Wall Rules

Breakable walls should:
- visually differ slightly
- reward exploration
- hide:
  - shortcuts
  - resources
  - optional traversal routes

## Hidden Area Philosophy

Hidden areas should reward:
- movement mastery
- curiosity
- experimentation

NOT obscure puzzle solving.

---

# 11. Tiled Workflow Rules

Maps will be built manually in Tiled.

AI systems should assume:
- `.tmx` format
- consistent layer naming
- consistent object naming

---

# 12. Tile Size and Grid

Recommended:

```text
tile_size = 32x32
```

Reasoning:
- Arcade-friendly
- readable collision
- manageable sprite scale
- good movement readability

---

# 13. Required Tilemap Layers

Every `.tmx` map should support these layers.

## Collision Layers

```text
Platforms
Walls
Ladders
Hazards
```

## Gameplay Layers

```text
Objects
Enemies
EnemySpawns
SavePoints
BreakableWalls
LevelExits
```

## Resource Layers

```text
WaterSources
LightSources
```

## Decoration Layers

```text
Decor_Back
Decor_Mid
Decor_Front
```

AI NOTE:
Layer names must remain consistent across all maps.

---

# 14. Required Object Types

## Player Spawn

Object name:

```text
PlayerSpawn
```

Properties:

```text
spawn_id
```

---

## Save Point

Object name:

```text
SavePoint
```

Properties:

```text
save_id
```

---

## Enemy Spawn

Object name:

```text
EnemySpawn
```

Properties:

```text
enemy_type
patrol_range
facing_direction
```

---

## Level Exit

Object name:

```text
LevelExit
```

Properties:

```text
target_level
target_spawn
```

---

## Breakable Wall

Object name:

```text
BreakableWall
```

Properties:

```text
health
break_method
```

---

# 15. Level Transition Rules

Transitions should:
- preserve player state
- preserve resources
- reset enemies
- reload level objects

Recommended transition types:
- tunnel exits
- cave openings
- fleshy growth entrances
- vertical shaft drops

Avoid:
- abstract menu transitions

---

# 16. Enemy Placement Philosophy

## Level 1

Enemy density:
- low

Purpose:
- teach combat
- teach movement

## Level 2

Enemy density:
- moderate

Purpose:
- create traversal pressure

## Level 3

Enemy density:
- high

Purpose:
- create survival tension
- encourage Haustoria usage

---

# 17. Environmental Creature Rules

Environmental creatures are important atmosphere tools.

Examples:
- swarming bugs
- passive tunnel creatures
- crawling background organisms

These may:
- damage player
- obstruct movement
- create pressure
- simply create atmosphere

Not every creature must be combat-focused.

---

# 18. Swarm Encounter Rules

Swarm encounters should:
- pressure movement
- encourage object throwing
- encourage repositioning

Avoid:
- tank-heavy enemies
- long DPS fights

Combat should remain:
- quick
- readable
- movement-oriented

---

# 19. Boss Arena Rules

Boss rooms should:
- temporarily lock exits
- constrain camera
- contain traversal features
- contain object interaction opportunities

Boss rooms should NOT:
- rely entirely on flat arenas

Recommended features:
- climbable walls
- bounce objects
- destructible cover
- traversal platforms

---

# 20. Performance and Scope Rules

AI implementation should prioritize:
- stable gameplay
- readable collision
- modular maps

Avoid:
- excessively large maps
- procedural generation
- unnecessary physics simulation

---

# 21. Recommended First Test Map

Create:

```text
test_zone_01.tmx
```

Required contents:
- ground platforms
- one ladder
- one wall-cling section
- one save point
- one throwable object
- one enemy
- one breakable wall
- one level exit
- one bounce object

Purpose:
- verify all core systems work together

---

# 22. AI Implementation Notes

The AI agent should:
- load maps using Arcade tilemaps
- use consistent layer names
- separate collision layers from visual layers
- keep object definitions data-driven
- avoid hardcoding map-specific logic
- use object properties for gameplay configuration

The AI should build:
1. test map first
2. level loading system second
3. progression flow third

Do not attempt full content production before systems are stable.
