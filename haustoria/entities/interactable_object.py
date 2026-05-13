"""
interactable_object.py — Pickupable, throwable, and bounce objects.

Object behavior is driven by the ObjectInteractionSystem.
"""

import arcade
from constants import (
    COLOR_SPEAR, COLOR_ROCK, COLOR_CRATE, COLOR_BOUNCE_OBJECT,
    OBJECT_GRAVITY, OBJECT_MAX_FALL, OBJECT_FRICTION,
)

# Object state constants
OBJ_STATE_IDLE = "idle"
OBJ_STATE_HELD = "held"
OBJ_STATE_THROWN = "thrown"
OBJ_STATE_SLIDING = "sliding"
OBJ_STATE_BROKEN = "broken"


# Object type tag constants
TAG_LIGHT = "LIGHT_OBJECT"
TAG_HEAVY = "HEAVY_OBJECT"
TAG_WEAPON = "WEAPON_OBJECT"
TAG_PLATFORM = "PLATFORM_OBJECT"
TAG_BREAKABLE = "BREAKABLE_OBJECT"
TAG_BOUNCE = "BOUNCE_OBJECT"


class InteractableObject(arcade.Sprite):
    """
    A world object that can be picked up, carried, dropped, thrown, or bounced on.

    Physics are manually applied by ObjectInteractionSystem (not Arcade engine).
    """

    def __init__(
        self,
        object_type: str,
        center_x: float,
        center_y: float,
        width: int = 20,
        height: int = 20,
        color=COLOR_ROCK,
        texture_path: str = None,
        tags: list = None,
        mass: float = 1.0,
        damage: int = 1,
        stun_power: float = 0.4,
        can_break_terrain: bool = False,
        can_bounce: bool = False,
    ):
        super().__init__(hit_box_algorithm="None")
        if texture_path:
            try:
                self.texture = arcade.load_texture(texture_path)
            except Exception as e:
                print(f"Failed to load object texture {texture_path}: {e}")
                self.texture = arcade.make_soft_square_texture(max(width, height), color, outer_alpha=255)
        else:
            self.texture = arcade.make_soft_square_texture(max(width, height), color, outer_alpha=255)
            
        self.width = width
        self.height = height
        self.center_x = center_x
        self.center_y = center_y

        self.object_id: str = f"{object_type}_{id(self)}"
        self.object_type: str = object_type
        self.tags: list = tags or []

        # Physics properties
        self.mass: float = mass
        self.is_heavy: bool = TAG_HEAVY in self.tags
        self.vel_x: float = 0.0
        self.vel_y: float = 0.0

        # Interaction properties
        self.damage: int = damage
        self.stun_power: float = stun_power
        self.can_break_terrain: bool = can_break_terrain
        self.can_bounce: bool = can_bounce
        self.is_grabbable: bool = True
        self.is_throwable: bool = True
        self.is_platform: bool = TAG_PLATFORM in self.tags
        self.is_breakable: bool = TAG_BREAKABLE in self.tags

        # State
        self.state: str = OBJ_STATE_IDLE
        self.is_held: bool = False
        self.held_by = None

        # Timers
        self.ignore_player_collision_timer: float = 0.0
        self.bounce_cooldown_timer: float = 0.0

        # Grounded flag (set by physics update)
        self.is_grounded: bool = False

    def update_animation(self):
        """Update sprite visual facing direction."""
        if self.state == OBJ_STATE_HELD and self.held_by:
            if self.held_by.facing_direction == 1:
                self.scale_x = abs(self.scale_x)
            elif self.held_by.facing_direction == -1:
                self.scale_x = -abs(self.scale_x)
        else:
            if self.vel_x > 0.1:
                self.scale_x = abs(self.scale_x)
            elif self.vel_x < -0.1:
                self.scale_x = -abs(self.scale_x)


def make_spear(center_x: float, center_y: float) -> InteractableObject:
    """Factory: throwing spear — light, weapon, can bounce."""
    return InteractableObject(
        object_type="throwing_spear",
        center_x=center_x, center_y=center_y,
        width=32, height=8, # Spear is horizontal now
        color=COLOR_SPEAR,
        texture_path="assets/sprites/objects/spear.png",
        tags=[TAG_LIGHT, TAG_WEAPON, TAG_BOUNCE],
        mass=0.6,
        damage=2,
        stun_power=LIGHT_STUN_POWER,
        can_bounce=True,
        can_break_terrain=True,
    )


def make_heavy_rock(center_x: float, center_y: float) -> InteractableObject:
    """Factory: heavy rock — heavy, weapon, breaks walls."""
    return InteractableObject(
        object_type="heavy_rock",
        center_x=center_x, center_y=center_y,
        width=24, height=20,
        color=COLOR_ROCK,
        texture_path="assets/sprites/objects/rock.png",
        tags=[TAG_HEAVY, TAG_WEAPON],
        mass=2.0,
        damage=2,
        stun_power=HEAVY_STUN_POWER,
        can_break_terrain=True,
    )


def make_wooden_crate(center_x: float, center_y: float) -> InteractableObject:
    """Factory: wooden crate — heavy, platform object."""
    return InteractableObject(
        object_type="wooden_crate",
        center_x=center_x, center_y=center_y,
        width=28, height=28,
        color=COLOR_CRATE,
        texture_path="assets/sprites/objects/crate.png",
        tags=[TAG_HEAVY, TAG_PLATFORM],
        mass=2.5,
        damage=1,
        stun_power=0.0,
    )


def make_bounce_object(center_x: float, center_y: float) -> InteractableObject:
    """Factory: bounce object (embedded spear tip / root spike)."""
    obj = InteractableObject(
        object_type="bounce_object",
        center_x=center_x, center_y=center_y,
        width=12, height=20,
        color=COLOR_BOUNCE_OBJECT,
        texture_path="assets/sprites/objects/bounce_spike.png",
        tags=[TAG_BOUNCE],
        mass=999.0,
        damage=0,
        stun_power=0.0,
        can_bounce=True,
    )
    obj.is_grabbable = False
    obj.is_throwable = False
    return obj


# Stun constants referenced by factories
LIGHT_STUN_POWER = 0.4
HEAVY_STUN_POWER = 1.2
