from __future__ import annotations

from typing import List, TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item


class Inventory(BaseComponent):
    entity: Actor

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[Item] = []

    def add_item(self, item: Item) -> bool:
        """
        Adds an item to the inventory, if there is room for it.
        If the item waqs added, return True to represent a turn passing.
        If not, return False, so the player does not waste a turn.
        """
        if len(self.items) >= self.capacity:
            return False
        else:
            self.items.append(item)
            return True

    def drop(self, item: Item):
        """Fjerner en `Item` fra inventory, og placerer det i GameMap, hvor spilleren står.

        Args:
            item (Item): Den fjernede item.
        """
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.game_map)

        self.engine.message_log.add_message(
            f"You dropped the {item.name}",
        )
