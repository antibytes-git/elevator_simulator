from typing import List

from src.models import Request, Passenger, Elevator, Direction


class Scheduler:
    def __init__(self, elevators: List[Elevator], max_capacity: int, num_floors: int = 10):
        self.elevators = elevators
        self.max_capacity = max_capacity
        self.num_floors = num_floors

    def assign_request(self, request: Request, current_time: int) -> Passenger:
        """Assign a passenger to the elevator with the minimum estimated cost.

        This uses an ETA estimator that accounts for current target stops and
        onboard passenger drop-offs so that full elevators are still considered
        based on when they'll have capacity, reducing the chance of unbounded
        waiting.
        """
        best_elevator = None
        min_cost = float("inf")

        for elevator in self.elevators:
            cost = self._calculate_eta_cost(elevator, request)
            if cost < min_cost or (
                cost == min_cost and self._prefer_elevator(elevator, best_elevator)
            ):
                min_cost = cost
                best_elevator = elevator

        # always assign (destination-dispatch constraint)
        passenger = Passenger(request.passenger_id, request.origin, request.destination, current_time)
        passenger.assigned_elevator = best_elevator.id

        self._insert_target_floors(best_elevator, request.origin)

        return passenger

    def _calculate_eta_cost(self, elevator: Elevator, request: Request) -> float:
        """Estimate time until passenger would be delivered if assigned to elevator.

        The estimate includes:
        - time until elevator reaches the origin (simulating current target queue)
        - travel time from origin to destination
        - directional penalties to prefer elevators already heading in the request direction
        """
        eta_to_origin = self._estimate_time_to_origin(elevator, request)
        travel = abs(request.origin - request.destination)

        # directional preference
        req_dir = Direction.UP if request.destination > request.origin else Direction.DOWN
        penalty = 0
        if elevator.direction != Direction.IDLE and elevator.direction != req_dir:
            penalty += self.num_floors * 0.5

        return eta_to_origin + travel + penalty

    def _estimate_time_to_origin(self, elevator: Elevator, request: Request) -> float:
        """Rudimentary simulation of elevator following its current target_floors
        and counting time until it would reach the request.origin and have
        available capacity. This prevents assigning only non-full elevators
        and helps avoid starvation by considering when space frees up.
        """
        pos = elevator.current_floor
        time = 0
        # copy state we can mutate
        targets = list(elevator.target_floors)
        onboard_dests = [p.destination for p in elevator.passengers_onboard]
        onboard_count = len(onboard_dests)

        # If no targets, just go straight to origin
        if not targets:
            return abs(pos - request.origin)

        # simulate moving through targets in order
        for t in targets:
            time += abs(pos - t)
            pos = t
            # if any onboard passenger has destination == t, they drop off
            drop_count = sum(1 for d in onboard_dests if d == t)
            if drop_count:
                onboard_count = max(0, onboard_count - drop_count)
            # if we've reached the origin during the simulated path
            if pos == request.origin:
                if onboard_count < self.max_capacity:
                    return time
                # otherwise continue; maybe space frees later

        # after finishing existing targets, go to origin
        time += abs(pos - request.origin)
        return time

    def _prefer_elevator(self, candidate: Elevator, current: Elevator) -> bool:
        if current is None:
            return True

        if len(candidate.target_floors) != len(current.target_floors):
            return len(candidate.target_floors) < len(current.target_floors)

        if len(candidate.passengers_onboard) != len(current.passengers_onboard):
            return len(candidate.passengers_onboard) < len(current.passengers_onboard)

        return candidate.id < current.id

    def _insert_target_floors(self, elevator: Elevator, floor: int):
        # add a pickup or dropoff stop.
        if floor not in elevator.target_floors:
            elevator.target_floors.append(floor)

        # reorder according to direction (LOOK-style sweep).
        if elevator.direction == Direction.UP or (
            elevator.direction == Direction.IDLE and elevator.target_floors and elevator.target_floors[0] >= elevator.current_floor
        ):
            up_stops = sorted([f for f in elevator.target_floors if f > elevator.current_floor])
            down_stops = sorted([f for f in elevator.target_floors if f <= elevator.current_floor], reverse=True)
            elevator.target_floors = up_stops + down_stops
        else:
            down_stops = sorted([f for f in elevator.target_floors if f < elevator.current_floor], reverse=True)
            up_stops = sorted([f for f in elevator.target_floors if f >= elevator.current_floor])
            elevator.target_floors = down_stops + up_stops