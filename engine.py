from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from actions import EscapeAction, MovementAction
from entity import Entity
from game_map import GameMap
from input_handlers import EventHandler


class Engine:
	def __init__(self, event_handler, game_map, player):
		""" Engine sørger for game logic

		 Args:
			entities (Set[Entity]): *Unordered list of unique items.*
			event_handler (EventHandler): Gi'r jo sig selv.
			player (Entity): Godt nok, med lykke og held.
		"""
		self.event_handler = event_handler
		self.game_map = game_map
		self.player = player
		self.update_fov()

	def handle_enemy_turns(self):
		for entity in self.game_map.entities - {self.player}:
			print(f"The {entity.name} questions the decisions that lead them to this point.")

	def handle_events(self, events):
		""" EventHandler.dispatch() sender `event` tester hvilken Eventhandler.ev_* funktion er en match.
		 Hvis det er `ev_keydown`, returneres der et `Action` objekt som vi kan bruge kalde.

		 Args:
			events (Iterable[Any]): Samling af events
		"""
		for event in events:
			# Hvis event_handler.dispatch(event) is not type(None), set action to be event_handler.dispatch(event) value
			if (action := self.event_handler.dispatch(event)) is not None:
				action.perform(self, self.player)
				self.handle_enemy_turns()
				self.update_fov()
			else:
				continue

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

		context.present(console)  # Hvad der opdaterer konsolerne
		console.clear()  # For at nulstille konsolen, og tegne på ny.