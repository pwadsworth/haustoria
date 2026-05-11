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
from constants import GRAVITY


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
        """Simple direct movement toward player."""
        dx = player.center_x - enemy.center_x
        dy = player.center_y - enemy.center_y
        dist = (dx * dx + dy * dy) ** 0.5
        if dist > 0:
            enemy.change_x = (dx / dist) * enemy.move_speed
            enemy.change_y += (dy / dist) * 0.5  # slight vertical drift
        # Swarm bugs float — damp vertical instead of hard gravity
        enemy.change_y = max(min(enemy.change_y, 3.0), -3.0)
        enemy.center_x += enemy.change_x
        enemy.center_y += enemy.change_y

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
        """Push enemy out of horizontal wall overlaps."""
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
