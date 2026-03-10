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
    def __init__(self, field: Field, cars: list[Car]) -> None:
        self.field = field
        self.states = [
            _CarState(
                name=car.name,
                x=car.x,
                y=car.y,
                direction=car.direction,
                commands=car.commands,
            )
            for car in cars
        ]

    def run(self) -> list[SimulationResult]:
        max_commands = max((len(s.commands) for s in self.states), default=0)

        for step in range(max_commands):
            for state in self.states:
                if not state.active:
                    continue
                if step >= len(state.commands):
                    continue

                command = state.commands[step]
                self._execute_command(state, command)
                self._check_collisions(state, step + 1)

        return [
            SimulationResult(
                car_name=s.name,
                x=s.x,
                y=s.y,
                direction=s.direction,
                collided=s.collided,
                collision_step=s.collision_step,
                collision_partner=s.collision_partner,
            )
            for s in self.states
        ]

    def _check_collisions(self, moved_state: _CarState, step: int) -> None:
        for other in self.states:
            if other is moved_state:
                continue
            if other.x == moved_state.x and other.y == moved_state.y:
                moved_state.active = False
                moved_state.collided = True
                moved_state.collision_step = step
                moved_state.collision_partner = other.name

                if other.active:
                    other.active = False
                    other.collided = True
                    other.collision_step = step
                    other.collision_partner = moved_state.name

    def _execute_command(self, state: _CarState, command: str) -> None:
        if command == "L":
            state.direction = state.direction.turn_left()
        elif command == "R":
            state.direction = state.direction.turn_right()
        elif command == "F":
            dx, dy = state.direction.move_delta()
            new_x, new_y = state.x + dx, state.y + dy
            if self.field.is_within_bounds(new_x, new_y):
                state.x = new_x
                state.y = new_y
