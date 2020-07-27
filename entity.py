from typing import Tuple

class Entity:
	""" A generic object to represent players, enemies, items, etc.
	 """
	def __init__(self, x, y ,char, color):
		"""[summary]

		Args:
			x (int): Entity position X
			y (int): Entity position Y
			char (str): Entity visuel repræsentation
			color (Tuple[int, int, int]): Entity farve RGB
		"""
		self.x = x
		self.y = y
		self.char = char
		self.color = color

	def move(self, dir_x, dir_y):
		"""Bevæger entity.

		 Args:
	 		dir_x (int): Direction X-akse
 			dir_y (int): Direction Y-akse
 		"""
		self.x += dir_x
		self.y += dir_y
