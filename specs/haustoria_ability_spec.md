# Haustoria Ability Spec — Haustoria

## 1. Purpose

This document defines the Haustoria ability system.

Haustoria is:
- a core thematic mechanic
- the primary survival recovery system
- a risk/reward interaction tool

The system should feel:
- invasive
- vulnerable
- unsettling
- simple to understand
- mechanically readable

Haustoria is NOT intended to be:
- a complex combo system
- precision combat
- a long cinematic mechanic

---

# 2. Core Design Philosophy

Haustoria exists to:
- recover water
- recover chlorophyll
- pressure enemy engagement
- reinforce the plant-parasite theme

The mechanic should encourage:
- risky close interaction
- aggressive recovery
- survival improvisation

The mechanic should NOT:
- dominate combat
- interrupt gameplay flow excessively
- require precise execution

---

# 3. Core Gameplay Loop

The player:
1. weakens or approaches enemy
2. activates Haustoria
3. attaches to enemy
4. drains resources
5. becomes vulnerable during drain
6. disengages

---

# 4. Activation Rules

## Input

```text
E = Haustoria
```

---

## Activation Conditions

Player may activate Haustoria if:

- enemy is in range
- enemy supports Haustoria
- player is not stunned
- player is not already using Haustoria
- enemy is not already dead

---

## Range Rules

Recommended:

```python
haustoria_range = 20-28 pixels
```

The range should feel:
- close
- dangerous
- intentional

---

# 5. Valid Targets

Most enemies should support Haustoria.

## Valid Target Types

```text
basic enemies
swarm enemies
environmental hostile creatures
some bosses
```

---

## Invalid Targets

Examples:
- mechanical enemies
- armored shell enemies
- environmental hazards
- dead enemies

---

# 6. Haustoria State

Player enters:

```text
USING_HAUSTORIA
```

Enemy may enter:

```text
DRAINED
```

Optional:
```text
STRUGGLING
```

---

# 7. Player Behavior During Haustoria

While attached:

Player:
- cannot move
- cannot dash
- cannot attack
- cannot jump
- remains vulnerable

---

## Allowed Actions

Player MAY:
- cancel manually later if desired
- rotate facing direction visually

---

## Forbidden Actions

Player MAY NOT:
- wall cling
- slide
- roll
- throw objects

---

# 8. Attachment Logic

When activated:

```python
lock player position to enemy
```

Recommended:

```python
player.x = enemy.x + attach_offset_x
player.y = enemy.y + attach_offset_y
```

---

## Visual Behavior

The player should:
- visually latch onto enemy
- appear rooted or connected

This may use:
- vines
- roots
- tendrils
- silhouette changes

---

# 9. Resource Drain

Haustoria drains:

```text
water
chlorophyll
enemy health
```

---

## Recommended Values

```python
drain_duration = 1.5

drain_rate_water = 2.0 / second
drain_rate_chlorophyll = 1.5 / second

enemy_drain_damage = 1.0 / second
```

---

## Drain Timing

Drain should:
- begin immediately
- occur continuously
- end automatically after duration

---

# 10. Drain Limits

The player cannot exceed:

```python
max_water
max_chlorophyll
```

Excess drain is ignored.

---

# 11. Enemy Resource Values

Enemies provide different amounts.

## Level 1

Enemies provide:
- generous resources

Purpose:
- teach mechanic safely

---

## Level 2

Enemies provide:
- moderate resources

Purpose:
- increase tension

---

## Level 3

Enemies become:
- primary survival source

Purpose:
- create predatory survival loop

---

# 12. Interrupt Conditions

Haustoria ends if:

```text
player takes damage
enemy dies
duration expires
enemy becomes invalid
```

---

## Interrupt Logic

```python
cancel_haustoria()
restore_player_control()
```

---

# 13. Vulnerability Rules

While using Haustoria:

Player:
- remains damageable
- has reduced mobility
- is committed to action

This is the mechanic's primary risk.

---

# 14. Enemy Reaction

Enemies may:
- struggle visually
- continue moving slowly
- attempt attacks
- panic

