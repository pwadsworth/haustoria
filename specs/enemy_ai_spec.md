# Enemy AI Spec — Haustoria

## 1. Purpose

This document defines enemy behavior systems for Haustoria.

The AI philosophy is:

- Simple enemies
- Readable behavior
- Movement pressure over precision combat
- Environmental hostility
- Swarm tension
- Moderate boss complexity

The majority of enemies should use:
- simple state machines
- deterministic logic
- lightweight pathing

Bosses and swarm encounters may use more advanced coordination.

---

# 2. AI Design Philosophy

## Core Principles

Enemy AI should:
- support traversal pressure
- encourage movement
- encourage object usage
- create atmosphere
- encourage Haustoria usage

Enemy AI should NOT:
- require precision reactions
- use highly tactical combat
- overwhelm the player with complexity
- dominate the movement systems

Movement and physics remain the core gameplay focus.

---

# 3. Enemy Intelligence Levels

## Standard Enemies

Use:
- simple patrol
- simple chase
- simple attack
- basic collision awareness

Do NOT use:
- advanced pathfinding
- prediction
- tactical teamwork

---

## Bosses and Swarms

May use:
- coordinated movement
- positioning pressure
- movement denial
- multi-phase attacks
- limited traversal awareness

Still avoid:
- precision-combat design
- extremely complex decision trees

---

# 4. AI Architecture

Recommended structure:

```text
entities/
    enemy.py
    boss.py

systems/
    enemy_ai_system.py
```

## AI Update Loop

Recommended order:

```python
update_detection()
update_state()
update_movement()
update_attack()
update_collision()
```

AI NOTE:
Keep AI logic separate from rendering and animation.

---

# 5. Enemy State Machine

Standard enemies use:

```text
IDLE
PATROL
CHASE
ATTACK
STUNNED
DEAD
```

Optional:

```text
RETREAT
SEARCH
SWARM
```

Bosses may extend this system.

---

# 6. Detection System

Enemies detect the player using:

- horizontal range
- vertical tolerance
- line-of-sight approximation

## Basic Detection

```python
distance_to_player <= detection_range
```

Recommended:
- avoid expensive raycasting initially
- use simple positional checks first

---

## Detection Rules

Enemies should:
- detect nearby movement
- lose interest if player escapes

Enemies should NOT:
- detect player across entire map
- track player perfectly through terrain

---

# 7. Patrol Behavior

Default state for most enemies.

## Patrol Logic

```python
move left/right
turn around at wall
turn around at edge
```

## Patrol Types

```text
STATIC
LINEAR
PLATFORM_LOOP
SHORT_RANGE_WANDER
```

Recommended default:
```text
LINEAR
```

---

# 8. Chase Behavior

When player detected:

```python
move toward player
```

## Chase Rules

Enemies:
- do not require advanced pathfinding
- should handle simple terrain
- may jump small gaps later

Avoid:
- full navigation meshes
- complex route planning

---

# 9. Attack Behavior

Combat is intentionally simple.

## Attack Trigger

```python
if distance_to_player <= attack_range:
    ATTACK
```

## Attack Types

```text
CONTACT_DAMAGE
SHORT_MELEE
PROJECTILE
SWARM_PRESSURE
```

Most enemies should use:
```text
CONTACT_DAMAGE
```

---

# 10. Attack Timing

Recommended:

```python
attack_windup = 0.2
attack_duration = 0.2
attack_cooldown = 0.8
```

Attacks should be:
- readable
- forgiving
- movement-reactable

---

# 11. Knockback and Stun

Enemies should react strongly to:
- thrown objects
- parries
- heavy attacks

## Stun Rules

```python
if stun_timer > 0:
    state = STUNNED
```

## Recommended Values

```python
light_stun = 0.4
heavy_stun = 1.0
```

---

# 12. Death Behavior

When enemy dies:

```python
play_death_animation()
disable_collision()
drop_resources()
```

Optional:
- spawn particles
- dissolve effect
- corpse remains

---

# 13. Haustoria Interaction

Most enemies should support Haustoria.

## Requirements

```python
can_be_haustoria_target = True
```

## During Haustoria

Enemy:
- may struggle visually
- may remain active
- may die during drain

Player:
- becomes vulnerable

---

# 14. Enemy Resource Values

Each enemy provides:

```python
water_value
chlorophyll_value
```

## Level Scaling

### Level 1
Enemies provide:
- generous resources

### Level 2
Enemies provide:
- moderate resources

### Level 3
Enemies become:
- primary survival source

---

# 15. Environmental Creature AI

Environmental creatures are simpler than enemies.

## Behavior Types

```text
AMBIENT
SWARM
CONTACT_HAZARD
PASSIVE
```

## Examples

