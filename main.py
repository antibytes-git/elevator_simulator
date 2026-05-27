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
    parser.add_argument('--num-elevators', '-e', type=int, default=3)
    parser.add_argument('--num-floors', '-f', type=int, default=10)
    parser.add_argument('--max-capacity', '-c', type=int, default=5)
    parser.add_argument('--log-file', '-l', default='elevator_log.jsonl', help='path to output log file')

    args = parser.parse_args()

    config = Config(num_elevators=args.num_elevators, num_floors=args.num_floors, max_capacity=args.max_capacity)
    requests = load_requests(args.input)

    print("Starting simulator...")
    simulator = Simulator(config, requests)
    # override logger path if requested
    simulator.logger = simulator.logger.__class__(filename=args.log_file)
    simulator.run()
    print(f"\nSimulation complete. Check {args.log_file} for step-by-step trace.")


if __name__ == "__main__":
    main()