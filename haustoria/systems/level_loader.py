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


# ---------------------------------------------------------------------------
# Helper: create a solid-color wall/platform sprite
# ---------------------------------------------------------------------------

def _make_block(cx: float, cy: float, w: int, h: int, color) -> arcade.Sprite:
    """Create a solid-color rectangular tile sprite."""
    sprite = arcade.SpriteSolidColor(w, h, color=color)
    sprite.center_x = cx
    sprite.center_y = cy
    return sprite


def _make_ladder_tile(cx: float, cy: float, h: int = 32) -> arcade.Sprite:
    """Create a single ladder segment sprite."""
    sprite = arcade.SpriteSolidColor(16, h, color=COLOR_LADDER)
    sprite.center_x = cx
    sprite.center_y = cy
    return sprite


def _make_water_source(cx: float, cy: float) -> arcade.Sprite:
    """Create a water source pickup sprite."""
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
# Zone 1 — Traversal tutorial
# ---------------------------------------------------------------------------
# Layout (pixel coords, Y=0 at bottom):
#
#  Section A: Open ground + platform staircase (x 0–1000)
#  Section B: Wall-cling shaft (x 1000–1300)
#  Section C: Ladder climb (x 1300–1700)
#  Section D: Enemy + object arena (x 1700–2800)
#  Section E: Breakable-wall shortcut (x 2200)
#  Section F: Level exit (x 2800)
# ---------------------------------------------------------------------------

def load_zone_01() -> LevelData:
    data = LevelData()
    data.name = "test_zone_01"
    data.width = 3200.0
    data.height = 1024.0
    data.spawn_x = 80
    data.spawn_y = 120

    W = data.wall_list
    P = data.platform_list
    L = data.ladder_list

    # ---- Ground floor (entire zone) ----
    W.append(_make_block(1600, 16, 3200, 32, COLOR_GROUND))

    # ---- Left boundary wall ----
    W.append(_make_block(-16, 512, 32, 1024, COLOR_WALL))

    # ---- Section A: Staircase platforms ----
    P.append(_make_block(300,  160, 192, 24, COLOR_PLATFORM))
    P.append(_make_block(560,  256, 192, 24, COLOR_PLATFORM))
    P.append(_make_block(820,  352, 192, 24, COLOR_PLATFORM))

    # Drop-off before shaft
    W.append(_make_block(960, 16, 32, 32, COLOR_GROUND))  # small step

    # ---- Section B: Wall-cling vertical shaft ----
    # Left wall face (player clings right side)
    W.append(_make_block(1024, 400, 32, 800, COLOR_WALL))
    # Right wall face (player clings left side)
    W.append(_make_block(1216, 400, 32, 800, COLOR_WALL))
    # Shaft floor
    W.append(_make_block(1120, 16, 192 - 32, 32, COLOR_GROUND))
    # Platform at top of shaft
    P.append(_make_block(1120, 680, 160, 24, COLOR_PLATFORM))

    # ---- Section C: Ladder climb ----
    # Vertical wall with ladder cutout
    W.append(_make_block(1360, 300, 32, 600, COLOR_WALL))
    # Ladder tiles (center x=1360)
    for row in range(10):
        L.append(_make_ladder_tile(1360, 64 + row * 48))
    # Landing platform above ladder
    P.append(_make_block(1520, 512, 320, 24, COLOR_PLATFORM))

    # ---- Section D: Enemy + object arena ----
    # Wide ground section continues from floor
    P.append(_make_block(2000, 320, 512, 24, COLOR_PLATFORM))  # mid platform
    P.append(_make_block(2400, 480, 320, 24, COLOR_PLATFORM))  # high platform

    # ---- Section E: Breakable wall (shortcut) ----
    bwall = BreakableTerrain(
        center_x=2200, center_y=80,
        width=32, height=128,
        health=2, break_method=BreakableTerrain.BREAK_ANY,
    )
    data.breakable_list.append(bwall)
    data.breakables.append(bwall)
    # Wall blocks around the breakable section
    W.append(_make_block(2200, 80, 32, 128, COLOR_WALL))  # visual backing (removed when broken)

    # ---- Section F: Exit ----
    exit_sprite = LevelExit(
        center_x=3050, center_y=80,
        width=48, height=80,
        target_level="test_zone_02",
        target_spawn="default",
    )
    data.level_exit_list.append(exit_sprite)
    data.level_exits.append(exit_sprite)

    # ---- Enemies ----
    e1 = make_basic_enemy(center_x=1800, center_y=80, facing=-1)
    e1.patrol_origin_x = 1800
    data.enemy_list.append(e1)
    data.enemies.append(e1)

    e2 = make_basic_enemy(center_x=2100, center_y=356, facing=1)
    e2.patrol_origin_x = 2100
    data.enemy_list.append(e2)
    data.enemies.append(e2)

    # ---- Objects ----
    spear = make_spear(center_x=200, center_y=80)
    data.object_list.append(spear)
    data.objects.append(spear)

    rock = make_heavy_rock(center_x=450, center_y=80)
    data.object_list.append(rock)
    data.objects.append(rock)

    crate = make_wooden_crate(center_x=650, center_y=280)
    data.object_list.append(crate)
    data.objects.append(crate)

    # Bounce objects (embedded spear tips)
    b1 = make_bounce_object(center_x=480, center_y=176)  # near staircase platform
    data.object_list.append(b1)
    data.objects.append(b1)

    b2 = make_bounce_object(center_x=1900, center_y=344)  # on mid platform
    data.object_list.append(b2)
    data.objects.append(b2)

    # ---- Water source ----
    ws = _make_water_source(150, 70)
    data.water_source_list.append(ws)

    # ---- Save point ----
    sp = SavePoint(center_x=250, center_y=58, save_id="sp_zone01")
    data.save_point_list.append(sp)
    data.save_points.append(sp)

    return data


