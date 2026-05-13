# Coding Standards Spec — Haustoria

## 1. Purpose

This document defines coding standards for the Haustoria project.

The main goal is:

```text
Code should be easy to understand, edit, debug, and extend.
```

This project is intended to be built with:
- Python
- Python Arcade
- Tiled `.tmx` maps
- Modular files and systems

The code should be suitable for:
- human editing
- AI-agent continuation
- beginner/intermediate Python readability

---

# 2. Core Coding Philosophy

Favor:

- simple code
- clear names
- small functions
- readable classes
- explicit behavior
- easy tuning
- predictable update order

Avoid:

- clever code
- hidden behavior
- deep inheritance chains
- overly abstract systems
- giant files
- hardcoded magic numbers
- complex one-line expressions

The code should read like an explanation of the game.

---

# 3. Project Structure Rules

Use the approved structure:

```text
haustoria/
│
├── main.py
├── constants.py
├── requirements.txt
├── README.md
│
├── game/
│   ├── __init__.py
│   ├── game_window.py
│   ├── player.py
│   ├── player_controller.py
│   ├── physics_helpers.py
│   ├── resources.py
│   ├── save_system.py
│   └── camera.py
│
├── entities/
│   ├── __init__.py
│   ├── base_entity.py
│   ├── enemy.py
│   ├── boss.py
│   ├── projectile.py
│   └── interactable_object.py
│
├── systems/
│   ├── __init__.py
│   ├── combat_system.py
│   ├── haustoria_system.py
│   ├── object_interaction_system.py
│   ├── resource_system.py
│   ├── collision_system.py
│   └── level_loader.py
│
├── levels/
├── assets/
└── docs/
```

AI NOTE:
Do not put all logic into `main.py` or `game_window.py`.

---

# 4. File Responsibility Rules

Each file should have one clear responsibility.

## `main.py`

Only starts the game.

```python
from game.game_window import HaustoriaGame
import arcade

if __name__ == "__main__":
    window = HaustoriaGame()
    window.setup()
    arcade.run()
```

---

## `constants.py`

Stores tunable values.

Examples:

```python
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Haustoria"

GRAVITY = 0.32
PLAYER_MOVE_SPEED = 4.0
PLAYER_JUMP_SPEED = 7.2
```

AI NOTE:
If a value affects game feel, put it in `constants.py`.

---

## `game_window.py`

Handles:
- Arcade window
- setup
- update order
- drawing
- level loading
- top-level game state

Should NOT contain:
- detailed player movement logic
- detailed enemy AI
- object interaction internals
- Haustoria drain calculations

---

## `player.py`

Stores player sprite data.

Should contain:
- player sprite
- player state fields
- resource values
- animation references

Should NOT contain:
- full movement system
- object interaction system
- enemy logic

---

## `player_controller.py`

Handles player movement and input interpretation.

Should contain:
- movement input
- jump logic
- dash logic
- wall logic
- roll/slide logic
- state transitions

---

## `systems/`

Each system controls one gameplay area.

Examples:
- `combat_system.py`
- `object_interaction_system.py`
- `haustoria_system.py`
- `resource_system.py`

AI NOTE:
Systems should communicate through clear method calls, not hidden global state.

---

# 5. Naming Conventions

Use Python standard naming.

## Files

Use lowercase snake_case.

```text
player_controller.py
object_interaction_system.py
haustoria_system.py
```

---

## Variables and Functions

Use lowercase snake_case.

```python
player_speed = 4.0
is_touching_wall = False

def update_player_movement():
    pass
```

---

## Classes

Use PascalCase.

```python
class Player:
    pass

class Enemy:
    pass

class ObjectInteractionSystem:
    pass
```

---

## Constants

Use uppercase snake_case.

```python
PLAYER_MAX_SPEED = 4.0
DASH_COOLDOWN = 0.8
```

---

## Booleans

Start with words like:

```text
is_
has_
can_
should_
```

Examples:

```python
is_grounded
has_key
can_dash
should_respawn
```

---

# 6. Function Design Rules

Functions should be short and focused.

Preferred function size:

```text
5–30 lines
```

If a function grows too large, split it.

---

## Good Function Example

```python
def can_start_dash(player):
    return player.is_grounded and player.dash_cooldown_timer <= 0
```

---

## Avoid

```python
def update_everything():
    # movement
    # enemies
    # resources
    # combat
    # camera
    # saving
    pass
```

---

# 7. Class Design Rules

Use simple classes.

Prefer composition over deep inheritance.

Good:

```python
class Player(arcade.Sprite):
    pass

class PlayerController:
    def update(self, player, delta_time):
        pass
```

Avoid:

```python
class AdvancedPhysicsCombatResourcePlayerEntityActor:
    pass
```

---

# 8. State Machine Rules

Use readable string constants or enums.

Recommended:

```python
PLAYER_STATE_IDLE = "idle"
PLAYER_STATE_RUNNING = "running"
PLAYER_STATE_JUMPING = "jumping"
```

Or:

```python
from enum import Enum

class PlayerState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    JUMPING = "jumping"
```

AI NOTE:
Use whichever is simpler and consistent. Do not mix several state styles.

---

# 9. Update Loop Standards

The update order should be consistent.

Recommended:

```python
def on_update(self, delta_time):
    self.update_input_timers(delta_time)
    self.player_controller.update(delta_time)
    self.physics_engine.update()
    self.object_system.update(delta_time)
    self.enemy_system.update(delta_time)
    self.combat_system.update(delta_time)
    self.haustoria_system.update(delta_time)
    self.resource_system.update(delta_time)
    self.update_camera()
```

AI NOTE:
Changing update order can break physics. Document any changes.

