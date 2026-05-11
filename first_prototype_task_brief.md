# First Prototype Task Brief — Haustoria

## 1. Purpose

This document defines the exact scope and implementation priorities for the first playable prototype of Haustoria.

The prototype goal is:

```text
Vertical Slice Prototype
```

The prototype should:
- demonstrate the core gameplay loop
- validate movement feel
- validate object interaction
- validate Haustoria
- validate traversal pressure
- remain small and stable

This prototype is NOT intended to:
- contain final content
- contain full progression
- contain polished art
- contain all enemy types
- contain Level 3 systems

---

# 2. Prototype Philosophy

The prototype should prioritize:

1. Stability
2. Movement feel
3. Object interaction
4. Traversal readability
5. Core gameplay loop

The prototype should NOT prioritize:
- polish
- quantity of content
- advanced AI
- cinematic systems
- final balancing

---

# 3. Primary Prototype Goals

The prototype must successfully prove:

## Movement
- running
- jumping
- wall cling
- wall jump
- climbing
- dash
- slide
- roll
- bounce tech

---

## Object Interaction
- pickup
- carry
- drop
- throw
- bounce interaction
- breakable terrain interaction

---

## Combat
- simple attack
- object damage
- stun
- forgiving combat flow

---

## Haustoria
- resource recovery
- vulnerable attachment state
- risk/reward interaction

---

## World Interaction
- save point
- level transition
- breakable terrain
- traversal routes

---

# 4. Prototype Scope Boundary

The prototype should ONLY include:

```text
One small interconnected mini-level
```

The prototype should NOT include:
- full Level 2
- full Level 3
- advanced survival systems
- large-scale content
- advanced bosses
- complex puzzles

---

# 5. Prototype Map Structure

Recommended map structure:

```text
test_zone_01.tmx
test_zone_02.tmx
test_boss_room.tmx
```

Maps should connect together.

The level should demonstrate:
- verticality
- traversal
- movement flow
- object usage

---

# 6. Prototype Gameplay Flow

Recommended flow:

```text
spawn
→ traversal tutorial
→ object interaction section
→ enemy section
→ Haustoria section
→ breakable wall shortcut
→ swarm encounter
→ mini-boss room
→ level exit
```

---

# 7. Prototype Art Direction

Use:

```text
Placeholder art only
```

The prototype should prioritize:
- readability
- collision clarity
- iteration speed

Acceptable placeholder visuals:
- colored boxes
- simple silhouettes
- temporary sprites
- debug textures

AI NOTE:
Do not block implementation waiting for final art.

---

# 8. Prototype Audio Scope

Use:

```text
Minimal placeholder audio
```

Required sounds:
- jump
- land
- throw
- hit
- enemy death
- Haustoria drain
- save point activation

Avoid:
- large audio pipelines
- full soundtrack implementation

---

# 9. Prototype Animation Scope

Use:

```text
Basic state animation
```

Required player states:
- idle
- run
- jump
- fall
- wall cling
- attack
- Haustoria
- carry object

Placeholder animations acceptable.

---

# 10. Prototype Enemy Scope

Include:

## One Basic Enemy

Features:
- patrol
- chase
- attack
- stun
- Haustoria-compatible

---

## One Swarm Enemy

Features:
- movement pressure
- contact danger
- lightweight AI

Avoid:
- advanced bosses initially

---

# 11. Prototype Resource System Scope

Use:
- simplified water/chlorophyll system

The system should:
- create light pressure
- support Haustoria testing

The system should NOT:
- dominate gameplay
- create severe punishment loops

---

# 12. Systems Explicitly Excluded

DO NOT implement yet:

```text
Advanced bosses
Procedural generation
Complex pathfinding
Advanced inventory
Crafting systems
Dialogue systems
NPC quest systems
Online systems
Advanced lighting engine
Full save serialization
Complex particle systems
Pymunk physics
Advanced cinematic systems
```

---

# 13. Required Debug Features

The prototype MUST include:

```text
Visible hitboxes
Collision outlines
Player state text
Enemy state text
FPS display
Object state labels
Velocity display
Debug toggle key
```

Recommended debug key:

```text
F3
```

---

# 14. Prototype Performance Target

Target:

```text
60 FPS
```

The AI agent should prioritize:
- stable framerate
- readable physics
- deterministic behavior

Avoid:
- expensive update loops
- unnecessary calculations

---

# 15. Prototype Camera Rules

Use:
- smooth scrolling camera

Use locked rooms only for:
- swarm encounters
- mini-boss room

Camera must:
- prioritize player visibility
- support movement readability

---

# 16. Prototype Traversal Requirements

The level must require:
- jumping
- wall movement
- climbing
- dash timing
- bounce interaction

The level should NOT require:
- precision-perfect inputs

Movement should feel:
- forgiving
- expressive
- physics-driven

---

# 17. Prototype Object Requirements

Required objects:

```text
throwing_spear
heavy_rock
wooden_crate
breakable_wall
bounce_object
```

The prototype must prove:
- object carrying
- object throwing
- object bouncing
- terrain breaking

---

# 18. Prototype Combat Requirements

Combat should demonstrate:
- attack hitboxes
- stun
- knockback
- thrown-object combat
- swarm pressure

Combat should remain:
- simple
- readable
- secondary to movement

---

# 19. Prototype Haustoria Requirements

Haustoria must support:
- enemy attachment
- drain timer
- interruption on damage
- resource gain
- vulnerable state

The prototype should clearly communicate:
- risk/reward design

---

# 20. Prototype Save System Requirements

Include:
- one save point

The save point should:
- restore resources
- restore respawn
- demonstrate checkpoint flow

---

# 21. Prototype Transition Requirements

The prototype should:
- transition between at least 2 maps

Transitions should:
- preserve player state
- reload scene cleanly

---

# 22. Recommended Build Order

The AI agent should implement:

1. Window and game loop
2. Tilemap loading
3. Player movement
4. Collision
5. Jumping/falling
6. Climbing
7. Wall movement
8. Dash/slide/roll
9. Object interaction
10. Throwing
11. Bounce tech
12. Enemy foundation
13. Combat
14. Haustoria
15. Save system
16. Swarm enemy
17. Mini-boss room
18. Polish/debug pass

---

# 23. Prototype Completion Criteria

The prototype is considered successful when the player can:

- move smoothly
- wall cling
- wall jump
- climb
- dash
- slide
- roll
- pick up objects
- throw objects
- bounce off objects
- break terrain
- fight enemies
- use Haustoria
- restore resources
- save progress
- survive a swarm encounter
- transition between maps

at stable 60 FPS.

---

# 24. AI Agent Priority Rules

The AI agent must prioritize:

1. Stable movement
2. Stable collision
3. Readable interactions
4. Playability
5. Debuggability

The AI agent must NOT prioritize:
- polish over functionality
- advanced enemy intelligence
- cinematic systems
- content quantity

---

# 25. Final Prototype Philosophy

The prototype should feel like:

```text
A small but complete playable slice of the final game
```

The player should already understand:
- the movement identity
- the object interaction identity
- the survival tension
- the hostile atmosphere
- the traversal focus

even with placeholder art.

