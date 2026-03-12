"""Tests for SQL batch job dependency resolver."""
import sqlite3
import pytest
from sql_batch_resolver import BatchResolver


class TestBatchResolverSetup:
    """Test database setup and data loading."""

    def test_create_tables(self):
        resolver = BatchResolver(":memory:")
        resolver.create_tables()
        conn = resolver.conn
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        assert "dependency_rules" in tables
        assert "prog_name" in tables

    def test_load_prog_name_data(self):
        resolver = BatchResolver(":memory:")
        resolver.create_tables()
        prog_data = [
            (1, 1, "JOB_START"),
            (1, 2, "DELETE_SET"),
        ]
        resolver.load_prog_names(prog_data)
        cursor = resolver.conn.execute("SELECT COUNT(*) FROM prog_name")
        assert cursor.fetchone()[0] == 2

    def test_load_dependency_rules(self):
        resolver = BatchResolver(":memory:")
        resolver.create_tables()
        dep_data = [
            (1, 1, 1, 0),
            (1, 2, 2, 1),
        ]
        resolver.load_dependency_rules(dep_data)
        cursor = resolver.conn.execute("SELECT COUNT(*) FROM dependency_rules")
        assert cursor.fetchone()[0] == 2


class TestExecutionOrder:
    """Test that steps are resolved in correct execution order."""

    def _make_resolver(self, prog_data, dep_data):
        resolver = BatchResolver(":memory:")
        resolver.create_tables()
        resolver.load_prog_names(prog_data)
        resolver.load_dependency_rules(dep_data)
        return resolver

    def test_single_step_no_dependency(self):
        """A single step with dep=0 should be at level 0."""
        resolver = self._make_resolver(
            prog_data=[(1, 1, "JOB_START")],
            dep_data=[(1, 1, 1, 0)],
        )
        result = resolver.resolve_order(unit_nbr=1)
        assert len(result) == 1
        assert result[0] == (1, 0, 1, "JOB_START")  # (unit, level, seq_id, name)

    def test_linear_chain(self):
        """Steps in a linear chain: 1->2->3."""
        resolver = self._make_resolver(
            prog_data=[
                (1, 1, "STEP_A"),
                (1, 2, "STEP_B"),
                (1, 3, "STEP_C"),
            ],
            dep_data=[
                (1, 1, 1, 0),
                (1, 2, 2, 1),
                (1, 3, 3, 2),
            ],
        )
        result = resolver.resolve_order(unit_nbr=1)
        levels = [(r[1], r[3]) for r in result]  # (level, name)
        assert levels == [(0, "STEP_A"), (1, "STEP_B"), (2, "STEP_C")]

    def test_parallel_steps(self):
        """Steps 3,4 both depend on 2 — should be at the same level."""
        resolver = self._make_resolver(
            prog_data=[
                (1, 1, "START"),
                (1, 2, "MIDDLE"),
                (1, 3, "BRANCH_A"),
                (1, 4, "BRANCH_B"),
            ],
            dep_data=[
                (1, 1, 1, 0),
                (1, 2, 2, 1),
                (1, 3, 3, 2),
                (1, 4, 4, 2),
            ],
        )
        result = resolver.resolve_order(unit_nbr=1)
        level_map = {r[3]: r[1] for r in result}
        assert level_map["BRANCH_A"] == level_map["BRANCH_B"]
        assert level_map["BRANCH_A"] == 2

    def test_join_after_parallel(self):
        """Step 5 depends on both 3 AND 4 — level = max(3,4) + 1."""
        resolver = self._make_resolver(
            prog_data=[
                (1, 1, "START"),
                (1, 2, "FORK"),
                (1, 3, "BRANCH_A"),
                (1, 4, "BRANCH_B"),
                (1, 5, "JOIN"),
            ],
            dep_data=[
                (1, 1, 1, 0),
                (1, 2, 2, 1),
                (1, 3, 3, 2),
                (1, 4, 4, 2),
                (1, 5, 5, 3),
                (1, 6, 5, 4),
            ],
        )
        result = resolver.resolve_order(unit_nbr=1)
        level_map = {r[3]: r[1] for r in result}
        assert level_map["JOIN"] == 3  # max(2,2) + 1


