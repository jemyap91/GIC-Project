from typing import Callable

from models import Car, Direction, Field
from simulation import Simulation


class App:
    def __init__(
        self,
        input_fn: Callable[..., str] = input,
        output_fn: Callable[..., None] = print,
    ) -> None:
        self._input = input_fn
        self._print = output_fn

    def run(self) -> None:
        while True:
            field, cars = self._setup_phase()
            results = Simulation(field, cars).run()
            self._show_results(cars, results)

            if not self._post_simulation_menu():
                break

    def _setup_phase(self) -> tuple[Field, list[Car]]:
        self._print("Welcome to Auto Driving Car Simulation!")
        self._print()
        field = self._get_field()
        cars: list[Car] = []

        while True:
            self._show_car_list(cars)
            self._print("Please choose from the following options:")
            self._print("[1] Add a car to field")
            self._print("[2] Run simulation")

            choice = self._input().strip()
            if choice == "2":
                break
            elif choice == "1":
                car = self._add_car(field, cars)
                if car:
                    cars.append(car)

        return field, cars

    def _get_field(self) -> Field:
        while True:
            self._print("Please enter the width and height of the simulation field in x y format:")
            parts = self._input().strip().split()
            if len(parts) == 2:
                try:
                    w, h = int(parts[0]), int(parts[1])
                    if w > 0 and h > 0:
                        self._print(f"You have created a field of {w} x {h}.")
                        self._print()
                        return Field(w, h)
                except ValueError:
                    pass
            self._print("Invalid input. Please enter two positive integers.")

    def _add_car(self, field: Field, existing_cars: list[Car]) -> Car | None:
        self._print("Please enter the name of the car:")
        name = self._input().strip()
        if not name:
            self._print("Car name cannot be empty.")
            return None
        if any(c.name == name for c in existing_cars):
            self._print(f"A car named '{name}' already exists.")
            return None

        self._print(f"Please enter initial position of car {name} in x y Direction format:")
        while True:
            parts = self._input().strip().split()
            if len(parts) == 3:
                try:
                    x, y = int(parts[0]), int(parts[1])
                    d = parts[2].upper()
                    if d in ("N", "S", "E", "W") and field.is_within_bounds(x, y):
                        if any(c.x == x and c.y == y for c in existing_cars):
                            self._print("Another car is already at that position.")
                            return None
                        direction = Direction(d)
                        break
                except ValueError:
                    pass
            self._print("Invalid input. Please enter x y Direction (e.g., 1 2 N).")

        self._print(f"Please enter the commands for car {name}:")
        while True:
            commands = self._input().strip().upper()
            if commands and all(c in "LRF" for c in commands):
                break
            if not commands:
                break
            self._print("Invalid commands. Please use only L, R, F.")

        return Car(name=name, x=x, y=y, direction=direction, commands=commands)

    def _show_car_list(self, cars: list[Car]) -> None:
        if cars:
            self._print("Your current list of cars are:")
            for car in cars:
                self._print(f"- {car}")
            self._print()

    def _show_results(self, cars: list[Car], results: list) -> None:
        self._print("Your current list of cars are:")
        for car in cars:
            self._print(f"- {car}")
        self._print()
        self._print("After simulation, the result is:")
        for result in results:
            self._print(f"- {result}")
        self._print()

    def _post_simulation_menu(self) -> bool:
        self._print("Please choose from the following options:")
        self._print("[1] Start over")
        self._print("[2] Exit")

        choice = self._input().strip()
        if choice == "1":
            return True
        self._print("Thank you for running the simulation. Goodbye!")
        return False
