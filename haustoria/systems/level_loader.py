"""
level_loader.py — Procedurally builds the two prototype test zones in code.

No .tmx files are required to run the prototype. Everything is defined here
as Python data. When Tiled maps are available, this file can be extended to
load them via arcade.load_tilemap().

Zone 1 (test_zone_01): full traversal tutorial
Zone 2 (test_zone_02): locked swarm room + level exit
"""

import arcade
from entities.interactable_object import (
    make_spear, make_heavy_rock, make_wooden_crate, make_bounce_object,
)
from entities.enemy import make_basic_enemy, make_swarm_bug
from entities.breakable_terrain import BreakableTerrain
from entities.save_point import SavePoint
from entities.level_exit import LevelExit
from constants import (
    COLOR_GROUND, COLOR_PLATFORM, COLOR_WALL, COLOR_LADDER,
    COLOR_WATER_SOURCE, SCREEN_WIDTH, SCREEN_HEIGHT,
)

TILE_SPRITES = {
    COLOR_GROUND: "assets/sprites/tiles/ground.png",
    COLOR_PLATFORM: "assets/sprites/tiles/platform.png",
    COLOR_WALL: "assets/sprites/tiles/wall.png",
}
LADDER_SPRITE = "assets/sprites/tiles/ladder.png"
WATER_SOURCE_SPRITE = "assets/sprites/environment/water_source.png"

# ---------------------------------------------------------------------------
# Helper: create a solid-color wall/platform sprite
# ---------------------------------------------------------------------------

def _make_block(cx: float, cy: float, w: int, h: int, color) -> arcade.Sprite:
    """Create a solid-color rectangular tile sprite."""
    texture_path = TILE_SPRITES.get(color)
    if texture_path:
        try:
            sprite = arcade.Sprite()
            sprite.texture = arcade.load_texture(texture_path)
            sprite.width = w
            sprite.height = h
        except Exception as e:
            print(f"Failed to load tile texture {texture_path}: {e}")
            sprite = arcade.SpriteSolidColor(w, h, color=color)
    else:
        sprite = arcade.SpriteSolidColor(w, h, color=color)
    sprite.center_x = cx
    sprite.center_y = cy
    return sprite


def _make_ladder_tile(cx: float, cy: float, h: int = 32) -> arcade.Sprite:
    """Create a single ladder segment sprite."""
    try:
        sprite = arcade.Sprite()
        sprite.texture = arcade.load_texture(LADDER_SPRITE)
        sprite.width = 16
        sprite.height = h
    except Exception as e:
        print(f"Failed to load ladder texture {LADDER_SPRITE}: {e}")
        sprite = arcade.SpriteSolidColor(16, h, color=COLOR_LADDER)
    sprite.center_x = cx
    sprite.center_y = cy
    return sprite


def _make_water_source(cx: float, cy: float) -> arcade.Sprite:
    """Create a water source pickup sprite."""
    try:
        sprite = arcade.Sprite()
        sprite.texture = arcade.load_texture(WATER_SOURCE_SPRITE)
        sprite.width = 24
        sprite.height = 24
    except Exception as e:
        print(f"Failed to load water source texture {WATER_SOURCE_SPRITE}: {e}")
        sprite = arcade.SpriteSolidColor(24, 24, color=COLOR_WATER_SOURCE)
    sprite.center_x = cx
    sprite.center_y = cy
    return sprite


# ---------------------------------------------------------------------------
# LevelData — what a loaded level contains
# ---------------------------------------------------------------------------

class LevelData:
    """Container for all sprite lists and entity lists for one zone."""

    def __init__(self):
        # Collision layers
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.platform_list = arcade.SpriteList(use_spatial_hash=True)
        self.ladder_list = arcade.SpriteList(use_spatial_hash=True)

        # Entity lists
        self.object_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.breakable_list = arcade.SpriteList()
        self.save_point_list = arcade.SpriteList()
        self.level_exit_list = arcade.SpriteList()
        self.water_source_list = arcade.SpriteList()

        # Python lists for typed entity objects
        self.enemies = []            # list[Enemy]
        self.objects = []            # list[InteractableObject]
        self.breakables = []         # list[BreakableTerrain]
        self.save_points = []        # list[SavePoint]
        self.level_exits = []        # list[LevelExit]

        # Player spawn
        self.spawn_x: float = 100.0
        self.spawn_y: float = 200.0

        # Level size (for camera bounds)
        self.width: float = 4000.0
        self.height: float = 1200.0

        # Zone name
        self.name: str = "unknown"

        # Swarm room info (for camera lock)
        self.swarm_room_cx: float = 0.0
        self.swarm_room_cy: float = 0.0
        self.has_swarm_room: bool = False


# ---------------------------------------------------------------------------
# ASCII Parser
# ---------------------------------------------------------------------------

