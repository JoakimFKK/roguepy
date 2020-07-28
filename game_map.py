from __future__ import annotations

import numpy as np
from tcod.console import Console

from typing import Iterable, Optional, TYPE_CHECKING

import tile_types

if TYPE_CHECKING:
	from entity import Entity


class GameMap:
	def __init__(self, width, height, entities: Iterable[Entity] = ()):
		self.width = width
		self.height = height
		self.entities = set(entities)
		# Fylder hele mappet op med vægge.
		self.tiles = np.full((width, height), fill_value=tile_types.wall, order='F')

		self.visible = np.full((width, height), fill_value=False, order="F")
		self.explored = np.full((width, height), fill_value=False, order="F")

	def get_blocking_entity_at_location(self, location_x: int, location_y: int):
		for entity in self.entities:
			if entity.blocks_movement and entity.x == location_x and entity.y == location_y:
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
		console.tiles_rgb[0:self.width, 0:self.height] = np.select(
			condlist=[self.visible, self.explored],
			choicelist=[self.tiles['light'], self.tiles['dark']],
			default=tile_types.SHROUD,
		)

		for entity in self.entities:
			# Tegn kun entities som er inden i FOV
			if self.visible[entity.x, entity.y]:
				console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)