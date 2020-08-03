from __future__ import annotations

import numpy as np
from tcod.console import Console

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

from entity import Actor, Item
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:
    def __init__(self, engine, width, height, entities: Iterable[Entity] = ()):
        self.engine = engine
        self.width = width
        self.height = height
        self.entities = set(entities)
        # Fylder hele mappet op med vægge.
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order='F')

        self.visible = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles spilleren kan se
        self.explored = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles spilleren har udforsket

        self.downstairs_location = (0, 0)

    @property
    def game_map(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """ Iterate igennem kortet for at finde "levende" `Actor`s """
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Item)
        )

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor
        return None

    # NOTE: Might not be needed
    def get_blocking_entity_at_location(self, location_x: int, location_y: int):
        for entity in self.entities:
            if (
                    entity.blocks_movement
                    and entity.x == location_x
                    and entity.y == location_y
            ):
                return entity
        return None

    def in_bounds(self, x, y) -> bool:
        """Returner True hvis (X, Y) er inden i mappet.

        Args:
            x (int): X-kordinat
            y (int): Y-kordinat
        Returns:
            bool
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console):
        """Render mappet
         Hvis en `tile` er i det `visible` array, så bliver det tegnet med lyse farver, & vice versa.
         Default værdien er `SHROUD`

         np.select allows us to conditionally draw the tiles we want, based on what’s specified in condlist. Since we’re passing [self.visible, self.explored], it will check if the tile being drawn is either visible, then explored. If it’s visible, it uses the first value in choicelist, in this case, self.tiles["light"]. If it’s not visible, but explored, then we draw self.tiles["dark"]. If neither is true, we use the default argument, which is just the SHROUD we defined earlier.

         Args:
            console (Console): Main console
        """
        console.tiles_rgb[0: self.width, 0: self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles['light'], self.tiles['dark']],
            default=tile_types.SHROUD,
        )

        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            # Tegn kun entities som er inden i FOV
            if self.visible[entity.x, entity.y]:
                console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)


class GameWorld:
    """
    Holds teh settings for the GameMap, and generates new maps when movind down the stairs.
    """

    def __init__(
            self,
            *,
            engine: Engine,
            map_width: int,
            map_height: int,
            max_rooms: int,
            room_min_size: int,
            room_max_size: int,
            max_monsters_per_room: int,
            max_items_per_room: int,
            current_floor: int = 0,
    ):
        self.engine = engine
        self.map_width = map_width
        self.map_height = map_height
        self.max_rooms = max_rooms
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size
        self.max_monsters_per_room = max_monsters_per_room
        self.max_items_per_room = max_items_per_room
        self.current_floor = current_floor

    def generate_floor(self) -> None:
        from procgen import generate_dungeon

        self.current_floor += 1

        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            max_monsters_per_room=self.max_monsters_per_room,
            max_items_per_room=self.max_items_per_room,
            engine=self.engine,
        )
