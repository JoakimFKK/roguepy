from __future__ import annotations
from typing import Optional, Tuple, TYPE_CHECKING

import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item


class Action:
    """Base-class for Actions"""
    def __init__(self, entity: Actor):
        super().__init__()
        self.entity = entity

    @property
    def engine(self):
        """ Returns the engine this action belongs to. """
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


class ActionWithDirection(Action):
    """Any action that requires a direction, such as bump, attack, etc."""
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
    """Attack action, where an entity attempts to move into a different entity."""
    def perform(self):
        target = self.target_actor

        if not target:
            raise exceptions.Impossible("Nothing to attack.")

        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        if damage > 0:
            self.engine.message_log.add_message(f'{attack_desc} for {damage} hit points.', attack_color)
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(f'{attack_desc} but critically misses.', attack_color)


class MovementAction(ActionWithDirection):
    """Action that attempts movement."""
    def perform(self):
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            raise exceptions.Impossible("That way is blocked.")  # Destination ikke indenfor mappet
        if not self.engine.game_map.tiles['walkable'][dest_x, dest_y]:
            raise exceptions.Impossible("That way is blocked.")  # Destination er blokeret.
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            raise exceptions.Impossible("That way is blocked.")  # Destination er blokeret af en entity

        self.entity.move(self.dir_x, self.dir_y)


class BumpAction(ActionWithDirection):
    """Action where entity attempts to move into a space that's occupied."""
    def perform(self):
        if self.target_actor:
            return MeleeAction(self.entity, self.dir_x, self.dir_y).perform()
        else:
            return MovementAction(self.entity, self.dir_x, self.dir_y).perform()


class WaitAction(Action):
    """Action where the entity does nothing."""
    def perform(self):
        pass


class PickUpAction(Action):
    """Picks up the item the entity is standing on, if any."""
    def __init__(self, entity: Actor):
        """
        Returns:
            entity: The actor performing the action.
        """
        super().__init__(entity)

    def perform(self):
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible('Shitter\'s full.')

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f"You picked up the {item.name}!", )
                return
        raise exceptions.Impossible("You attempt to pick up the air, to no avail.")


class ItemAction(Action):
    def __init__(self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None):
        """Performs the action of a given `Item` object.

        Args:
            entity: The actor using the item.
            item:  The `Item` that is being used
            target_xy: The affected tile-coordinates of the effect.
        """
        super().__init__(entity)

        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """ Return the actor at this actions destination. """
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self):
        """Invoke the items ability, this action will be given to provide context."""
        self.item.consumable.activate(self)


class DropItem(ItemAction):
    """Drops the selected item from Inventory."""
    def perform(self):
        self.entity.inventory.drop(self.item)
