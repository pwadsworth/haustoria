"""
combat_system.py — Melee attack hitbox, knockback, object-hit damage.
"""

import arcade
from entities.enemy import Enemy, ENEMY_STUNNED, ENEMY_DEAD
from entities.interactable_object import InteractableObject, OBJ_STATE_THROWN
from constants import (
    ATTACK_HITBOX_OFFSET, ATTACK_HITBOX_SIZE,
    ENEMY_KNOCKBACK_X, ENEMY_KNOCKBACK_Y,
    PLAYER_KNOCKBACK_X, PLAYER_KNOCKBACK_Y,
    LIGHT_STUN, HEAVY_STUN,
)


class CombatSystem:
    """
    Resolves melee attacks and thrown-object impacts against enemies.

    Melee attack is a rectangular hitbox in front of the player.
    Thrown objects deal damage on collision (detected each frame).
    """

    def update(self, player, enemy_list, object_list, delta_time: float):
        """Check active attack hitbox and thrown-object hits."""
        if player.is_attacking:
            self._resolve_melee(player, enemy_list)
        self._resolve_thrown_object_hits(object_list, enemy_list)

    # ------------------------------------------------------------------
    # Melee
    # ------------------------------------------------------------------

    def _resolve_melee(self, player, enemy_list):
        """Create a temporary hitbox sprite and check for enemy overlap."""
        hitbox = arcade.SpriteSolidColor(
            ATTACK_HITBOX_SIZE, ATTACK_HITBOX_SIZE, color=(255, 0, 0, 0)
        )
        hitbox.center_x = (
            player.center_x + player.facing_direction * ATTACK_HITBOX_OFFSET
        )
        hitbox.center_y = player.center_y

        for enemy in list(enemy_list):
            if not isinstance(enemy, Enemy):
                continue
            if enemy.state == ENEMY_DEAD:
                continue
            if arcade.check_for_collision(hitbox, enemy):
                self._hit_enemy(enemy, damage=1, stun=LIGHT_STUN,
                                source_x=player.center_x)

    def _hit_enemy(self, enemy: Enemy, damage: int, stun: float, source_x: float):
        """Apply damage, stun, and knockback to an enemy."""
        if enemy.state == ENEMY_DEAD:
            return
        enemy.take_damage(damage, stun_duration=stun)
        # Knockback direction
        kick_dir = 1 if enemy.center_x > source_x else -1
        enemy.vel_x = kick_dir * ENEMY_KNOCKBACK_X
        enemy.vel_y = ENEMY_KNOCKBACK_Y

    # ------------------------------------------------------------------
    # Thrown object impacts
    # ------------------------------------------------------------------

    def _resolve_thrown_object_hits(self, object_list, enemy_list):
        """Thrown objects deal damage and stun on contact with enemies."""
        for obj in object_list:
            if not isinstance(obj, InteractableObject):
                continue
            if obj.state != OBJ_STATE_THROWN:
                continue

            for enemy in list(enemy_list):
                if not isinstance(enemy, Enemy):
                    continue
                if enemy.state == ENEMY_DEAD:
                    continue
                if arcade.check_for_collision(obj, enemy):
                    stun = HEAVY_STUN if obj.is_heavy else LIGHT_STUN
                    self._hit_enemy(enemy, damage=obj.damage, stun=stun,
                                    source_x=obj.center_x)
                    # Object stops after hit
                    obj.vel_x *= -0.2
                    obj.vel_y = 1.0

    # ------------------------------------------------------------------
    # Enemy damages player (called by collision system)
    # ------------------------------------------------------------------

    def enemy_hits_player(self, player, enemy: Enemy):
        """Apply contact damage from an enemy to the player."""
        if enemy.state in (ENEMY_DEAD, ENEMY_STUNNED):
            return
        if player.is_invincible or player.is_dead:
            return

        died = player.take_damage(enemy.contact_damage, source_x=enemy.center_x)
        # Knock player back
        kick_dir = 1 if player.center_x > enemy.center_x else -1
        player.change_x = kick_dir * PLAYER_KNOCKBACK_X
        player.change_y = PLAYER_KNOCKBACK_Y

        # Interrupt Haustoria
        player.is_using_haustoria = False
        player.haustoria_timer = 0.0
