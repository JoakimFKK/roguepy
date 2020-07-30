from __future__ import annotations

from typing import TYPE_CHECKING

import color
from input_handlers import GameOverEventHandler
from components.base_component import BaseComponent
from render_order import RenderOrder

if TYPE_CHECKING:
	from entity import Actor


class Fighter(BaseComponent):
	parent: Actor

	def __init__(self, hp: int, defense: int, power: int):
		self.max_hp = hp
		self._hp = hp
		self.defense = defense
		self.power = power

	@property
	def hp(self) -> int:
		""" Getter for hp """
		return self._hp

	@hp.setter
	def hp(self, value: int):
		""" Setter for HP """
		self._hp = max(0, min(value, self.max_hp))
		if self._hp == 0 and self.parent.ai:
			self.die()

	def die(self):
		if self.engine.player is self.parent:
			death_message = "You have perished at your local Wall-Mart"
			death_message_color = color.player_die
			self.engine.event_handler = GameOverEventHandler(self.engine)
		else:
			death_message = f"{self.parent.name}'s ancestors are smiling at them, {self.engine.player.name}, can you say the same?"
			death_message_color = color.enemy_die

		self.parent.char = '%'
		self.parent.color = (191, 0, 0)
		self.parent.blocks_movement = False
		self.parent.ai = None
		self.parent.render_order = RenderOrder.CORPSE
		self.parent.name = f"a dead {self.parent.name}."

		self.engine.message_log.add_message(death_message, death_message_color)

	def heal(self, amount: int):
		if self.hp == self.max_hp:
			return 0

		new_hp_value = self.hp + amount

		if new_hp_value > self.max_hp:
			new_hp_value = self.max_hp

		amount_recovered = new_hp_value - self.hp

		self.hp = new_hp_value

		return amount_recovered

	def take_damage(self, amount: int):
		self.hp -= amount