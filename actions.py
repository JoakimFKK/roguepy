from __future__ import annotations
from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity


class Action:
    def __init__(self, entity: Actor):
        super().__init__()
        self.entity = entity

    @property
    def engine(self):
        """ Returnerer `engine` til hvor `Action` hører til """
        return self.entity.game_map.engine


    def perform(self):
        """Perform this action with the objects needed to determine its scope.

            self.engine is the scope this action is being performed in
            self.entity is the object performing the action

            Args:
                engine (Engine): `engine` is the scope this action is being performed in.
                entity (Entity): `entity` is the object performing the action.
            """
        raise NotImplementedError


class EscapeAction(Action):
    def perform(self):
        raise SystemExit(0)


class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dir_x: int, dir_y: int):
        super().__init__(entity)

        self.dir_x = dir_x
        self.dir_y = dir_y

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """ Returnerer `action`s destination """
        return self.entity.x + self.dir_x, self.entity.y + self.dir_y

    @property
    def blocking_entity(self):
        """ Returnerer den blokerendes entity på `action`s plads """
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        """ Return the actor at this actions destination """
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self):
        raise NotImplementedError


class MeleeAction(ActionWithDirection):
    def perform(self):
        target = self.target_actor

        if not target:
            return

        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if damage > 0:
            print(f"{attack_desc} for {damage} hit points.")
            target.fighter.hp -= damage
        else:
            print(f"{attack_desc} but freakin' fails, dude.")


class MovementAction(ActionWithDirection):
    def perform(self):
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            return  # Destination ikke indenfor mappet
        if not self.engine.game_map.tiles['walkable'][dest_x, dest_y]:
            return  # Destination er blokeret.
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return  # Destination er blokeret af en entity

        self.entity.move(self.dir_x, self.dir_y)


class BumpAction(ActionWithDirection):
    def perform(self):
        if self.target_actor:
            return MeleeAction(self.entity, self.dir_x, self.dir_y).perform()
        else:
            return MovementAction(self.entity, self.dir_x, self.dir_y).perform()


class WaitAction(Action):
    def perform(self):
        pass