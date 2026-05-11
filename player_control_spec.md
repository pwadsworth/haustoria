# Player Control Spec

## Design Goals
- Physics-driven interaction is primary
- Medium-floaty movement
- Simple combat
- Movement tech emerges naturally

## Input Map
- A/D: Move
- Space: Jump
- W/Up: Climb
- S/Down: Down input
- Shift: Dash
- F: Pick up / Drop
- J: Attack / Throw
- E: Haustoria

## Core Physics
```python
max_run_speed = 4.0
gravity = 0.32
max_fall_speed = 6.5
jump_velocity = -7.2
```

## Movement States
```text
IDLE
RUNNING
JUMPING
FALLING
WALL_CLINGING
WALL_BOUNCING
CLIMBING
DASHING
SLIDING
ROLLING
ATTACKING
USING_HAUSTORIA
```

## Dash
```python
dash_speed = 7.5
dash_duration = 0.18
dash_cooldown = 0.8
```

## Wall Movement
```python
wall_slide_speed = 1.5
wall_push_force = 4.5
wall_jump_window = 0.25
```

## Spear Bounce
```python
bounce_velocity = -8.0
```

## Combat
Attack direction follows movement vector.
