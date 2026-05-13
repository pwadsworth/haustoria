"""
constants.py — All tunable gameplay values for Haustoria.

If a value affects game feel, it goes here — not scattered in other files.
"""

import arcade

# ---------------------------------------------------------------------------
# Screen
# ---------------------------------------------------------------------------
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Haustoria"
TARGET_FPS = 60

# ---------------------------------------------------------------------------
# World / Tile
# ---------------------------------------------------------------------------
TILE_SIZE = 32

# ---------------------------------------------------------------------------
# Physics
# ---------------------------------------------------------------------------
GRAVITY = 0.5               # pixels/frame² applied by PhysicsEnginePlatformer
PLAYER_MAX_FALL_SPEED = 12.0  # cap downward speed (pixels/frame)

# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 80

# ---------------------------------------------------------------------------
# Player Movement
# ---------------------------------------------------------------------------
PLAYER_MOVE_SPEED = 5.0     # pixels/frame horizontal
PLAYER_JUMP_SPEED = 12.0    # pixels/frame initial vertical (positive = up)

COYOTE_TIME = 0.10          # seconds after leaving ledge where jump still fires
JUMP_BUFFER_TIME = 0.12     # seconds early jump press is remembered

# ---------------------------------------------------------------------------
# Dash
# ---------------------------------------------------------------------------
DASH_SPEED = 15.0
DASH_DURATION = 0.2
DASH_COOLDOWN = 0.8

#  ---------------------------------------------------------------------------
# Wall Movement
# ---------------------------------------------------------------------------
WALL_SLIDE_SPEED = 0.84     # max fall speed while wall-clinging (px/frame)
WALL_JUMP_X_FORCE = 8.0     # horizontal kick on wall jump
WALL_JUMP_Y_FORCE = 11.0    # vertical kick on wall jump
WALL_JUMP_WINDOW = 0.25     # seconds after leaving wall where jump fires
WALL_BOUNCE_LOCKOUT = 0.25  # prevent immediate re-cling after wall jump

# ---------------------------------------------------------------------------
# Slide / Roll
# ---------------------------------------------------------------------------
SLIDE_SPEED = 10.0
SLIDE_DURATION = 0.22
SLIDE_COOLDOWN = 0.5

ROLL_SPEED = 9.0
ROLL_DURATION = 0.30
ROLL_COOLDOWN = 0.6

# ---------------------------------------------------------------------------
# Climbing (ladder)
# ---------------------------------------------------------------------------
CLIMB_SPEED = 3.5

# ---------------------------------------------------------------------------
# Object Carry
# ---------------------------------------------------------------------------
HOLD_OFFSET_X = 10          # pixels in front of player
HOLD_OFFSET_Y = 0

HEAVY_SPEED_MULT = 0.75
HEAVY_JUMP_MULT = 0.85

# ---------------------------------------------------------------------------
# Object Throw
# ---------------------------------------------------------------------------
THROW_FORCE_X = 14.0
THROW_FORCE_Y = 5.0         # slight upward arc
THROW_IGNORE_TIMER = 0.2    # seconds to skip player collision after throw

# ---------------------------------------------------------------------------
# Bounce Object
# ---------------------------------------------------------------------------
BOUNCE_VELOCITY = 14.0      # upward speed given to player on bounce
BOUNCE_COOLDOWN = 0.2

# ---------------------------------------------------------------------------
# Object Physics (manual, not Arcade engine)
# ---------------------------------------------------------------------------
OBJECT_GRAVITY = 0.6
OBJECT_MAX_FALL = 16.0
OBJECT_FRICTION = 0.85      # horizontal damping when grounded

# ---------------------------------------------------------------------------
# Combat
# ---------------------------------------------------------------------------
ATTACK_DURATION = 0.2
ATTACK_COOLDOWN = 0.5
ATTACK_HITBOX_OFFSET = 36   # pixels in front of player
ATTACK_HITBOX_SIZE = 32

PLAYER_KNOCKBACK_X = 6.0
PLAYER_KNOCKBACK_Y = 4.0

ENEMY_KNOCKBACK_X = 8.0
ENEMY_KNOCKBACK_Y = 5.0

LIGHT_STUN = 0.4
HEAVY_STUN = 1.2

