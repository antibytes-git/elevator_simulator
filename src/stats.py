import statistics
from typing import List
from src.models import Passenger


class StatsTracker:
    def __init__(self):
        self.metrics = {}

    def calculate(self, passengers: list[Passenger], elevators=None, num_ticks=None):
        """Calculate comprehensive statistics from completed passengers and elevator state.
        
        Args:
            passengers: List of completed Passenger objects with pickup/dropoff times
            elevators: List of Elevator objects (optional, for utilization metrics)
            num_ticks: Total simulation ticks (optional, for idle time calculation)
        """
        if not passengers:
            print("No passengers served.")
            return

        # Time-based metrics
        wait_times = [p.pickup_time - p.spawn_time for p in passengers if p.pickup_time is not None]
        travel_times = [p.dropoff_time - p.pickup_time for p in passengers if p.dropoff_time is not None and p.pickup_time is not None]
        total_times = [p.dropoff_time - p.spawn_time for p in passengers if p.dropoff_time is not None and p.spawn_time is not None]

        # Calculate detailed statistics for each metric
        def calc_stats(name: str, data: List[int]) -> dict:
            if not data:
                return None
            stats_dict = {
                "count": len(data),
                "min": min(data),
                "max": max(data),
                "avg": sum(data) / len(data),
                "median": statistics.median(data),
                "p25": statistics.quantiles(data, n=4)[0] if len(data) > 1 else data[0],
                "p75": statistics.quantiles(data, n=4)[2] if len(data) > 1 else data[0],
                "p95": statistics.quantiles(data, n=20)[18] if len(data) > 1 else data[0],
            }
            return stats_dict

        self.metrics["wait_time"] = calc_stats("Wait", wait_times)
        self.metrics["travel_time"] = calc_stats("Travel", travel_times)
        self.metrics["total_time"] = calc_stats("Total", total_times)

        # Service level metrics
        self.metrics["service_levels"] = self._calculate_service_levels(total_times)
        
        # Elevator utilization metrics (if elevators provided)
        if elevators:
            self.metrics["elevator_utilization"] = self._calculate_elevator_utilization(elevators, num_ticks)

        self._print_comprehensive_report()

    def _calculate_service_levels(self, total_times: List[int]) -> dict:
        """Calculate percentage of passengers served within target times."""
        if not total_times:
            return {}
        
        targets = {30: "within 30 seconds", 60: "within 1 minute", 120: "within 2 minutes"}
        service_levels = {}
        
        for threshold, label in targets.items():
            count = sum(1 for t in total_times if t <= threshold)
            percentage = (count / len(total_times)) * 100
            service_levels[label] = f"{percentage:.1f}%"
        
        return service_levels

    def _calculate_elevator_utilization(self, elevators, num_ticks: int) -> dict:
        """Calculate elevator utilization metrics."""
        if not elevators or not num_ticks or num_ticks == 0:
            return {}
        
        utilization = {}
        for elevator in elevators:
            # Count ticks when elevator had passengers
            # Note: This would need to be tracked during simulation for accurate calculation
            utilization[f"elevator_{elevator.id}"] = {
                "current_floor": elevator.current_floor,
                "passengers_onboard": len(elevator.passengers_onboard),
                "target_stops": len(elevator.target_floors),
            }
        
        return utilization

    def _print_comprehensive_report(self):
        """Print detailed statistics report with formatting similar to SampleCode.txt"""
        print("\n" + "=" * 60)
        print("SIMULATION STATISTICS REPORT")
        print("=" * 60)

        # Wait Time Metrics
        print("\n📊 WAIT TIME METRICS (Time from button press to pickup)")
        print("-" * 60)
        self._print_metric_section(self.metrics.get("wait_time"))

        # Travel Time Metrics
        print("\n📊 TRAVEL TIME METRICS (Time from pickup to destination)")
        print("-" * 60)
        self._print_metric_section(self.metrics.get("travel_time"))

        # Total Time Metrics
        print("\n📊 TOTAL TIME METRICS (Time from button press to destination)")
        print("-" * 60)
        self._print_metric_section(self.metrics.get("total_time"))

        # Service Levels
        if self.metrics.get("service_levels"):
            print("\n📈 SERVICE LEVEL METRICS")
            print("-" * 60)
            for label, percentage in self.metrics["service_levels"].items():
                print(f"  Passengers {label}: {percentage}")

        # Elevator Utilization
        if self.metrics.get("elevator_utilization"):
            print("\n⚙️  ELEVATOR STATUS")
            print("-" * 60)
            for elev_id, status in self.metrics["elevator_utilization"].items():
                print(f"  {elev_id}:")
                print(f"    Current Floor: {status['current_floor']}")
                print(f"    Passengers Onboard: {status['passengers_onboard']}")
                print(f"    Target Stops: {status['target_stops']}")

        print("\n" + "=" * 60)

    def _print_metric_section(self, stats_dict: dict):
        """Print a single metric section with all statistics."""
        if not stats_dict:
            print("  No data available")
            return

        print(f"  Count: {stats_dict['count']}")
        print(f"  Min: {stats_dict['min']:.1f}")
        print(f"  Max: {stats_dict['max']:.1f}")
        print(f"  Average: {stats_dict['avg']:.2f}")
        print(f"  Median (50th percentile): {stats_dict['median']:.2f}")
        print(f"  25th Percentile: {stats_dict['p25']:.2f}")
        print(f"  75th Percentile: {stats_dict['p75']:.2f}")
        print(f"  95th Percentile: {stats_dict['p95']:.2f}")