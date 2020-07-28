# Official import
# 3rd party
import tcod.event

# Local import
from actions import (
	Action,
	BumpAction,
	EscapeAction,
)


class EventHandler(tcod.event.EventDispatch[Action]):
	""" !TODO! """

	def __init__(self, engine):
		self.engine = engine

	def handle_events(self):
		for event in tcod.event.wait():
			# action = self.dispatch(event)
			if (action := self.dispatch(event)) is not None:
				action.perform()

				self.engine.handle_enemy_turns()
				self.engine.update_fov()

	def ev_quit(self, event: tcod.event.Quit):
		""" Override af EventHandler.ev_quit, sørger for lukning af programmet. """
		raise SystemExit(0)  # `SystemExit(0)` lukker programmet ned uden at give den normale fejl besked.

	def ev_keydown(self, event: tcod.event.KeyDown):
		""" Registering af key presses.
		 Returnerer type `None` hvis invalid key press.
		 """
		action = None
		key = event.sym

		player = self.engine.player

		if key == tcod.event.K_UP:
			action = BumpAction(player, dir_x=0, dir_y=-1)
		elif key == tcod.event.K_DOWN:
			action = BumpAction(player, dir_x=0, dir_y=1)
		elif key == tcod.event.K_LEFT:
			action = BumpAction(player, dir_x=-1, dir_y=0)
		elif key == tcod.event.K_RIGHT:
			action = BumpAction(player, dir_x=1, dir_y=0)

		elif key == tcod.event.K_ESCAPE:
			action = EscapeAction(player)

		# Hvis en ikke valid tast blev trykket
		return action