# ---------------------------------------------------------------------------
# Haustoria Ability
# ---------------------------------------------------------------------------
HAUSTORIA_RANGE = 56        # pixels — close/dangerous range
HAUSTORIA_DRAIN_DURATION = 1.8
HAUSTORIA_WATER_RATE = 20.0    # units per second gained
HAUSTORIA_CHLOROPHYLL_RATE = 20.0
HAUSTORIA_ENEMY_DAMAGE_RATE = 15.0  # health drained from enemy per second

# ---------------------------------------------------------------------------
# Player Resources
# ---------------------------------------------------------------------------
PLAYER_MAX_HEALTH = 5
PLAYER_MAX_WATER = 100.0
PLAYER_MAX_CHLOROPHYLL = 100.0

WATER_DRAIN_RATE = 0.8      # units per second
CHLOROPHYLL_DRAIN_RATE = 0.4

# ---------------------------------------------------------------------------
# Enemies
# ---------------------------------------------------------------------------
BASIC_ENEMY_HEALTH = 30
BASIC_ENEMY_MOVE_SPEED = 2.0
BASIC_ENEMY_PATROL_RANGE = 200
BASIC_ENEMY_DETECTION_RANGE = 220
BASIC_ENEMY_ATTACK_RANGE = 20
BASIC_ENEMY_ATTACK_DAMAGE = 0.5
BASIC_ENEMY_WATER_VALUE = 20.0
BASIC_ENEMY_CHLOROPHYLL_VALUE = 15.0
BASIC_ENEMY_CONTACT_DAMAGE = 0.5

SWARM_BUG_HEALTH = 6
SWARM_BUG_MOVE_SPEED = 3.5
SWARM_BUG_CONTACT_DAMAGE = 0.5
SWARM_BUG_WATER_VALUE = 5.0
SWARM_BUG_CHLOROPHYLL_VALUE = 3.0

SWARM_AGGRO_RANGE = 600        # px — Distance to trigger swarm chase

# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------
CAMERA_LERP_SPEED = 0.12    # 0.0 = frozen, 1.0 = instant snap

# ---------------------------------------------------------------------------
# Tilemap Layer Names (must stay consistent across all .tmx files)
# ---------------------------------------------------------------------------
LAYER_PLATFORMS = "Platforms"
LAYER_WALLS = "Walls"
LAYER_LADDERS = "Ladders"
LAYER_HAZARDS = "Hazards"
LAYER_OBJECTS = "Objects"
LAYER_ENEMIES = "Enemies"
LAYER_ENEMY_SPAWNS = "EnemySpawns"
LAYER_SAVE_POINTS = "SavePoints"
LAYER_BREAKABLE_WALLS = "BreakableWalls"
LAYER_LEVEL_EXITS = "LevelExits"
LAYER_WATER_SOURCES = "WaterSources"
LAYER_DECOR_BACK = "Decor_Back"
LAYER_DECOR_FRONT = "Decor_Front"

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG_MODE = True
DEBUG_KEY = arcade.key.F3

# ---------------------------------------------------------------------------
# Colors (placeholder art palette)
# ---------------------------------------------------------------------------
COLOR_GROUND = (80, 55, 40)
COLOR_PLATFORM = (100, 70, 50)
COLOR_WALL = (90, 60, 45)
COLOR_LADDER = (160, 120, 60)
COLOR_PLAYER = (240, 240, 200)   # bright cream — stands out against dark bg
COLOR_BASIC_ENEMY = (180, 80, 60)
COLOR_SWARM_BUG = (220, 120, 40)
COLOR_SPEAR = (200, 200, 180)
COLOR_ROCK = (140, 140, 130)
COLOR_CRATE = (160, 130, 90)
COLOR_BREAKABLE_WALL = (160, 100, 80)
COLOR_BOUNCE_OBJECT = (100, 200, 180)
COLOR_SAVE_POINT = (100, 200, 120)
COLOR_LEVEL_EXIT = (180, 180, 60)
COLOR_WATER_SOURCE = (80, 160, 220)
COLOR_RESOURCE_WATER = (80, 160, 220)
COLOR_RESOURCE_CHLOROPHYLL = (80, 200, 100)
COLOR_RESOURCE_HEALTH = (220, 80, 80)
COLOR_HITBOX = (255, 80, 80, 160)
COLOR_HAUSTORIA_ACTIVE = (180, 255, 140)
