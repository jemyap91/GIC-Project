# Auto Driving Car Simulation — Assumptions & Notes

## Assumptions

1. **Coordinate System:** (0,0) is the bottom-left corner. x increases to the right, y increases upward.
2. **Field Bounds:** A field of width W and height H has valid coordinates from (0,0) to (W-1, H-1), as per the spec example where a 10x10 field has upper-right at (9,9).
3. **Unique Car Names:** Each car must have a unique name. Duplicate names are rejected.
4. **No Overlapping Start Positions:** Two cars cannot start at the same position.
5. **Case-Insensitive Input:** Directions (N/S/E/W) and commands (L/R/F) accept both upper and lower case.
6. **Sequential Processing Order:** Cars process commands in the order they were added to the simulation.
7. **Empty Commands:** A car with empty commands stays at its initial position for the entire simulation but can still be collided into.
8. **Collision with Stopped Cars:** A car that has already collided remains at its collision position. Other cars can still collide with it.
9. **Sequential Pass-Through:** Because cars process commands sequentially within each step (not simultaneously), two cars can "pass through" each other if they swap positions in the same step. This is a consequence of sequential processing, not simultaneous movement.

## How to Run

```bash
python main.py
```

## How to Run Tests

```bash
python -m pytest -v
```

## Identified Improvements

- Visual grid rendering in the terminal to show car positions
- Save/load simulation configurations from files
- Undo/replay functionality for stepping through simulation
- Support for obstacles or terrain on the field
- Support for more than two cars colliding at the same position simultaneously
