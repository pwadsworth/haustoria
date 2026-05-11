# Technical Architecture Spec

## Engine
Python Arcade using:
```python
arcade.PhysicsEnginePlatformer
```

## Main Window
```python
class HaustoriaGame(arcade.Window):
    def setup(self):
        pass
```

## File Structure
```text
haustoria/
├── main.py
├── constants.py
├── game/
├── entities/
├── systems/
├── levels/
├── assets/
└── docs/
```

## Tilemap Layers
```text
Platforms
Walls
Ladders
Hazards
Objects
Enemies
SavePoints
```

## Main Loop Order
```python
handle_state_transitions()
update_player_controller()
physics_engine.update()
update_objects()
update_enemies()
```
