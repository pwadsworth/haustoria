"""
resources.py — Manages water/chlorophyll passive drain and UI resource bars.
"""

import arcade
from constants import (
    WATER_DRAIN_RATE, CHLOROPHYLL_DRAIN_RATE,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_RESOURCE_WATER, COLOR_RESOURCE_CHLOROPHYLL, COLOR_RESOURCE_HEALTH,
)


class ResourceSystem:
    """
    Handles passive resource drain each frame and draws the HUD bars.
    Does NOT handle Haustoria gain — that lives in haustoria_system.py.
    """

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
        bar_x = 20
        bar_width = 160
        bar_height = 14
        padding = 6

        # --- Health (red dots) ---
        for i in range(player.max_health):
            color = COLOR_RESOURCE_HEALTH if i < player.health else (60, 20, 20)
            arcade.draw_circle_filled(
                bar_x + i * 22 + 11,
                SCREEN_HEIGHT - 20,
                8,
                color,
            )

        # --- Water bar ---
        self._draw_bar(
            bar_x, SCREEN_HEIGHT - 48,
            bar_width, bar_height,
            player.water / player.max_water,
            COLOR_RESOURCE_WATER,
            "Water",
        )

        # --- Chlorophyll bar ---
        self._draw_bar(
            bar_x, SCREEN_HEIGHT - 48 - bar_height - padding,
            bar_width, bar_height,
            player.chlorophyll / player.max_chlorophyll,
            COLOR_RESOURCE_CHLOROPHYLL,
            "Chloro",
        )

    def _draw_bar(self, x, y, width, height, fraction, color, label):
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
        # Label
        arcade.draw_text(label, x + width + 6, y, (200, 200, 200), 10)
