from cli import App


def make_app(inputs: list[str]) -> tuple[App, list[str]]:
    """Helper to create an App with mocked I/O."""
    input_iter = iter(inputs)
    output_lines: list[str] = []

    def mock_input(_prompt: str = "") -> str:
        return next(input_iter)

    def mock_print(*args: object) -> None:
        output_lines.append(" ".join(str(a) for a in args))

    app = App(input_fn=mock_input, output_fn=mock_print)
    return app, output_lines


def enter_steps(n: int) -> list[str]:
    """Generate n Enter key presses for visualization replay."""
    return [""] * n


class TestCLIFieldSetup:
    def test_welcome_message_and_field_creation(self):
        inputs = ["10 10", "2", "2"]  # create field, run (no cars), exit
        app, output = make_app(inputs)
        app.run()

        assert "Welcome to Auto Driving Car Simulation!" in output
        assert "You have created a field of 10 x 10." in output


class TestCLIAddCar:
    def test_add_single_car_and_exit(self):
        inputs = [
            "10 10",     # field dimensions
            "1",         # add car
            "A",         # car name
            "1 2 N",     # position
            "FFRFFFFRRL",  # commands (10 steps)
            "2",         # run simulation
            *enter_steps(10),  # Enter through 10 visualization steps
            "2",         # exit
        ]
        app, output = make_app(inputs)
        app.run()

        assert any("A, (1,2) N, FFRFFFFRRL" in line for line in output)
        assert any("A, (5,4) S" in line for line in output)


class TestCLISimulation:
    def test_scenario_1_single_car(self):
        inputs = [
            "10 10", "1", "A", "1 2 N", "FFRFFFFRRL",
            "2",  # run
            *enter_steps(10),  # 10 steps
            "2",  # exit
        ]
        app, output = make_app(inputs)
        app.run()

        assert any("A, (5,4) S" in line for line in output)

    def test_scenario_2_two_cars_collision(self):
        inputs = [
            "10 10",
            "1", "A", "1 2 N", "FFRFFFFRRL",
            "1", "B", "7 8 W", "FFLFFFFFFF",
            "2",  # run
            *enter_steps(10),  # max(10, 10) = 10 steps
            "2",  # exit
        ]
        app, output = make_app(inputs)
        app.run()

        assert any("A, collides with B at (5,4) at step 7" in line for line in output)
        assert any("B, collides with A at (5,4) at step 7" in line for line in output)

    def test_start_over(self):
        inputs = [
            "10 10",
            "1", "A", "1 2 N", "FF",
            "2",  # run
            *enter_steps(2),  # 2 steps
            "1",  # start over
            "5 5",  # new field
            "1", "B", "0 0 N", "F",
            "2",  # run
            *enter_steps(1),  # 1 step
            "2",  # exit
        ]
        app, output = make_app(inputs)
        app.run()

        welcome_count = sum(1 for line in output if "Welcome to Auto Driving Car Simulation!" in line)
        assert welcome_count == 2

    def test_exit_message(self):
        inputs = [
            "10 10",
            "2",  # run (no cars)
            "2",  # exit
        ]
        app, output = make_app(inputs)
        app.run()

        assert any("Thank you for running the simulation. Goodbye!" in line for line in output)


class TestCLIValidation:
    def test_invalid_field_dimensions_reprompts(self):
        inputs = [
            "abc",       # invalid
            "-1 5",      # invalid (negative)
            "10 10",     # valid
            "2",         # run
            "2",         # exit
        ]
        app, output = make_app(inputs)
        app.run()

        invalid_count = sum(1 for line in output if "Invalid input" in line)
        assert invalid_count == 2

    def test_duplicate_car_name_rejected(self):
        inputs = [
            "10 10",
            "1", "A", "1 2 N", "FF",
            "1", "A",  # duplicate name
            "1", "B", "3 3 E", "FF",  # valid second car
            "2",  # run
            *enter_steps(2),  # max(2, 2) = 2 steps
            "2",  # exit
        ]
        app, output = make_app(inputs)
        app.run()

        assert any("already exists" in line for line in output)

    def test_position_outside_field_rejected(self):
        inputs = [
            "5 5",
            "1", "A",
            "10 10 N",  # out of bounds
            "1", "A", "2 2 N", "FF",  # retry with valid
            "2",  # run
            *enter_steps(2),  # 2 steps
            "2",  # exit
        ]
        app, output = make_app(inputs)
        app.run()

        assert any("Invalid input" in line for line in output)

    def test_case_insensitive_direction(self):
        inputs = [
            "10 10",
            "1", "A", "1 2 n", "ff",  # lowercase
            "2",  # run
            *enter_steps(2),  # 2 steps
            "2",  # exit
        ]
        app, output = make_app(inputs)
        app.run()

        assert any("A, (1,4) N" in line for line in output)

    def test_duplicate_starting_position_rejected(self):
        inputs = [
            "10 10",
            "1", "A", "1 2 N", "FF",
            "1", "B", "1 2 E",  # same position as A
            "1", "B", "3 3 E", "FF",  # valid position
            "2",  # run
            *enter_steps(2),  # max(2, 2) = 2 steps
            "2",  # exit
        ]
        app, output = make_app(inputs)
        app.run()

        assert any("already at that position" in line for line in output)


class TestCLIVisualization:
    def test_simulation_shows_grid_steps(self):
        """Verify the grid is rendered during simulation."""
        inputs = [
            "10 10",
            "1", "A", "1 2 N", "FF",
            "2",   # run simulation
            "",    # Enter for step 1
            "",    # Enter for step 2 (simulation complete)
            "2",   # exit
        ]
        app, output = make_app(inputs)
        app.run()

        # Should see step indicators
        assert any("Step 1 of 2" in line for line in output)
        assert any("Step 2 of 2" in line for line in output)
        # Should see grid borders
        assert any(line.startswith("+") and line.endswith("+") for line in output)
        # Should still see final results
        assert any("A, (1,4) N" in line for line in output)

    def test_simulation_with_no_cars_skips_visualization(self):
        """No cars means no steps, so no visualization."""
        inputs = [
            "10 10",
            "2",  # run (no cars)
            "2",  # exit
        ]
        app, output = make_app(inputs)
        app.run()

        assert not any("Step" in line for line in output)
        assert any("Thank you for running the simulation. Goodbye!" in line for line in output)
