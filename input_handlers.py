from __future__ import annotations
from typing import Optional, TYPE_CHECKING

import tcod.event

import actions
from actions import (
	Action,
	BumpAction,
	PickUpAction,
	WaitAction,
)

import color
import exceptions

if TYPE_CHECKING:
	from engine import Engine
	from entity import Item


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

CURSOR_Y_KEYS = {
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: -10,
    tcod.event.K_PAGEDOWN: 10,
}

CONFIRM_KEYS = {
	tcod.event.K_RETURN,
	tcod.event.K_KP_ENTER
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

	def handle_events(self, event: tcod.event.Event):
		self.handle_action(self.dispatch(event))

	def handle_action(self, action: Optional[Action]) -> bool:
		"""Handle actions returned from event methods.

		Returns True if the action will advance a turn.
		"""
		if action is None:
			return False

		try:
			action.perform()
		except exceptions.Impossible as e:
			self.engine.message_log.add_message(e.args[0], color.impossible)
			return False  # Skip enemy turn on exception

		self.engine.handle_enemy_turns()
		self.engine.update_fov()
		return True


	def ev_quit(self, event: tcod.event.Quit):
		""" Override af EventHandler.ev_quit, sørger for lukning af programmet. """
		raise SystemExit(0)  # `SystemExit(0)` lukker programmet ned uden at give den normale fejl besked.

	def on_render(self, console: tcod.Console):
		self.engine.render(console)

	def ev_mousemotion(self, event):
		if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
			self.engine.mouse_location = event.tile.x, event.tile.y



class MainGameEventHandler(EventHandler):
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
		# Exit the game
		elif key == tcod.event.K_ESCAPE:
			raise SystemExit(0)
		# Message Log
		elif key == tcod.event.K_v:
			self.engine.event_handler = HistoryViewer(self.engine)
		# Pick up item
		elif key == tcod.event.K_g:
			action = PickUpAction(player)
		elif key == tcod.event.K_i:
			self.engine.event_handler = InventoryActiveHandler(self.engine)
		elif key == tcod.event.K_d:
			self.engine.event_handler = InventoryDropHandler(self.engine)
		elif key == tcod.event.K_SLASH:
			self.engine.event_handler = LookHandler(self.engine)

		# Hvis en ikke valid tast blev trykket
		return action


class GameOverEventHandler(EventHandler):
	def ev_keydown(self, event):
		action: Optional[Action] = None

		key = event.sym

		if key == tcod.event.K_ESCAPE:
			raise SystemExit(0)

		# Hvis en ikke valid tast bliver trykket
		return action






class HistoryViewer(EventHandler):
	"""Print the history on a larger window which can be navigated. """
	def __init__(self, engine):
		super().__init__(engine)
		self.log_length = len(engine.message_log.messages)
		self.cursor = self.log_length - 1

	def on_render(self, console):
		super().on_render(console)  # Draw the main state as the background

		log_console = tcod.Console(console.width - 6, console.height - 6)

		# Draw a frame with a custom banner title
		log_console.draw_frame(0, 0, log_console.width, log_console.height)
		log_console.print_box(
			0, 0, log_console.width, 1, "-|Message history|-", alignment=tcod.CENTER,
		)

		# Render the message log using the cursor parameter.
		self.engine.message_log.render_messages(
			log_console,
			1,
			1,
			log_console.width - 2,
			log_console.height - 2,
			self.engine.message_log.messages[: self.cursor + 1],
		)
		log_console.blit(console, 3, 3)

	def ev_keydown(self, event):
		# Fancy conditional movement to make it feel right
		if event.sym in CURSOR_Y_KEYS:
			adjust = CURSOR_Y_KEYS[event.sym]
			if adjust < 0 and self.cursor == 0:
				# Only move from the top to the bottom when you're at the edge.
				self.cursor = self.log_length - 1
			elif adjust > 0 and self.cursor == self.log_length - 1:
				# Same with bottom to top movement
				self.cursor = 0
			else:
				# Otherwise move while staying clamped to the bounds of the history log
				self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
		elif event.sym == tcod.event.K_HOME:
			self.cursor = 0  # Move to top message
		elif event.sym == tcod.event.K_END:
			self.cursor = self.log_length - 1  # Move directly to last message
		else:  # Any other key moves back to the main game state
			self.engine.event_handler = MainGameEventHandler(self.engine)


class AskUserEventHandler(EventHandler):
	""" Handles user input for actions which require special input """
	def handle_action(self, action):
		"""Return to the main event handler when a valid action was performed

		Args:
			action (Action): The action which an Actor is attempting.
		"""
		if super().handle_action(action):
			self.engine.event_handler = MainGameEventHandler(self.engine)
			return True
		return False

	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
		""" By default any key exists this input handler."""
		if event.sym in {  # Ignorer modifier taster (shift, ctrl, alt)
			tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT,
		}:
			return None
		return self.on_exit()

	def ev_mousebuttondown(self, event):
		"""By default, any mouse click exits this input handler. """
		return self.on_exit()

	def on_exit(self) -> Optional[Action]:
		""" Called when the user is trying to exit or cancel an action. """
		self.engine.event_handler = MainGameEventHandler(self.engine)
		return None


class InventoryEventHandler(AskUserEventHandler):
	""" This handler lets the user select an item. What happens depends on the subclass. """
	TITLE = "<missing title>"

	def on_render(self, console: tcod.Console) -> None:
		""" Render an inventory menu, which displays the items and a letter that corresponds with the item. """
		super().on_render(console)
		number_of_items_in_inventory = len(self.engine.player.inventory.items)

		height = number_of_items_in_inventory + 2

		if height <= 3:
			height = 3

		if self.engine.player.x <= 30:
			x = 40
		else:
			x = 0

		y = 0

		width = len(self.TITLE) + 4

		console.draw_frame(
			x=x,
			y=y,
			width=width,
			height=height,
			title=self.TITLE,
			clear=True,
			fg=(255, 255, 255),
			bg=(0, 0, 0),
		)

		if number_of_items_in_inventory > 0:
			for i, item, in enumerate(self.engine.player.inventory.items):
				item_key = chr(ord('a') + i)
				console.print(
					x + 1,
					y + i + 1,
					f'({item_key}) {item.name}',
				)
		else:
			console.print(x + 1, y + 1, "(Moths fly out of your empty sack.)")

	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
		player = self.engine.player
		key = event.sym
		index = key - tcod.event.K_a

		if 0 <= index <= 26:
			try:
				selected_item = player.inventory.items[index]
			except IndexError:
				self.engine.message_log.add_message(
					"Invalid entry.",
					color.invalid,
				)
				return None
			return self.on_item_selected(selected_item)
		return super().ev_keydown(event)

	def on_item_selected(self, item: Item) -> Optional[Action]:
		"""Called when the user selects a valid item."""
		raise NotImplementedError


class InventoryActiveHandler(InventoryEventHandler):
	""" Handle using an inventory item """
	TITLE = "Select an item to use."

	def on_item_selected(self, item: Item) -> Optional[Action]:
		""" Return the action for the selected item. """
		return item.consumable.get_action(self.engine.player)


class InventoryDropHandler(InventoryEventHandler):
	""" Handling dropping an inventory item. """
	TITLE = "Select an item to drop."

	def on_item_selected(self, item: Item) -> Optional[Action]:
		""" drop item """
		return actions.DropItem(self.engine.player, item)



class SelectIndexHandler(AskUserEventHandler):
	""" Handles asking the user for an index on the map. """
	def __init__(self, engine):
		""" Sets the cursor to the player when this handler is constructed. """
		super().__init__(engine)
		player = self.engine.player
		engine.mouse_location = player.x, player.y

	def on_render(self, console):
		""" Highlight the tile under the cursor. """
		super().on_render(console)
		x, y = self.engine.mouse_location
		console.tiles_rgb['bg'][x, y] = color.white
		console.tiles_rgb['fg'][x, y] = color.black

	def ev_keydown(self, event) -> Optional[Action]:
		""" Check for key movements or confirmation keys. """
		key = event.SystemExit
		if key in MOVE_KEYS:
			modifier = 1  # Holding modifier keys will speed up key movement
			if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
				modifier *= 5
			if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
				modifier *= 10
			if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
				modifier *= 20

			x, y = self.engine.mouse_location
			dir_x, dir_y = MOVE_KEYS[key]
			x += dir_x * modifier
			y += dir_y * modifier

			# Clamp the cursor index to the map size
			x = max(0, min(x, self.engine.game_map.width - 1))
			y = max(0, min(y, self.engine.game_map.height - 1))
			self.engine.mouse_location = x, y
			return None

		elif key in CONFIRM_KEYS:
			return self.on_index_selected(*self.engine.mouse_location)
		return super().ev_keydown(event)

	def ev_mousebuttondown(self, event):
		""" Left click confirms a selection. """
		if self.engine.game_map.in_bounds(*event.tile):
			if event.button == 1:
				return self.on_index_selected(*event.tile)

		return super().ev_mousebuttondown(event)

	def on_index_selected(self, x: int, y: int) -> Optional[Action]:
		""" Called when the index is selected. """
		raise NotImplementedError()


class LookHandler(SelectIndexHandler):
	""" Let's the player look around using the keyboard. """
	def on_index_selected(self, x, y) -> None:
		self.engine.event_handler = MainGameEventHandler(self.engine)