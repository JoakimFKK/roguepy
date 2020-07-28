from __future__ import annotations

import random

import tcod

from game_map import GameMap
import entity_factories
import tile_types

if TYPE_CHECKING:
	from engine import Engine


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
	max_monsters_per_room: int,
	engine: Engine,
) -> GameMap:
	"""Genererer et Dungeon Map

	 Args:
		 max_rooms (int): Maks antal af rum i dungeon
		 room_min_size (int): Mindste størrelse af et rum
		 room_max_size (int): Største størrelse af et rum
		 map_width (int): Hele Dungeons bredde
		 map_height (int): Hele Dungeons højde
		 player ([type]): Player entity

	 Returns:
		GameMap: Området hvor PCen er.
	"""
	player = engine.player
	dungeon = GameMap(engine, map_width, map_height, entities=[player, ])

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
			# Første rum, hvor spilleren starter
			player.place(*new_room.center, dungeon)
		else:
			for x, y in tunnel_between(rooms[-1].center, new_room.center):
				dungeon.tiles[x, y] = tile_types.floor

		place_entities(new_room, dungeon, max_monsters_per_room)

		rooms.append(new_room)

	return dungeon


def place_entities(room, dungeon, maximum_monsters):
	"""Funktion som finder X og Y koordinater til placering og spawning af NPCer.

	Hvis en `entity`s X/Y-koordinat ville være oven på en andens så vil den ikke spawnes.
	Der er også en 80% chance for at en anden type `monster` vil spawnes ved hver spawn.

	Args:
		room ([type]): [description]
		dungeon ([type]): [description]
		maximum_monsters ([type]): [description]
	"""
	number_of_monsters = random.randint(0, maximum_monsters)

	for _ in range(number_of_monsters):
		# Note +/-1 for ikke at spawne entities inde i væg
		x = random.randint(room.pos_x + 1, room.room_width - 1)
		y = random.randint(room.pos_y + 1, room.room_height - 1)

		if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
			if random.random() < 0.8:
				entity_factories.orc.spawn(dungeon, x, y)
			else:
				entity_factories.troll.spawn(dungeon, x, y)


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
