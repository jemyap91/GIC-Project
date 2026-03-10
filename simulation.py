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
