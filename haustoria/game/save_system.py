"""
save_system.py — Checkpoint save and respawn logic.
"""


class SaveSystem:
    """
    Stores one checkpoint per save-point activation.

    On player death, game_window calls respawn() to restore saved state.
    """

    def __init__(self):
        self.saved_x: float = 100.0
        self.saved_y: float = 200.0
        self.saved_water: float = 100.0
        self.saved_chlorophyll: float = 100.0
        self.saved_health: int = 5
        self.has_save: bool = False

    def save(self, player, save_point):
        """Record current checkpoint from a save point interaction."""
        self.saved_x = save_point.center_x
        self.saved_y = save_point.center_y + 40  # spawn above bench
        self.saved_water = player.max_water
        self.saved_chlorophyll = player.max_chlorophyll
        self.saved_health = player.max_health
        self.has_save = True

        # Restore resources immediately on save
        player.restore_resources()

        print(f"[SaveSystem] Saved at ({self.saved_x:.0f}, {self.saved_y:.0f})")

    def respawn(self, player):
        """Restore player to last save point position and full resources."""
        player.center_x = self.saved_x
        player.center_y = self.saved_y
        player.change_x = 0
        player.change_y = 0
        player.health = self.saved_health
        player.water = self.saved_water
        player.chlorophyll = self.saved_chlorophyll
        player.is_dead = False
        player.is_stunned = False
        player.is_using_haustoria = False
        player.held_object = None
        from game.player import STATE_IDLE
        player.set_state(STATE_IDLE)
        print(f"[SaveSystem] Respawned at ({self.saved_x:.0f}, {self.saved_y:.0f})")
