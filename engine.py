from typing import Set, Iterable, Any

from tcod.context import Context
from tcod.console import Console

from actions import EscapeAction, MovementAction
from entity import Entity
from input_handlers import EventHandler


class Engine:
	def __init__(self, entities, event_handler, player):
		""" Engine sørger for game logic

		 Args:
			entities (Set[Entity]): *Unordered list of unique items.*
			event_handler (EventHandler): Gi'r jo sig selv.
			player (Entity): Godt nok, med lykke og held.
		"""
		self.entities = entities
		self.event_handler = event_handler
		self.player = player

	def handle_events(self, events):
		""" EventHandler.dispatch() sender `event` tester hvilken Eventhandler.ev_* funktion er en match.
		 Hvis det er `ev_keydown`, returneres der et `Action` objekt som vi kan bruge kalde.

		 Args:
			events (Iterable[Any]): Samling af events
		"""
		for event in events:
			# Hvis event_handler.dispatch(event) is not type(None), set action to be event_handler.dispatch(event) value
			if (action := self.event_handler.dispatch(event)) is not None:
				if isinstance(action, MovementAction):  # # if action is an instance of MovementAction, do ...
					self.player.move(dir_x=action.dir_x, dir_y=action.dir_y)
				elif isinstance(action, EscapeAction):
					raise SystemExit(0)
			else:
				continue

	def render(self, console, context):
		"""Tegner konsolen

		 Args:
			console (Console): Konsolen der skal tegnes
			context (context): TODO
		"""
		for entity in self.entities:
			console.print(entity.x, entity.y, entity.char, fg=entity.color)

		context.present(console)  # Hvad der opdaterer konsolerne
		console.clear()  # For at nulstille konsolen, og tegne på ny.