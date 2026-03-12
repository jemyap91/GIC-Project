from dataclasses import dataclass
from models import Car, Direction, Field, SimulationResult


@dataclass
class _CarState:
    name: str
    x: int
    y: int
    direction: Direction
    commands: str
    active: bool = True
    collided: bool = False
    collision_step: int | None = None
    collision_partner: str | None = None


class Simulation:
    def __init__(self, field, cars):
        self.field = field
        self.states = [
            _CarState(
                name=c.name, x=c.x, y=c.y,
                direction=c.direction, commands=c.commands,
            )
            for c in cars
        ]

    def run(self):
        max_commands = max((len(s.commands) for s in self.states), default=0)

        for step in range(max_commands):
            for state in self.states:
                if not state.active or step >= len(state.commands):
                    continue
                self._execute(state, state.commands[step])
                self._check_collisions(state, step + 1)

        return [
            SimulationResult(
                car_name=s.name, x=s.x, y=s.y,
                direction=s.direction, collided=s.collided,
                collision_step=s.collision_step,
                collision_partner=s.collision_partner,
            )
            for s in self.states
        ]

    def _execute(self, state, command):
        if command == "L":
            state.direction = state.direction.turn_left()
        elif command == "R":
            state.direction = state.direction.turn_right()
        elif command == "F":
            dx, dy = state.direction.move_delta()
            nx, ny = state.x + dx, state.y + dy
            if self.field.is_within_bounds(nx, ny):
                state.x, state.y = nx, ny

    def _check_collisions(self, moved, step):
        for other in self.states:
            if other is moved:
                continue
            if other.x == moved.x and other.y == moved.y:
                moved.active = False
                moved.collided = True
                moved.collision_step = step
                moved.collision_partner = other.name

                if other.active:
                    other.active = False
                    other.collided = True
                    other.collision_step = step
                    other.collision_partner = moved.name
