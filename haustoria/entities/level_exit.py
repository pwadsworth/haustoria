"""
level_exit.py — Triggers a level transition when the player enters it.
"""

import arcade
from constants import COLOR_LEVEL_EXIT


class LevelExit(arcade.Sprite):
    """
    An invisible (or semi-visible) region that transitions to another level.

    CollisionSystem detects player overlap and calls game_window.load_level().
    """

    def __init__(
        self,
        center_x: float,
        center_y: float,
        width: int = 48,
        height: int = 80,
        target_level: str = "test_zone_02",
        target_spawn: str = "default",
    ):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(
            max(width, height), COLOR_LEVEL_EXIT, outer_alpha=120
        )
        self.width = width
        self.height = height
        self.center_x = center_x
        self.center_y = center_y

        self.exit_id: str = f"exit_{id(self)}"
        self.target_level: str = target_level
        self.target_spawn: str = target_spawn
        self.requires_condition: str | None = None
        self.triggered: bool = False
