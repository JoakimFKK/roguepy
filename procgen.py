from __future__ import annotations

import random

import tcod

from game_map import GameMap
import tile_types


class RectangularRoom:
	def __init__(self, x, y, width, height):
		"""[summary]

		Args:
			x (int): X-kordinat for top-højre hjørne
			y (int): Y-kordinat for bund-venstre hjørne
			width (int): Bredde på rum
			height (int): Højde på rum
		"""
		self.pos_x = x
		self.pos_y = y
		self.room_width = x + width
		self.room_height = y + height

	@property
	def center(self):
		"""Returnerer centrum i rummet.

		Returns:
			tuple(int, int): midtpunktet for X og Y i rummet.
		"""
		center_x = int((self.pos_x + self.room_width) / 2)
		center_y = int((self.pos_y + self.room_height) / 2)

		return center_x, center_y

	@property
	def inner(self):
		"""Returnerer rummets indre som et 2D array index

		Returns:
		tuple(slice, slice): Giver os rum dimensionerne.
		"""
		return slice(self.pos_x + 1, self.room_width), slice(self.pos_y + 1, self.room_height)

	def intersects(self, other: RectangularRoom):
		return (
			self.pos_x <= other.room_width
			and self.room_width >= other.pos_x
			and self.pos_y <= other.room_height
			and self.room_height >= other.pos_y
		)


def generate_dungeon(
	max_rooms: int,
	room_min_size: int,
	room_max_size: int,
	map_width: int,
	map_height: int,
	player,
) -> GameMap:
	dungeon = GameMap(map_width, map_height)
	rooms = []

	for room in range(max_rooms):
		room_width = random.randint(room_min_size, room_max_size)
		room_height = random.randint(room_min_size, room_max_size)

		pos_x = random.randint(0, dungeon.width - room_width - 1)
		pos_y = random.randint(0, dungeon.height - room_height - 1)

		new_room = RectangularRoom(pos_x, pos_y, room_width, room_height)

		if any(new_room.intersects(other_room) for other_room in rooms):
			continue

		dungeon.tiles[new_room.inner] = tile_types.floor

		if len(rooms) == 0:
			player.x, player.y = new_room.center
		else:
			for x, y in tunnel_between(rooms[-1].center, new_room.center):
				dungeon.tiles[x, y] = tile_types.floor

		rooms.append(new_room)

	return dungeon


def tunnel_between(start, end):
	"""Returner en L-formet tunnel mellem de to punkter

	Args:
		start ([type]): [description]
		end ([type]): [description]
	"""
	start_x, start_y = start
	end_x, end_y = end

	if random.random() < 0.5:
		# Først horizontalt, så vertikalt
		corner_x, corner_y = end_x, start_y
	else:
		# Først Vertikalt, så horizontalt
		corner_x, corner_y = start_x, end_y

	# https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
	for x, y in tcod.los.bresenham((start_x, start_y), (corner_x, corner_y)).tolist():
		yield x, y
	for x, y in tcod.los.bresenham((corner_x, corner_y), (end_x, end_y)).tolist():
		yield x, y
