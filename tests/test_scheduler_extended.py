import unittest
from src.models import Elevator, Request
from src.scheduler import Scheduler


class TestSchedulerExtended(unittest.TestCase):
    def test_assign_when_elevators_full_estimates_space(self):
        elevators = [Elevator(0), Elevator(1)]
        # elevator 0 is full
        elevators[0].passengers_onboard.append(type('P', (), {'destination': 5, 'id': 999}))
        elevators[0].passengers_onboard.append(type('P', (), {'destination': 6, 'id': 1000}))

        scheduler = Scheduler(elevators, max_capacity=2, num_floors=10)

        # request at floor 2 should be assigned to whichever elevator frees space earlier
        req = Request(time_step=0, passenger_id=1, origin=2, destination=8)
        passenger = scheduler.assign_request(req, current_time=0)

        self.assertIn(passenger.assigned_elevator, (0, 1))

    def test_assign_same_floor_to_less_loaded_elevator(self):
        elevators = [Elevator(0), Elevator(1)]
        elevators[0].target_floors.append(0)

        scheduler = Scheduler(elevators, max_capacity=1, num_floors=10)
        req = Request(time_step=0, passenger_id=1, origin=0, destination=2)

        passenger = scheduler.assign_request(req, current_time=0)
        self.assertEqual(passenger.assigned_elevator, 1)


if __name__ == '__main__':
    unittest.main()
