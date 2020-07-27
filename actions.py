class Action:
    pass


class EscapeAction(Action):
    pass


class MovementAction(Action):
    def __init__(self, dir_x : int, dir_y : int):
        """Initialisering

        Args:
            dir_x (int): Direktion på X-aksen
            dir_y (int): Direktion på Y-aksen
        """
        super().__init__()  # Kalder på den klasse vi arver fras `__init__` funktion.

        self.dir_x = dir_x
        self.dir_y = dir_y