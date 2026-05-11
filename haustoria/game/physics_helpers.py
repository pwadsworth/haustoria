"""
physics_helpers.py — Shared collision and physics utility functions.

Centralized here so the same checks aren't duplicated across systems.
"""

import arcade
from constants import TILE_SIZE


def is_on_ground(player, physics_engine) -> bool:
    """Return True if the physics engine says the player can jump (is grounded)."""
    return physics_engine.can_jump()


def is_touching_wall_left(sprite, wall_list) -> bool:
    """Return True if sprite would collide with a wall 2px to its left."""
    sprite.center_x -= 2
    hit = arcade.check_for_collision_with_list(sprite, wall_list)
    sprite.center_x += 2
    return len(hit) > 0


def is_touching_wall_right(sprite, wall_list) -> bool:
    """Return True if sprite would collide with a wall 2px to its right."""
    sprite.center_x += 2
    hit = arcade.check_for_collision_with_list(sprite, wall_list)
    sprite.center_x -= 2
    return len(hit) > 0


def is_player_above_object(player, obj, tolerance: float = 8.0) -> bool:
    """Return True if the player's bottom is at or above the object's top."""
    return player.bottom >= obj.top - tolerance


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp value between minimum and maximum."""
    return max(minimum, min(maximum, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b by factor t."""
    return a + (b - a) * t


def distance_between(ax: float, ay: float, bx: float, by: float) -> float:
    """Euclidean distance between two points."""
    return ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
