"""
player_controller.py — Reads input flags and drives all player movement.

Handles: movement, jumping, coyote time, jump buffer, climbing,
         wall cling, wall jump, dash, slide, roll, attack input.
"""

import arcade
from game.player import (
    Player,
    STATE_IDLE, STATE_RUNNING, STATE_JUMPING, STATE_FALLING,
    STATE_WALL_CLINGING, STATE_CLIMBING, STATE_DASHING,
    STATE_SLIDING, STATE_ROLLING, STATE_ATTACKING, STATE_STUNNED,
    STATE_USING_HAUSTORIA,
)
from game.physics_helpers import (
    is_on_ground, is_touching_wall_left, is_touching_wall_right, clamp,
)
from constants import (
    PLAYER_MOVE_SPEED, PLAYER_JUMP_SPEED, PLAYER_MAX_FALL_SPEED,
    COYOTE_TIME, JUMP_BUFFER_TIME,
    DASH_SPEED, DASH_DURATION, DASH_COOLDOWN,
    SLIDE_SPEED, SLIDE_DURATION, SLIDE_COOLDOWN,
    ROLL_SPEED, ROLL_DURATION, ROLL_COOLDOWN,
    WALL_SLIDE_SPEED, WALL_JUMP_X_FORCE, WALL_JUMP_Y_FORCE,
    WALL_BOUNCE_LOCKOUT, WALL_JUMP_WINDOW,
    CLIMB_SPEED, ATTACK_DURATION, ATTACK_COOLDOWN,
    HEAVY_SPEED_MULT, HEAVY_JUMP_MULT,
)


