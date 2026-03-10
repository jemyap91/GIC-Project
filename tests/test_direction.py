from models import Direction


class TestDirectionTurnRight:
    def test_north_turns_right_to_east(self):
        assert Direction.N.turn_right() == Direction.E

    def test_east_turns_right_to_south(self):
        assert Direction.E.turn_right() == Direction.S

    def test_south_turns_right_to_west(self):
        assert Direction.S.turn_right() == Direction.W

    def test_west_turns_right_to_north(self):
        assert Direction.W.turn_right() == Direction.N


class TestDirectionTurnLeft:
    def test_north_turns_left_to_west(self):
        assert Direction.N.turn_left() == Direction.W

    def test_west_turns_left_to_south(self):
        assert Direction.W.turn_left() == Direction.S

    def test_south_turns_left_to_east(self):
        assert Direction.S.turn_left() == Direction.E

    def test_east_turns_left_to_north(self):
        assert Direction.E.turn_left() == Direction.N


class TestDirectionMoveDelta:
    """Direction.move_delta() returns (dx, dy) for a forward move."""

    def test_north_moves_up(self):
        assert Direction.N.move_delta() == (0, 1)

    def test_south_moves_down(self):
        assert Direction.S.move_delta() == (0, -1)

    def test_east_moves_right(self):
        assert Direction.E.move_delta() == (1, 0)

    def test_west_moves_left(self):
        assert Direction.W.move_delta() == (-1, 0)
