from __future__ import annotations
import lzma
import pickle
from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.map import compute_fov

from input_handlers import MainGameEventHandler
from message_log import MessageLog
import render_functions
from turn_queue import TurnQueue

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap, GameWorld
    from input_handlers import EventHandler


class Engine:
    game_map: GameMap
    game_world: GameWorld

    def __init__(self, player: Actor):
        """ Engine sørger for game logic

         Args:
            entities (Set[Entity]): *Unordered list of unique items.*
            event_handler (EventHandler): Gi'r jo sig selv.
            player (Entity): Godt nok, med lykke og held.
        """
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player
        self.turn_queue = TurnQueue()

    def handle_enemy_turns(self):
        while True:
            ticket = self.turn_queue.next()
            entity_to_act = ticket.value
            if entity_to_act == self.player:
                return

            if entity_to_act.ai:
                entity_to_act.ai.perform()

    def update_fov(self):
        """ Opdater `game_map` baseret på spillerens FOV"""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles['transparent'],
            (self.player.x, self.player.y),
            radius=8,
        )
        # Hvis en `tile` er synlig, sæt den til `explored`
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console):
        """Tegner konsolen"""
        self.game_map.render(console)

        self.message_log.render(
            console=console,
            x=21,
            y=45,
            width=40,
            height=5,
        )

        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )

        render_functions.render_dungeon_level(
            console=console,
            dungeon_level=self.game_world.current_floor,
            location=(0, 47),
        )

        render_functions.render_names_at_mouse_location(console, x=21, y=44, engine=self)

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, 'wb') as f:
            f.write(save_data)
