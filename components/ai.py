from __future__ import annotations

import random
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import tcod

from actions import Action, BumpAction, MeleeAction, MovementAction, WaitAction

if TYPE_CHECKING:
    from entity import Actor


class BaseAI(Action):
    def perform(self) -> None:
        raise NotImplementedError()

    def get_path_to(self, dest_x, dest_y) -> List[Tuple[int, int]]:
        """ Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Kopier den 'walkable' list.
        # Note `cost` fordi vi ser hvor meget tid det koster at komme over til målet.
        cost = np.array(self.entity.game_map.tiles['walkable'], dtype=np.int8)

        for entity in self.entity.game_map.entities:
            # Check that an entity blocks movement and that cost isn't zero (blockin)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add to the cost of a blocked position
                # A lower number means more enemies will crowd behind each other in hallways.
                # A higher number means enemies will take longer paths in order to surround the player
                cost[
                    entity.x, entity.y] += 10  # This encourages the entity to move around that area, since the entity will try to go the path with the smallest cost

        # Create a graph from the cost array and pass that graph to a new pathfinder
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))  # Start position

        # Compute the path to the destination and remove the starting point
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]]
        return [(index[0], index[1]) for index in path]


class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

    def perform(self):
        target = self.engine.player
        dir_x = target.x - self.entity.x
        dir_y = target.y - self.entity.y
        distance = max(abs(dir_x), abs(dir_y))  # https://en.wikipedia.org/wiki/Chebyshev_distance
        # print(f"{self.entity.name}s turn")
        # Prøve at angribe
        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            # print(f"{self.entity.name} inside .visible consitional")
            if distance <= 1:  # Hvis distancen mellem entity og target er 1 eller mindre (de rører hinanden)
                # print(f"{self.entity.name} distance <= 1")
                # print("AI ATTACKS")
                return MeleeAction(self.entity, dir_x, dir_y).perform()
            print("SETTING PATH")
            self.path = self.get_path_to(target.x, target.y)

        if self.path:  # Hvis entity har en path
            # print(f"{self.entity.name} if self.path")
            dest_x, dest_y = self.path.pop(0)  # Fjern den ældste entry
            print("AI MOVES")
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
                             ).perform()

        # print(f"{self.entity.name} wait action")
        return WaitAction(self.entity).perform()


class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for a given number of turns, then revert back to its previous AI.
    If an actor occupies a tile it is randomly moving into, it will attack.
    """

    def __init__(self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int):
        super().__init__(entity)
        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self):
        """ Revert the AI back to the original state if the effect is over. """
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer confused.",
            )
            self.entity.ai = self.previous_ai
        else:
            # Pick a random direction
            dir_x, dir_y = random.choice(
                [
                    (-1, -1),  # Northwest
                    (0, -1),  # North
                    (1, -1),  # Northeast
                    (-1, 0),  # West
                    (1, 0),  # East
                    (-1, 1),  # Southwest
                    (0, 1),  # South
                    (1, 1),  # Southeast
                ]
            )

            self.turns_remaining -= 1
            # The actor will either try to move or attack in the chosen random direction.
            # It's possible the actor will just bump into the wall, wasting a turn.
            return BumpAction(self.entity, dir_x, dir_y, ).perform()
