class Action:
    pass


class EscapeAction(Action):
    pass


class MovementAction(Action):
    def __init__(self, dx : int, dy : int):
        """Initialisering

        Args:
            dx (int): Direktion på X-aksen
            dy (int): Direktion på Y-aksen
        """
        super().__init__()  # Kalder på den klasse vi arver fras `__init__` funktion.

        self.dx = dx
        self.dy = dy