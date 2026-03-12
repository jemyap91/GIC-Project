from models import Car, Direction, Field
from simulation import Simulation


class TestSingleCar:
    def test_scenario_1(self):
        field = Field(10, 10)
        car = Car(name="A", x=1, y=2, direction=Direction.N, commands="FFRFFFFRRL")
        results = Simulation(field, [car]).run()

        assert len(results) == 1
        assert results[0].car_name == "A"
        assert results[0].x == 5
        assert results[0].y == 4
        assert results[0].direction == Direction.S
        assert results[0].collided is False

    def test_no_commands(self):
        field = Field(10, 10)
        car = Car(name="A", x=3, y=3, direction=Direction.E, commands="")
        results = Simulation(field, [car]).run()

        assert results[0].x == 3
        assert results[0].y == 3

    def test_only_turns(self):
        field = Field(10, 10)
        car = Car(name="A", x=0, y=0, direction=Direction.N, commands="LLLL")
        results = Simulation(field, [car]).run()

        assert results[0].x == 0
        assert results[0].y == 0
        assert results[0].direction == Direction.N

    def test_move_forward(self):
        field = Field(10, 10)
        car = Car(name="A", x=0, y=0, direction=Direction.N, commands="FFF")
        results = Simulation(field, [car]).run()

        assert results[0].y == 3


class TestBoundary:
    def test_south_boundary(self):
        field = Field(10, 10)
        car = Car(name="A", x=0, y=0, direction=Direction.S, commands="F")
        results = Simulation(field, [car]).run()
        assert results[0].y == 0

    def test_north_boundary(self):
        field = Field(10, 10)
        car = Car(name="A", x=5, y=9, direction=Direction.N, commands="F")
        results = Simulation(field, [car]).run()
        assert results[0].y == 9

    def test_west_boundary(self):
        field = Field(10, 10)
        car = Car(name="A", x=0, y=5, direction=Direction.W, commands="F")
        results = Simulation(field, [car]).run()
        assert results[0].x == 0

    def test_east_boundary(self):
        field = Field(10, 10)
        car = Car(name="A", x=9, y=5, direction=Direction.E, commands="F")
        results = Simulation(field, [car]).run()
        assert results[0].x == 9

    def test_boundary_skip_then_continue(self):
        field = Field(5, 5)
        car = Car(name="A", x=0, y=0, direction=Direction.S, commands="FRF")
        results = Simulation(field, [car]).run()

        assert results[0].x == 0
        assert results[0].y == 0
        assert results[0].direction == Direction.W


class TestCollision:
    def test_scenario_2(self):
        field = Field(10, 10)
        car_a = Car(name="A", x=1, y=2, direction=Direction.N, commands="FFRFFFFRRL")
        car_b = Car(name="B", x=7, y=8, direction=Direction.W, commands="FFLFFFFFFF")
        results = Simulation(field, [car_a, car_b]).run()

        assert results[0].collided is True
        assert results[0].x == 5
        assert results[0].y == 4
        assert results[0].collision_step == 7
        assert results[0].collision_partner == "B"

        assert results[1].collided is True
        assert results[1].collision_partner == "A"

    def test_no_collision(self):
        field = Field(10, 10)
        car_a = Car(name="A", x=0, y=0, direction=Direction.N, commands="FF")
        car_b = Car(name="B", x=9, y=9, direction=Direction.S, commands="FF")
        results = Simulation(field, [car_a, car_b]).run()

        assert results[0].collided is False
        assert results[1].collided is False

    def test_unequal_command_lengths(self):
        field = Field(10, 10)
        car_a = Car(name="A", x=0, y=0, direction=Direction.N, commands="FFFFF")
        car_b = Car(name="B", x=5, y=5, direction=Direction.E, commands="FF")
        results = Simulation(field, [car_a, car_b]).run()

        assert results[0].y == 5
        assert results[0].collided is False
        assert results[1].x == 7
        assert results[1].collided is False

    def test_collision_stops_movement(self):
        field = Field(10, 10)
        car_a = Car(name="A", x=0, y=0, direction=Direction.E, commands="FFF")
        car_b = Car(name="B", x=1, y=0, direction=Direction.N, commands="FFF")
        results = Simulation(field, [car_a, car_b]).run()

        assert results[0].collided is True
        assert results[0].x == 1
        assert results[0].collision_step == 1

    def test_collide_with_stopped_car(self):
        field = Field(10, 10)
        car_a = Car(name="A", x=0, y=0, direction=Direction.E, commands="FFF")
        car_b = Car(name="B", x=1, y=0, direction=Direction.N, commands="FFF")
        car_c = Car(name="C", x=3, y=0, direction=Direction.W, commands="FF")
        results = Simulation(field, [car_a, car_b, car_c]).run()

        assert results[0].collision_step == 1
        assert results[0].collision_partner == "B"
        assert results[2].collided is True
        assert results[2].x == 1
        assert results[2].collision_step == 2

    def test_sequential_processing_no_false_collision(self):
        field = Field(10, 10)
        car_a = Car(name="A", x=5, y=5, direction=Direction.N, commands="F")
        car_b = Car(name="B", x=4, y=5, direction=Direction.E, commands="F")
        results = Simulation(field, [car_a, car_b]).run()

        assert results[0].collided is False
        assert results[0].y == 6
        assert results[1].collided is False
        assert results[1].x == 5