```text
crawl_bug
swarm_gnat
flesh_mite
tunnel_crawler
```

Many environmental creatures:
- do not attack directly
- exist for pressure and atmosphere

---

# 16. Swarm AI

Swarm behavior is important.

Swarm enemies should:
- pressure movement
- deny safe positioning
- encourage throwing objects
- encourage repositioning

Swarm AI should NOT:
- individually behave intelligently

---

## Swarm Movement

Recommended behavior:

```python
move toward player
maintain loose group spacing
apply contact pressure
```

---

## Swarm Spawn Rules

Swarm encounters should:
- enter in waves
- emerge from environment
- increase panic gradually

Avoid:
- instant overwhelming floods

---

# 17. Boss AI Structure

Bosses use:
- multiple phases
- movement pressure
- arena interaction

Bosses should NOT:
- become precision reaction tests

---

## Boss State Structure

```text
INTRO
PHASE_1
PHASE_2
STUNNED
TRANSITION
DEFEATED
```

Optional:
```text
PHASE_3
```

---

# 18. Boss Arena Philosophy

Boss arenas should include:
- climbable surfaces
- verticality
- movement routes
- throwable objects
- bounce opportunities

Avoid:
- flat empty arenas

Bosses should interact with movement systems.

---

# 19. Boss Difficulty Philosophy

Boss difficulty should come from:
- movement pressure
- positioning
- environmental danger
- enemy summoning
- swarm behavior

NOT:
- frame-perfect combat

---

# 20. Boss Examples

## Dragonfly

Behavior:
- aerial movement
- swooping attacks
- movement pressure

Arena:
- vertical
- climbable
- open air

---

## Burrowyrm

Behavior:
- tunnel emergence
- charge attacks
- terrain pressure

Arena:
- narrow tunnels
- uneven terrain

---

## Bell Beast

Behavior:
- area denial
- environmental summoning
- swarm support

Arena:
- oppressive
- layered
- limited safe zones

---

# 21. Pathing Philosophy

Avoid:
- complex pathfinding
- navigation meshes
- expensive AI calculations

Prefer:
- direct movement
- collision-aware movement
- simple terrain handling

---

# 22. Terrain Interaction

Enemies may:
- collide with walls
- turn around at edges
- climb simple slopes
- use ladders later if needed

Avoid initially:
- advanced traversal
- wall-climbing enemies
- movement-tech-aware enemies

---

# 23. Object Interaction

Most enemies:
- react to thrown objects
- take knockback
- become stunned

Bosses may:
- destroy objects
- ignore light objects
- break terrain

---

# 24. Breakable Terrain Interaction

Some enemies or bosses may:
- destroy weak walls
- expose shortcuts
- reshape arenas

Do NOT heavily rely on:
- scripted destruction sequences

---

# 25. Darkness Interaction

Darkness should:
- increase tension
- obscure enemies partially
- encourage movement

Enemies should not:
- become invisible unfairly

Maintain gameplay readability.

---

# 26. Performance Rules

AI implementation should prioritize:
- stable framerate
- lightweight updates
- predictable behavior

Avoid:
- per-frame expensive calculations
- large behavior trees
- unnecessary pathfinding

---

# 27. Recommended Enemy Counts

## Standard Rooms

```text
1–4 enemies
```

## Swarm Rooms

```text
8–20 simple swarm entities
```

## Boss Rooms

```text
1 boss + optional swarm support
```

AI NOTE:
Swarm enemies should use extremely lightweight logic.

---

# 28. Prototype Enemy Set

The first prototype should include:

```text
basic_ground_enemy
swarm_bug
simple_environmental_creature
```

## Prototype Goals

Verify:
- patrol
- chase
- attack
- stun
- knockback
- Haustoria
- object damage

before building bosses.

---

# 29. AI Agent Build Order

The AI agent should implement:

1. Basic patrol enemy
2. Chase behavior
3. Attack behavior
4. Stun system
5. Haustoria support
6. Swarm behavior
7. Environmental creatures
8. Boss framework
9. Boss-specific logic

Do NOT build bosses first.

---

# 30. AI Agent Rules

The AI agent must:

1. Keep AI readable and modular
2. Use state machines
3. Avoid overengineering
4. Prioritize movement pressure
5. Keep combat forgiving
6. Keep AI lightweight
7. Use placeholder enemies first
8. Avoid precision combat assumptions
9. Keep bosses traversal-oriented
10. Keep the game playable after every AI addition

---

# 31. Recommended Next Document

After this Enemy AI Spec, create:

```text
Prototype Build Brief
```

This document should define:
- exact MVP scope
- what NOT to build yet
- first playable milestone
- required temporary art/assets
- debugging tools
- AI-agent coding priorities
