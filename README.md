# Destination Dispatch Elevator Simulator

Enterprise-focused, configurable destination-dispatch elevator simulator.

This repository implements a discrete-time simulator where passengers supply origin and destination up-front and are immediately assigned an elevator (destination dispatch). 

## Quickstart

1. Create a virtual environment and install dev dependencies (optional):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the simulator with CLI options:

```bash
python main.py --input data/requests.csv --num-elevators 3 --num-floors 10 --max-capacity 5 --log-file elevator_log.jsonl
```

3. The simulator writes a structured JSONL trace to the log file and prints summary statistics to stdout.

## Notable Improvements

- Models are implemented with `dataclasses` for clearer state and typing.
- Scheduler estimates ETA including onboard drop-offs so full elevators are still considered in assignment decisions (reduces starvation risk).
- Multiple elevator banks are supported via configurable `--num-elevators`, allowing the simulator to dispatch requests across a fleet rather than a single car.
- Tie-breaker heuristics prefer less-loaded elevators when cost estimates are equal, which prevents one elevator from monopolizing same-floor requests and improves multi-elevator utilization.
- Structured JSONL logging via Python `logging` for traceability and downstream analysis.
- CLI for configurable runs and log path override.
- Basic request validation to drop malformed rows.
- Expanded regression tests for same-floor waiting and multi-elevator capacity scenarios.

## Testing

Run unit tests with:

```bash
PYTHONPATH=./ python -m unittest discover -s tests -p 'test_*.py'
```

## Design Notes

- The scheduler uses a cost estimate (ETA + travel time + simple directional penalty) and simulates current elevator targets to estimate when capacity frees up. This keeps the system compatible with the destination-dispatch requirement (assign immediately) while ensuring assignments are realistic and avoid unbounded waiting.
- Multi-elevator support is implemented by maintaining separate elevator state and assigning each request to the best elevator based on estimated delivery cost and fewer pending targets.
- Time advances in discrete units; one unit equals moving one floor.

## Alternative Elevator Scheduling Algorithms

This simulator currently uses destination-dispatch assignment with a LOOK-style elevator stop ordering strategy. Other viable elevator algorithms include:

- Nearest-car / collective control: Assign the closest available elevator to a hall call, with elevators stopping for pick-ups on their current path.
- Zoned control: Divide a building into floor ranges and dedicate elevator banks to each zone to reduce travel time for high-rise traffic.
- Traffic-based scheduling: Use peak/off-peak traffic patterns to group up/down calls or express cars for lobby-to-upper floors.
- Group supervision: Manage multiple elevators together to balance load, minimize waiting time, and reduce unnecessary travel.
- Predictive or machine learning dispatch: Use historical or real-time data to forecast demand and pre-position cars.
- Fairness-driven strategies: Employ oldest-request-first or starvation-avoidance heuristics for more equitable service.
- Genetic or optimization-based dispatch: Use integer programming, simulated annealing, or genetic algorithms to optimize assignments over a horizon.

## Next Steps & Enterprise Ideas

- Add CI (GitHub Actions) to run tests and linters.
- Add metrics export (Prometheus) and HTTP endpoints for live requests.
- Add Dockerfile and packaging via `pyproject.toml`/`poetry`.
- Introduce Strategy Pattern for dispatcher algorithms to easily swap scheduling logic via CLI.
- Improve simulation realism by accounting for door open/close durations, boarding delays, and acceleration kinematics.
- Implement fault injection (e.g., simulating elevator breakdowns, maintenance modes, or overweight scenarios).
- Add data visualization tools (e.g., a CLI animation or timeline chart generator) to better observe simulator behavior.
