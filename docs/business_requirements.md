### Project Overview

Build a discrete-time Python simulation of an intelligent Destination Dispatch elevator system. In this system, passengers provide their origin and destination upfront, are assigned an elevator immediately, and cannot change their destination once assigned.

### Core Objectives

* **Serve Everyone:** Ensure all requests are served so no passenger waits indefinitely.
* **Optimize Time:** Minimize each passenger's total time, which is the sum of their wait time and travel time.
* **Enforce Constraints:** Honor real-world constraints such as elevator capacity and directional logic.
 
-- Implementation note: The scheduler now estimates ETA including onboard drop-offs so that even when elevators are momentarily full, assignments consider when capacity will free, preventing indefinite waiting.



### Technical Requirements

* **Time Mechanics:** Time runs in discrete units, where one unit equals traveling one floor. The simulation must tick forward one unit at a time without peeking ahead at future requests.
* **Configurability:** The model must allow you to configure the number of elevators, the number of floors, and the maximum passenger capacity per elevator.
* **Algorithm:** You must design and implement a custom scheduler algorithm that meets the project's objectives.



### Inputs and Outputs

* **Inputs:** The system must accept a list of requests containing the time step, a unique passenger ID, the origin floor, and the destination floor.
* **Logging:** Output a log file that records the locations of all elevators at every single time step, starting from zero.
* **Statistics:** Upon completion, the system must output minimum, maximum, and average wait and total times for the passengers.



### Deliverables

* **Codebase:** Submit a public GitHub repository containing your Python code.
* **Documentation:** Include a README.md detailing how to run the code, time spent on the project, assumptions and trade-offs made, and future improvements.