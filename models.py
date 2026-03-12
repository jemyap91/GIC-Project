from dataclasses import dataclass
from enum import Enum


class Direction(Enum):
    N = "N"
    E = "E"
    S = "S"
    W = "W"

    def turn_right(self):
        order = [Direction.N, Direction.E, Direction.S, Direction.W]
        return order[(order.index(self) + 1) % 4]

    def turn_left(self):
        order = [Direction.N, Direction.E, Direction.S, Direction.W]
        return order[(order.index(self) - 1) % 4]

    def move_delta(self):
        return {
            Direction.N: (0, 1),
            Direction.S: (0, -1),
            Direction.E: (1, 0),
            Direction.W: (-1, 0),
        }[self]


@dataclass
class Field:
    width: int
    height: int

    def is_within_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height


@dataclass
class Car:
    name: str
    x: int
    y: int
    direction: Direction
    commands: str

    def __str__(self):
        return f"{self.name}, ({self.x},{self.y}) {self.direction.value}, {self.commands}"


@dataclass
class SimulationResult:
    car_name: str
    x: int
    y: int
    direction: Direction
    collided: bool
    collision_step: int | None
    collision_partner: str | None

    def __str__(self):
        if self.collided:
            return (
                f"{self.car_name}, collides with {self.collision_partner} "
                f"at ({self.x},{self.y}) at step {self.collision_step}"
            )
        return f"{self.car_name}, ({self.x},{self.y}) {self.direction.value}"
