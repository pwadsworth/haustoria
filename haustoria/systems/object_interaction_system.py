"""
object_interaction_system.py — Pickup, carry, drop, throw, bounce, object physics.
"""

import arcade
from entities.interactable_object import (
    InteractableObject, OBJ_STATE_IDLE, OBJ_STATE_HELD,
    OBJ_STATE_THROWN, OBJ_STATE_BROKEN,
    TAG_BOUNCE,
)
from constants import (
    HOLD_OFFSET_X, HOLD_OFFSET_Y,
    THROW_FORCE_X, THROW_FORCE_Y, THROW_IGNORE_TIMER,
    BOUNCE_VELOCITY, BOUNCE_COOLDOWN,
    OBJECT_GRAVITY, OBJECT_MAX_FALL, OBJECT_FRICTION,
)


class ObjectInteractionSystem:
    """
    Manages the full lifecycle of world objects:
    pickup → carry → drop/throw → physics → collision → bounce/break.
    """

    def __init__(self, wall_list, breakable_list):
        self.wall_list = wall_list
        self.breakable_list = breakable_list

    # ------------------------------------------------------------------
    # Pickup
    # ------------------------------------------------------------------

    def try_pickup(self, player, object_list: arcade.SpriteList):
        """Attempt to pick up the nearest grabbable object."""
        if player.held_object is not None:
            return
        best = None
        best_dist = 60.0  # max pickup range in pixels
        for obj in object_list:
            if not isinstance(obj, InteractableObject):
                continue
            if not obj.is_grabbable or obj.is_held or obj.state == OBJ_STATE_BROKEN:
                continue
            dx = obj.center_x - player.center_x
            dy = obj.center_y - player.center_y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < best_dist:
                best = obj
                best_dist = dist
        if best:
            self._attach(player, best)

    def _attach(self, player, obj: InteractableObject):
        obj.is_held = True
        obj.state = OBJ_STATE_HELD
        obj.held_by = player
        obj.vel_x = 0.0
        obj.vel_y = 0.0
        player.held_object = obj

    # ------------------------------------------------------------------
    # Drop
    # ------------------------------------------------------------------

    def drop(self, player):
        """Drop the held object in front of the player."""
        obj = player.held_object
        if obj is None:
            return
        self._detach(player, obj)
        # Give slight outward nudge
        obj.vel_x = player.facing_direction * 1.5
        obj.vel_y = 0.0
        obj.state = OBJ_STATE_IDLE

    # ------------------------------------------------------------------
    # Throw
    # ------------------------------------------------------------------

    def throw(self, player):
        """Throw the held object in the player's facing direction."""
        obj = player.held_object
        if obj is None:
            return
        self._detach(player, obj)
        obj.vel_x = player.facing_direction * THROW_FORCE_X
        obj.vel_y = THROW_FORCE_Y
        obj.state = OBJ_STATE_THROWN
        obj.ignore_player_collision_timer = THROW_IGNORE_TIMER

    def _detach(self, player, obj: InteractableObject):
        obj.is_held = False
        obj.held_by = None
        player.held_object = None
        # Place object slightly in front of player
        obj.center_x = player.center_x + player.facing_direction * HOLD_OFFSET_X
        obj.center_y = player.center_y

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, player, object_list: arcade.SpriteList, delta_time: float):
        """Update all object physics and check for bouncing."""
        for obj in object_list:
            if not isinstance(obj, InteractableObject):
                continue
            obj.ignore_player_collision_timer = max(
                0.0, obj.ignore_player_collision_timer - delta_time
            )
            obj.bounce_cooldown_timer = max(
                0.0, obj.bounce_cooldown_timer - delta_time
            )

            if obj.state == OBJ_STATE_HELD:
                self._update_held(player, obj)
            elif obj.state in (OBJ_STATE_THROWN, OBJ_STATE_IDLE, OBJ_STATE_IDLE):
                self._update_free_physics(obj)

        # Check player bounce on objects
        self._check_player_bounce(player, object_list)

    def _update_held(self, player, obj: InteractableObject):
        """Snap held object to carry position beside the player."""
        obj.center_x = player.center_x + player.facing_direction * HOLD_OFFSET_X
        obj.center_y = player.center_y + HOLD_OFFSET_Y

    def _update_free_physics(self, obj: InteractableObject):
        """Apply simple gravity and damping to a free-flying object."""
        if obj.state == OBJ_STATE_BROKEN:
            return

        # Gravity
        obj.vel_y -= OBJECT_GRAVITY
        obj.vel_y = max(obj.vel_y, -OBJECT_MAX_FALL)

        # Move
        obj.center_x += obj.vel_x
        obj.center_y += obj.vel_y

        # Wall collision (simple AABB resolve)
        hit_walls = arcade.check_for_collision_with_list(obj, self.wall_list)
        for wall in hit_walls:
            if obj.vel_x > 0:
                obj.right = wall.left
                obj.vel_x *= -0.3
            elif obj.vel_x < 0:
                obj.left = wall.right
                obj.vel_x *= -0.3

        # Floor collision
        floor_hits = arcade.check_for_collision_with_list(obj, self.wall_list)
        for wall in floor_hits:
            if obj.vel_y < 0:
                obj.bottom = wall.top
                obj.vel_y = 0
                obj.is_grounded = True
                obj.state = OBJ_STATE_IDLE

        # Horizontal friction when grounded
        if obj.is_grounded:
            obj.vel_x *= OBJECT_FRICTION
            if abs(obj.vel_x) < 0.1:
                obj.vel_x = 0.0

        # Check thrown object hits breakable terrain
        if obj.state == OBJ_STATE_THROWN:
            self._check_breakable_hit(obj)

    def _check_breakable_hit(self, obj: InteractableObject):
        """Thrown object vs breakable terrain."""
        from entities.breakable_terrain import BreakableTerrain
        hits = arcade.check_for_collision_with_list(obj, self.breakable_list)
        for wall in hits:
            if isinstance(wall, BreakableTerrain):
                dmg_type = "HEAVY_OBJECT" if obj.is_heavy else "THROWN_OBJECT"
                wall.hit(obj.damage, dmg_type)
                obj.vel_x *= -0.4
                obj.vel_y = 0

    # ------------------------------------------------------------------
    # Player bounce
    # ------------------------------------------------------------------

    def _check_player_bounce(self, player, object_list: arcade.SpriteList):
        """If player falls onto a bounce object, launch them upward."""
        if player.is_dead or player.change_y >= 0:
            return  # Must be falling

        for obj in object_list:
            if not isinstance(obj, InteractableObject):
                continue
            if not obj.can_bounce or obj.bounce_cooldown_timer > 0:
                continue
            if not arcade.check_for_collision(player, obj):
                continue
            # Must be coming from above
            if player.bottom < obj.top - 10:
                continue

            player.change_y = BOUNCE_VELOCITY
            obj.bounce_cooldown_timer = BOUNCE_COOLDOWN
            print(f"[ObjectSystem] Player bounced off {obj.object_type}")
