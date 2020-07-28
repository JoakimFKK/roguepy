from typing import Tuple, TypeVar, TYPE_CHECKING
import copy

if TYPE_CHECKING:
	from game_map import GameMap

T = TypeVar('T', bound="Entity")


class Entity:
	""" A generic object to represent players, enemies, items, etc.
	 """
	def __init__(
		self,
		x: int = 0,
		y: int = 0,
		char: str = "?",
		color: Tuple[int, int, int] = (255, 255, 255),
		name: str = "<Unnamed>",
		blocks_movement: bool = False,
	):
		"""[summary]

		Args:
			x (int, optional): X-Koordinat. Defaults to 0.
			y (int, optional): Y-Koordinat. Defaults to 0.
			char (str, optional): Hvilket char `entity`en bliver tegnet med. Defaults to "?".
			color (Tuple[int, int, int], optional): Farven på `entity` i RGB. Defaults to (255, 255, 255).
			name (str, optional): Navnet på `entity`. Defaults to "<Unnamed>".
			blocks_movement (bool, optional): Beskriver om `entity`en kan bevæge sig. Defaults to False.
		"""
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.name = name
		self.blocks_movement = blocks_movement

	def spawn(self: T, game_map: GameMap, x: int, y: int) -> T:
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
		game_map.entities.add(clone)
		return clone

	def move(self, dir_x, dir_y):
		"""Bevæger entity.

			Args:
				dir_x (int): Direction X-akse
				dir_y (int): Direction Y-akse
			"""
		self.x += dir_x
		self.y += dir_y
		print(f"{self.x}, {self.y}")