# Official import
# 3rd party
import tcod.event

# Local import
from actions import Action, EscapeAction, MovementAction

class EventHandler(tcod.event.EventDispatch[Action]):
	"""  """
	def ev_quit(self, event : tcod.event.Quit):
		""" Override af EventHandler.ev_quit, sørger for lukning af programmet. """
		raise SystemExit(0)  # `SystemExit(0)` lukker programmet ned uden at give den normale fejl besked.

	def ev_keydown(self, event : tcod.event.KeyDown):
		""" Registering af key presses.
		 Returnerer type `None` hvis invalid key press.
		 """
		action = None
		key = event.sym

		if key == tcod.event.K_UP:
			action = MovementAction(dx=0, dy=-1)
		elif key == tcod.event.K_DOWN:
			action = MovementAction(dx=0, dy=1)
		elif key == tcod.event.K_LEFT:
			action = MovementAction(dx=-1, dy=0)
		elif key == tcod.event.K_RIGHT:
			action = MovementAction(dx=1, dy=0)

		elif key == tcod.event.K_ESCAPE:
			action = EscapeAction()

		return action