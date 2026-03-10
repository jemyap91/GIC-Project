from models import Field


class TestFieldBounds:
    def test_origin_is_within_bounds(self):
        field = Field(10, 10)
        assert field.is_within_bounds(0, 0) is True

    def test_max_corner_is_within_bounds(self):
        field = Field(10, 10)
        assert field.is_within_bounds(9, 9) is True

    def test_negative_x_is_out_of_bounds(self):
        field = Field(10, 10)
        assert field.is_within_bounds(-1, 0) is False

    def test_negative_y_is_out_of_bounds(self):
        field = Field(10, 10)
        assert field.is_within_bounds(0, -1) is False

    def test_x_equal_to_width_is_out_of_bounds(self):
        field = Field(10, 10)
        assert field.is_within_bounds(10, 0) is False

    def test_y_equal_to_height_is_out_of_bounds(self):
        field = Field(10, 10)
        assert field.is_within_bounds(0, 10) is False

    def test_center_is_within_bounds(self):
        field = Field(10, 10)
        assert field.is_within_bounds(5, 5) is True

    def test_small_field(self):
        field = Field(1, 1)
        assert field.is_within_bounds(0, 0) is True
        assert field.is_within_bounds(1, 0) is False
