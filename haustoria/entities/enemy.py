"""
enemy.py — Enemy sprite with state machine fields.

Enemy behavior is driven by EnemyAISystem.
"""

import arcade
from constants import (
    BASIC_ENEMY_HEALTH, BASIC_ENEMY_MOVE_SPEED,
    BASIC_ENEMY_PATROL_RANGE, BASIC_ENEMY_DETECTION_RANGE,
    BASIC_ENEMY_ATTACK_RANGE, BASIC_ENEMY_ATTACK_DAMAGE,
    BASIC_ENEMY_WATER_VALUE, BASIC_ENEMY_CHLOROPHYLL_VALUE,
    BASIC_ENEMY_CONTACT_DAMAGE,
    SWARM_BUG_HEALTH, SWARM_BUG_MOVE_SPEED,
    SWARM_BUG_CONTACT_DAMAGE, SWARM_BUG_WATER_VALUE, SWARM_BUG_CHLOROPHYLL_VALUE,
    COLOR_BASIC_ENEMY, COLOR_SWARM_BUG,
)

# Enemy state constants
ENEMY_IDLE = "idle"
ENEMY_PATROL = "patrol"
ENEMY_CHASE = "chase"
ENEMY_ATTACK = "attack"
ENEMY_STUNNED = "stunned"
ENEMY_DEAD = "dead"


class Enemy(arcade.Sprite):
    """
    A hostile entity with patrol, chase, attack, stun, and Haustoria support.

    EnemyAISystem reads and sets state each frame.
    """

    def __init__(
        self,
        enemy_type: str,
        center_x: float,
        center_y: float,
        width: int,
        height: int,
        color,
        health: int,
        move_speed: float,
        patrol_range: float,
        detection_range: float,
        attack_range: float,
        contact_damage: int,
        attack_damage: int,
        water_value: float,
        chlorophyll_value: float,
        facing_direction: int = 1,
    ):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(max(width, height), color, outer_alpha=255)
        self.width = width
        self.height = height
        self.center_x = center_x
        self.center_y = center_y

        # Identity
        self.enemy_type: str = enemy_type
        self.facing_direction: int = facing_direction

        # Animation State
        self.textures_list = None
        self.attack_texture = None
        self.cur_texture_index = 0.0
        self.animation_speed = 15.0 # Fast flapping for bugs

        # Resources
        self.health: int = health
        self.max_health: int = health

        # Combat
        self.contact_damage: int = contact_damage
        self.attack_damage: int = attack_damage

        # Movement
        self.move_speed: float = move_speed
        self.patrol_range: float = patrol_range
        self.patrol_origin_x: float = center_x   # centre of patrol / orbit
        self.patrol_origin_y: float = center_y   # centre of patrol / orbit
        self.detection_range: float = detection_range
        self.attack_range: float = attack_range

        # Haustoria
        self.can_be_haustoria_target: bool = True
        self.water_value: float = water_value
        self.chlorophyll_value: float = chlorophyll_value

        # State machine
        self.state: str = ENEMY_PATROL
        self.previous_state: str = ENEMY_PATROL

        # Timers
        self.stun_timer: float = 0.0
        self.attack_cooldown_timer: float = 0.0
        self.attack_windup_timer: float = 0.0
        self.death_timer: float = 0.5  # brief delay before removal

        # Velocity (manual)
        self.vel_x: float = 0.0
        self.vel_y: float = 0.0

    def take_damage(self, amount: int, stun_duration: float = 0.0):
        """Apply damage and optionally stun the enemy."""
        if self.state == ENEMY_DEAD:
            return
        self.health -= amount
        if stun_duration > 0:
            self.stun_timer = stun_duration
            self.state = ENEMY_STUNNED
        if self.health <= 0:
            self.health = 0
            self.state = ENEMY_DEAD

    def set_state(self, new_state: str):
        if new_state != self.state:
            self.previous_state = self.state
            self.state = new_state

    def update_timers(self, delta_time: float):
        self.stun_timer = max(0.0, self.stun_timer - delta_time)
        self.attack_cooldown_timer = max(0.0, self.attack_cooldown_timer - delta_time)
        self.attack_windup_timer = max(0.0, self.attack_windup_timer - delta_time)
        if self.stun_timer <= 0 and self.state == ENEMY_STUNNED:
            self.set_state(ENEMY_PATROL)

    def update_animation(self, delta_time: float):
        """Update sprite texture based on loaded animations."""
        if self.state == ENEMY_ATTACK and self.attack_texture:
            self.texture = self.attack_texture
        elif self.textures_list:
            self.cur_texture_index += self.animation_speed * delta_time
            if self.cur_texture_index >= len(self.textures_list):
                self.cur_texture_index -= len(self.textures_list)
                
            idx = int(self.cur_texture_index)
            if idx >= len(self.textures_list): idx = 0
            self.texture = self.textures_list[idx]
            
        # Re-enforce physical dimensions
        # Make sure it keeps its initial hitbox size regardless of texture
        if self.enemy_type == "swarm_bug":
            self.width = 16
            self.height = 16
        elif self.enemy_type == "basic_ground_enemy":
            self.width = 28
            self.height = 36
            
        # Flip based on horizontal direction
        if self.facing_direction == 1:
            self.scale_x = abs(self.scale_x)
        elif self.facing_direction == -1:
            self.scale_x = -abs(self.scale_x)


