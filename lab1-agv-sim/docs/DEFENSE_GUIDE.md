# Defense Guide — INFO1167 Lab #1 Robótica

## 1. Problem statement (what the teacher asked)
- Simulate 4 AGV robots in a 2D QR-node warehouse.
- Random assignment + graph-based navigation.
- Pick cart, deliver cart, return to base, recharge, repeat.
- Explain algorithms and geometric movement.

## 2. How we solved it
- Warehouse = graph (`nodes = cells`, `edges = adjacency`).
- Routing = Dijkstra shortest path.
- Robot controller = finite-state machine.
- Rotation = 10° discrete heading updates before movement.
- Recharge = battery increases to 100% in charging state.

## 3. Show this live
```bash
python scripts/run_simulation.py --ticks 800 --seed 42
```
Then present:
- `outputs/summary.json`
- `outputs/snapshot.png`

## 4. Key technical points to mention
1. Deterministic simulation using seed.
2. Assignment and routing are decoupled.
3. State-machine guarantees full cycle compliance.
4. Graph algorithms included: Dijkstra (used), BFS/DFS (evidence).

## 5. Likely teacher questions

### Q: Why graph algorithms?
Because the assignment map is explicitly node-based (QR nodes), so shortest-path on a graph is the natural model.

### Q: Why Dijkstra and not only DFS?
DFS finds a path, not necessarily shortest. Dijkstra gives minimum-cost routes for non-negative edges.

### Q: How did you enforce rotation in steps?
Before moving to next node, robot computes desired heading and rotates by max 10° each tick until aligned.

### Q: How does cycle restart happen?
After delivery, robot returns to base, charges to 100%, then becomes available for a new random cart assignment.
