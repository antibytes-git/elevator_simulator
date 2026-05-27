import json
import logging
from typing import List

from src.models import Elevator


class Logger:
    """Structured logger writing per-tick state as JSON lines to a file.

    This wrapper provides a consistent output format for downstream analysis
    while remaining configurable via standard logging settings.
    """

    def __init__(self, filename: str = "elevator_log.jsonl", level: int = logging.INFO):
        self.filename = filename
        self.logger = logging.getLogger("elevator_simulator")
        self.logger.propagate = False
        # prevent duplicate handlers during tests/reloads
        if not self.logger.handlers:
            handler = logging.FileHandler(self.filename, mode="w")
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)
        self.logger.setLevel(level)

        # header
        header = {"type": "header", "message": "Elevator Simulator Log"}
        self.logger.info(json.dumps(header))

    def log_tick(self, tick: int, elevators: List[Elevator]):
        state = {
            "type": "tick",
            "tick": tick,
            "elevators": [
                {
                    "id": e.id,
                    "current_floor": e.current_floor,
                    "direction": e.direction.name,
                    "passengers": [p.id for p in e.passengers_onboard],
                    "target_floors": list(e.target_floors),
                }
                for e in elevators
            ],
        }
        line = json.dumps(state)
        self.logger.info(line)