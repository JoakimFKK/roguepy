from __future__ import annotations
from typing import TYPE_CHECKING


from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from actions import EscapeAction, MovementAction
import exceptions
from input_handlers import MainGameEventHandler
from message_log import MessageLog
from render_functions import render_bar, render_names_at_mouse_location

if TYPE_CHECKING:
	from entity import Actor
	from game_map import GameMap
	from input_handlers import EventHandler



class Engine:
	game_map: GameMap

	def __init__(self, player: Actor):
		""" Engine sørger for game logic

		 Args:
			entities (Set[Entity]): *Unordered list of unique items.*
			event_handler (EventHandler): Gi'r jo sig selv.
			player (Entity): Godt nok, med lykke og held.
		"""
		self.event_handler: EventHandler = MainGameEventHandler(self)
		self.message_log = MessageLog()
		self.mouse_location = (0, 0)
		self.player = player

	def handle_enemy_turns(self):
		for entity in self.game_map.entities - {self.player}:
			if entity.ai:
				try:
					entity.ai.perform()
				except exceptions.Impossible:
					pass


	def update_fov(self):
		""" Opdater `game_map` baseret på spillerens FOV"""
		self.game_map.visible[:] = compute_fov(
			self.game_map.tiles['transparent'],
			(self.player.x, self.player.y),
			radius=8,
		)
		# Hvis en `tile` er synlig, sæt den til `explored`
		self.game_map.explored |= self.game_map.visible

	def render(self, console: Console):
		"""Tegner konsolen

			Args:
				console (Console): Konsolen der skal tegnes
				context (context): TODO
			"""
		self.game_map.render(console)

		self.message_log.render(
			console=console,
			x=21,
			y=45,
			width=40,
			height=5,
		)

		render_bar(
			console=console,
			current_value=self.player.fighter.hp,
			maximum_value=self.player.fighter.max_hp,
			total_width=20,
		)

		render_names_at_mouse_location(console, x=21, y=44, engine=self)