import heapq
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any

from src.config import Config
from src.models import Request, Elevator, Direction
from src.scheduler import Scheduler
from src.logger import Logger
from src.stats import StatsTracker


class EventType(Enum):
    PASSENGER_REQUEST = auto()
    ELEVATOR_ARRIVED = auto()
    DOORS_CLOSED = auto()


@dataclass(order=True)
class Event:
    timestamp: int
    # field(compare=False) ensures the heapq only sorts by timestamp
    event_type: EventType = field(compare=False)
    data: Any = field(compare=False)


class EventDrivenSimulator:
    def __init__(self, config: Config, requests: list[Request]):
        self.config = config
        self.time = 0
        self.event_queue = []
        
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

        # Pre-load all initial passenger requests into the event queue
        for req in requests:
            heapq.heappush(self.event_queue, Event(req.time_step, EventType.PASSENGER_REQUEST, req))

    def run(self):
        """Main Event Loop. Runs until the event queue is empty."""
        while self.event_queue:
            # 1. Jump forward in time to the next event
            event = heapq.heappop(self.event_queue)
            
            # Ensure time only moves forward
            assert event.timestamp >= self.time 
            self.time = event.timestamp
            
            # 2. Route to appropriate handler
            if event.event_type == EventType.PASSENGER_REQUEST:
                self._handle_passenger_request(event.data)
            elif event.event_type == EventType.ELEVATOR_ARRIVED:
                self._handle_elevator_arrived(event.data)
            elif event.event_type == EventType.DOORS_CLOSED:
                self._handle_doors_closed(event.data)
                
        # Simulation complete
        self.stats.calculate(self.completed_passengers, self.elevators, self.time)

    def _handle_passenger_request(self, req: Request):
        # Assign request using the scheduler
        passenger = self.scheduler.assign_request(req, self.time)
        self.waiting_passengers.append(passenger)
        
        elevator = self.elevators[passenger.assigned_elevator]
        
        # If the elevator is IDLE, we must kickstart its movement
        if elevator.direction == Direction.IDLE:
            self._schedule_next_movement(elevator)

    def _handle_elevator_arrived(self, elevator: Elevator):
        # Update state: The elevator has actually reached the floor
        elevator.current_floor = elevator.target_floors.pop(0) if elevator.target_floors else elevator.current_floor
        
        # ... Process passenger drop-offs and pick-ups ...
        # Calculate total boarding/alighting time
        delay = 0 
        # e.g., delay += num_passengers * self.config.action_time
        
        # Schedule the doors closing event
        heapq.heappush(
            self.event_queue, 
            Event(self.time + delay, EventType.DOORS_CLOSED, elevator)
        )

    def _handle_doors_closed(self, elevator: Elevator):
        # The elevator is ready to move again
        self._schedule_next_movement(elevator)

    def _schedule_next_movement(self, elevator: Elevator):
        """Calculates when the elevator will arrive at its next target and schedules it."""
        if not elevator.target_floors:
            elevator.direction = Direction.IDLE
            return
            
        next_target = elevator.target_floors[0]
        distance = abs(next_target - elevator.current_floor)
        
        # Assuming 1 tick per floor travel time
        arrival_time = self.time + distance 
        
        elevator.direction = Direction.UP if next_target > elevator.current_floor else Direction.DOWN
        heapq.heappush(self.event_queue, Event(arrival_time, EventType.ELEVATOR_ARRIVED, elevator))