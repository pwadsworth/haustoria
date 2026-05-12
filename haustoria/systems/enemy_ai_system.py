"""
enemy_ai_system.py — State machine AI for basic enemies and swarm bugs.

Standard enemy: IDLE → PATROL ↔ CHASE → ATTACK → STUNNED → DEAD
Swarm bug: always moves toward player, contact damage.
"""

import arcade
from entities.enemy import (
    Enemy, ENEMY_IDLE, ENEMY_PATROL, ENEMY_CHASE,
    ENEMY_ATTACK, ENEMY_STUNNED, ENEMY_DEAD,
)
from game.physics_helpers import distance_between
from constants import GRAVITY, SWARM_AGGRO_RANGE


class EnemyAISystem:
    """
    Updates all enemy entities each frame via their state machines.

    Enemies do simple direct movement toward the player.
    No pathfinding — collision-aware movement only.
    """

    def __init__(self, wall_list, platform_list):
        self.wall_list = wall_list
        self.platform_list = platform_list
        self._all_walls = None  # combined list, built lazily
        self._swarm_bugs = []   # updated each frame for separation steering

    def _get_all_walls(self) -> arcade.SpriteList:
        """Merge wall + platform lists once for collision checks."""
        if self._all_walls is None:
            self._all_walls = arcade.SpriteList(use_spatial_hash=True)
            for s in self.wall_list:
                self._all_walls.append(s)
            for s in self.platform_list:
                self._all_walls.append(s)
        return self._all_walls

    def update(self, enemy_list, player, delta_time: float):
        """Update every enemy in the list."""
        import math, random

        # Rebuild swarm bug list for separation steering this frame
        self._swarm_bugs = [
            e for e in enemy_list
            if isinstance(e, Enemy) and e.enemy_type == "swarm_bug" and e.state != ENEMY_DEAD
        ]

        # Per-bug orbit params are initialised lazily inside _move_swarm_bug
        # (nothing needed here)

        for enemy in list(enemy_list):
            if not isinstance(enemy, Enemy):
                continue
            enemy.update_timers(delta_time)
            if enemy.state == ENEMY_DEAD:
                self._update_dead(enemy, enemy_list, delta_time)
                continue
            self._update_detection(enemy, player)
            self._update_movement(enemy, player, delta_time)

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def _update_detection(self, enemy: Enemy, player):
        """Transition between PATROL/CHASE based on player distance."""
        if enemy.state in (ENEMY_STUNNED, ENEMY_DEAD, ENEMY_ATTACK):
            return

        dist = distance_between(
            enemy.center_x, enemy.center_y,
            player.center_x, player.center_y,
        )

        if dist <= enemy.detection_range:
            if enemy.state != ENEMY_CHASE:
                enemy.set_state(ENEMY_CHASE)
        else:
            if enemy.state == ENEMY_CHASE:
                enemy.set_state(ENEMY_PATROL)

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    def _update_movement(self, enemy: Enemy, player, delta_time: float):
        if enemy.state == ENEMY_STUNNED:
            self._apply_gravity(enemy)
            return

        if enemy.enemy_type == "swarm_bug":
            self._move_swarm_bug(enemy, player, delta_time)
        elif enemy.state == ENEMY_PATROL:
            self._move_patrol(enemy, delta_time)
        elif enemy.state == ENEMY_CHASE:
            self._move_chase(enemy, player, delta_time)
        elif enemy.state == ENEMY_ATTACK:
            self._move_attack(enemy, player, delta_time)

        self._apply_gravity(enemy)
        self._resolve_wall_collisions(enemy)
        self._check_edge_turn(enemy)

    def _move_patrol(self, enemy: Enemy, delta_time: float):
        """Walk left/right within patrol_range of origin."""
        limit = enemy.patrol_origin_x + enemy.facing_direction * enemy.patrol_range / 2
        if enemy.facing_direction == 1 and enemy.center_x >= limit:
            enemy.facing_direction = -1
        elif enemy.facing_direction == -1 and enemy.center_x <= limit:
            enemy.facing_direction = 1
        enemy.change_x = enemy.facing_direction * enemy.move_speed

    def _move_chase(self, enemy: Enemy, player, delta_time: float):
        """Move directly toward player horizontally."""
        dx = player.center_x - enemy.center_x
        dist = abs(dx)
        if dist <= enemy.attack_range:
            enemy.set_state(ENEMY_ATTACK)
            enemy.attack_windup_timer = 0.2
            return
        enemy.facing_direction = 1 if dx > 0 else -1
        enemy.change_x = enemy.facing_direction * enemy.move_speed

    def _move_attack(self, enemy: Enemy, player, delta_time: float):
        """Stand still, deal damage when windup expires."""
        enemy.change_x = 0
        if enemy.attack_windup_timer <= 0 and enemy.attack_cooldown_timer <= 0:
            # Attack fires — damage is dealt by CollisionSystem
            enemy.attack_cooldown_timer = 0.9
            # Return to chase
            enemy.set_state(ENEMY_CHASE)

    def _move_swarm_bug(self, enemy: Enemy, player, delta_time: float):
        """
        Two-mode movement:
        - ORBIT: player is beyond SWARM_AGGRO_RANGE  →  lazy elliptical orbits
                 around the spawn point (random per-bug radius/speed/wobble).
        - CHASE: player is within SWARM_AGGRO_RANGE  →  pursuit + separation
                 flocking toward the player.

        Tune SWARM_AGGRO_RANGE in constants.py.
        """
        import math, random
        import arcade as _arc

        px, py = player.center_x, player.center_y
        ex, ey = enemy.center_x, enemy.center_y

        # --- Initialise per-bug parameters on first call ---
        if not hasattr(enemy, '_orbit_angle'):
            enemy._orbit_angle   = random.uniform(0, 2 * math.pi)
            enemy._orbit_radius  = random.uniform(28, 64)       # ellipse half-width
            enemy._orbit_speed   = random.uniform(0.5, 1.2) * random.choice([-1, 1])
            enemy._wobble_phase  = random.uniform(0, 2 * math.pi)
            enemy._wobble_speed  = random.uniform(1.0, 2.2)
            enemy._wobble_amp    = random.uniform(10, 24)       # vertical wobble
        if not hasattr(enemy, '_swarm_angle_offset'):
            enemy._swarm_angle_offset = 0.0
            enemy._swarm_spin_rate    = 0.0

        dist_to_player = math.hypot(px - ex, py - ey)

        # ================================================================
        # ORBIT MODE  (player is far away)
        # ================================================================
        if dist_to_player > SWARM_AGGRO_RANGE:
            enemy._orbit_angle  += enemy._orbit_speed  * delta_time
            enemy._wobble_phase += enemy._wobble_speed * delta_time

            spawn_x = enemy.patrol_origin_x
            spawn_y = enemy.patrol_origin_y

            # Elliptical target: horizontal radius, half that vertically + wobble
            target_x = spawn_x + math.cos(enemy._orbit_angle) * enemy._orbit_radius
            target_y = (spawn_y
                        + math.sin(enemy._orbit_angle) * enemy._orbit_radius * 0.45
                        + math.sin(enemy._wobble_phase) * enemy._wobble_amp)

            dx = target_x - ex
            dy = target_y - ey
            od = math.hypot(dx, dy)
            if od > 0.5:
                spd = min(od * 0.25, enemy.move_speed)
                enemy.change_x = (dx / od) * spd
                enemy.change_y = (dy / od) * spd * 0.8
            else:
                enemy.change_x *= 0.85
                enemy.change_y *= 0.85

        # ================================================================
        # CHASE MODE  (player is close — pursuit + separation + jitter)
        # ================================================================
        else:
            # --- Per-bug initialisation ---
            if not hasattr(enemy, '_jitter_t'):
                import random as _rnd
                enemy._jitter_t       = _rnd.uniform(0, 6.28)
                enemy._jitter_freq_x  = _rnd.uniform(0.3, 0.8)   # Hz
                enemy._jitter_freq_y  = _rnd.uniform(0.4, 1.0)
                enemy._jitter_amp_x   = _rnd.uniform(20, 40)      # px offset
                enemy._jitter_amp_y   = _rnd.uniform(12, 28)

            enemy._jitter_t += delta_time
            t = enemy._jitter_t

            # Each bug steers toward a slightly different point around the player.
            # This breaks identical mirroring without risking a flipped pursuit vector.
            target_x = px + math.sin(t * enemy._jitter_freq_x) * enemy._jitter_amp_x
            target_y = py + math.cos(t * enemy._jitter_freq_y) * enemy._jitter_amp_y

            tdx  = target_x - ex
            tdy  = target_y - ey
            dist = max(math.hypot(tdx, tdy), 1.0)

            pursuit_x = (tdx / dist) * enemy.move_speed
            pursuit_y = (tdy / dist) * enemy.move_speed

            # Ease off when very close to player (use real player dist)
            STOP_DIST = 28.0
            if dist_to_player < STOP_DIST:
                t2 = dist_to_player / STOP_DIST
                pursuit_x *= t2
                pursuit_y *= t2

            # Separation from swarm-mates
            sep_x = sep_y = 0.0
            SEP_RADIUS   = 12.0
            SEP_STRENGTH = enemy.move_speed * 1.8
            for other in self._swarm_bugs:
                if other is enemy:
                    continue
                odx = ex - other.center_x
                ody = ey - other.center_y
                od  = math.hypot(odx, ody)
                if 0 < od < SEP_RADIUS:
                    scale  = (SEP_RADIUS - od) / SEP_RADIUS
                    sep_x += (odx / od) * scale * SEP_STRENGTH
                    sep_y += (ody / od) * scale * SEP_STRENGTH

            vx = pursuit_x + sep_x * 1.4
            vy = pursuit_y + sep_y * 1.4

            spd = math.hypot(vx, vy)
            max_spd = enemy.move_speed * 1.5
            if spd > max_spd:
                vx = (vx / spd) * max_spd
                vy = (vy / spd) * max_spd

            enemy.change_x = vx
            # Moderate inertia so bugs don't mirror every micro-movement
            enemy.change_y += (vy - enemy.change_y) * 0.25
            enemy.change_y = max(min(enemy.change_y, enemy.move_speed * 1.5),
                                 -enemy.move_speed * 1.5)

        # ================================================================
        # Sub-stepped wall collision  (both modes)
        # ================================================================
        MAX_STEP = 3.0

        rx = enemy.change_x
        while abs(rx) > 0.001:
            s   = max(-MAX_STEP, min(MAX_STEP, rx))
            rx -= s
            enemy.center_x += s
            for wall in _arc.check_for_collision_with_list(enemy, self.wall_list):
                if s > 0:
                    enemy.right = wall.left
                else:
                    enemy.left = wall.right
                enemy.change_x *= -0.2
                rx = 0
                break

        ry = enemy.change_y
        while abs(ry) > 0.001:
            s   = max(-MAX_STEP, min(MAX_STEP, ry))
            ry -= s
            enemy.center_y += s
            for wall in _arc.check_for_collision_with_list(enemy, self.wall_list):
                if s < 0:   # hit floor — kick upward so bugs fly off instead of sliding
                    enemy.bottom = wall.top
                    enemy.change_y = enemy.move_speed * 1.1
                else:       # hit ceiling — gentle downward nudge
                    enemy.top = wall.bottom
                    enemy.change_y = -enemy.move_speed * 0.3
                ry = 0
                break

    def _apply_gravity(self, enemy: Enemy):
        """Simple gravity for ground-based enemies (not swarm bugs)."""
        if enemy.enemy_type == "swarm_bug":
            return
        enemy.vel_y -= GRAVITY
        enemy.vel_y = max(enemy.vel_y, -12.0)
        enemy.center_y += enemy.vel_y
        enemy.center_x += enemy.change_x

        # Ground resolution
        hits = arcade.check_for_collision_with_list(enemy, self._get_all_walls())
        for wall in hits:
            if enemy.vel_y < 0:
                enemy.bottom = wall.top
                enemy.vel_y = 0

    def _resolve_wall_collisions(self, enemy: Enemy):
        """Push enemy out of horizontal wall overlaps (X axis only)."""
        hits = arcade.check_for_collision_with_list(enemy, self.wall_list)
        for wall in hits:
            if enemy.change_x > 0:
                enemy.right = wall.left
                enemy.facing_direction = -1
            elif enemy.change_x < 0:
                enemy.left = wall.right
                enemy.facing_direction = 1

    def _check_edge_turn(self, enemy: Enemy):
        """Turn around at platform edges (probe 4px ahead + 20px down)."""
        if enemy.enemy_type == "swarm_bug":
            return
        probe = arcade.SpriteSolidColor(8, 8, color=(0, 0, 0, 0))
        probe.center_x = enemy.center_x + enemy.facing_direction * (enemy.width / 2 + 4)
        probe.center_y = enemy.bottom - 20
        edge_hit = arcade.check_for_collision_with_list(probe, self._get_all_walls())
        if not edge_hit:
            enemy.facing_direction *= -1

    def _update_dead(self, enemy: Enemy, enemy_list, delta_time: float):
        """Brief delay then remove dead enemy."""
        enemy.death_timer -= delta_time
        if enemy.death_timer <= 0:
            enemy.remove_from_sprite_lists()
            if enemy in enemy_list:
                pass  # already removed
