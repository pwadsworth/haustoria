# Object Interaction Spec — Haustoria

## 1. Purpose

This document defines the complete object interaction system for Haustoria.

Object interaction is one of the game's primary gameplay pillars.

Objects are used for:
- traversal
- movement tech
- environmental interaction
- combat
- platforming
- pressure management

The object system should feel:
- physics-driven
- readable
- emergent
- modular
- forgiving

The game is NOT intended to be a precision physics simulator.

---

# 2. Core Design Philosophy

Objects should support:
- experimentation
- movement creativity
- environmental manipulation
- simple combat

Objects should NOT:
- require precise aiming
- require complex inventory management
- require realistic simulation

The player should quickly understand:
- what can be picked up
- what can be thrown
- what can be bounced on
- what can break terrain

---

# 3. Object System Overview

The object interaction system supports:

```text
Pickup
Carry
Drop
Throw
Bounce
Push
Break
Stun
Platforming
```

Objects exist both:
- as gameplay tools
- as environmental elements

---

# 4. Object Categories

## Light Objects

Examples:
- spears
- sticks
- small rocks
- pods

Behavior:
- easy to carry
- easy to throw
- minimal movement penalty

---

## Heavy Objects

Examples:
- crates
- large rocks
- root chunks

Behavior:
- slower movement
- reduced jump strength
- stronger impact

---

## Weapon Objects

Examples:
- spears
- sharp branches
- heavy stones

Behavior:
- damage enemies
- may stun enemies
- may bounce player

---

## Platform Objects

Examples:
- crates
- stable debris
- embedded roots

Behavior:
- support standing
- support bounce chaining
- support traversal

---

## Breakable Objects

Examples:
- weak pods
- brittle shells
- cracked debris

Behavior:
- destroyed on impact
- may release resources
- may expose secrets

---

# 5. Base Object Class

Recommended file:

```text
entities/interactable_object.py
```

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
    can_bounce: bool

    mass: float
    damage: int
    stun_power: float

    velocity_x: float
    velocity_y: float

    held_by: object | None

    ignore_player_collision_timer: float
```

---

# 6. Object State Machine

Objects use a lightweight state machine.

## States

```text
IDLE
HELD
THROWN
SLIDING
BROKEN
DISABLED
```

---

# 7. Pickup Rules

Input:

```text
F = pickup
```

## Pickup Conditions

Player may pick up object if:
- object is grabbable
- player is close enough
- player is not already holding object

---

## Pickup Logic

```python
pick_up(object)
```

Effects:
- object enters HELD state
- object physics disabled
- player collision disabled
- object follows player

---

# 8. Carrying Rules

Held objects should:
- visually attach to player
- move with player
- ignore normal physics

## Carry Position

```python
held_object.x = player.x + facing_direction * hold_offset_x
held_object.y = player.y + hold_offset_y
```

Recommended:

```python
hold_offset_x = 18
hold_offset_y = -4
```

---

## Carry Movement Restrictions

### Light Objects

No movement penalty.

### Heavy Objects

Apply:

```python
move_speed_multiplier = 0.75
jump_multiplier = 0.85
```

---

## Carry Restrictions

Player MAY:
- run
- jump
- dash
- roll
- wall cling

Player MAY NOT:
- slide

AI NOTE:
Sliding while holding objects creates unnecessary collision complexity.

---

# 9. Drop Rules

Input:

```text
F while holding = drop
```

## Drop Logic

```python
detach object
enable physics
place object slightly in front of player
```

## Drop Velocity

```python
object.velocity_x = player.velocity_x * 0.5
object.velocity_y = 0
```

---

# 10. Throw Rules

Input:

```text
J while holding = throw
```

No mouse aiming.

Throw direction uses:
- player movement vector
- fallback facing direction

---

## Throw Velocity

Recommended:

```python
throw_force_x = 8.0
throw_force_y = -1.5
```

## Throw Logic

```python
object.velocity_x = direction_x * throw_force_x
object.velocity_y = throw_force_y
```

---

## Throw Collision Ignore

Prevent immediate self-collision.

```python
ignore_player_collision_timer = 0.2
```

---

# 11. Object Physics Philosophy

The system should feel:
- responsive
- readable
- arcade-like

NOT:
- fully realistic

---

## Object Motion

Objects should:
- arc through air
- bounce lightly
- slide slightly
- collide consistently

Objects should NOT:
- rotate physically
- tumble realistically
- require advanced rigid-body simulation

---

# 12. Bounce Objects

Bounce objects support movement tech.

Examples:
- spears
- root spikes
- hardened branches

---

## Bounce Conditions

Player must:
- collide from above
- be falling

---

## Bounce Logic

```python
if player.velocity_y > 0:
    apply bounce
