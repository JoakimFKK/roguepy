from __future__ import annotations
from typing import TYPE_CHECKING


from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from actions import EscapeAction, MovementAction
from input_handlers import MainGameEventHandler

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
		self.player = player

	def handle_enemy_turns(self):
		for entity in self.game_map.entities - {self.player}:
			if entity.ai:
				entity.ai.perform()


	def update_fov(self):
		""" Opdater `game_map` baseret på spillerens FOV"""
		self.game_map.visible[:] = compute_fov(
			self.game_map.tiles['transparent'],
			(self.player.x, self.player.y),
			radius=8,
		)
		# Hvis en `tile` er synlig, sæt den til `explored`
		self.game_map.explored |= self.game_map.visible

	def render(self, console, context):
		"""Tegner konsolen

		 Args:
			console (Console): Konsolen der skal tegnes
			context (context): TODO
		"""
		self.game_map.render(console)

		console.print(
			x=1,
			y=47,
			string=f"HP: {self.player.fighter.hp}/{self.player.fighter.max_hp}",
		)

		context.present(console)  # Hvad der opdaterer konsolerne
		console.clear()  # For at nulstille konsolen, og tegne på ny.