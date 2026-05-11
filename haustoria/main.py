"""
main.py — Entry point for Haustoria.

Only responsibility: create the window and start the game loop.
"""

import arcade
from game.game_window import HaustoriaGame


def main():
    window = HaustoriaGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
