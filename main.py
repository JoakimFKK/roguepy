#!/usr/bin/env python3
import copy
import traceback

import tcod

import color
from engine import Engine
import entity_factories
from procgen import generate_dungeon


def main():
    """ TODO """
    screen_width = 80   # X-kordinat
    screen_height = 50  # Y-kordinat

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    max_monsters_per_room = 2


    tileset = tcod.tileset.load_tilesheet(
        "resources/tileset.png",
        32,
        8,
        tcod.tileset.CHARMAP_TCOD,
    )

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)

    engine.game_map = generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        max_monsters_per_room=max_monsters_per_room,
        engine=engine
    )

    engine.update_fov()

    # NOTE STOP
    engine.message_log.add_message(
        "STOP! You violated the law. Pay the court a fine, or serve your sentence!",
        color.welcome_text,
    )
    engine.message_log.add_message(
        "\"Go commit not alive\" is whispered throughout the dungeon.",
        color.welcome_text,
    )

    engine.message_log.add_message(
        "You contemplate the suggestion, and come to the conclusion that they might be on to something.",
        color.welcome_text,
    )

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="What if *hits bong* we made a rogue-like?",
        vsync=True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")  # `order="F"` sætter coordinat-systemet til `[x, y]`
        while True:
            root_console.clear()
            engine.event_handler.on_render(console=root_console)
            context.present(root_console)

            try:
                for event in tcod.event.wait():
                    context.convert_event(event)
                    engine.event_handler.handle_events(event)
            except Exception:
                traceback.print_exc()  # Print error to stderr
                # Then print the error to the message log.
                engine.message_log.add_message(traceback.format_exc(), color.error)

            engine.event_handler.handle_events(context)


if __name__ == "__main__":
    main()