---

# 10. Input Handling Standards

Arcade key events should set input flags.

Do not put full movement behavior directly inside key press events.

Good:

```python
def on_key_press(self, key, modifiers):
    if key == arcade.key.A:
        self.input_left = True
```

Then movement happens in update.

Avoid:

```python
def on_key_press(self, key, modifiers):
    self.player.center_x -= 50
```

---

# 11. Constants and Tuning Rules

All tunable gameplay values should be constants.

Examples:
- jump speed
- gravity
- dash cooldown
- wall slide speed
- throw force
- attack duration
- resource drain rate

Avoid magic numbers:

Bad:

```python
self.player.change_y = -7.2
```

Good:

```python
self.player.change_y = -PLAYER_JUMP_SPEED
```

---

# 12. Comments and Docstrings

Use comments to explain WHY, not obvious WHAT.

Good:

```python
# Prevent immediate wall re-cling after wall jump.
player.wall_bounce_timer = WALL_BOUNCE_LOCKOUT
```

Avoid:

```python
# Add one to x
x += 1
```

---

## Docstrings

Use docstrings for systems and non-obvious functions.

```python
def start_haustoria(player, enemy):
    """Locks the player to an enemy and starts resource drain."""
```

---

# 13. Debug Code Standards

Debug tools are required.

Use one global debug flag:

```python
DEBUG_MODE = False
```

Recommended debug features:
- hitbox drawing
- player state text
- enemy state text
- velocity display
- FPS display
- object labels
- collision outlines

Toggle:

```text
F3
```

AI NOTE:
Do not delete debug tools after prototype. Keep them toggleable.

---

# 14. Error Handling Rules

Prefer clear failure messages.

Good:

```python
if "Walls" not in self.scene:
    raise ValueError("Tilemap is missing required layer: Walls")
```

Avoid silent failure.

Bad:

```python
try:
    load_level()
except:
    pass
```

---

# 15. Asset Loading Rules

Use clear asset paths.

Recommended:

```python
ASSET_PATH = "assets"
PLAYER_SPRITE_PATH = "assets/sprites/player/player_idle.png"
```

If an asset is missing, use a placeholder sprite when possible.

AI NOTE:
Missing final art should not block development.

---

# 16. Tiled Map Rules in Code

Layer names must be constants or clearly documented.

Example:

```python
LAYER_WALLS = "Walls"
LAYER_PLATFORMS = "Platforms"
LAYER_LADDERS = "Ladders"
LAYER_OBJECTS = "Objects"
```

Do not scatter raw layer strings everywhere.

---

# 17. Entity Loading Rules

Entity creation should be data-driven from Tiled properties.

Good:

```python
enemy_type = tiled_object.properties["enemy_type"]
create_enemy(enemy_type, tiled_object.center_x, tiled_object.center_y)
```

Avoid:

```python
if current_level == "garden":
    spawn_dragonfly()
```

---

# 18. System Communication Rules

Systems may receive:
- player
- scene
- sprite lists
- delta time
- game state

Avoid:
- systems importing each other in circles
- global mutable state
- hidden dependencies

Good:

```python
self.object_system.update(self.player, self.object_list, delta_time)
```

---

# 19. Collision Rules

Collision logic should be centralized where practical.

Use helper functions for repeated collision checks.

Recommended file:

```text
game/physics_helpers.py
```

Example:

```python
def is_player_above_object(player, obj):
    return player.bottom >= obj.top - COLLISION_TOLERANCE
```

---

# 20. Placeholder Rules

Use placeholders freely during prototype.

Acceptable placeholders:
- colored rectangles
- simple generated textures
- temporary sprites
- simple sounds

AI NOTE:
Playable prototype comes before final art.

---

# 21. Performance Rules

Avoid expensive work every frame.

Avoid:
- loading assets inside update loops
- scanning every sprite list unnecessarily
- complex pathfinding
- creating many temporary objects every frame

Good:
- load assets once
- reuse lists
- update only active entities

---

# 22. Testing Rules

Each new feature should be tested in the prototype map.

Minimum manual test after changes:

```text
Can the game launch?
Can the player move?
Can the player jump?
Can collision still work?
Can debug mode still toggle?
```

For system-specific changes, test the relevant interaction immediately.

---

# 23. AI Agent Coding Rules

The AI agent must:

1. Keep code readable
2. Keep files small
3. Keep functions focused
4. Keep constants tunable
5. Avoid clever abstractions
6. Avoid deep inheritance
7. Avoid giant manager classes
8. Avoid hiding logic in event handlers
9. Keep debug tools available
10. Keep the game runnable after every major change

---

# 24. Forbidden Patterns

Avoid these unless explicitly approved:

```text
One huge main.py
Hardcoded level-specific hacks
Unclear abbreviations
Complex metaprogramming
Unnecessary decorators
Large inheritance chains
Silent exception handling
Magic numbers
Premature optimization
Full custom physics engine before Arcade physics is tested
```

---

# 25. Preferred Coding Style

Prefer this style:

```python
def update_dash(player, delta_time):
    if player.dash_cooldown_timer > 0:
        player.dash_cooldown_timer -= delta_time

    if not player.is_dashing:
        return

    player.dash_timer -= delta_time

    if player.dash_timer <= 0:
        stop_dash(player)
```

Readable.
Explicit.
Easy to edit.

---

# 26. Final Standard

When choosing between two solutions:

Choose the one that is:

```text
easier to read
easier to debug
easier to change
less clever
more explicit
```

THE MOST IMPORTANT RULE IS:
Haustoria should be built as a clear, modular Arcade project that a human or AI can keep extending without getting lost.