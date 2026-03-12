import pytest
from sql_batch_resolver import BatchResolver


def make_resolver(prog_data, dep_data):
    r = BatchResolver(":memory:")
    r.create_tables()
    r.load_prog_names(prog_data)
    r.load_dependency_rules(dep_data)
    return r


class TestSetup:
    def test_create_tables(self):
        r = BatchResolver(":memory:")
        r.create_tables()
        tables = [row[0] for row in r.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )]
        assert "dependency_rules" in tables
        assert "prog_name" in tables

    def test_load_data(self):
        r = make_resolver(
            [(1, 1, "JOB_START"), (1, 2, "DELETE_SET")],
            [(1, 1, 1, 0), (1, 2, 2, 1)],
        )
        assert r.conn.execute("SELECT COUNT(*) FROM prog_name").fetchone()[0] == 2
        assert r.conn.execute("SELECT COUNT(*) FROM dependency_rules").fetchone()[0] == 2


class TestExecutionOrder:
    def test_single_step(self):
        r = make_resolver([(1, 1, "JOB_START")], [(1, 1, 1, 0)])
        result = r.resolve_order(1)
        assert result == [(1, 0, 1, "JOB_START")]

    def test_linear_chain(self):
        r = make_resolver(
            [(1, 1, "A"), (1, 2, "B"), (1, 3, "C")],
            [(1, 1, 1, 0), (1, 2, 2, 1), (1, 3, 3, 2)],
        )
        levels = [(row[1], row[3]) for row in r.resolve_order(1)]
        assert levels == [(0, "A"), (1, "B"), (2, "C")]

    def test_parallel_branches(self):
        r = make_resolver(
            [(1, 1, "ROOT"), (1, 2, "MID"), (1, 3, "LEFT"), (1, 4, "RIGHT")],
            [(1, 1, 1, 0), (1, 2, 2, 1), (1, 3, 3, 2), (1, 4, 4, 2)],
        )
        level_map = {row[3]: row[1] for row in r.resolve_order(1)}
        assert level_map["LEFT"] == level_map["RIGHT"] == 2

    def test_join_after_fork(self):
        r = make_resolver(
            [(1, 1, "S"), (1, 2, "F"), (1, 3, "L"), (1, 4, "R"), (1, 5, "J")],
            [(1, 1, 1, 0), (1, 2, 2, 1), (1, 3, 3, 2), (1, 4, 4, 2),
             (1, 5, 5, 3), (1, 6, 5, 4)],
        )
        level_map = {row[3]: row[1] for row in r.resolve_order(1)}
        assert level_map["J"] == 3

    def test_diamond_no_duplicates(self):
        r = make_resolver(
            [(1, 1, "TOP"), (1, 2, "L"), (1, 3, "R"), (1, 4, "BOT")],
            [(1, 1, 1, 0), (1, 2, 2, 1), (1, 3, 3, 1),
             (1, 4, 4, 2), (1, 5, 4, 3)],
        )
        result = r.resolve_order(1)
        bot_rows = [row for row in result if row[2] == 4]
        assert len(bot_rows) == 1
        assert bot_rows[0][1] == 2


