# Robotica Lab #1 AGV Simulation — Execution Plan

## Objective
Deliver a production-ready Python project that satisfies the full lab requirements:
- Simulate 4 AGV robots on a 2D node map.
- Assign carts and destinations.
- Route robots with graph algorithms.
- Implement orientation/rotation step behavior.
- Deliver carts, return to base, recharge to 100%, repeat cycle.
- Provide strong docs + defense-ready explanation.

## Deliverables
1. `src/agv_sim/` robust simulation package (engine, models, graph algorithms, scheduler, metrics).
2. `scripts/run_simulation.py` CLI runner with reproducible seeds.
3. `tests/` automated tests for routing, assignment, state transitions, and cycle completion.
4. `docs/research/AGV_Project_Research.pdf` polished research and implementation rationale.
5. `README.md` and `docs/DEFENSE_GUIDE.md` for teacher presentation.
6. Public GitHub repository with clean structure and setup instructions.

## Quality gates
- Deterministic runs with configurable random seed.
- No linter/test failures.
- Assignment rules mapped line-by-line into implementation checklist.
- Reproducible command to run simulation and generate outputs.

## Build order
1) Extract requirements from original PDF.
2) Draft technical design and data model.
3) Implement core simulator.
4) Add visualization + reporting outputs.
5) Add tests and run validation.
6) Build research PDF + defense notes.
7) Initialize and push public repo.
