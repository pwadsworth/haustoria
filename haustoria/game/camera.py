"""
camera.py — Smooth-follow camera for Haustoria.

Wraps arcade.Camera2D with lerp-based smooth follow and optional room lock.
"""

import arcade
from game.physics_helpers import lerp, clamp
from constants import CAMERA_LERP_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT


class Camera:
    """
    Smooth-follow camera that tracks the player.

    Supports:
    - Lerped smooth following
    - Hard bounds (level boundaries)
    - Room lock (boss / swarm rooms)
    """

    def __init__(self):
        self.arcade_camera = arcade.Camera2D()

        # Current camera center
        self.pos_x: float = SCREEN_WIDTH / 2
        self.pos_y: float = SCREEN_HEIGHT / 2

        # Level bounds (set by level loader)
        self.min_x: float = SCREEN_WIDTH / 2
        self.min_y: float = SCREEN_HEIGHT / 2
        self.max_x: float = float("inf")
        self.max_y: float = float("inf")

        # Room lock state
        self.is_locked: bool = False
        self.lock_x: float = SCREEN_WIDTH / 2
        self.lock_y: float = SCREEN_HEIGHT / 2

    def set_bounds(self, level_width: float, level_height: float):
        """Set camera scroll limits based on level size."""
        self.min_x = SCREEN_WIDTH / 2
        self.min_y = SCREEN_HEIGHT / 2
        self.max_x = max(level_width - SCREEN_WIDTH / 2, self.min_x)
        self.max_y = max(level_height - SCREEN_HEIGHT / 2, self.min_y)

    def lock_to_room(self, center_x: float, center_y: float):
        """Lock camera to a fixed room center (boss/swarm rooms)."""
        self.is_locked = True
        self.lock_x = center_x
        self.lock_y = center_y

    def unlock(self):
        """Return to player-following mode."""
        self.is_locked = False

    def update(self, player_x: float, player_y: float):
        """Move camera toward target position each frame."""
        if self.is_locked:
            target_x = self.lock_x
            target_y = self.lock_y
        else:
            target_x = player_x
            target_y = player_y

        # Clamp to level bounds
        target_x = clamp(target_x, self.min_x, self.max_x)
        target_y = clamp(target_y, self.min_y, self.max_y)

        # Smooth lerp toward target
        self.pos_x = lerp(self.pos_x, target_x, CAMERA_LERP_SPEED)
        self.pos_y = lerp(self.pos_y, target_y, CAMERA_LERP_SPEED)

        self.arcade_camera.position = (self.pos_x, self.pos_y)

    def use(self):
        """Activate this camera for world-space drawing."""
        self.arcade_camera.use()