class TestFullDataset:
    @pytest.fixture
    def resolver(self):
        return make_resolver(
            [
                (1, 1, "PKGIDS_CMMN_UTILITY.PROCIDS_JOB_START"),
                (1, 2, "pkgids_ptf_hrchy_processing.Procids_delete_job_set_nbr"),
                (1, 3, "PKGIDS_PTF_EXTR.ext_static_ptf_table"),
                (1, 4, "PKGIDS_PTF_EXTR.ext_eff_ptf_table"),
                (1, 5, "pkgids_ptf_hrchy_processing.procids_get_tree_a"),
                (1, 6, "pkgids_ptf_hrchy_processing.procids_get_tree_b"),
                (1, 7, "pkgids_ptf_hrchy_processing.procids_get_tree_c"),
                (1, 8, "pkgids_ptf_hrchy_processing.procids_get_tree_d"),
                (1, 9, "pkgids_ptf_hrchy_processing.procids_get_tree_e"),
                (1, 10, "pkgids_ptf_hrchy_processing.procids_get_active_portf"),
                (1, 11, "pkgids_ptf_lineage.procids_process_ptf_lineage"),
                (1, 12, "pkgids_ptf_lineage.procids_summary_to_bookable_rs"),
                (1, 13, "PKGIDS_CMMN_UTILITY.PROCIDS_JOB_END"),
            ],
            [
                (1, 1, 1, 0), (1, 2, 2, 1), (1, 3, 3, 2), (1, 4, 4, 2),
                (1, 5, 5, 3), (1, 6, 5, 4), (1, 7, 6, 3), (1, 8, 6, 4),
                (1, 9, 7, 3), (1, 10, 7, 4), (1, 11, 8, 3), (1, 12, 9, 3),
                (1, 13, 8, 4), (1, 14, 9, 4), (1, 15, 10, 5), (1, 16, 10, 6),
                (1, 17, 10, 7), (1, 18, 10, 8), (1, 19, 10, 9),
                (1, 20, 11, 10), (1, 21, 12, 11), (1, 22, 13, 12),
            ],
        )

    def test_first_and_last(self, resolver):
        result = resolver.resolve_order(1)
        assert result[0][3] == "PKGIDS_CMMN_UTILITY.PROCIDS_JOB_START"
        assert result[-1][3] == "PKGIDS_CMMN_UTILITY.PROCIDS_JOB_END"

    def test_parallel_groups(self, resolver):
        level_map = {r[2]: r[1] for r in resolver.resolve_order(1)}
        assert level_map[3] == level_map[4]
        assert len({level_map[i] for i in range(5, 10)}) == 1

    def test_step_10_after_trees(self, resolver):
        level_map = {r[2]: r[1] for r in resolver.resolve_order(1)}
        assert level_map[10] > max(level_map[i] for i in range(5, 10))

    def test_total_steps(self, resolver):
        assert len(resolver.resolve_order(1)) == 13

    def test_all_levels(self, resolver):
        level_map = {r[2]: r[1] for r in resolver.resolve_order(1)}
        assert level_map == {
            1: 0, 2: 1, 3: 2, 4: 2,
            5: 3, 6: 3, 7: 3, 8: 3, 9: 3,
            10: 4, 11: 5, 12: 6, 13: 7,
        }


class TestOutput:
    def test_shows_all_steps(self):
        r = make_resolver(
            [(1, 1, "START"), (1, 2, "MID"), (1, 3, "END")],
            [(1, 1, 1, 0), (1, 2, 2, 1), (1, 3, 3, 2)],
        )
        output = r.format_execution_plan(1)
        assert "START" in output and "MID" in output and "END" in output

    def test_has_header(self):
        r = make_resolver([(1, 1, "JOB")], [(1, 1, 1, 0)])
        output = r.format_execution_plan(1)
        assert "UNIT_NBR" in output
        assert "STEP_PROG_NAME" in output

    def test_empty_result(self):
        r = BatchResolver(":memory:")
        r.create_tables()
        assert r.format_execution_plan(999) == "No steps found."

    def test_parallel_grouped(self):
        r = make_resolver(
            [(1, 1, "ROOT"), (1, 2, "BRANCH_X"), (1, 3, "BRANCH_Y")],
            [(1, 1, 1, 0), (1, 2, 2, 1), (1, 3, 3, 1)],
        )
        lines = r.format_execution_plan(1).split("\n")
        assert len([l for l in lines if "BRANCH" in l]) == 2

    def test_unit_nbr_per_row(self):
        r = make_resolver([(1, 1, "START"), (1, 2, "END")], [(1, 1, 1, 0), (1, 2, 2, 1)])
        step_lines = [l for l in r.format_execution_plan(1).split("\n") if "START" in l or "END" in l]
        for line in step_lines:
            assert "1" in line


class TestEdgeCases:
    def test_nonexistent_unit(self):
        r = BatchResolver(":memory:")
        r.create_tables()
        assert r.resolve_order(999) == []

    def test_multiple_units(self):
        r = make_resolver(
            [(1, 1, "U1"), (2, 1, "U2")],
            [(1, 1, 1, 0), (2, 1, 1, 0)],
        )
        assert r.resolve_order(1)[0][3] == "U1"
        assert r.resolve_order(2)[0][3] == "U2"


class TestSqlQuery:
    def test_returns_valid_sql(self):
        sql = BatchResolver(":memory:").get_sql_query()
        assert "RECURSIVE" in sql
        assert "step_levels" in sql
        assert "max_levels" in sql


class TestExcelLoading:
    def test_loads_all_data(self):
        r = BatchResolver(":memory:")
        r.create_tables()
        r.load_from_excel("SQL_Test_1.xlsx")
        assert r.conn.execute("SELECT COUNT(*) FROM prog_name").fetchone()[0] == 13
        assert r.conn.execute("SELECT COUNT(*) FROM dependency_rules").fetchone()[0] == 22

    def test_end_to_end(self):
        r = BatchResolver(":memory:")
        r.create_tables()
        r.load_from_excel("SQL_Test_1.xlsx")
        result = r.resolve_order(1)
        assert len(result) == 13
        assert result[0][3] == "PKGIDS_CMMN_UTILITY.PROCIDS_JOB_START"
        assert result[-1][3] == "PKGIDS_CMMN_UTILITY.PROCIDS_JOB_END"
