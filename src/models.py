from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Direction(Enum):
    UP = 1
    DOWN = -1
    IDLE = 0


@dataclass
class Request:
    time_step: int
    passenger_id: int
    origin: int
    destination: int


@dataclass
class Passenger:
    id: int
    origin: int
    destination: int
    spawn_time: int
    assigned_elevator: Optional[int] = None
    pickup_time: Optional[int] = None
    dropoff_time: Optional[int] = None


@dataclass
class Elevator:
    id: int
    current_floor: int = 0
    direction: Direction = Direction.IDLE
    passengers_onboard: List[Passenger] = field(default_factory=list)
    target_floors: List[int] = field(default_factory=list)