def make_basic_enemy(center_x: float, center_y: float, facing: int = 1) -> Enemy:
    """Factory: basic ground-patrolling enemy."""
    enemy = Enemy(
        enemy_type="basic_ground_enemy",
        center_x=center_x, center_y=center_y,
        width=28, height=36,
        color=COLOR_BASIC_ENEMY,
        health=BASIC_ENEMY_HEALTH,
        move_speed=BASIC_ENEMY_MOVE_SPEED,
        patrol_range=BASIC_ENEMY_PATROL_RANGE,
        detection_range=BASIC_ENEMY_DETECTION_RANGE,
        attack_range=BASIC_ENEMY_ATTACK_RANGE,
        contact_damage=BASIC_ENEMY_CONTACT_DAMAGE,
        attack_damage=BASIC_ENEMY_ATTACK_DAMAGE,
        water_value=BASIC_ENEMY_WATER_VALUE,
        chlorophyll_value=BASIC_ENEMY_CHLOROPHYLL_VALUE,
        facing_direction=facing,
    )
    
    # Load textures (4-frame worm animation)
    base_path = "../assets/sprites/enemies/basic_enemy"
    try:
        enemy.textures_list = [arcade.load_texture(f"{base_path}/worm_move_{i}.png") for i in range(3)]
        enemy.attack_texture = arcade.load_texture(f"{base_path}/worm_attack.png")
        enemy.texture = enemy.textures_list[0]
        enemy.animation_speed = 4.0 # Slower crawling speed
    except Exception as e:
        print(f"Failed to load basic enemy textures: {e}")
        
    return enemy


def make_swarm_bug(center_x: float, center_y: float) -> Enemy:
    """Factory: lightweight swarm bug — contact damage, no stun reaction."""
    bug = Enemy(
        enemy_type="swarm_bug",
        center_x=center_x, center_y=center_y,
        width=7, height=6,
        color=COLOR_SWARM_BUG,
        health=SWARM_BUG_HEALTH,
        move_speed=SWARM_BUG_MOVE_SPEED,
        patrol_range=0,
        detection_range=999,      # always chases
        attack_range=16,
        contact_damage=SWARM_BUG_CONTACT_DAMAGE,
        attack_damage=0,
        water_value=SWARM_BUG_WATER_VALUE,
        chlorophyll_value=SWARM_BUG_CHLOROPHYLL_VALUE,
    )
    
    # Load textures
    base_path = "../assets/sprites/enemies/swarm_bug"
    try:
        bug.textures_list = [arcade.load_texture(f"{base_path}/bug_fly_{i}.png") for i in range(4)]
        bug.texture = bug.textures_list[0]
        # Increase drawing size slightly to make them visible but keep small hit box
        bug.width = 16
        bug.height = 16
    except Exception as e:
        print(f"Failed to load swarm bug textures: {e}")
        
    bug.can_be_haustoria_target = True
    return bug
