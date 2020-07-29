from __future__ import annotations
from typing import Optional, TYPE_CHECKING

import tcod.event

from actions import (
	Action,
	BumpAction,
	EscapeAction,
	WaitAction,
)

if TYPE_CHECKING:
	from engine import Engine


MOVE_KEYS = {
    # Arrow keys.
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
    # Vi keys.
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}

WAIT_KEYS = {
	tcod.event.K_PERIOD,
	tcod.event.K_KP_5,
	tcod.event.K_CLEAR,
}


class EventHandler(tcod.event.EventDispatch[Action]):
	""" !TODO! """
	def __init__(self, engine: Engine):
		self.engine = engine

	def handle_events(self):
		raise NotImplementedError()


	def ev_quit(self, event: tcod.event.Quit):
		""" Override af EventHandler.ev_quit, sørger for lukning af programmet. """
		raise SystemExit(0)  # `SystemExit(0)` lukker programmet ned uden at give den normale fejl besked.



class MainGameEventHandler(EventHandler):
	def handle_events(self):
		for event in tcod.event.wait():
			action = self.dispatch(event)

			if action is None:
				continue

			action.perform()

			self.engine.handle_enemy_turns()
			self.engine.update_fov()

	def ev_keydown(self, event):
		""" Registering af key presses.
		 Returnerer type `None` hvis invalid key press.
		 """

		action: Optional[Action] = None
		key = event.sym

		player = self.engine.player

		if key in MOVE_KEYS:
			dir_x, dir_y = MOVE_KEYS[key]
			action = BumpAction(player, dir_x, dir_y)
		elif key in WAIT_KEYS:
			action = WaitAction(player)

		elif key == tcod.event.K_ESCAPE:
			action = EscapeAction(player)

		# Hvis en ikke valid tast blev trykket
		return action


class GameOverEventHandler(EventHandler):
	def handle_events(self):
		for event in tcod.event.wait():
			action = self.dispatch(event)

			if action is None:
				continue

			action.perform()

	def ev_keydown(self, event):
		action: Optional[Action] = None

		key = event.sym

		if key == tcod.event.K_ESCAPE:
			action = EscapeAction(self.engine.player)

		# Hvis en ikke valid tast bliver trykket
		return action