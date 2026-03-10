from dataclasses import dataclass
from enum import Enum


class Direction(Enum):
    N = "N"
    E = "E"
    S = "S"
    W = "W"

    def turn_right(self) -> "Direction":
        order = [Direction.N, Direction.E, Direction.S, Direction.W]
        return order[(order.index(self) + 1) % 4]

    def turn_left(self) -> "Direction":
        order = [Direction.N, Direction.E, Direction.S, Direction.W]
        return order[(order.index(self) - 1) % 4]

    def move_delta(self) -> tuple[int, int]:
        deltas = {
            Direction.N: (0, 1),
            Direction.S: (0, -1),
            Direction.E: (1, 0),
            Direction.W: (-1, 0),
        }
        return deltas[self]


@dataclass
class Field:
    width: int
    height: int

    def is_within_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
