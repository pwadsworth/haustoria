"""
game_window.py — Main Arcade window: update order, draw, input, level loading.

Responsibility: wire all systems together and own top-level game state.
Does NOT contain detailed movement, AI, or interaction internals.
"""

import arcade
import arcade.color

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, TARGET_FPS,
    DEBUG_KEY, DEBUG_MODE, GRAVITY,
    COLOR_HAUSTORIA_ACTIVE,
)
from game.player import Player, STATE_DEAD, STATE_USING_HAUSTORIA
from game.player_controller import PlayerController
from game.camera import Camera
from game.resources import ResourceSystem
from game.save_system import SaveSystem
from systems.level_loader import load_level, LevelData
from systems.object_interaction_system import ObjectInteractionSystem
from systems.enemy_ai_system import EnemyAISystem
from systems.combat_system import CombatSystem
from systems.haustoria_system import HaustoriaSystem
from systems.collision_system import CollisionSystem

# Respawn delay after death
RESPAWN_DELAY = 2.0


class HaustoriaGame(arcade.Window):
    """
    Top-level game window.

    Update order (per spec §9):
    1. Player timers
    2. Player controller (movement)
    3. Physics engine
    4. Object interaction system
    5. Enemy AI system
    6. Combat system
    7. Haustoria system
    8. Collision system
    9. Resource system
    10. Camera
    """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color((20, 18, 28))

        # Systems (constructed once, updated every frame)
        self.resource_system = ResourceSystem()
        self.save_system = SaveSystem()
        self.haustoria_system = HaustoriaSystem()
        self.combat_system = CombatSystem()
        self.collision_system = CollisionSystem()

        # Cameras
        self.world_camera = Camera()
        self.gui_camera = arcade.Camera2D()

        # Game state
        self.debug_mode: bool = DEBUG_MODE
        self.current_level_name: str = "test_zone_01"
        self.respawn_timer: float = 0.0
        self.is_transitioning: bool = False

        # Populated by setup()
        self.player: Player | None = None
        self.player_list: arcade.SpriteList | None = None  # single-sprite list for drawing
        self.level_data: LevelData | None = None
        self.physics_engine = None
        self.player_controller: PlayerController | None = None
        self.object_system: ObjectInteractionSystem | None = None
        self.enemy_ai: EnemyAISystem | None = None

        # Track total time for flicker effects
        self._total_time: float = 0.0

        # Held keys set — populated by on_key_press/on_key_release
        self._held_keys: set = set()

        # One-shot input flags (set in on_key_press, consumed in update)
        self._input_pickup_drop = False
        self._input_throw_attack = False
        self._input_haustoria = False
        self._input_jump = False
        self._input_dash = False
        self._input_interact = False   # E key — also Haustoria
        self._input_respawn = False

        # Text objects created in setup() once the GL context is ready
        self._dbg_texts = []
        self._death_text = None
        self._respawn_text = None

    # ------------------------------------------------------------------
    # Setup / Level Loading
    # ------------------------------------------------------------------

    def setup(self):
        """Initialize player and load the first level."""
        self.player = Player()
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self._setup_collision_callbacks()
        self.load_level(self.current_level_name)

        # Create Text objects here — after the window/GL context is ready
        _dbg_color = (200, 255, 200)
        _dbg_y = SCREEN_HEIGHT - 80
        self._dbg_texts = [
            arcade.Text("", 10, _dbg_y - i * 16, _dbg_color, 11)
            for i in range(6)
        ]
        self._death_text = arcade.Text(
            "YOU DIED", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30,
            (200, 50, 50), 48, anchor_x="center",
        )
        self._respawn_text = arcade.Text(
            "Press R to respawn", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20,
            (180, 180, 180), 20, anchor_x="center",
        )

    def load_level(self, level_name: str, spawn_id: str = "default"):
        """Load a level, rebuild physics engine and systems."""
        self.current_level_name = level_name
        self.level_data = load_level(level_name)
        data = self.level_data

        # Position player at spawn
        self.player.center_x = data.spawn_x
        self.player.center_y = data.spawn_y
        self.player.change_x = 0
        self.player.change_y = 0
        self.player.is_dead = False

        # Solid walls — block all sides
        combined_walls = arcade.SpriteList(use_spatial_hash=True)
        for s in data.wall_list:
            combined_walls.append(s)
        # Breakable walls also block movement until broken
        for s in data.breakable_list:
            combined_walls.append(s)

        # Build physics engine
        # NOTE: platform_list is passed to platforms= (one-way, block only from above)
        #       so players can jump through from below and land from above.
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            walls=combined_walls,
            platforms=data.platform_list,
            gravity_constant=GRAVITY,
            ladders=data.ladder_list,
        )

        # Build systems that depend on level geometry
        self.player_controller = PlayerController(
            self.player, self.physics_engine, combined_walls
        )
        self.object_system = ObjectInteractionSystem(
            data.wall_list, data.breakable_list
        )
        self.enemy_ai = EnemyAISystem(data.wall_list, data.platform_list)

        # Camera bounds
        self.world_camera.set_bounds(data.width, data.height)
        self.world_camera.unlock()

        # Lock camera for swarm/boss rooms
        if data.has_swarm_room:
            self.world_camera.lock_to_room(data.swarm_room_cx, data.swarm_room_cy)

        # Snap camera to player spawn immediately
        self.world_camera.pos_x = data.spawn_x
        self.world_camera.pos_y = data.spawn_y

        # Auto-save at start of a new zone (uses default if no save point visited)
        if self.save_system.has_save is False:
            self.save_system.saved_x = data.spawn_x
            self.save_system.saved_y = data.spawn_y
            self.save_system.has_save = True

        self.is_transitioning = False
        print(f"[Game] Loaded level: {level_name}")

    def _setup_collision_callbacks(self):
        """Wire collision system callbacks to game_window methods."""
        self.collision_system.on_save_activate = self._on_save_activate
        self.collision_system.on_level_exit = self._on_level_exit
        self.collision_system.on_water_pickup = self._on_water_pickup

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_save_activate(self, player, save_point):
        self.save_system.save(player, save_point)

    def _on_level_exit(self, target_level: str, target_spawn: str):
        if self.is_transitioning:
            return
        self.is_transitioning = True
        print(f"[Game] Transitioning to {target_level}")
        self.load_level(target_level, target_spawn)

    def _on_water_pickup(self, player, water_sprite):
        player.water = min(player.max_water, player.water + 30.0)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def on_update(self, delta_time: float):
        data = self.level_data
        if data is None:
            return

        self._total_time += delta_time

        # Handle death + respawn
        if self.player.is_dead:
            self.respawn_timer -= delta_time
            if self.respawn_timer <= 0 and self._input_respawn:
                self.save_system.respawn(self.player)
                self.respawn_timer = 0.0
            # Auto-respawn after delay
            if self.respawn_timer <= -RESPAWN_DELAY:
                self.save_system.respawn(self.player)
                self.respawn_timer = 0.0
            self._reset_one_shot_inputs()
            return

        # 1. Player timers
        self.player.update_timers(delta_time)
        self.player.update_animation(delta_time)

        # 2. Feed one-shot inputs into controller
        self._feed_inputs_to_controller()

        # 3. Player controller movement
        self.player_controller.update(delta_time)

        # 4. Physics engine
        self.physics_engine.update()

        # 4b. Re-apply wall-slide cap after gravity is applied
        self.player_controller.apply_post_physics_clamp()

        # 5. Object interaction
        self.object_system.update(
            self.player, data.object_list, delta_time
        )

        # 6. Enemy AI
        self.enemy_ai.update(data.enemy_list, self.player, delta_time)

        # 7. Combat
        self.combat_system.update(
            self.player, data.enemy_list, data.object_list, delta_time
        )

        # 8. Haustoria
        self.haustoria_system.update(self.player, delta_time)

        # 9. Collision (non-physics events)
        self.collision_system.update(
            self.player,
            data.enemy_list,
            data.save_point_list,
            data.level_exit_list,
            data.water_source_list,
            data.ladder_list,
            self.combat_system,
            self.player_controller,
            interaction_key_pressed=self._input_interact,
        )

        # 10. Resource drain (HUD)
        self.resource_system.update(self.player, delta_time)

        # 11. Camera
        self.world_camera.update(self.player.center_x, self.player.center_y)

        # Death check
        if self.player.is_dead and self.respawn_timer == 0.0:
            self.respawn_timer = RESPAWN_DELAY

        # Reset one-shot inputs at end of frame
        self._reset_one_shot_inputs()
        self.player_controller.reset_frame_inputs()

    def _feed_inputs_to_controller(self):
        """Copy window input flags into the player controller."""
        ctrl = self.player_controller

        # Held keys
        keys = self._held_keys
        ctrl.input_left = arcade.key.A in keys or arcade.key.LEFT in keys
        ctrl.input_right = arcade.key.D in keys or arcade.key.RIGHT in keys
        ctrl.input_up = arcade.key.W in keys or arcade.key.UP in keys
        ctrl.input_down = arcade.key.S in keys or arcade.key.DOWN in keys
        ctrl.input_jump_held = arcade.key.SPACE in keys

        # One-shot
        ctrl.input_jump = self._input_jump
        ctrl.input_dash = self._input_dash
        ctrl.input_throw_attack = self._input_throw_attack

        # Pickup/drop (F key)
        if self._input_pickup_drop:
            if self.player.held_object:
                self.object_system.drop(self.player)
            else:
                self.object_system.try_pickup(self.player, self.level_data.object_list)

        # Throw (J while holding)
        if self._input_throw_attack and self.player.held_object:
            self.object_system.throw(self.player)
            ctrl.input_throw_attack = False  # consumed by throw

        # Haustoria (E)
        if self._input_haustoria or self._input_interact:
            if not self.player.is_using_haustoria:
                self.haustoria_system.try_activate(self.player, self.level_data.enemy_list)

    def _reset_one_shot_inputs(self):
        self._input_jump = False
        self._input_dash = False
        self._input_pickup_drop = False
        self._input_throw_attack = False
        self._input_haustoria = False
        self._input_interact = False
        self._input_respawn = False

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def on_draw(self):
        self.clear()
        data = self.level_data
        if data is None:
            return

        # --- World space ---
        self.world_camera.use()

        # Terrain
        data.wall_list.draw()
        data.platform_list.draw()
        data.ladder_list.draw()
        data.breakable_list.draw()

        # Entities
        data.object_list.draw()
        data.save_point_list.draw()
        data.level_exit_list.draw()
        data.water_source_list.draw()
        data.enemy_list.draw()

        # Player (flash when invincible) — Arcade 3.x: draw via SpriteList
        if not self.player.is_invincible or int(self._total_time * 10) % 2 == 0:
            self.player_list.draw()

        # Haustoria visual — draw line to target
        if self.player.is_using_haustoria and self.haustoria_system.current_target:
            t = self.haustoria_system.current_target
            arcade.draw_line(
                self.player.center_x, self.player.center_y,
                t.center_x, t.center_y,
                COLOR_HAUSTORIA_ACTIVE, 3,
            )

        if self.debug_mode:
            self._draw_debug_world()

        # --- GUI space ---
        self.gui_camera.use()
        self.resource_system.draw_hud(self.player)

        if self.debug_mode:
            self._draw_debug_gui()

        if self.player.is_dead:
            self._draw_death_screen()

    # ------------------------------------------------------------------
    # Debug drawing
    # ------------------------------------------------------------------

    def _draw_debug_world(self):
        """Draw hitboxes and state labels in world space."""
        # Player hitbox
        arcade.draw_lrbt_rectangle_outline(
            self.player.left, self.player.right,
            self.player.bottom, self.player.top,
            (80, 255, 80), 1,
        )
        # Enemy hitboxes + state
        for enemy in self.level_data.enemy_list:
            arcade.draw_lrbt_rectangle_outline(
                enemy.left, enemy.right,
                enemy.bottom, enemy.top,
                (255, 80, 80), 1,
            )
            arcade.draw_text(
                enemy.state,
                enemy.center_x - 20, enemy.top + 4,
                (255, 180, 80), 9,
            )
        # Object hitboxes + state
        for obj in self.level_data.object_list:
            arcade.draw_lrbt_rectangle_outline(
                obj.left, obj.right,
                obj.bottom, obj.top,
                (80, 180, 255), 1,
            )

    def _draw_debug_gui(self):
        """Draw player state text, velocity, FPS in screen space."""
        p = self.player
        lines = [
            f"State: {p.current_state}",
            f"Vel: ({p.change_x:.1f}, {p.change_y:.1f})",
            f"Pos: ({p.center_x:.0f}, {p.center_y:.0f})",
            f"Grounded: {p.is_grounded}  WallL: {p.is_touching_wall_left}  WallR: {p.is_touching_wall_right}",
            f"Held: {p.held_object.object_type if p.held_object else 'None'}",
            f"FPS: {1.0 / max(self.delta_time, 0.001):.0f}",
        ]
        for txt, line in zip(self._dbg_texts, lines):
            txt.value = line
            txt.draw()

    def _draw_death_screen(self):
        """Overlay when player is dead."""
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 0, 0, 140)
        )
        self._death_text.draw()
        self._respawn_text.draw()

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def on_key_press(self, key, modifiers):
        self._held_keys.add(key)
        if key == arcade.key.SPACE:
            self._input_jump = True
        elif key == arcade.key.LSHIFT or key == arcade.key.RSHIFT:
            self._input_dash = True
        elif key == arcade.key.F:
            self._input_pickup_drop = True
        elif key == arcade.key.J:
            self._input_throw_attack = True
        elif key == arcade.key.E:
            self._input_haustoria = True
            self._input_interact = True
        elif key == DEBUG_KEY:
            self.debug_mode = not self.debug_mode
            print(f"[Debug] Debug mode {'ON' if self.debug_mode else 'OFF'}")
        elif key == arcade.key.R:
            self._input_respawn = True

    def on_key_release(self, key, modifiers):
        self._held_keys.discard(key)
