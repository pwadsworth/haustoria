"""
player.py — Player sprite data and state fields.

This class stores state. Movement logic lives in player_controller.py.
"""

import arcade
from constants import (
    PLAYER_MAX_HEALTH, PLAYER_MAX_WATER, PLAYER_MAX_CHLOROPHYLL,
    COLOR_PLAYER, COYOTE_TIME, JUMP_BUFFER_TIME,
    DASH_COOLDOWN, SLIDE_COOLDOWN, ROLL_COOLDOWN, ATTACK_COOLDOWN,
)

# Player state constants
STATE_IDLE = "idle"
STATE_RUNNING = "running"
STATE_JUMPING = "jumping"
STATE_FALLING = "falling"
STATE_WALL_CLINGING = "wall_clinging"
STATE_CLIMBING = "climbing"
STATE_DASHING = "dashing"
STATE_SLIDING = "sliding"
STATE_ROLLING = "rolling"
STATE_ATTACKING = "attacking"
STATE_USING_HAUSTORIA = "using_haustoria"
STATE_STUNNED = "stunned"
STATE_DEAD = "dead"


class Player(arcade.Sprite):
    """
    The player character — a daikon-like creature.

    Stores all state and resource values.
    PlayerController handles the movement behavior.
    """

    def __init__(self):
        super().__init__()

        # --- Placeholder sprite (colored rectangle) ---
        self.texture = arcade.make_soft_square_texture(
            48, (180, 230, 140, 255), center_alpha=255, outer_alpha=255
        )
        self.width = 22
        self.height = 44

        # --- Resources ---
        self.health: int = PLAYER_MAX_HEALTH
        self.max_health: int = PLAYER_MAX_HEALTH
        self.water: float = PLAYER_MAX_WATER
        self.max_water: float = PLAYER_MAX_WATER
        self.chlorophyll: float = PLAYER_MAX_CHLOROPHYLL
        self.max_chlorophyll: float = PLAYER_MAX_CHLOROPHYLL

        # --- State machine ---
        self.current_state: str = STATE_IDLE
        self.previous_state: str = STATE_IDLE

        # --- Facing direction (+1 = right, -1 = left) ---
        self.facing_direction: int = 1

        # --- Status flags ---
        self.is_grounded: bool = False
        self.is_touching_wall_left: bool = False
        self.is_touching_wall_right: bool = False
        self.is_climbing: bool = False
        self.is_on_ladder: bool = False
        self.is_dashing: bool = False
        self.is_sliding: bool = False
        self.is_rolling: bool = False
        self.is_attacking: bool = False
        self.is_using_haustoria: bool = False
        self.is_stunned: bool = False
        self.is_dead: bool = False
        self.is_invincible: bool = False

        # --- Object holding ---
        self.held_object = None  # InteractableObject or None

        # --- Timers ---
        self.coyote_timer: float = 0.0
        self.jump_buffer_timer: float = 0.0
        self.dash_timer: float = 0.0
        self.dash_cooldown_timer: float = 0.0
        self.slide_timer: float = 0.0
        self.slide_cooldown_timer: float = 0.0
        self.roll_timer: float = 0.0
        self.roll_cooldown_timer: float = 0.0
        self.wall_bounce_timer: float = 0.0
        self.attack_timer: float = 0.0
        self.attack_cooldown_timer: float = 0.0
        self.haustoria_timer: float = 0.0
        self.stun_timer: float = 0.0
        self.invincibility_timer: float = 0.0

        # --- Respawn position (set by save system) ---
        self.respawn_x: float = 100.0
        self.respawn_y: float = 200.0

    def set_state(self, new_state: str):
        """Transition player to a new state, recording the previous one."""
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state

    def take_damage(self, amount: int, source_x: float = 0.0):
        """Apply damage and knockback direction. Returns True if player died."""
        if self.is_invincible or self.is_dead:
            return False
        self.health -= amount
        self.is_invincible = True
        self.invincibility_timer = 0.8
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            self.set_state(STATE_DEAD)
            return True
        # Interrupt Haustoria on damage
        self.is_using_haustoria = False
        self.haustoria_timer = 0.0
        return False

    def restore_resources(self):
        """Fully restore water and chlorophyll (save point activation)."""
        self.water = self.max_water
        self.chlorophyll = self.max_chlorophyll
        self.health = self.max_health

    def update_timers(self, delta_time: float):
        """Tick all cooldown timers down. Called once per frame."""
        self.coyote_timer = max(0.0, self.coyote_timer - delta_time)
        self.jump_buffer_timer = max(0.0, self.jump_buffer_timer - delta_time)
        self.dash_timer = max(0.0, self.dash_timer - delta_time)
        self.dash_cooldown_timer = max(0.0, self.dash_cooldown_timer - delta_time)
        self.slide_timer = max(0.0, self.slide_timer - delta_time)
        self.slide_cooldown_timer = max(0.0, self.slide_cooldown_timer - delta_time)
        self.roll_timer = max(0.0, self.roll_timer - delta_time)
        self.roll_cooldown_timer = max(0.0, self.roll_cooldown_timer - delta_time)
        self.wall_bounce_timer = max(0.0, self.wall_bounce_timer - delta_time)
        self.attack_timer = max(0.0, self.attack_timer - delta_time)
        self.attack_cooldown_timer = max(0.0, self.attack_cooldown_timer - delta_time)
        self.haustoria_timer = max(0.0, self.haustoria_timer - delta_time)
        self.stun_timer = max(0.0, self.stun_timer - delta_time)
        self.invincibility_timer = max(0.0, self.invincibility_timer - delta_time)
        if self.invincibility_timer <= 0.0:
            self.is_invincible = False
        if self.stun_timer <= 0.0:
            self.is_stunned = False
        if self.attack_timer <= 0.0:
            self.is_attacking = False
        if self.dash_timer <= 0.0:
            self.is_dashing = False
        if self.slide_timer <= 0.0:
            self.is_sliding = False
        if self.roll_timer <= 0.0:
            self.is_rolling = False