Simple enemies:
- often remain vulnerable

Bosses:
- may resist aggressively

---

# 15. Boss Haustoria Rules

Bosses should:
- support limited Haustoria opportunities
- expose temporary weak states

Bosses should NOT:
- allow constant draining

---

## Boss Drain Windows

Recommended:
- stagger state
- exposed phase
- stunned phase

---

# 16. Resource Source Replacement

In Level 3:
- environmental resources become extremely rare or absent

Haustoria becomes:
- the primary recovery mechanic

This creates:
- survival pressure
- aggressive play incentives

---

# 17. Visual Effects

Haustoria should visually communicate:
- parasitic attachment
- draining
- vulnerability
- organic horror

---

## Recommended Effects

- root/tendril lines
- pulsing glow
- inverse silhouette
- subtle screen distortion
- enemy discoloration

Avoid:
- excessive visual clutter

---

# 18. Audio Design

Recommended sounds:
- wet/rooting sound
- draining pulse
- subtle breathing
- enemy distress

The sound design should feel:
- organic
- uncomfortable
- restrained

Avoid:
- loud exaggerated effects

---

# 19. Camera Rules

During Haustoria:
- camera should remain stable
- avoid dramatic zooms initially

Optional later:
- subtle focus shift

---

# 20. Combat Interaction

Haustoria is NOT a replacement for combat.

Combat still matters for:
- creating safe opportunities
- controlling enemies
- surviving swarms

---

## Intended Combat Flow

```text
fight → stagger/opening → Haustoria → disengage
```

---

# 21. Swarm Interaction

Using Haustoria during swarms should feel dangerous.

The player:
- becomes vulnerable to surrounding enemies
- risks interruption

This creates:
- positioning pressure
- timing decisions

---

# 22. Environmental Creature Interaction

Some environmental creatures may:
- provide tiny resource values
- be consumed quickly

This supports:
- desperation survival behavior

Especially in Level 3.

---

# 23. Haustoria Failure States

Potential failure scenarios:

```text
interrupted drain
resource depletion during combat
swarm overwhelm
bad positioning
```

The system should punish:
- careless positioning

NOT:
- mistimed frame-perfect execution

---

# 24. UI Requirements

The player should clearly see:
- drain active state
- resource gain
- drain interruption

Recommended:
- subtle resource pulse
- color feedback
- outline changes

---

# 25. Animation Requirements

Minimum prototype animations:

```text
attach
drain_loop
detach
interrupt
```

Placeholder animations acceptable initially.

---

# 26. Enemy Compatibility Rules

Enemies should expose:

```python
can_be_haustoria_target
water_value
chlorophyll_value
```

Bosses may additionally expose:

```python
haustoria_window_active
```

---

# 27. Tiled Workflow

Enemy properties may define:

```text
can_be_haustoria_target
water_value
chlorophyll_value
```

This allows:
- easy balancing
- level-specific tuning

---

# 28. Prototype Implementation Scope

The first prototype should support:

- one valid enemy target
- basic drain
- interrupt on damage
- player lock state
- resource gain
- visual placeholder effect

Avoid:
- complex boss interactions initially

---

# 29. AI Agent Implementation Rules

The AI agent must:

1. Keep Haustoria modular
2. Keep drain logic separate from combat logic
3. Keep player lock state explicit
4. Preserve collision correctness during attachment
5. Avoid cinematic scripting
6. Prioritize readability
7. Keep interruption handling stable
8. Keep resource values tunable
9. Use placeholder effects initially
10. Keep gameplay responsive after detachment

---

# 30. Recommended Build Order

The AI agent should implement:

1. Activation input
2. Range check
3. Player lock state
4. Resource gain
5. Enemy damage
6. Drain timer
7. Interrupt logic
8. Visual effects
9. Audio feedback
10. Boss compatibility

---

# 31. Recommended Next Document

After this Haustoria Ability Spec, create:

```text
Prototype Build Brief
```

This document should define:
- exact MVP scope
- systems intentionally excluded
- debugging tools
- required temporary assets
- milestone goals
- AI-agent execution priorities