class PlayerController:
    """
    Interprets input flags and applies movement to the player sprite.

    The game window sets input flags each frame; this controller
    translates them into velocity changes and state transitions.
    """

    def __init__(self, player: Player, physics_engine, wall_list):
        self.player = player
        self.physics_engine = physics_engine
        self.wall_list = wall_list

        # --- Raw input flags (set by game_window key handlers) ---
        self.input_left: bool = False
        self.input_right: bool = False
        self.input_up: bool = False
        self.input_down: bool = False
        self.input_jump: bool = False       # pressed this frame
        self.input_jump_held: bool = False  # held
        self.input_dash: bool = False
        self.input_pickup: bool = False
        self.input_throw_attack: bool = False
        self.input_haustoria: bool = False

        # Consumed flags (reset after processing)
        self._jump_consumed: bool = False
        self._dash_consumed: bool = False
        self._pickup_consumed: bool = False
        self._attack_consumed: bool = False
        self._haustoria_consumed: bool = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, delta_time: float):
        """Main update — called once per frame BEFORE physics_engine.update()."""
        p = self.player

        # Cannot do anything while dead
        if p.is_dead:
            return

        # Locked into Haustoria — nothing else runs
        if p.is_using_haustoria:
            return

        self._update_ground_status()
        self._update_wall_status()
        self._update_coyote_timer(delta_time)
        self._update_jump_buffer()

        # Stunned: just fall, no control
        if p.is_stunned:
            self._apply_fall_cap()
            self._resolve_state()
            return

        # Active movement
        if p.is_dashing:
            self._update_dash(delta_time)
        elif p.is_sliding:
            self._update_slide(delta_time)
        elif p.is_rolling:
            self._update_roll(delta_time)
        elif p.is_on_ladder:
            self._update_climb()
        else:
            self._update_horizontal()
            self._update_wall_cling()
            self._update_jump()
            self._apply_fall_cap()

        self._try_dash()
        self._try_slide_or_roll()
        self._try_attack()
        self._update_facing()
        self._resolve_state()

    # ------------------------------------------------------------------
    # Ground / Wall detection
    # ------------------------------------------------------------------

    def _update_ground_status(self):
        p = self.player
        was_grounded = p.is_grounded
        p.is_grounded = self.physics_engine.can_jump()

        # Start coyote timer when player just left the ground
        if was_grounded and not p.is_grounded:
            p.coyote_timer = COYOTE_TIME

    def _update_wall_status(self):
        p = self.player
        p.is_touching_wall_left = is_touching_wall_left(p, self.wall_list)
        p.is_touching_wall_right = is_touching_wall_right(p, self.wall_list)

    # ------------------------------------------------------------------
    # Coyote time / Jump buffer
    # ------------------------------------------------------------------

    def _update_coyote_timer(self, delta_time: float):
        pass  # timer already ticked in player.update_timers()

    def _update_jump_buffer(self):
        """If jump was pressed, store a buffer so it fires on landing."""
        if self.input_jump and not self._jump_consumed:
            self.player.jump_buffer_timer = JUMP_BUFFER_TIME
            # NOTE: do NOT set _jump_consumed here.
            # The actual jump handlers (_update_wall_cling, _update_jump)
            # set it when the jump fires, preventing double-fire.

    # ------------------------------------------------------------------
    # Horizontal movement
    # ------------------------------------------------------------------

    def _update_horizontal(self):
        p = self.player

        # During wall-jump lockout, preserve the kick velocity.
        # This is what makes wall-to-wall bouncing work: the player cannot
        # fight the kick direction while the lockout is active.
        if p.wall_bounce_timer > 0:
            return

        speed = PLAYER_MOVE_SPEED
        if p.held_object and getattr(p.held_object, 'is_heavy', False):
            speed *= HEAVY_SPEED_MULT

        if self.input_left:
            p.change_x = -speed
        elif self.input_right:
            p.change_x = speed
        else:
            p.change_x = 0

    # ------------------------------------------------------------------
    # Wall cling
    # ------------------------------------------------------------------

    def _update_wall_cling(self):
        p = self.player
        if p.is_grounded or p.wall_bounce_timer > 0:
            return

        clinging_left  = p.is_touching_wall_left  and self.input_left
        clinging_right = p.is_touching_wall_right and self.input_right
        touching_wall  = clinging_left or clinging_right

        if touching_wall and p.change_y < 0:
            # Slow the fall while clinging (post-physics clamp is in apply_post_physics_clamp)
            p.change_y = max(p.change_y, -WALL_SLIDE_SPEED)

            # Wall jump: jump pressed while clinging
            if self.input_jump and not self._jump_consumed:
                kick_dir = 1 if clinging_left else -1
                p.change_x = kick_dir * WALL_JUMP_X_FORCE
                p.change_y = WALL_JUMP_Y_FORCE
                p.wall_bounce_timer = WALL_BOUNCE_LOCKOUT
                p.jump_buffer_timer = 0.0
                self._jump_consumed = True
                p.set_state(STATE_JUMPING)

    # ------------------------------------------------------------------
    # Jump
    # ------------------------------------------------------------------

    def _update_jump(self):
        p = self.player
        can_jump = p.is_grounded or p.coyote_timer > 0

        # Fire jump from buffer or fresh press
        fire_jump = (
            (self.input_jump and not self._jump_consumed) or
            (p.jump_buffer_timer > 0 and p.is_grounded)
        )

        if fire_jump and can_jump:
            jump_speed = PLAYER_JUMP_SPEED
            if p.held_object and getattr(p.held_object, 'is_heavy', False):
                jump_speed *= HEAVY_JUMP_MULT
            p.change_y = jump_speed
            p.coyote_timer = 0.0
            p.jump_buffer_timer = 0.0
            self._jump_consumed = True
            p.set_state(STATE_JUMPING)

        # Variable jump height — release jump early to cut height
        if not self.input_jump_held and p.change_y > 3.0 and not p.is_grounded:
            p.change_y *= 0.85

    # ------------------------------------------------------------------
    # Climbing
    # ------------------------------------------------------------------

    def update_ladder_status(self, on_ladder: bool):
        """Called by collision system when player overlaps a ladder."""
        self.player.is_on_ladder = on_ladder

    def _update_climb(self):
        p = self.player
        if self.input_up:
            p.change_y = CLIMB_SPEED
        elif self.input_down:
            p.change_y = -CLIMB_SPEED
        else:
            p.change_y = 0
        p.change_x = 0

    # ------------------------------------------------------------------
    # Dash
    # ------------------------------------------------------------------

    def _try_dash(self):
        p = self.player
        if not self.input_dash or self._dash_consumed:
            return
        if p.dash_cooldown_timer > 0 or p.is_dashing:
            return
        if p.is_using_haustoria or p.is_stunned:
            return

        p.is_dashing = True
        p.dash_timer = DASH_DURATION
        p.dash_cooldown_timer = DASH_COOLDOWN
        p.change_y = 0  # horizontal-only dash
        self._dash_consumed = True

    def _update_dash(self, delta_time: float):
        p = self.player
        p.change_x = p.facing_direction * DASH_SPEED
        p.change_y = 0  # lock vertical during dash
        if p.dash_timer <= 0:
            p.is_dashing = False

    # ------------------------------------------------------------------
    # Slide / Roll
    # ------------------------------------------------------------------

    def _try_slide_or_roll(self):
        p = self.player
        if p.is_dashing or p.is_using_haustoria or p.is_stunned:
            return
        if p.held_object:
            return  # cannot slide while holding

        if self.input_down and self.input_left or self.input_down and self.input_right:
            if p.is_grounded and p.slide_cooldown_timer <= 0 and not p.is_sliding:
                p.is_sliding = True
                p.slide_timer = SLIDE_DURATION
                p.slide_cooldown_timer = SLIDE_COOLDOWN
        elif not p.is_grounded and p.roll_cooldown_timer <= 0 and not p.is_rolling:
            pass  # roll in air — reserved

    def _update_slide(self, delta_time: float):
        p = self.player
        p.change_x = p.facing_direction * SLIDE_SPEED
        if p.slide_timer <= 0:
            p.is_sliding = False

    def _update_roll(self, delta_time: float):
        p = self.player
        p.change_x = p.facing_direction * ROLL_SPEED
        if p.roll_timer <= 0:
            p.is_rolling = False

    # ------------------------------------------------------------------
    # Attack
    # ------------------------------------------------------------------

    def _try_attack(self):
        p = self.player
        if not self.input_throw_attack or self._attack_consumed:
            return
        if p.held_object:
            return  # throw is handled by object system
        if p.attack_cooldown_timer > 0 or p.is_using_haustoria:
            return

        p.is_attacking = True
        p.attack_timer = ATTACK_DURATION
        p.attack_cooldown_timer = ATTACK_COOLDOWN
        self._attack_consumed = True

    # ------------------------------------------------------------------
    # Facing
    # ------------------------------------------------------------------

    def _update_facing(self):
        p = self.player
        if self.input_right:
            p.facing_direction = 1
        elif self.input_left:
            p.facing_direction = -1

    # ------------------------------------------------------------------
    # Fall cap
    # ------------------------------------------------------------------

    def _apply_fall_cap(self):
        """Don't let the player fall faster than terminal velocity."""
        p = self.player
        if p.change_y < -PLAYER_MAX_FALL_SPEED:
            p.change_y = -PLAYER_MAX_FALL_SPEED

    # ------------------------------------------------------------------
    # State resolution
    # ------------------------------------------------------------------

    def _resolve_state(self):
        """Determine current state from flags for animation/debug."""
        p = self.player
        if p.is_dead:
            return
        if p.is_stunned:
            p.set_state(STATE_STUNNED)
        elif p.is_using_haustoria:
            p.set_state(STATE_USING_HAUSTORIA)
        elif p.is_dashing:
            p.set_state(STATE_DASHING)
        elif p.is_sliding:
            p.set_state(STATE_SLIDING)
        elif p.is_rolling:
            p.set_state(STATE_ROLLING)
        elif p.is_attacking:
            p.set_state(STATE_ATTACKING)
        elif p.is_on_ladder:
            p.set_state(STATE_CLIMBING)
        elif not p.is_grounded and (p.is_touching_wall_left or p.is_touching_wall_right):
            if p.change_y < 0:
                p.set_state(STATE_WALL_CLINGING)
        elif not p.is_grounded and p.change_y > 0:
            p.set_state(STATE_JUMPING)
        elif not p.is_grounded and p.change_y <= 0:
            p.set_state(STATE_FALLING)
        elif abs(p.change_x) > 0.1:
            p.set_state(STATE_RUNNING)
        else:
            p.set_state(STATE_IDLE)

    # ------------------------------------------------------------------
    # Frame-reset consumed flags
    # ------------------------------------------------------------------

    def reset_frame_inputs(self):
        """
        Call at start of each frame AFTER processing, before next key event.
        Resets single-frame-consumed flags so they can fire again.
        """
        self._jump_consumed = False
        self._dash_consumed = False
        self._pickup_consumed = False
        self._attack_consumed = False
        self._haustoria_consumed = False
        self.input_jump = False
        self.input_dash = False
        self.input_pickup = False
        self.input_throw_attack = False
        self.input_haustoria = False

    def apply_post_physics_clamp(self):
        """
        Re-apply the wall-slide speed cap AFTER physics_engine.update().

        The physics engine adds gravity each frame, which can push change_y
        past the cap set in _update_wall_cling.  Calling this after physics
        ensures the slide speed stays bounded.
        """
        p = self.player
        if p.is_grounded or p.wall_bounce_timer > 0 or p.is_dead:
            return

        clinging = (
            (p.is_touching_wall_left  and self.input_left) or
            (p.is_touching_wall_right and self.input_right)
        )
        if clinging and p.change_y < -WALL_SLIDE_SPEED:
            p.change_y = -WALL_SLIDE_SPEED
