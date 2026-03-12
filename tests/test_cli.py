from cli import App


def make_app(inputs):
    input_iter = iter(inputs)
    output = []

    def mock_input(_prompt=""):
        return next(input_iter)

    def mock_print(*args):
        output.append(" ".join(str(a) for a in args))

    return App(input_fn=mock_input, output_fn=mock_print), output


class TestFieldSetup:
    def test_welcome_and_field_creation(self):
        app, output = make_app(["10 10", "2", "2"])
        app.run()

        assert "Welcome to Auto Driving Car Simulation!" in output
        assert "You have created a field of 10 x 10." in output


class TestAddCar:
    def test_add_car_and_run(self):
        app, output = make_app([
            "10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2", "2",
        ])
        app.run()

        assert any("A, (1,2) N, FFRFFFFRRL" in line for line in output)
        assert any("A, (5,4) S" in line for line in output)


class TestSimulation:
    def test_scenario_1(self):
        app, output = make_app([
            "10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2", "2",
        ])
        app.run()
        assert any("A, (5,4) S" in line for line in output)

    def test_scenario_2_collision(self):
        app, output = make_app([
            "10 10",
            "1", "A", "1 2 N", "FFRFFFFRRL",
            "1", "B", "7 8 W", "FFLFFFFFFF",
            "2", "2",
        ])
        app.run()

        assert any("A, collides with B at (5,4) at step 7" in line for line in output)
        assert any("B, collides with A at (5,4) at step 7" in line for line in output)

    def test_start_over(self):
        app, output = make_app([
            "10 10", "1", "A", "1 2 N", "FF", "2",
            "1",  # start over
            "5 5", "1", "B", "0 0 N", "F", "2", "2",
        ])
        app.run()

        welcome_count = sum(1 for line in output if "Welcome" in line)
        assert welcome_count == 2

    def test_exit_message(self):
        app, output = make_app(["10 10", "2", "2"])
        app.run()
        assert any("Goodbye!" in line for line in output)


class TestValidation:
    def test_invalid_field_reprompts(self):
        app, output = make_app(["abc", "-1 5", "10 10", "2", "2"])
        app.run()

        invalid_count = sum(1 for line in output if "Invalid input" in line)
        assert invalid_count == 2

    def test_duplicate_name_rejected(self):
        app, output = make_app([
            "10 10",
            "1", "A", "1 2 N", "FF",
            "1", "A",  # duplicate
            "1", "B", "3 3 E", "FF",
            "2", "2",
        ])
        app.run()
        assert any("already exists" in line for line in output)

    def test_out_of_bounds_rejected(self):
        app, output = make_app([
            "5 5",
            "1", "A", "10 10 N",  # out of bounds
            "1", "A", "2 2 N", "FF",
            "2", "2",
        ])
        app.run()
        assert any("Invalid input" in line for line in output)

    def test_case_insensitive_direction(self):
        app, output = make_app([
            "10 10", "1", "A", "1 2 n", "ff", "2", "2",
        ])
        app.run()
        assert any("A, (1,4) N" in line for line in output)

    def test_duplicate_position_rejected(self):
        app, output = make_app([
            "10 10",
            "1", "A", "1 2 N", "FF",
            "1", "B", "1 2 E",  # same spot
            "1", "B", "3 3 E", "FF",
            "2", "2",
        ])
        app.run()
        assert any("already at that position" in line for line in output)