class TestFullDataset:
    """Test with the actual dataset from the Excel file."""

    @pytest.fixture
    def resolver(self):
        resolver = BatchResolver(":memory:")
        resolver.create_tables()
        resolver.load_prog_names([
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
        ])
        resolver.load_dependency_rules([
            (1, 1, 1, 0),
            (1, 2, 2, 1),
            (1, 3, 3, 2),
            (1, 4, 4, 2),
            (1, 5, 5, 3),
            (1, 6, 5, 4),
            (1, 7, 6, 3),
            (1, 8, 6, 4),
            (1, 9, 7, 3),
            (1, 10, 7, 4),
            (1, 11, 8, 3),
            (1, 12, 9, 3),
            (1, 13, 8, 4),
            (1, 14, 9, 4),
            (1, 15, 10, 5),
            (1, 16, 10, 6),
            (1, 17, 10, 7),
            (1, 18, 10, 8),
            (1, 19, 10, 9),
            (1, 20, 11, 10),
            (1, 21, 12, 11),
            (1, 22, 13, 12),
        ])
        return resolver

    def test_step_1_is_first(self, resolver):
        result = resolver.resolve_order(unit_nbr=1)
        assert result[0][3] == "PKGIDS_CMMN_UTILITY.PROCIDS_JOB_START"
        assert result[0][1] == 0  # level 0

    def test_step_13_is_last(self, resolver):
        result = resolver.resolve_order(unit_nbr=1)
        assert result[-1][3] == "PKGIDS_CMMN_UTILITY.PROCIDS_JOB_END"

    def test_steps_3_4_are_parallel(self, resolver):
        result = resolver.resolve_order(unit_nbr=1)
        level_map = {r[2]: r[1] for r in result}  # seq_id -> level
        assert level_map[3] == level_map[4]

    def test_steps_5_through_9_are_parallel(self, resolver):
        result = resolver.resolve_order(unit_nbr=1)
        level_map = {r[2]: r[1] for r in result}  # seq_id -> level
        levels_5_to_9 = {level_map[i] for i in range(5, 10)}
        assert len(levels_5_to_9) == 1  # all same level

    def test_step_10_after_5_through_9(self, resolver):
        result = resolver.resolve_order(unit_nbr=1)
        level_map = {r[2]: r[1] for r in result}
        assert level_map[10] > level_map[5]
        assert level_map[10] > level_map[9]

    def test_total_steps(self, resolver):
        result = resolver.resolve_order(unit_nbr=1)
        assert len(result) == 13

    def test_all_levels_correct(self, resolver):
        """Verify the complete level assignment for all 13 steps."""
        result = resolver.resolve_order(unit_nbr=1)
        level_map = {r[2]: r[1] for r in result}  # seq_id -> level
        expected = {
            1: 0,   # root
            2: 1,   # depends on 1
            3: 2,   # depends on 2
            4: 2,   # depends on 2
            5: 3,   # depends on 3,4
            6: 3,   # depends on 3,4
            7: 3,   # depends on 3,4
            8: 3,   # depends on 3,4
            9: 3,   # depends on 3,4
            10: 4,  # depends on 5,6,7,8,9
            11: 5,  # depends on 10
            12: 6,  # depends on 11
            13: 7,  # depends on 12
        }
        assert level_map == expected


