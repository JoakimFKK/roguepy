#!/usr/bin/env python3
import copy
import traceback

import tcod

from consts import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SAVE_GAME,
    TITLE,
    TILESHEET,
    TILESHEET_COL,
    TILESHEET_ROW,
)

import color
import exceptions
import setup_game
import input_handlers


def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active Engine, then save it."""
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game Saved.")


def main() -> None:
    """ TODO """
    tileset = tcod.tileset.load_tilesheet(
        TILESHEET,
        TILESHEET_COL,
        TILESHEET_ROW,
        tcod.tileset.CHARMAP_CP437,
    )

    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

    with tcod.context.new_terminal(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            tileset=tileset,
            title=TITLE,
            vsync=True,
    ) as context:
        root_console = tcod.Console(SCREEN_WIDTH, SCREEN_HEIGHT,
                                    order="F")  # `order="F"` sætter coordinat-systemet til `[x, y]`
        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(root_console)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(),
                            color.error,
                        )

        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # Save and quit
            save_game(handler, SAVE_GAME)
            raise
        except BaseException:  # Save on any other unexpected exception
            save_game(handler, SAVE_GAME)
            raise


if __name__ == "__main__":
    main()
