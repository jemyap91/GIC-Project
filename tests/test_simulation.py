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
