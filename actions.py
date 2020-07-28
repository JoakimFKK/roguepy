from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class Action:
    def perform(self, engine, entity):
        """Perform this action with the objects needed to determine its scope.
        This method must be overriden by Action subclasses.

        Args:
            engine (Engine): `engine` is the scope this action is being performed in.
            entity (Entity): `entity` is the object performing the action.
        """
        raise NotImplementedError


class EscapeAction(Action):
    def perform(self, engine, entity):
        raise SystemExit(0)


class ActionWithDirection(Action):
    def __init__(self, dir_x: int, dir_y: int):
        super().__init__()

        self.dir_x = dir_x
        self.dir_y = dir_y

    def perform(self, engine, entity):
        raise NotImplementedError


class MeleeAction(ActionWithDirection):
    def perform(self, engine, entity):
        dest_x = entity.x + self.dir_x
        dest_y = entity.y + self.dir_y

        target = engine.game_map.get_blocking_entity_at_location(dest_x, dest_y)
        if not target:  # Hvis target er None
            return  # Ingen entities at angribe

        print(f"You passionately brush {target.name}'s cheek, making them very uncomfortable.")


class MovementAction(ActionWithDirection):
    def perform(self, engine, entity):
        dest_x = entity.x + self.dir_x
        dest_y = entity.y + self.dir_y

        if not engine.game_map.in_bounds(dest_x, dest_y):
            return  # Destination ikke indenfor mappet
        if not engine.game_map.tiles['walkable'][dest_x, dest_y]:
            return  # Destination er blokeret.
        if engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return  # Destination er blokeret af en entity

        entity.move(self.dir_x, self.dir_y)


class BumpAction(ActionWithDirection):
    def perform(self, engine, entity):
        dest_x = entity.x + self.dir_x
        dest_y = entity.y + self.dir_y

        if engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return MeleeAction(self.dir_x, self.dir_y).perform(engine, entity)
        else:
            return MovementAction(self.dir_x, self.dir_y).perform(engine, entity)