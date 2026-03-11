from models import Direction, Field
from visualizer import render_grid


class TestRenderGrid:
    def test_empty_field(self):
        field = Field(3, 3)
        car_states = []
        lines = render_grid(field, car_states)

        assert lines[0] == "+------+"
        assert lines[1] == "|      |"
        assert lines[2] == "|      |"
        assert lines[3] == "|      |"
        assert lines[4] == "+------+"

    def test_single_car_facing_north(self):
        field = Field(5, 3)
        car_states = [
            {"name": "A", "x": 2, "y": 1, "direction": Direction.N, "collided": False, "active": True},
        ]
        lines = render_grid(field, car_states)

        # y=2 (top row) -> line index 1
        # y=1 (middle row) -> line index 2
        # y=0 (bottom row) -> line index 3
        assert "A^" in lines[2]

    def test_single_car_facing_east(self):
        field = Field(5, 3)
        car_states = [
            {"name": "A", "x": 0, "y": 0, "direction": Direction.E, "collided": False, "active": True},
        ]
        lines = render_grid(field, car_states)

        # y=0 is bottom row -> line index 3
        assert "A>" in lines[3]

    def test_collided_car_shows_asterisk(self):
        field = Field(5, 3)
        car_states = [
            {"name": "A", "x": 1, "y": 1, "direction": Direction.N, "collided": True, "active": False},
        ]
        lines = render_grid(field, car_states)

        assert "A*" in lines[2]

    def test_two_cars_on_field(self):
        field = Field(5, 3)
        car_states = [
            {"name": "A", "x": 0, "y": 2, "direction": Direction.N, "collided": False, "active": True},
            {"name": "B", "x": 4, "y": 0, "direction": Direction.W, "collided": False, "active": True},
        ]
        lines = render_grid(field, car_states)

        assert "A^" in lines[1]  # y=2 is top row
        assert "B<" in lines[3]  # y=0 is bottom row

    def test_grid_dimensions_match_field(self):
        field = Field(4, 2)
        car_states = []
        lines = render_grid(field, car_states)

        # Width: 4 cells * 2 chars each + 2 borders = 10 chars per line
        # Height: 2 rows + 2 border rows = 4 lines
        assert len(lines) == 4  # 2 rows + 2 borders
        assert lines[0] == "+--------+"
        assert lines[1] == "|        |"
