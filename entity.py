from __future__ import annotations

import copy
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union

from render_order import RenderOrder

if TYPE_CHECKING:
	from components.ai import BaseAI
	from components.consumable import Consumable
	from components.fighter import Fighter
	from components.inventory import Inventory
	from game_map import GameMap

T = TypeVar('T', bound="Entity")


class Entity:
	""" A generic object to represent players, enemies, items, etc.
	"""
	parent: Union[GameMap, Inventory]

	def __init__(
		self,
		parent: Optional[GameMap] = None,
		x: int = 0,
		y: int = 0,
		char: str = "?",
		color: Tuple[int, int, int] = (255, 255, 255),
		name: str = "<Unnamed>",
		blocks_movement: bool = False,  # todo Ændr navnet så det er mere åbenlyst.
		render_order: RenderOrder = RenderOrder.CORPSE,
	):
		"""[summary]

		Args:
			x (int, optional): X-Koordinat. Defaults to 0.
			y (int, optional): Y-Koordinat. Defaults to 0.
			char (str, optional): Hvilket char `entity`en bliver tegnet med. Defaults to "?".
			color (Tuple[int, int, int], optional): Farven på `entity` i RGB. Defaults to (255, 255, 255).
			name (str, optional): Navnet på `entity`. Defaults to "<Unnamed>".
			blocks_movement (bool, optional): Beskriver hvis `entity` blokerer movement. Defaults to False.
		"""
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.name = name
		self.blocks_movement = blocks_movement
		self.render_order = render_order
		if parent:
			# If parent isn't provided now then it will be set later.
			self.parent = parent
			parent.entities.add(self)

	@property
	def game_map(self):
		return self.parent.game_map

	def spawn(self: T, game_map, x: int, y: int) -> T:
		"""Spawner en kopi af instancen til en given position

			Args:
				self (T): Entity objekt
				game_map (GameMap): GameMappet
				x (int): X-Koordinat
				y (int): Y-Koordinat

			Returns:
				T: Klon af Entity objektet.
			"""
		clone = copy.deepcopy(self)
		clone.x, clone.y = x, y
		clone.parent = game_map
		game_map.entities.add(clone)
		return clone

	def place(self, x, y, game_map: Optional[GameMap] = None):
		"""Placer denne entity på en ny lokation. Handles moving across GameMaps

		Args:
			x ([type]): [description]
			y ([type]): [description]
			game_map (Optional[GameMap]): [description]
		"""
		self.x = x
		self.y = y
		if game_map:
			if hasattr(self, "parent"):  # Hvis attributen ikke er initialiseret
				if self.parent is self.game_map:
					self.game_map.entities.remove(self)
			self.parent = game_map
			game_map.entities.add(self)

	def move(self, dir_x, dir_y):
		"""Bevæger entity.

			Args:
				dir_x (int): Direction X-akse
				dir_y (int): Direction Y-akse
			"""
		self.x += dir_x
		self.y += dir_y
		# print(f"{self.x}, {self.y}")


class Actor(Entity):
	def __init__(
		self,
		*,
		x: int = 0,
		y: int = 0,
		char: str = '?',
		color: Tuple[int, int, int] = (255, 255, 255),
		name: str = '<Unnamed>',
		ai_cls: Type[BaseAI],  # Evnen til at bevæge sig og foretage handlinger
		fighter: Fighter,  # Evnen til at give og tage skade.
		inventory: Inventory,
	):
		super().__init__(
			x=x,
			y=y,
			char=char,
			color=color,
			name=name,
			blocks_movement=True,  # `Actor` vil altid* blokere bevægelse
			render_order=RenderOrder.ACTOR,
		)

		self.ai: Optional[BaseAI] = ai_cls(self)

		self.fighter = fighter
		self.fighter.parent = self

		self.inventory = inventory
		self.inventory.parent = self

	@property
	def is_alive(self) -> bool:
		""" Returnerer True så længe at `Actor` kan `perform` `Action`s. """
		return bool(self.ai)


class Item(Entity):
	def __init__(
		self,
		*,
		x: int = 0,
		y: int = 0,
		char: str = '?',
		color: Tuple[int, int, int] = (255, 255, 255),
		name: str = '<Unnamed>',
		consumable: Consumable,
	):
		super().__init__(
			x=x,
			y=y,
			char=char,
			color=color,
			name=name,
			blocks_movement=False,
			render_order=RenderOrder.ITEM,
		)

		self.consumable = consumable
		self.consumable.parent = self