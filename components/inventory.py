from __future__ import annotations

from typing import List, TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
	from entity import Actor, Item


class Inventory(BaseComponent):
	parent: Actor

	def __init__(self, capacity: int):
		self.capacity = capacity
		self.items: List[Item] = []


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
