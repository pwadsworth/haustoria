"""
haustoria_system.py — The Haustoria parasitic drain ability.

Activation: player presses E near a valid enemy.
Effect: player locks in place, drains enemy health/resources over time.
Risk: player is fully vulnerable during drain.
Interruption: any damage to player ends the drain.
"""

import arcade
from entities.enemy import Enemy, ENEMY_DEAD, ENEMY_STUNNED
from game.player import STATE_USING_HAUSTORIA
from constants import (
    HAUSTORIA_RANGE, HAUSTORIA_DRAIN_DURATION,
    HAUSTORIA_WATER_RATE, HAUSTORIA_CHLOROPHYLL_RATE,
    HAUSTORIA_ENEMY_DAMAGE_RATE,
)


class HaustoriaSystem:
    """
    Manages the Haustoria attachment state.

    Activation requirements (from spec §4):
    - enemy in range
    - enemy is a valid target (can_be_haustoria_target)
    - player is not stunned or already draining
    - enemy is not dead
    """

    def __init__(self):
        self.current_target: Enemy | None = None

    # ------------------------------------------------------------------
    # Try activation
    # ------------------------------------------------------------------

    def try_activate(self, player, enemy_list) -> bool:
        """Attempt to start Haustoria on the nearest valid enemy."""
        if player.is_using_haustoria or player.is_stunned or player.is_dead:
            return False

        target = self._find_target(player, enemy_list)
        if target is None:
            return False

        # Lock in
        player.is_using_haustoria = True
        player.haustoria_timer = HAUSTORIA_DRAIN_DURATION
        player.set_state(STATE_USING_HAUSTORIA)
        self.current_target = target
        print(f"[Haustoria] Attached to {target.enemy_type}")
        return True

    def _find_target(self, player, enemy_list) -> "Enemy | None":
        """Return the closest valid Haustoria target within range."""
        best = None
        best_dist = HAUSTORIA_RANGE

        for enemy in enemy_list:
            if not isinstance(enemy, Enemy):
                continue
            if not enemy.can_be_haustoria_target:
                continue
            if enemy.state == ENEMY_DEAD:
                continue

            dx = enemy.center_x - player.center_x
            dy = enemy.center_y - player.center_y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < best_dist:
                best = enemy
                best_dist = dist

        return best

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, player, delta_time: float):
        """Drain resources and check interruption each frame."""
        if not player.is_using_haustoria:
            return

        target = self.current_target

        # Check interruption conditions
        if self._should_interrupt(player, target):
            self._cancel(player)
            return

        # Lock player to enemy position
        if target is not None:
            player.center_x = target.center_x
            player.center_y = target.center_y + 10
            player.change_x = 0
            player.change_y = 0

        # Drain resources from enemy to player
        gain_water = HAUSTORIA_WATER_RATE * delta_time
        gain_chlorophyll = HAUSTORIA_CHLOROPHYLL_RATE * delta_time
        drain_damage = HAUSTORIA_ENEMY_DAMAGE_RATE * delta_time

        player.water = min(player.max_water, player.water + gain_water)
        player.chlorophyll = min(player.max_chlorophyll,
                                 player.chlorophyll + gain_chlorophyll)

        if target is not None:
            target.health -= drain_damage
            if target.health <= 0:
                target.state = ENEMY_DEAD
                self._cancel(player)
                return

        # Auto-end when timer expires (timer ticked in player.update_timers)
        if player.haustoria_timer <= 0:
            self._cancel(player)

    def _should_interrupt(self, player, target) -> bool:
        """Return True if Haustoria should be forcibly ended."""
        if target is None:
            return True
        if target.state == ENEMY_DEAD:
            return True
        # Damage interruption is handled in player.take_damage() → is_using_haustoria = False
        if not player.is_using_haustoria:
            return True
        return False

    def _cancel(self, player):
        """End Haustoria and restore player control."""
        player.is_using_haustoria = False
        player.haustoria_timer = 0.0
        self.current_target = None
        print("[Haustoria] Detached")
