from typing import Iterable, List, Reversible, Tuple
import textwrap

import tcod

import color


class Message:
	def __init__(self, text: str, fg: Tuple[int, int, int]):
		self.plain_text = text
		self.fg = fg
		self.count = 1  # fx "Du angriber(x3)

	@property
	def full_text(self) -> str:
		""" Den fulde besked, plus karakter antal """
		if self.count > 1:
			return f"{self.plain_text} (x{self.count})"
		return self.plain_text


class MessageLog:
	def __init__(self):
		self.messages: List[Message] = []

	def add_message(
		self,
		text: str,
		fg: Tuple[int, int, int] = color.white,
		*,
		stack: bool = True,
	) -> None:
		"""Tilføj en besked til log.

		Args:
			text (str): Beskedens brødtekst
			fg (Tuple[int, int, int], optional): Forgrundsfarve. Defaults to color.white.
			stack (bool, optional): Hvis True, så kan beskedens stackes, fx "Du angriber(x3). Defaults to true.
		"""
		if stack and self.messages and text == self.messages[-1].plain_text:
			self.messages[-1].count += 1
		else:
			self.messages.append(Message(text, fg))

	def render(
		self,
		console: tcod.Console,
		x: int,
		y: int,
		width: int,
		height: int,
	):
		"""Står for rendering af log.

			x (int): MessageLogs X-koordinat
			y (int): MessageLogs Y-Koordinat
			width (int): MessageLogs bredde
			height (int): MessageLogs højde.
		"""
		self.render_messages(console, x, y, width, height, self.messages)

	@staticmethod
	def wrap(string: str, width: int) -> Iterable[str]:
		"""Return a wrapped text"""
		for line in string.splitlines():  # handle newlines in messages.
			yield from textwrap.wrap(
				line, width, expand_tabs=True,
			)


	@classmethod
	def render_messages(
		cls,
		console: tcod.Console,
		x: int,
		y: int,
		width: int,
		height: int,
		messages: Reversible[Message],
	) -> None:
		"""Render the messages provided

		Beskederne er renderet baglæns fra den sidste besked

		Args:
			console (tcod.Console): Consolen
			x (int): X-Koordinat
			y (int): Y-Koordinat
			width (int): Bredde
			height (int): højde
			messages (Reversible[Message]): Listen af beskeder
		"""
		y_offset = height - 1

		for message in reversed(messages):
			for line in reversed(list(cls.wrap(message.full_text, width))):
				console.print(x=x, y=y + y_offset, string=line, fg=message.fg)
				y_offset -= 1
				if y_offset < 0:
					return  # Ikke mere plads til at printe beskeden