"""
save_point.py — Interactive checkpoint bench.
"""

import arcade
from constants import COLOR_SAVE_POINT


class SavePoint(arcade.Sprite):
    """A bench-like checkpoint. Activates when player presses E nearby."""

    def __init__(self, center_x: float, center_y: float, save_id: str = "sp_01"):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(36, COLOR_SAVE_POINT, outer_alpha=255)
        self.width = 36
        self.height = 20
        self.center_x = center_x
        self.center_y = center_y
        self.save_id: str = save_id
        self.is_activated: bool = False

    def activate(self):
        self.is_activated = True
        # Visual feedback: brighten slightly (placeholder)
        print(f"[SavePoint] {self.save_id} activated")
