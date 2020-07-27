import numpy as np
from tcod.console import Console

import tile_types


class GameMap:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		# Fylder hele mappet op med vægge.
		self.tiles = np.full((width, height), fill_value=tile_types.wall, order='F')

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
		console.tiles_rgb[0:self.width, 0:self.height] = self.tiles['dark']