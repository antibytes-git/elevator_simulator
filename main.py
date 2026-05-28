import argparse
import csv
from src.config import Config
from src.models import Request
from src.simulator import Simulator


def load_requests(filepath: str) -> list[Request]:
    requests = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                requests.append(Request(
                    time_step=int(row['time_step']),
                    passenger_id=int(row['passenger_id']),
                    origin=int(row['origin']),
                    destination=int(row['destination'])
                ))
            except Exception:
                # skip malformed rows
                continue
    return requests


def main():
    parser = argparse.ArgumentParser(description="Run the destination-dispatch elevator simulator")
    parser.add_argument('--input', '-i', default='data/requests.csv', help='path to requests CSV')
    parser.add_argument('--num-elevators', '-e', type=int, default=3, help='number of elevators')
    parser.add_argument('--num-floors', '-f', type=int, default=10, help='number of floors')
    parser.add_argument('--max-capacity', '-c', type=int, default=5, help='max capacity per elevator')
    parser.add_argument('--log-file', '-l', default='elevator_log.jsonl', help='path to output log file')
    parser.add_argument('--action-time', '-a', type=int, default=0, help='time cost per boarding/alighting action (seconds)')
    parser.add_argument('--scheduler', '-s', choices=['eta', 'scan'], default='eta', 
                        help='scheduling strategy: eta (smart) or scan (simple sweep)')

    args = parser.parse_args()

    config = Config(
        num_elevators=args.num_elevators, 
        num_floors=args.num_floors, 
        max_capacity=args.max_capacity,
        action_time=args.action_time,
        scheduler_strategy=args.scheduler
    )
    requests = load_requests(args.input)

    print("=" * 60)
    print("ELEVATOR SIMULATOR")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Elevators: {config.num_elevators}")
    print(f"  Floors: {config.num_floors}")
    print(f"  Max Capacity: {config.max_capacity}")
    print(f"  Action Time: {config.action_time}s per boarding/alighting")
    print(f"  Scheduler: {config.scheduler_strategy.upper()}")
    print(f"  Requests: {len(requests)}")
    print("=" * 60)
    print("Starting simulator...\n")
    
    simulator = Simulator(config, requests)
    # override logger path if requested
    simulator.logger = simulator.logger.__class__(filename=args.log_file)
    simulator.run()
    print(f"\nSimulation complete. Check {args.log_file} for step-by-step trace.")


if __name__ == "__main__":
    main()