# ---------------------------------------------------------------------------
# Zone 2 — Locked swarm room
# ---------------------------------------------------------------------------
# Camera locks to this room. 12 swarm bugs spawn in waves.
# A level exit leads to the end.
# ---------------------------------------------------------------------------

def load_zone_02() -> LevelData:
    data = LevelData()
    data.name = "test_zone_02"
    data.width = 1280.0
    data.height = 720.0
    data.spawn_x = 80
    data.spawn_y = 120

    # Camera locks to center of this room
    data.has_swarm_room = True
    data.swarm_room_cx = 640
    data.swarm_room_cy = 360

    W = data.wall_list
    P = data.platform_list

    # ---- Room boundaries ----
    W.append(_make_block(640,    8, 1280,  16, COLOR_GROUND))   # floor
    W.append(_make_block(640,  712, 1280,  16, COLOR_WALL))     # ceiling
    W.append(_make_block(   8, 360,   16, 720, COLOR_WALL))     # left
    W.append(_make_block(1272, 360,   16, 720, COLOR_WALL))     # right

    # ---- Interior platforms ----
    P.append(_make_block(320,  240, 192, 24, COLOR_PLATFORM))
    P.append(_make_block(640,  400, 256, 24, COLOR_PLATFORM))
    P.append(_make_block(960,  240, 192, 24, COLOR_PLATFORM))

    # ---- Bounce objects in arena ----
    b1 = make_bounce_object(center_x=320, center_y=264)
    data.object_list.append(b1)
    data.objects.append(b1)

    # ---- Throwable rock for combat ----
    rock = make_heavy_rock(center_x=160, center_y=80)
    data.object_list.append(rock)
    data.objects.append(rock)

    # ---- Swarm bugs (spawned in a loose cluster) ----
    spawn_positions = [
        (900, 600), (950, 600), (1000, 600), (1050, 600),
        (900, 550), (950, 550), (1000, 550), (1050, 550),
        (800, 600), (850, 600), (800, 550), (850, 550),
    ]
    for sx, sy in spawn_positions:
        bug = make_swarm_bug(center_x=sx, center_y=sy)
        data.enemy_list.append(bug)
        data.enemies.append(bug)

    # ---- Level exit ----
    exit_sprite = LevelExit(
        center_x=1240, center_y=80,
        width=48, height=80,
        target_level="test_zone_01",  # loops back for prototype
        target_spawn="default",
    )
    data.level_exit_list.append(exit_sprite)
    data.level_exits.append(exit_sprite)

    # ---- Save point before boss room ----
    sp = SavePoint(center_x=100, center_y=58, save_id="sp_zone02")
    data.save_point_list.append(sp)
    data.save_points.append(sp)

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