def load_zone_from_ascii(data: LevelData, layout: list[str], tile_size: int = 32):
    """
    Parses a top-down list of strings to generate the level.
    """
    rows = len(layout)
    data.height = rows * tile_size
    data.width = max(len(line) for line in layout) * tile_size

    for row_idx, row in enumerate(layout):
        # Y coordinate: row 0 is the TOP of the map
        y = (rows - 1 - row_idx) * tile_size + (tile_size / 2)
        
        for col_idx, char in enumerate(row):
            x = col_idx * tile_size + (tile_size / 2)
            
            if char == 'W':
                data.wall_list.append(_make_block(x, y, tile_size, tile_size, COLOR_WALL))
            elif char == 'G':
                data.wall_list.append(_make_block(x, y, tile_size, tile_size, COLOR_GROUND))
            elif char == 'P':
                # Jump-through platforms are visually thinner (24px height)
                data.platform_list.append(_make_block(x, y, tile_size, 24, COLOR_PLATFORM))
            elif char == 'L':
                data.ladder_list.append(_make_ladder_tile(x, y, tile_size))
            elif char == 'B':
                bwall = BreakableTerrain(
                    center_x=x, center_y=y,
                    width=tile_size, height=tile_size,
                    health=1, break_method=BreakableTerrain.BREAK_ANY,
                )
                data.breakable_list.append(bwall)
                data.breakables.append(bwall)
            elif char == 'H':
                bwall = BreakableTerrain(
                    center_x=x, center_y=y,
                    width=tile_size, height=tile_size,
                    health=2, break_method=BreakableTerrain.BREAK_ANY,
                )
                data.breakable_list.append(bwall)
                data.breakables.append(bwall)
            elif char == 'E':
                e = make_basic_enemy(center_x=x, center_y=y, facing=-1)
                e.patrol_origin_x = x
                data.enemy_list.append(e)
                data.enemies.append(e)
            elif char == 'S':
                bug = make_swarm_bug(center_x=x, center_y=y)
                data.enemy_list.append(bug)
                data.enemies.append(bug)
            elif char == 'R':
                r = make_heavy_rock(center_x=x, center_y=y)
                data.object_list.append(r)
                data.objects.append(r)
            elif char == 'C':
                c = make_wooden_crate(center_x=x, center_y=y)
                data.object_list.append(c)
                data.objects.append(c)
            elif char == 'p':
                s = make_spear(center_x=x, center_y=y)
                data.object_list.append(s)
                data.objects.append(s)
            elif char == 'b':
                bo = make_bounce_object(center_x=x, center_y=y)
                data.object_list.append(bo)
                data.objects.append(bo)
            elif char == 'w':
                ws = _make_water_source(x, y)
                data.water_source_list.append(ws)
            elif char == 'v':
                sp = SavePoint(center_x=x, center_y=y, save_id=f"sp_{data.name}_{col_idx}_{row_idx}")
                data.save_point_list.append(sp)
                data.save_points.append(sp)
            elif char == 'x':
                target = "test_zone_02" if data.name == "test_zone_01" else "test_zone_01"
                ex = LevelExit(
                    center_x=x, center_y=y,
                    width=48, height=tile_size*2,
                    target_level=target,
                    target_spawn="default"
                )
                data.level_exit_list.append(ex)
                data.level_exits.append(ex)
            elif char == '+':
                data.spawn_x = x
                data.spawn_y = y
            elif char == '@':
                data.has_swarm_room = True
                data.swarm_room_cx = x
                data.swarm_room_cy = y


# ---------------------------------------------------------------------------
# Zone 1 — Traversal tutorial
# ---------------------------------------------------------------------------

ZONE_01_MAP = [
    "WGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGW",
    "W                                                                                                                                             W",
    "W                                                                                                                                             W",
    "W                                                                                                                                             W",
    "W                                                                                                                                             W",
    "W                                                                                                                                             W",
    "W                                                                                                                                             W",
    "W                               W    W                                         LW                                                             W",
    "W                        PPP    W    W                                         LW                                                             W",
    "W                               W    W   w                                     LWPPPP                                                         W",
    "W                              PW    WPPPPPPP                                  LW                                                             W",
    "W                               W    W                                         LW                                                             W",
    "W                               W    W                                         LW                                                             W",
    "W                          PP   W    W                                         LW                                                             W", "W                               W    W                                         LW        PPPPPPPPPP                                           W",
    "W                               W    W           PPPP                          LW                                                             W",
    "W                       P       W    W                                         LW                                                             W",
    "W                               W    W                                         LW               E                                             W",
    "W                   PPP         W    W                                         LW    PPPPPPPPPPPPPPPP                                         W",
    "W                               W    W                                         LW                                                             W",
    "W                               W    W                   PPPP                  LW                                                             W",
    "W                PPP            W    W                                         LW                                                             W",
    "W                               W    W                                         LW                        PPPPPPPPPPPPPPPP                     W",
    "W           PPP                 W    W                                         LW                                                             W",
    "W                               W    W                             p           LW                                                             W",
    "W      PPP                      W    W                          PPPP           LW                   H                                         W",
    "W                                    B                                         LW                   H                                         W",
    "W                                    B                                         LW                   H                                         W",
    "W +           R            R         B                                         LW      E             H                                       xW",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
]

def load_zone_01() -> LevelData:
    data = LevelData()
    data.name = "test_zone_01"
    load_zone_from_ascii(data, ZONE_01_MAP)
    return data


# ---------------------------------------------------------------------------
# Zone 2 — Locked swarm room
# ---------------------------------------------------------------------------

ZONE_02_MAP = [
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "W                                      W",
    "W                                      W",
    "W                                      W",
    "W                             S S S S  W",
    "W                             S S S S  W",
    "W                                      W",
    "W                                      W",
    "W                                      W",
    "W                                      W",
    "W                                      W",
    "W                   @                  W",
    "W               PPPPPPPP               W",
    "W                                      W",
    "W                                      W",
    "W                                      W",
    "W      PPPPPP              PPPPPP      W",
    "W                                      W",
    "W                                      W",
    "W +   v       R    b                  xW",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
]

def load_zone_02() -> LevelData:
    data = LevelData()
    data.name = "test_zone_02"
    load_zone_from_ascii(data, ZONE_02_MAP)
    return data


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_level(level_name: str) -> LevelData:
    """
    Load a level by name.
    Falls back to test zones if no .tmx file is present.
    """
    loaders = {
        "test_zone_01": load_zone_01,
        "test_zone_02": load_zone_02,
    }
    if level_name not in loaders:
        print(f"[LevelLoader] Unknown level '{level_name}', loading zone 01.")
        return load_zone_01()
    return loaders[level_name]()
