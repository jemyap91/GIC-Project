from models import Car, Direction, SimulationResult


class TestCar:
    def test_car_creation(self):
        car = Car(name="A", x=1, y=2, direction=Direction.N, commands="FFRFF")
        assert car.name == "A"
        assert car.x == 1
        assert car.y == 2
        assert car.direction == Direction.N
        assert car.commands == "FFRFF"

    def test_car_string_representation(self):
        car = Car(name="A", x=1, y=2, direction=Direction.N, commands="FFRFF")
        assert str(car) == "A, (1,2) N, FFRFF"


class TestSimulationResult:
    def test_result_no_collision(self):
        result = SimulationResult(
            car_name="A", x=5, y=4, direction=Direction.S,
            collided=False, collision_step=None, collision_partner=None,
        )
        assert str(result) == "A, (5,4) S"

    def test_result_with_collision(self):
        result = SimulationResult(
            car_name="A", x=5, y=4, direction=Direction.S,
            collided=True, collision_step=7, collision_partner="B",
        )
        assert str(result) == "A, collides with B at (5,4) at step 7"
