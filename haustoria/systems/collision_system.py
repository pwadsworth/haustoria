"""
collision_system.py — Custom collision resolution not handled by the physics engine.

Handles:
- Player touching enemies (contact damage)
- Player touching save points (E to activate)
- Player touching level exits (transition trigger)
- Player touching water sources (resource pickup)
- Ladder overlap detection
"""

import arcade
from entities.enemy import Enemy, ENEMY_DEAD, ENEMY_STUNNED
from entities.save_point import SavePoint
from entities.level_exit import LevelExit


class CollisionSystem:
    """
    Resolves all non-physics collision events each frame.

    Receives results back through callbacks to avoid circular imports.
    """

    def __init__(self):
        # These callbacks are set by game_window after construction
        self.on_save_activate = None    # fn(player, save_point)
        self.on_level_exit = None       # fn(target_level, target_spawn)
        self.on_water_pickup = None     # fn(player, water_sprite)

    # ------------------------------------------------------------------
    # Main update
    # ------------------------------------------------------------------

    def update(
        self,
        player,
        enemy_list,
        save_point_list,
        level_exit_list,
        water_source_list,
        ladder_list,
        combat_system,
        player_controller,
        interaction_key_pressed: bool,
    ):
        if player.is_dead:
            return

        self._check_enemy_contact(player, enemy_list, combat_system)
        self._check_ladder(player, ladder_list, player_controller)
        self._check_save_points(player, save_point_list, interaction_key_pressed)
        self._check_level_exits(player, level_exit_list)
        self._check_water_sources(player, water_source_list)

    # ------------------------------------------------------------------
    # Enemy contact
    # ------------------------------------------------------------------

    def _check_enemy_contact(self, player, enemy_list, combat_system):
        """Enemy body contact deals damage to the player."""
        hits = arcade.check_for_collision_with_list(player, enemy_list)
        for enemy in hits:
            if not isinstance(enemy, Enemy):
                continue
            if enemy.state in (ENEMY_DEAD, ENEMY_STUNNED):
                continue
            combat_system.enemy_hits_player(player, enemy)

    # ------------------------------------------------------------------
    # Ladders
    # ------------------------------------------------------------------

    def _check_ladder(self, player, ladder_list, player_controller):
        """Inform the controller whether the player overlaps a ladder."""
        hits = arcade.check_for_collision_with_list(player, ladder_list)
        player_controller.update_ladder_status(len(hits) > 0)

    # ------------------------------------------------------------------
    # Save points
    # ------------------------------------------------------------------

    def _check_save_points(self, player, save_point_list, interaction_key_pressed: bool):
        """Activate nearby save point when player presses E."""
        hits = arcade.check_for_collision_with_list(player, save_point_list)
        for sp in hits:
            if not isinstance(sp, SavePoint):
                continue
            if interaction_key_pressed and self.on_save_activate:
                self.on_save_activate(player, sp)
                sp.activate()

    # ------------------------------------------------------------------
    # Level exits
    # ------------------------------------------------------------------

    def _check_level_exits(self, player, level_exit_list):
        """Fire level transition when player enters an exit zone."""
        hits = arcade.check_for_collision_with_list(player, level_exit_list)
        for exit_sprite in hits:
            if not isinstance(exit_sprite, LevelExit):
                continue
            if exit_sprite.triggered:
                continue
            exit_sprite.triggered = True
            if self.on_level_exit:
                self.on_level_exit(exit_sprite.target_level, exit_sprite.target_spawn)

    # ------------------------------------------------------------------
    # Water sources
    # ------------------------------------------------------------------

    def _check_water_sources(self, player, water_source_list):
        """Collect water source pickups on contact."""
        hits = arcade.check_for_collision_with_list(player, water_source_list)
        for ws in hits:
            if self.on_water_pickup:
                self.on_water_pickup(player, ws)
            ws.remove_from_sprite_lists()
