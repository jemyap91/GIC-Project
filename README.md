# GIC Project

## Auto Driving Car Simulation

An interactive CLI program that simulates autonomous cars moving on a grid field, with collision detection.

### How to run

```
python3 main.py
```

Follow the prompts to create a field, add cars with positions and commands (L/R/F), then run the simulation.

### How to run tests

```
python3 -m pytest
```

---

## SQL Batch Job Dependency Resolver

Resolves execution order for batch job stored procedures based on dependency rules, using a recursive SQL query (SQLite).

### How to run

```
python3 sql_batch_resolver.py
```

This reads `SQL_Test_1.xlsx` and prints the execution plan with steps grouped by level. Steps at the same level can run in parallel.

You can also pass a different Excel file:

```
python3 sql_batch_resolver.py path/to/file.xlsx
```

### Requirements

```
pip install openpyxl
```
