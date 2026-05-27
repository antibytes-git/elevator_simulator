from src.models import Passenger

class StatsTracker:
    def calculate(self, passengers: list[Passenger]):
        if not passengers:
            print("No passengers served.")
            return

        wait_times = [p.pickup_time - p.spawn_time for p in passengers if p.pickup_time is not None]
        travel_times = [p.dropoff_time - p.pickup_time for p in passengers if p.dropoff_time is not None and p.pickup_time is not None]
        total_times = [p.dropoff_time - p.spawn_time for p in passengers if p.dropoff_time is not None and p.spawn_time is not None]

        def print_stats(name, data):
            if not data:
                return
            print(f"{name} Time - Min: {min(data)}, Max: {max(data)}, Avg: {sum(data)/len(data):.2f}")

        print("\n--- Simulation Statistics ---")
        print_stats("Wait", wait_times)
        print_stats("Travel", travel_times)
        print_stats("Total", total_times)