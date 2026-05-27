import unittest
from src.config import Config
from src.models import Request
from src.simulator import Simulator

class TestSimulator(unittest.TestCase):
    def test_simulator_run_completes_passenger(self):
        config = Config(num_elevators=1, num_floors=10, max_capacity=5)
        requests = [
            Request(time_step=0, passenger_id=1, origin=0, destination=2)
        ]
        
        simulator = Simulator(config, requests)
        simulator.run()
        
        self.assertEqual(len(simulator.completed_passengers), 1)
        self.assertEqual(simulator.completed_passengers[0].pickup_time, 0)
        self.assertEqual(simulator.completed_passengers[0].dropoff_time, 2)

    def test_simulator_multiple_passengers_overlap(self):
        config = Config(num_elevators=1, num_floors=10, max_capacity=5)
        requests = [
            Request(time_step=0, passenger_id=1, origin=1, destination=5),
            Request(time_step=2, passenger_id=2, origin=3, destination=8)
        ]
        
        simulator = Simulator(config, requests)
        simulator.run()
        
        self.assertEqual(len(simulator.completed_passengers), 2)
        for p in simulator.completed_passengers:
            self.assertIsNotNone(p.dropoff_time)