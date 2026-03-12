import sqlite3


RESOLVE_QUERY = """
WITH RECURSIVE step_levels AS (
    -- Root steps have no dependency (dep_id = 0)
    SELECT d.unit_nbr, d.step_seq_id, 0 AS exec_level
    FROM dependency_rules d
    WHERE d.unit_nbr = ? AND d.step_dep_id = 0

    UNION ALL

    -- Each step's level = parent's level + 1
    SELECT d.unit_nbr, d.step_seq_id, sl.exec_level + 1
    FROM dependency_rules d
    JOIN step_levels sl
      ON d.step_dep_id = sl.step_seq_id AND d.unit_nbr = sl.unit_nbr
    WHERE d.step_dep_id != 0
),
-- Take the MAX level across all paths to handle multiple dependencies
max_levels AS (
    SELECT unit_nbr, step_seq_id, MAX(exec_level) AS exec_level
    FROM step_levels
    GROUP BY unit_nbr, step_seq_id
)
SELECT ml.unit_nbr, ml.exec_level, ml.step_seq_id, p.step_prog_name
FROM max_levels ml
JOIN prog_name p ON ml.unit_nbr = p.unit_nbr AND ml.step_seq_id = p.step_seq_id
ORDER BY ml.exec_level, ml.step_seq_id
"""


class BatchResolver:

    def __init__(self, db_path=":memory:"):
        self.conn = sqlite3.connect(db_path)

    def create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS prog_name (
                unit_nbr INTEGER NOT NULL,
                step_seq_id INTEGER NOT NULL,
                step_prog_name TEXT NOT NULL,
                PRIMARY KEY (unit_nbr, step_seq_id)
            );
            CREATE TABLE IF NOT EXISTS dependency_rules (
                unit_nbr INTEGER NOT NULL,
                rule_id INTEGER NOT NULL,
                step_seq_id INTEGER NOT NULL,
                step_dep_id INTEGER NOT NULL,
                PRIMARY KEY (unit_nbr, rule_id)
            );
        """)

    def load_prog_names(self, data):
        self.conn.executemany("INSERT INTO prog_name VALUES (?, ?, ?)", data)
        self.conn.commit()

    def load_dependency_rules(self, data):
        self.conn.executemany("INSERT INTO dependency_rules VALUES (?, ?, ?, ?)", data)
        self.conn.commit()

    def load_from_excel(self, filepath):
        import openpyxl
        wb = openpyxl.load_workbook(filepath)

        prog_data = [
            (row[0], row[1], row[2])
            for row in wb["PROG_NAME"].iter_rows(min_row=2, values_only=True)
            if row[0] is not None
        ]
        self.load_prog_names(prog_data)

        dep_data = [
            (row[0], row[1], row[2], row[3])
            for row in wb["DEPENDENCY_RULES"].iter_rows(min_row=2, values_only=True)
            if row[0] is not None
        ]
        self.load_dependency_rules(dep_data)

    def get_sql_query(self):
        return RESOLVE_QUERY

    def resolve_order(self, unit_nbr):
        return self.conn.execute(RESOLVE_QUERY, (unit_nbr,)).fetchall()

    def format_execution_plan(self, unit_nbr):
        results = self.resolve_order(unit_nbr)
        if not results:
            return "No steps found."

        lines = []
        lines.append(f"{'UNIT_NBR':<12}{'STEP_SEQ_ID':<14}{'STEP_PROG_NAME':<55}{'EXEC_LEVEL'}")
        lines.append("-" * 95)

        prev_level = -1
        for unit, level, seq_id, prog_name in results:
            if level != prev_level:
                if prev_level != -1:
                    lines.append("")
                prev_level = level
            lines.append(f"{unit:<12}{seq_id:<14}{prog_name:<55}{level}")

        return "\n".join(lines)


if __name__ == "__main__":
    import sys

    filepath = sys.argv[1] if len(sys.argv) > 1 else "SQL_Test_1.xlsx"
    resolver = BatchResolver()
    resolver.create_tables()
    resolver.load_from_excel(filepath)

    units = resolver.conn.execute(
        "SELECT DISTINCT unit_nbr FROM prog_name ORDER BY unit_nbr"
    ).fetchall()

    for (unit_nbr,) in units:
        print(resolver.format_execution_plan(unit_nbr))
        print()

    print("=== SQL Query ===")
    print(resolver.get_sql_query())
