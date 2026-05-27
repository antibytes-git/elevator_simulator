# System Design: Destination Dispatch Elevator Simulator

## 1. Overview
This document outlines the system architecture, core components, and data models for the discrete-time Destination Dispatch Elevator Simulator. The system aims to assign passengers to elevators immediately upon request, honoring constraints (capacity, direction) and optimizing for minimal wait and travel times.

## 2. Core Components

### 2.1 Configuration (`src/config.py`)
Loads and stores runtime parameters:
- `num_elevators`: Integer representing the total number of elevator cars.
- `num_floors`: Integer representing the total number of floors.
- `max_capacity`: Integer representing the maximum number of passengers an elevator can hold at one time.

### 2.2 Data Models (`src/models.py`)
- **Request**: Represents an incoming request (time_step, passenger_id, origin, destination).
- **Passenger**: Tracks passenger state, including their `id`, `origin`, `destination`, `assigned_elevator`, `spawn_time`, `pickup_time`, and `dropoff_time`.
- **Elevator**: Represents a single elevator car tracking its `id`, `current_floor`, `direction` (UP, DOWN, IDLE), `passengers_onboard`, and a queue of `target_floors`.

### 2.3 Simulation Engine (`src/simulator.py`)
The heart of the system. It runs a discrete time loop (tick = 1 floor movement):
1. **Increment Time**: Advances time by 1 unit.
2. **Read Requests**: Checks for any new `Request` objects corresponding to the current time tick.
3. **Dispatch**: Sends new requests to the `Scheduler`.
4. **Movement**: Moves all elevators one step toward their next target floor.
5. **Boarding/Alighting**: Loads waiting passengers and unloads arriving passengers if an elevator reaches a target floor.
6. **Log**: Triggers the `Logger` to record current state.
7. **Termination Condition**: Stops when all requests are fulfilled and all elevators are empty.

### 2.4 Scheduler Algorithm (`src/scheduler.py`)
Responsible for immediately assigning an incoming request to an elevator.

**Proposed Algorithm (Cost-based Minimum ETA):**
For each incoming request, the scheduler will compute a "cost" (Estimated Time of Arrival + Added delay for existing passengers) for each elevator.
- **Constraints**: If adding the passenger causes the elevator to exceed `max_capacity` on that route, apply a heavy penalty or invalidate.
- **Directional Logic**: Prioritize elevators that are moving in the direction of the passenger's origin and destination. 
- **Assignment**: The elevator with the lowest cost is immediately assigned the passenger. The passenger's origin and destination floors are injected into that elevator's route queue.

### 2.5 Logger & Metrics (`src/logger.py`, `src/stats.py`)
- **Logger**: Maintains a file handler. At the end of every tick, writes a formatted string detailing the `current_floor` of every elevator (e.g., `Tick 5: E1@Floor2, E2@Floor4`).
- **Stats Tracker**: Upon completion, analyzes all `Passenger` objects to compute minimum, maximum, and average values for:
  - **Wait Time**: `pickup_time - spawn_time`
  - **Travel Time**: `dropoff_time - pickup_time`
  - **Total Time**: `wait_time + travel_time`

## 3. Data Flow

1. **Initialization**: Load configuration and parse input file into a queue of `Request` objects.
2. **Tick loop begins** (Time = 0):
   - Extract requests matching the current tick.
   - For each request: Scheduler evaluates all elevators and assigns the best fit.
   - Elevators update their internal state (board/alight/move 1 floor).
   - State logged to output file.
3. **Completion**: Simulation ends when the request queue is empty and all elevators are idle.
4. **Reporting**: Pass terminal passenger data to Stats Tracker, print final aggregated metrics.

## 4. Assumptions & Trade-offs
- **Instant Boarding**: Boarding and alighting take 0 time ticks (or are abstracted into the travel time) to simplify discrete floor logic, unless requested otherwise.
- **Greedy Optimization**: The assignment is fixed once dispatched (destination dispatch constraint). The system cannot re-assign a passenger later if a better route opens up.
- **No Future Knowledge**: The scheduler only evaluates current and past state; it does not scan upcoming rows in the request file.