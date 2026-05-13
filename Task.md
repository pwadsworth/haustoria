# Haustoria Prototype — Task Checklist

## Live Testing — Build Order

### ✅ Verified working
- [x] Window launches, level renders, HUD visible
- [x] Player visible (bright cream), spawns on floor at (80, 54)
- [x] Move left/right (A/D) — feel good
- [x] Jump (Space) + coyote time + jump buffer
- [x] Dash (Shift) — feel good
- [x] Platforms are one-way (fixed — were incorrectly solid)
- [x] Wall cling — slide speed correct (1.2 px/frame, post-physics clamp)
- [x] Wall jump — kicks away from wall, lockout preserves kick direction
- [x] Wall-to-wall bouncing between two close walls
- [x] Wall-cling shaft — entry gap at bottom, open top, exit platform to right
- [x] Objects — no longer tunnel through floor (sub-stepped physics)
- [x] Swarm bugs — natural flocking (separation + angle spread + orbit)
- [x] Debug overlay (F3 toggle, on by default)
- [x] Resource bars (Water/Chloro draining, HUD visible)

### 🔲 Still to test in-game
- [x] Ladder climb (W near the ladder in the shaft area → Section C)
- [x] Slide (Ctrl or crouch input?)
- [x] Object pickup (F) + carry + movement penalty
- [x] Throw (J while holding) — aim at wall / enemy
- [x] Bounce object (jump onto green bounce pad)
- [x] Enemy patrol + chase detection
- [x] Melee attack (J with no held object) + hit stun
- [ ] Haustoria drain (E near stunned/close enemy) → water/chloro gain
- [x] Save point interaction (E near save point) + respawn (R after dying)
- [ ] Breakable terrain (throw heavy rock at breakable wall)
- [x] Level exit → Zone 2 transition
- [x] Zone 2 swarm encounter — flocking in motion

### 🔲 Polish / known deferred items
- [ ] Replace remaining `arcade.draw_text` (enemy labels in debug world)
- [x] Ladder section access (Section C) — verify ladder tiles line up
- [x] Spawn position for Zone 2
- [ ] Tiled `.tmx` map loading (post-prototype)
