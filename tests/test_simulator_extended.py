import unittest
from src.config import Config
from src.models import Request
from src.simulator import Simulator


class TestSimulatorExtended(unittest.TestCase):
    def test_no_starvation_multiple_requests_single_elevator(self):
        # single elevator with capacity 1, two simultaneous requests
        config = Config(num_elevators=1, num_floors=10, max_capacity=1)
        requests = [
            Request(time_step=0, passenger_id=1, origin=0, destination=2),
            Request(time_step=0, passenger_id=2, origin=0, destination=3),
        ]

        sim = Simulator(config, requests)
        sim.run()

        # both passengers should be completed and have finite pickup times
        self.assertEqual(len(sim.completed_passengers), 2)
        pickups = [p.pickup_time for p in sim.completed_passengers]
        self.assertTrue(all(p is not None for p in pickups))

    def test_same_floor_capacity_regression(self):
        # ensure same-floor waiting passenger is served after the first passenger boards
        config = Config(num_elevators=1, num_floors=10, max_capacity=1)
        requests = [
            Request(time_step=0, passenger_id=1, origin=0, destination=2),
            Request(time_step=0, passenger_id=2, origin=0, destination=3),
        ]

        sim = Simulator(config, requests)
        sim.run()

        self.assertEqual(len(sim.completed_passengers), 2)
        self.assertEqual(sorted([p.id for p in sim.completed_passengers]), [1, 2])
        self.assertNotEqual(sim.completed_passengers[0].pickup_time, sim.completed_passengers[1].pickup_time)

    def test_multiple_elevators_handle_same_origin_requests(self):
        config = Config(num_elevators=2, num_floors=10, max_capacity=1)
        requests = [
            Request(time_step=0, passenger_id=1, origin=0, destination=2),
            Request(time_step=0, passenger_id=2, origin=0, destination=3),
        ]

        sim = Simulator(config, requests)
        sim.run()

        self.assertEqual(len(sim.completed_passengers), 2)
        assigned_elevators = {p.assigned_elevator for p in sim.completed_passengers}
        self.assertEqual(assigned_elevators, {0, 1})


if __name__ == '__main__':
    unittest.main()
