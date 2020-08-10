"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy
import lzma  # Compression
import pickle  # De-, and serializing python object structure.
import traceback
from typing import Optional

import tcod

import color
from consts import (
    MAP_WIDTH,
    MAP_HEIGHT,
    ROOM_MAX_SIZE,
    ROOM_MIN_SIZE,
    MAX_ROOMS,
    MAX_MONSTERS_PER_ROOM,
    MAX_ITEMS_PER_ROOM,
    MAIN_MENU_IMAGE,
    SAVE_GAME,
)
from engine import Engine
import entity_factories
import input_handlers
from game_map import GameWorld

# Load the background image and remove the alpha channel
background_image = tcod.image.load(MAIN_MENU_IMAGE)[:, :, :3]  # RGB channels


def new_game() -> Engine:
    """Return a brand new game session as an Engine instance"""
    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)

    from FOOBAR import map_generation

    engine.game_world = GameWorld(
        engine=engine,
        max_rooms=MAX_ROOMS,
        room_min_size=ROOM_MIN_SIZE,
        room_max_size=ROOM_MAX_SIZE,
        map_width=MAP_WIDTH,
        map_height=MAP_HEIGHT,
        max_monsters_per_room=MAX_MONSTERS_PER_ROOM,
        max_items_per_room=MAX_ITEMS_PER_ROOM,
    )
    engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon.",
        color.welcome_text,
    )
    return engine


def load_game(filename: str) -> Engine:
    """Load an engine from a file."""
    with open(filename, 'rb') as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""

    def on_render(self, console: tcod.Console) -> None:
        """Render the main menu on a background image."""
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "WALL-MART AT AROUND MIDNIGHT",
            fg=color.menu_title,
            alignment=tcod.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "What a horrible night to have a curse.",
            fg=color.menu_title,
            alignment=tcod.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(
                ["[N] Play a new game", "[C] Continue last save", "[Q] Quit", ]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.menu_text,
                bg=color.black,
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64),  # TODO LOOK UP
            )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[input_handlers.BaseEventHandler]:
        """Handles Main Menu inputs."""
        if event.sym in (tcod.event.K_q, tcod.event.K_ESCAPE):
            # If the player presses "Q" or "ESCAPE", exit the game.
            raise SystemExit(0)
        elif event.sym == tcod.event.K_c:
            # If the player selects "Continue last save"
            try:
                return input_handlers.MainGameEventHandler(load_game(SAVE_GAME))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game to load.")
            except Exception as exc:  # Unexpected error
                traceback.print_exc()
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.K_n:
            return input_handlers.MainGameEventHandler(new_game())

        return None
