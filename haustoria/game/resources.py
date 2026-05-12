"""
resources.py — Manages water/chlorophyll passive drain and UI resource bars.

Uses arcade.Text objects (pre-created in __init__) instead of draw_text to
avoid the Arcade 3.x PerformanceWarning about draw_text being slow.
"""

import arcade
from constants import (
    WATER_DRAIN_RATE, CHLOROPHYLL_DRAIN_RATE,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_RESOURCE_WATER, COLOR_RESOURCE_CHLOROPHYLL, COLOR_RESOURCE_HEALTH,
)

_BAR_X = 20
_BAR_W = 160
_BAR_H = 14
_PADDING = 6


class ResourceSystem:
    """
    Handles passive resource drain each frame and draws the HUD bars.
    Does NOT handle Haustoria gain — that lives in haustoria_system.py.
    """

    def __init__(self):
        # Lazy: created on first draw_hud() call once GL context is ready
        self._water_label: arcade.Text | None = None
        self._chloro_label: arcade.Text | None = None

    def _ensure_labels(self):
        """Create Text objects on first draw (after GL context exists)."""
        if self._water_label is None:
            label_color = (200, 200, 200)
            self._water_label = arcade.Text(
                "Water", _BAR_X + _BAR_W + 6, SCREEN_HEIGHT - 48, label_color, 10
            )
            self._chloro_label = arcade.Text(
                "Chloro", _BAR_X + _BAR_W + 6,
                SCREEN_HEIGHT - 48 - _BAR_H - _PADDING,
                label_color, 10
            )

    def update(self, player, delta_time: float):
        """Drain water and chlorophyll passively over time."""
        if player.is_dead:
            return
        player.water = max(0.0, player.water - WATER_DRAIN_RATE * delta_time)
        player.chlorophyll = max(0.0, player.chlorophyll - CHLOROPHYLL_DRAIN_RATE * delta_time)

    def draw_hud(self, player):
        """
        Draw health, water, and chlorophyll bars in screen space.
        Call this with the GUI camera active (not world camera).
        """
        self._ensure_labels()
        # --- Health (red dots) ---
        for i in range(player.max_health):
            color = COLOR_RESOURCE_HEALTH if i < player.health else (60, 20, 20)
            arcade.draw_circle_filled(
                _BAR_X + i * 22 + 11,
                SCREEN_HEIGHT - 20,
                8,
                color,
            )

        # --- Water bar ---
        self._draw_bar(
            _BAR_X, SCREEN_HEIGHT - 48,
            _BAR_W, _BAR_H,
            player.water / player.max_water,
            COLOR_RESOURCE_WATER,
        )
        self._water_label.draw()

        # --- Chlorophyll bar ---
        self._draw_bar(
            _BAR_X, SCREEN_HEIGHT - 48 - _BAR_H - _PADDING,
            _BAR_W, _BAR_H,
            player.chlorophyll / player.max_chlorophyll,
            COLOR_RESOURCE_CHLOROPHYLL,
        )
        self._chloro_label.draw()

    def _draw_bar(self, x, y, width, height, fraction, color):
        fraction = max(0.0, min(1.0, fraction))
        # Background
        arcade.draw_lrbt_rectangle_filled(x, x + width, y, y + height, (30, 30, 30))
        # Fill
        if fraction > 0:
            arcade.draw_lrbt_rectangle_filled(
                x, x + width * fraction, y, y + height, color
            )
        # Border
        arcade.draw_lrbt_rectangle_outline(x, x + width, y, y + height, (200, 200, 200), 1)
