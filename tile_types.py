from typing import Tuple

import numpy as np


# Tile graphics structured type compatible with Console.tiles_rgb
graphic_dt = np.dtype(
	[
		('ch', np.int32),  # Unicode codepoint
		('fg', '3B'),  # 3 unsigned bytes, for RGB colors
		('bg', '3B'),  # -----------||--------------
	]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
	[
		('walkable', np.bool),  # Hvis `tile` kan gås på
		('transparent', np.bool),  # Hvis `tile` blokerer FOV
		('dark', graphic_dt),  # Graphics for `tile` når ikke i FOV
	]
)


def new_tile(
	*,  # enforce the use of keywords, so that parameter order doesn't matter
	walkable: int,
	transparent: int,
	dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
):
	"""* == Parameters after “*” or “*identifier” are keyword-only parameters and may only be passed used keyword arguments.

	Args:
		transparent (int): [description]
		dark (Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]): [description]

	Returns:
		[type]: [description]
	"""
	return np.array((walkable, transparent, dark), dtype=tile_dt)


floor = new_tile(
	walkable=True,
	transparent=True,
	dark=(
		ord('.'),  # `ord("")` returner int værdi af unicode
		(255, 255, 255),
		(50, 50, 150)
	),
)

wall = new_tile(
	walkable=False,
	transparent=False,
	dark=(
		ord('#'),
		(255, 255, 255),
		(0, 0, 100)
	),
)