from src.config import Config
from src.models import Request, Elevator, Direction
from src.scheduler import Scheduler
from src.logger import Logger
from src.stats import StatsTracker


class Simulator:
    def __init__(self, config: Config, requests: list[Request]):
        self.config = config
        self.requests = requests
        self.time = 0
        self.elevators = [Elevator(i) for i in range(config.num_elevators)]
        self.scheduler = Scheduler(
            self.elevators, 
            config.max_capacity, 
            config.num_floors,
            strategy=config.scheduler_strategy
        )
        self.logger = Logger()
        self.stats = StatsTracker()
        self.waiting_passengers = []
        self.completed_passengers = []
        self.action_time = 0  # Current action delay (door open/close)
        
        # Track elevator utilization over time
        self.elevator_occupancy_history = []

    def _is_valid_request(self, r: Request) -> bool:
        if r.origin < 0 or r.origin >= self.config.num_floors:
            return False
        if r.destination < 0 or r.destination >= self.config.num_floors:
            return False
        if r.origin == r.destination:
            return False
        return True

    def step(self) -> bool:
        """Perform a single simulation tick. Returns True if there is more work to do."""
        # Reset action time at start of each step
        self.action_time = 0
        
        # 1. Read Requests
        current_requests = [r for r in self.requests if r.time_step == self.time]
        self.requests = [r for r in self.requests if r.time_step > self.time]

        # 2. Validate & Dispatch
        for req in current_requests:
            if not self._is_valid_request(req):
                # skip malformed requests but keep running
                continue
            passenger = self.scheduler.assign_request(req, self.time)
            self.waiting_passengers.append(passenger)

        # 3 & 4. Boarding/Alighting & Movement
        for elevator in self.elevators:
            # Passengers getting off
            arrived = [p for p in list(elevator.passengers_onboard) if p.destination == elevator.current_floor]
            for p in arrived:
                p.dropoff_time = self.time
                elevator.passengers_onboard.remove(p)
                self.completed_passengers.append(p)
                # Each passenger drop-off takes action_time
                self.action_time += self.config.action_time

            # Passengers getting on
            boarding = [p for p in list(self.waiting_passengers) if p.assigned_elevator == elevator.id and p.origin == elevator.current_floor]
            for p in boarding:
                if len(elevator.passengers_onboard) < self.config.max_capacity:
                    p.pickup_time = self.time
                    self.waiting_passengers.remove(p)
                    elevator.passengers_onboard.append(p)
                    self.scheduler._insert_target_floors(elevator, p.destination)
                    # Each passenger boarding takes action_time
                    self.action_time += self.config.action_time

            # remove the current stop once passengers intending to board/alight have been processed
            if elevator.target_floors and elevator.target_floors[0] == elevator.current_floor:
                elevator.target_floors.pop(0)

            # ensure any waiting passengers assigned to this elevator have their origin present
            for p in list(self.waiting_passengers):
                if p.assigned_elevator == elevator.id and p.origin not in elevator.target_floors:
                    self.scheduler._insert_target_floors(elevator, p.origin)

            # find next target that is not the current floor
            next_target = None
            for t in elevator.target_floors:
                if t != elevator.current_floor:
                    next_target = t
                    break

            if next_target is not None:
                elevator.direction = Direction.UP if next_target > elevator.current_floor else Direction.DOWN
                elevator.current_floor += elevator.direction.value
            else:
                elevator.direction = Direction.IDLE

        # Track elevator occupancy for utilization metrics
        total_occupancy = sum(len(e.passengers_onboard) for e in self.elevators)
        self.elevator_occupancy_history.append(total_occupancy)

        self.logger.log_tick(self.time, self.elevators)
        self.time += 1

        return bool(self.requests or self.waiting_passengers or any(e.target_floors for e in self.elevators) or any(e.passengers_onboard for e in self.elevators))

    def run(self):
        while self.step():
            pass

        self.stats.calculate(self.completed_passengers, self.elevators, self.time)