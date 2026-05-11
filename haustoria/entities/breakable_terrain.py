"""
breakable_terrain.py — A wall tile that can be destroyed by thrown objects.
"""

import arcade
from constants import COLOR_BREAKABLE_WALL


class BreakableTerrain(arcade.Sprite):
    """
    A destructible wall section.

    Destroyed when hit by an object whose damage_type matches break_method.
    Removing it from its sprite list opens the path.
    """

    BREAK_ANY = "ANY_DAMAGE"
    BREAK_THROWN = "THROWN_OBJECT"
    BREAK_HEAVY = "HEAVY_OBJECT"
    BREAK_SPEAR = "SPEAR"

    def __init__(
        self,
        center_x: float,
        center_y: float,
        width: int = 32,
        height: int = 64,
        health: int = 2,
        break_method: str = "ANY_DAMAGE",
    ):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(
            max(width, height), COLOR_BREAKABLE_WALL, outer_alpha=200
        )
        self.width = width
        self.height = height
        self.center_x = center_x
        self.center_y = center_y

        self.breakable_id: str = f"breakable_{id(self)}"
        self.health: int = health
        self.max_health: int = health
        self.break_method: str = break_method
        self.is_broken: bool = False

    def hit(self, damage: int, damage_type: str = "ANY_DAMAGE"):
        """Apply damage if the damage type matches break_method."""
        matches = (
            self.break_method == self.BREAK_ANY or
            damage_type == self.break_method or
            damage_type == self.BREAK_ANY
        )
        if not matches:
            return

        self.health -= damage
        if self.health <= 0:
            self.is_broken = True
            self.remove_from_sprite_lists()
            print(f"[BreakableTerrain] {self.breakable_id} broken!")
