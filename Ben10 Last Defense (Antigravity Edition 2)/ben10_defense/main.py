"""
main.py — Entry point for Ben 10 Last Defense (Package edition).

Run from the project root:
    python main.py
"""
import sys
import os

# The working directory is intentionally left as the root project directory
# so that assets (mp3, wav, ttf) can be found.

from ben10_defense.data import CURRENT_DIFF
from ben10_defense.sound import stop_music
from ben10_defense.screens.menu import menu
from ben10_defense.screens.story import story
from ben10_defense.screens.difficulty import choose_difficulty
from ben10_defense.screens.game import game
from ben10_defense.screens.end_screen import end_screen


def main():
    while True:
        menu()
        story()
        diff = choose_difficulty()
        CURRENT_DIFF[0] = diff
        result = game()
        if result is None:
            continue   # M key pressed → back to menu
        end_screen(bool(result))


if __name__ == '__main__':
    main()
