from typing import Callable

from models import Direction, Field

DIRECTION_SYMBOLS = {
    Direction.N: "^",
    Direction.S: "v",
    Direction.E: ">",
    Direction.W: "<",
}


def render_grid(field: Field, car_states: list[dict]) -> list[str]:
    """Render an ASCII grid with car positions. Returns list of lines."""
    cell_width = 2  # each cell is 2 chars wide (name + direction)
    grid_width = field.width * cell_width

    # Build empty grid rows (top row = highest y)
    rows: list[list[str]] = []
    for _ in range(field.height):
        rows.append([" "] * grid_width)

    # Place cars on grid
    for car in car_states:
        x, y = car["x"], car["y"]
        row_index = field.height - 1 - y  # flip: y=0 is bottom
        col_index = x * cell_width
        name = car["name"]
        if car["collided"]:
            symbol = "*"
        else:
            symbol = DIRECTION_SYMBOLS[car["direction"]]
        rows[row_index][col_index] = name
        rows[row_index][col_index + 1] = symbol

    # Build output lines
    border = "+" + "-" * grid_width + "+"
    lines = [border]
    for row in rows:
        lines.append("|" + "".join(row) + "|")
    lines.append(border)

    return lines


def render_legend(car_states: list[dict]) -> str:
    """Render a one-line legend of car positions."""
    parts = []
    for car in car_states:
        status = "*" if car["collided"] else car["direction"].value
        parts.append(f"{car['name']}=({car['x']},{car['y']}) {status}")
    return "Cars: " + " | ".join(parts)


def replay(
    field: Field,
    cars: list,
    steps: list[list[dict]],
    input_fn: Callable[..., str] = input,
    output_fn: Callable[..., None] = print,
) -> None:
    """Replay simulation step-by-step with Enter to advance."""
    total_steps = len(steps)

    for i, step_states in enumerate(steps):
        output_fn("\033[2J\033[H")  # clear screen
        output_fn(f"Step {i + 1} of {total_steps}:")
        output_fn()
        for line in render_grid(field, step_states):
            output_fn(line)
        output_fn()
        output_fn(render_legend(step_states))

        if i < total_steps - 1:
            output_fn("[Press Enter for next step]")
            input_fn()
        else:
            output_fn("Simulation complete. Press Enter to continue.")
            input_fn()
