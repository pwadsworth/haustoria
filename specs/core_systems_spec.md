# Core Systems Spec

## Game Overview
Haustoria is a 2D side-scrolling platformer focused on:
- Physics-driven interaction
- Object manipulation
- Movement tech
- Simple combat
- Light survival pressure

## Game Loop
```python
while game_running:
    handle_input()
    update_player()
    update_entities()
    update_resources()
    handle_collisions()
    render()
```

## Player Variables
```python
health = 100
water = 100
chlorophyll = 100
```

## Resource Drain
```python
water -= 0.05 per second
chlorophyll -= 0.02 per second
```

## Haustoria
```python
if player presses "E" near enemy:
    lock_player_to_enemy()
    gain_water += X
    gain_chlorophyll += Y
```

## Saving
```python
if player interacts with bench:
    save_position()
    restore_resources()
```
