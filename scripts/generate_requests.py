import csv
import random

# --- Configuration ---
NUM_REQUESTS = 100
NUM_FLOORS = 10
MAX_TIME_STEP = 50
OUTPUT_FILE = 'data/requests_large.csv'

def generate_requests():
    """Generates a list of random elevator requests."""
    requests = []

    # Example: Lobby-heavy traffic profile (weight floor 0 much higher)
    floor_weights = [10] + [1] * (NUM_FLOORS - 1)
    floors = list(range(NUM_FLOORS))
    
    current_time = 0
    for i in range(1, NUM_REQUESTS + 1):
        # Exponential distribution for realistic passenger arrival intervals (e.g., avg 5 ticks apart)
        current_time += int(random.expovariate(1.0 / 5.0))

        origin = random.choices(floors, weights=floor_weights, k=1)[0]
        destination = random.choices(floors, weights=floor_weights, k=1)[0]

        # Ensure origin and destination are not the same
        while origin == destination:
            destination = random.choices(floors, weights=floor_weights, k=1)[0]

        request = {
            'time_step': current_time,
            'passenger_id': i,
            'origin': origin,
            'destination': destination
        }
        requests.append(request)

    # Sort requests by time_step for a more realistic simulation sequence
    requests.sort(key=lambda r: r['time_step'])
    return requests

def write_to_csv(requests, filename):
    """Writes the generated requests to a CSV file."""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['time_step', 'passenger_id', 'origin', 'destination']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(requests)
    print(f"Successfully generated {len(requests)} requests in '{filename}'")

if __name__ == "__main__":
    print("Generating mock elevator request data...")
    generated_data = generate_requests()
    write_to_csv(generated_data, OUTPUT_FILE)