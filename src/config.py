class Config:
    def __init__(
        self, 
        num_elevators: int = 3, 
        num_floors: int = 10, 
        max_capacity: int = 5,
        action_time: int = 0,
        scheduler_strategy: str = "eta"
    ):
        """Initialize simulator configuration.
        
        Args:
            num_elevators: Number of elevators in the system
            num_floors: Total number of floors in the building
            max_capacity: Maximum passengers per elevator
            action_time: Time cost for each boarding/alighting action (seconds)
                        e.g., door open/close delays
            scheduler_strategy: Scheduling algorithm to use ("eta", "scan")
                              - "eta": ETA-based smart scheduling (default)
                              - "scan": Simple sweep algorithm
        """
        self.num_elevators = num_elevators
        self.num_floors = num_floors
        self.max_capacity = max_capacity
        self.action_time = action_time
        self.scheduler_strategy = scheduler_strategy