```

---

## Bounce Velocity

```python
bounce_velocity = -8.0
```

Stronger than normal jump.

---

## Optional Reduced Bounce

```python
if jump_pressed:
    full bounce
else:
    reduced bounce
```

---

## Bounce Cooldown

```python
object_bounce_cooldown = 0.2
```

Prevents infinite exploit loops.

---

# 13. Pushable Objects

Optional early implementation.

Heavy objects may:
- be pushed
- resist movement

---

## Push Rules

```python
if player pushes object:
    object.velocity_x += push_force
```

Avoid:
- complicated friction simulation

---

# 14. Object Damage System

Objects may damage:
- enemies
- breakable terrain
- environmental creatures

---

## Damage Formula

Simple recommended approach:

```python
impact_damage = base_damage + speed_modifier
```

Avoid:
- realistic force calculations

---

## Example Values

```python
light_object_damage = 1
heavy_object_damage = 2
spear_damage = 2
```

---

# 15. Stun System

Thrown objects may stun enemies.

## Example

```python
rock_stun_duration = 1.0
```

Heavy objects:
- stun longer

Light objects:
- stun briefly or not at all

---

# 16. Object Breakage

Breakable objects should:
- shatter
- disappear
- optionally spawn resources

---

## Break Conditions

```text
Heavy impact
Thrown collision
Enemy attack
Boss attack
```

---

## Break Behavior

```python
play_break_effect()
disable_collision()
remove_object()
```

Optional:
- particle effect
- sound
- resource spawn

---

# 17. Breakable Terrain Interaction

Some objects may break terrain.

Examples:
- heavy rock
- spear
- boss-thrown debris

---

## Terrain Break Rules

```python
if object.damage_type matches wall.break_method:
    break_wall()
```

---

# 18. Object Persistence

Objects persist:
- while level loaded

Objects reset:
- on level reload
- on death reload
- on leaving unloaded area

---

# 19. Object Respawning

Most objects should NOT respawn automatically.

Exceptions:
- tutorial areas
- infinite practice areas
- scripted boss arenas

---

# 20. Environmental Object Design

Objects should:
- visually communicate purpose
- be readable in darkness
- contrast with terrain

---

## Readability Rules

Bounce objects:
- visually sharp or vertical

Heavy objects:
- visibly bulky

Breakable objects:
- visibly cracked or unstable

---

# 21. Object Placement Philosophy

Objects should:
- support traversal
- support movement experimentation
- support combat creativity

Avoid:
- cluttering rooms excessively

---

## Level 1 Placement

Objects:
- common
- safe
- easy to experiment with

---

## Level 2 Placement

Objects:
- more strategic
- support traversal pressure

---

## Level 3 Placement

Objects:
- survival-critical
- movement-critical
- sparse but meaningful

---

# 22. Enemy Interaction

Enemies should:
- react to thrown objects
- receive knockback
- become stunned

Bosses may:
- destroy objects
- ignore light impacts
- create objects dynamically

---

# 23. Camera and Object Rules

The camera should prioritize:
- player visibility
- object readability

Thrown objects should remain visible briefly if possible.

Avoid:
- offscreen important throws

---

# 24. Tiled Object Workflow

Objects placed in Tiled should use properties.

## Example Properties

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

---

# 25. Recommended Prototype Objects

The first prototype should include:

```text
throwing_spear
heavy_rock
wooden_crate
breakable_pod
```

---

## Prototype Goals

Verify:
- pickup
- carry
- throw
- bounce
- stun
- break terrain

before expanding object variety.

---

# 26. Debug Requirements

AI implementation should support debug visualization.

Recommended:
- collision boxes
- object states
- bounce triggers
- throw vectors

---

# 27. Performance Rules

Avoid:
- advanced rigid-body simulation
- excessive collision checks
- hundreds of active physics objects

Prefer:
- lightweight arcade physics
- predictable movement
- stable interactions

---

# 28. AI Agent Rules

The AI agent must:

1. Keep objects modular
2. Use object properties instead of hardcoding
3. Keep object logic separate from player logic
4. Keep object logic separate from combat logic
5. Use placeholder sprites initially
6. Prioritize stable collision behavior
7. Keep object movement readable
8. Avoid realistic physics complexity
9. Preserve horizontal momentum during bounce
10. Keep the game playable after every object feature addition

---

# 29. Recommended Build Order

The AI agent should implement:

1. Pickup
2. Carry
3. Drop
4. Throw
5. Collision
6. Damage
7. Stun
8. Bounce
9. Breakable terrain
10. Pushable heavy objects

Do NOT implement advanced object chains first.

---

# 30. Recommended Next Document

After this Object Interaction Spec, create:

```text
Prototype Build Brief
```

This document should define:
- exact MVP scope
- systems intentionally excluded
- temporary assets
- debugging tools
- required prototype milestones
- AI-agent coding priorities