class TestFormattedOutput:
    """Test the formatted output showing execution sequence."""

    def test_format_output_shows_levels(self):
        resolver = BatchResolver(":memory:")
        resolver.create_tables()
        resolver.load_prog_names([
            (1, 1, "START"),
            (1, 2, "MIDDLE"),
            (1, 3, "END"),
        ])
        resolver.load_dependency_rules([
            (1, 1, 1, 0),
            (1, 2, 2, 1),
            (1, 3, 3, 2),
        ])
        output = resolver.format_execution_plan(unit_nbr=1)
        assert "START" in output
        assert "MIDDLE" in output
        assert "END" in output

    def test_format_output_groups_parallel_steps(self):
        resolver = BatchResolver(":memory:")
        resolver.create_tables()
        resolver.load_prog_names([
            (1, 1, "START"),
            (1, 2, "BRANCH_A"),
            (1, 3, "BRANCH_B"),
        ])
        resolver.load_dependency_rules([
            (1, 1, 1, 0),
            (1, 2, 2, 1),
            (1, 3, 3, 1),
        ])
        output = resolver.format_execution_plan(unit_nbr=1)
        # Both branches should appear at the same level in output
        lines = output.strip().split("\n")
        branch_lines = [l for l in lines if "BRANCH" in l]
        assert len(branch_lines) == 2

    def test_format_output_includes_unit_nbr_per_row(self):
        """Each output row should show UNIT_NBR and STEP_PROG_NAME."""
        resolver = BatchResolver(":memory:")
        resolver.create_tables()
        resolver.load_prog_names([
            (1, 1, "START"),
            (1, 2, "END"),
        ])
        resolver.load_dependency_rules([
            (1, 1, 1, 0),
            (1, 2, 2, 1),
        ])
        output = resolver.format_execution_plan(unit_nbr=1)
        # Every step line should contain the unit_nbr
        step_lines = [l for l in output.split("\n") if "START" in l or "END" in l]
        for line in step_lines:
            assert "1" in line

    def test_format_output_has_header_row(self):
        """Output should have a header showing column names."""
        resolver = BatchResolver(":memory:")
        resolver.create_tables()
        resolver.load_prog_names([(1, 1, "JOB")])
        resolver.load_dependency_rules([(1, 1, 1, 0)])
        output = resolver.format_execution_plan(unit_nbr=1)
        assert "UNIT_NBR" in output
        assert "STEP_PROG_NAME" in output


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_nonexistent_unit_returns_empty(self):
        resolver = BatchResolver(":memory:")
        resolver.create_tables()
        result = resolver.resolve_order(unit_nbr=999)
        assert result == []

    def test_format_empty_result(self):
        resolver = BatchResolver(":memory:")
        resolver.create_tables()
        output = resolver.format_execution_plan(unit_nbr=999)
        assert output == "No steps found."

    def test_diamond_dependency(self):
        """Diamond: 1 -> 2,3 -> 4. Step 4 should be level 2, not duplicated."""
        resolver = BatchResolver(":memory:")
        resolver.create_tables()
        resolver.load_prog_names([
            (1, 1, "ROOT"),
            (1, 2, "LEFT"),
            (1, 3, "RIGHT"),
            (1, 4, "BOTTOM"),
        ])
        resolver.load_dependency_rules([
            (1, 1, 1, 0),
            (1, 2, 2, 1),
            (1, 3, 3, 1),
            (1, 4, 4, 2),
            (1, 5, 4, 3),
        ])
        result = resolver.resolve_order(unit_nbr=1)
        # Step 4 should appear exactly once
        step_4_rows = [r for r in result if r[2] == 4]
        assert len(step_4_rows) == 1
        assert step_4_rows[0][1] == 2  # level = max(1,1) + 1

    def test_multiple_unit_nbrs(self):
        """Each unit_nbr is resolved independently."""
        resolver = BatchResolver(":memory:")
        resolver.create_tables()
        resolver.load_prog_names([
            (1, 1, "UNIT1_STEP"),
            (2, 1, "UNIT2_STEP"),
        ])
        resolver.load_dependency_rules([
            (1, 1, 1, 0),
            (2, 1, 1, 0),
        ])
        result1 = resolver.resolve_order(unit_nbr=1)
        result2 = resolver.resolve_order(unit_nbr=2)
        assert len(result1) == 1
        assert result1[0][3] == "UNIT1_STEP"
        assert len(result2) == 1
        assert result2[0][3] == "UNIT2_STEP"


class TestGetSqlQuery:
    """Test that the raw SQL query is accessible."""

    def test_get_sql_query_returns_string(self):
        resolver = BatchResolver(":memory:")
        sql = resolver.get_sql_query()
        assert isinstance(sql, str)
        assert "recursive" in sql.lower() or "RECURSIVE" in sql

    def test_get_sql_query_contains_key_clauses(self):
        resolver = BatchResolver(":memory:")
        sql = resolver.get_sql_query()
        assert "step_levels" in sql.lower()
        assert "max_levels" in sql.lower()
        assert "JOIN" in sql


class TestLoadFromExcel:
    """Test loading data directly from the Excel file."""

    def test_load_from_xlsx(self):
        resolver = BatchResolver(":memory:")
        resolver.create_tables()
        resolver.load_from_excel("SQL_Test_1.xlsx")
        cursor = resolver.conn.execute("SELECT COUNT(*) FROM prog_name")
        assert cursor.fetchone()[0] == 13
        cursor = resolver.conn.execute("SELECT COUNT(*) FROM dependency_rules")
        assert cursor.fetchone()[0] == 22

    def test_end_to_end_from_excel(self):
        """Full integration: load from Excel, resolve, format."""
        resolver = BatchResolver(":memory:")
        resolver.create_tables()
        resolver.load_from_excel("SQL_Test_1.xlsx")
        result = resolver.resolve_order(unit_nbr=1)
        assert len(result) == 13
        assert result[0][3] == "PKGIDS_CMMN_UTILITY.PROCIDS_JOB_START"
        assert result[-1][3] == "PKGIDS_CMMN_UTILITY.PROCIDS_JOB_END"
        output = resolver.format_execution_plan(unit_nbr=1)
        assert "PKGIDS_CMMN_UTILITY.PROCIDS_JOB_START" in output
        assert "PKGIDS_CMMN_UTILITY.PROCIDS_JOB_END" in output
        assert "UNIT_NBR" in output
