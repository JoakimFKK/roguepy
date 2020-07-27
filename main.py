#!/usr/bin/env python3
import tcod

from actions import EscapeAction, MovementAction
from input_handlers import EventHandler

def main():
    """ TODO """
    screen_width = 80   # X-kordinat
    screen_height = 50  # Y-kordinat

    # Sætter PC i midten af konsolen
    player_x = int(screen_width / 2)
    player_y = int(screen_height / 2)

    tileset = tcod.tileset.load_tilesheet(
        "resources/tileset.png",
        32,
        8,
        tcod.tileset.CHARMAP_TCOD,
    )

    event_handler = EventHandler()

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset = tileset,
        title = "What if *hits bong* we made a rogue-like?",
        vsync = True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")  # `order="F"` sætter coordinat-systemet til `[x, y]`
        while True:
            root_console.print(x=player_x, y=player_y, string="@")
            context.present(root_console)  # Hvad der opdaterer konsolerne
            root_console.clear()  # For at nulstille konsolen, og tegne på ny.

            for event in tcod.event.wait():
                """ EventHandler.dispatch() sender `event` tester hvilken Eventhandler.ev_* funktion er en match.
                 Hvis det er `ev_keydown`, returneres der et `Action` objekt som vi kan bruge kalde.
                 """
                # Hvis event_handler.dispatch(event) is not type(None), set action to be event_handler.dispatch(event) value
                if (action := event_handler.dispatch(event)) is not None:
                    if isinstance(action, MovementAction):  # if action is an instance of MovementAction, do ...
                        player_x += action.dx
                        player_y += action.dy
                    elif isinstance(action, EscapeAction):
                        raise SystemExit(0)
                else:
                    continue





if __name__ == "__main__":
    main()