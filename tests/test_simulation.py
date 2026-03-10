from models import Car, Direction, Field, SimulationResult
from simulation import Simulation


class TestSingleCarSimulation:
    """Scenario 1 from spec: car A at (1,2) N with commands FFRFFFFRRL ends at (5,4) S."""

    def test_spec_scenario_1(self):
        field = Field(10, 10)
        car = Car(name="A", x=1, y=2, direction=Direction.N, commands="FFRFFFFRRL")
        sim = Simulation(field, [car])
        results = sim.run()

        assert len(results) == 1
        assert results[0].car_name == "A"
        assert results[0].x == 5
        assert results[0].y == 4
        assert results[0].direction == Direction.S
        assert results[0].collided is False

    def test_single_car_no_commands(self):
        field = Field(10, 10)
        car = Car(name="A", x=3, y=3, direction=Direction.E, commands="")
        sim = Simulation(field, [car])
        results = sim.run()

        assert results[0].x == 3
        assert results[0].y == 3
        assert results[0].direction == Direction.E

    def test_single_car_only_turns(self):
        field = Field(10, 10)
        car = Car(name="A", x=0, y=0, direction=Direction.N, commands="LLLL")
        sim = Simulation(field, [car])
        results = sim.run()

        assert results[0].x == 0
        assert results[0].y == 0
        assert results[0].direction == Direction.N

    def test_single_car_move_forward(self):
        field = Field(10, 10)
        car = Car(name="A", x=0, y=0, direction=Direction.N, commands="FFF")
        sim = Simulation(field, [car])
        results = sim.run()

        assert results[0].x == 0
        assert results[0].y == 3


class TestBoundaryHandling:
    def test_car_at_south_boundary_facing_south_stays_put(self):
        field = Field(10, 10)
        car = Car(name="A", x=0, y=0, direction=Direction.S, commands="F")
        sim = Simulation(field, [car])
        results = sim.run()

        assert results[0].x == 0
        assert results[0].y == 0

    def test_car_at_north_boundary_facing_north_stays_put(self):
        field = Field(10, 10)
        car = Car(name="A", x=5, y=9, direction=Direction.N, commands="F")
        sim = Simulation(field, [car])
        results = sim.run()

        assert results[0].x == 5
        assert results[0].y == 9

    def test_car_at_west_boundary_facing_west_stays_put(self):
        field = Field(10, 10)
        car = Car(name="A", x=0, y=5, direction=Direction.W, commands="F")
        sim = Simulation(field, [car])
        results = sim.run()

        assert results[0].x == 0
        assert results[0].y == 5

    def test_car_at_east_boundary_facing_east_stays_put(self):
        field = Field(10, 10)
        car = Car(name="A", x=9, y=5, direction=Direction.E, commands="F")
        sim = Simulation(field, [car])
        results = sim.run()

        assert results[0].x == 9
        assert results[0].y == 5

    def test_boundary_ignored_then_continues(self):
        """Car hits boundary, ignores, then continues with next command."""
        field = Field(5, 5)
        car = Car(name="A", x=0, y=0, direction=Direction.S, commands="FRF")
        sim = Simulation(field, [car])
        results = sim.run()

        # F ignored (south boundary), R turns to W, F ignored (west boundary)
        assert results[0].x == 0
        assert results[0].y == 0
        assert results[0].direction == Direction.W


class TestMultiCarCollision:
    """Scenario 2 from spec: two cars collide at (5,4) at step 7."""

    def test_spec_scenario_2_collision(self):
        field = Field(10, 10)
        car_a = Car(name="A", x=1, y=2, direction=Direction.N, commands="FFRFFFFRRL")
        car_b = Car(name="B", x=7, y=8, direction=Direction.W, commands="FFLFFFFFFF")
        sim = Simulation(field, [car_a, car_b])
        results = sim.run()

        result_a = results[0]
        result_b = results[1]

        assert result_a.collided is True
        assert result_a.x == 5
        assert result_a.y == 4
        assert result_a.collision_step == 7
        assert result_a.collision_partner == "B"

        assert result_b.collided is True
        assert result_b.x == 5
        assert result_b.y == 4
        assert result_b.collision_step == 7
        assert result_b.collision_partner == "A"

    def test_two_cars_no_collision(self):
        field = Field(10, 10)
        car_a = Car(name="A", x=0, y=0, direction=Direction.N, commands="FF")
        car_b = Car(name="B", x=9, y=9, direction=Direction.S, commands="FF")
        sim = Simulation(field, [car_a, car_b])
        results = sim.run()

        assert results[0].collided is False
        assert results[0].x == 0
        assert results[0].y == 2

        assert results[1].collided is False
        assert results[1].x == 9
        assert results[1].y == 7

    def test_unequal_command_lengths(self):
        """Car B has fewer commands. After B stops, A continues."""
        field = Field(10, 10)
        car_a = Car(name="A", x=0, y=0, direction=Direction.N, commands="FFFFF")
        car_b = Car(name="B", x=5, y=5, direction=Direction.E, commands="FF")
        sim = Simulation(field, [car_a, car_b])
        results = sim.run()

        assert results[0].x == 0
        assert results[0].y == 5
        assert results[0].collided is False

        assert results[1].x == 7
        assert results[1].y == 5
        assert results[1].collided is False

    def test_collision_stops_further_commands(self):
        """After collision, collided cars don't move further."""
        field = Field(10, 10)
        car_a = Car(name="A", x=0, y=0, direction=Direction.E, commands="FFF")
        car_b = Car(name="B", x=1, y=0, direction=Direction.N, commands="FFF")
        sim = Simulation(field, [car_a, car_b])
        results = sim.run()

        assert results[0].collided is True
        assert results[0].x == 1
        assert results[0].y == 0
        assert results[0].collision_step == 1

        assert results[1].collided is True
        assert results[1].x == 1
        assert results[1].y == 0
        assert results[1].collision_step == 1

    def test_car_collides_with_already_stopped_car(self):
        """A third car can collide with an already-collided stationary car."""
        field = Field(10, 10)
        car_a = Car(name="A", x=0, y=0, direction=Direction.E, commands="FFF")
        car_b = Car(name="B", x=1, y=0, direction=Direction.N, commands="FFF")
        car_c = Car(name="C", x=3, y=0, direction=Direction.W, commands="FF")
        sim = Simulation(field, [car_a, car_b, car_c])
        results = sim.run()

        assert results[0].collided is True
        assert results[0].collision_step == 1
        assert results[0].collision_partner == "B"

        assert results[1].collided is True
        assert results[1].collision_step == 1

        assert results[2].collided is True
        assert results[2].x == 1
        assert results[2].y == 0
        assert results[2].collision_step == 2

    def test_duplicate_starting_position_collision(self):
        """Sequential processing: A moves first, B moves to A's old position — no collision."""
        field = Field(10, 10)
        car_a = Car(name="A", x=5, y=5, direction=Direction.N, commands="F")
        car_b = Car(name="B", x=4, y=5, direction=Direction.E, commands="F")
        sim = Simulation(field, [car_a, car_b])
        results = sim.run()

        assert results[0].collided is False
        assert results[0].x == 5
        assert results[0].y == 6
        assert results[1].collided is False
        assert results[1].x == 5
        assert results[1].y == 5
