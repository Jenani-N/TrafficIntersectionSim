import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

#number of vechicles per min
arrivalRate = 10
serviceRate = 15

lanes = 2

#length of simulation (min)
simulationDuration = 120

#Pre-timed green and red light duration times (used for simulations)
schedule = [
    (50 / 60, 7 / 60),
    (30 / 60, 20 / 60),
    (40 / 60, 10 / 60),
    (50 / 60, 5 / 60),
    (50 / 60, 10 / 60),
]

#used to store metrics
results = []

#environment
class TrafficIntersection:
    def __init__(self, env, laneNume, service_rate):
        self.env = env
        self.lanes = simpy.Resource(env, laneNume)
        self.service_rate = service_rate
        self.queue_length = []
        self.queue = []

        #always starting with a green light
        self.is_green = True

    def serve_vehicle(self):
        service_time = random.expovariate(self.service_rate)
        yield self.env.timeout(service_time)


#controller to change the green and red light
def traffic_light_controller(env, intersection, greenLight, redLight):
    while True:
        intersection.is_green = True
        yield env.timeout(greenLight)
        intersection.is_green = False
        yield env.timeout(redLight)

#Event - vehicle arrival
def vehicle_generator(env, intersection, arrival_rate):
    while True:
        yield env.timeout(random.expovariate(arrival_rate))
        env.process(vehicle_process(env, intersection))

#processing each vehicle arrival
def vehicle_process(env, intersection):
    arrival_time = env.now
    intersection.queue.append(arrival_time)

    #Until the light is green
    while not intersection.is_green:
        yield env.timeout(0.1)

    #Continue when light is green and the lane is available
    with intersection.lanes.request() as request:
        yield request
        wait_time = env.now - arrival_time
        intersection.queue_length.append(len(intersection.queue))
        intersection.queue.pop(0)
        waitTime.append(wait_time)
        yield env.process(intersection.serve_vehicle())

#Simulation run (repeated 5 times for each pre-timed schedule defined)
for green, red in schedule:
    env = simpy.Environment()
    intersection = TrafficIntersection(env, lanes, serviceRate)
    waitTime = []

    env.process(vehicle_generator(env, intersection, arrivalRate))
    env.process(traffic_light_controller(env, intersection, green, red))
    env.run(until=simulationDuration)

    avg_wait = np.mean(waitTime) #getting average wait time of all vehicles
    queue_len = len(waitTime) / simulationDuration
    utilization = arrivalRate / (lanes * serviceRate)

    #collected data for each simulation (metrics)
    results.append({
        'green': green * 60,
        'red': red * 60,
        'avgWaitTime': avg_wait,
        'queue_length': queue_len,
        'vehicles': len(waitTime),
        'utilization': utilization
    })

#Getting the collected data (metrics) for graphs
green_times = [r['green'] for r in results]
avg_waits = [r['avgWaitTime'] for r in results]
queue_lengths = [r['queue_length'] for r in results]
vehicle_counts = [r['vehicles'] for r in results]


# ** Result Visuals (Graphs) **




# Average Wait Time Graph
plt.figure()
plt.plot(green_times, avg_waits, marker='o', color='blue')
plt.title('Average Wait Time vs Green Light Duration')
plt.xlabel('Green Light Duration (seconds)')
plt.ylabel('Average Wait Time (minutes)')
plt.grid(True)
plt.show()

# Queue Length Graph (vehicles per min)
plt.figure()
plt.plot(green_times, queue_lengths, marker='s', color='orange')
plt.title('Queue Length vs Green Light Duration')
plt.xlabel('Green Light Duration (seconds)')
plt.ylabel('Approximate Queue Length (vehicles)')
plt.grid(True)
plt.show()

# Overall Results (Avg Wait Time and Queue Length
fig, ax1 = plt.subplots()
ax1.set_xlabel('Green Light Duration (seconds)')
ax1.set_ylabel('Avg Wait Time (minutes)', color='tab:blue')
ax1.plot(green_times, avg_waits, marker='o', color='tab:blue')
ax1.tick_params(axis='y', labelcolor='tab:blue')

ax2 = ax1.twinx()
ax2.set_ylabel('Vehicles Processed', color='tab:green')
ax2.plot(green_times, vehicle_counts, marker='s', color='tab:green')
ax2.tick_params(axis='y', labelcolor='tab:green')

plt.title('Avg Wait Time & Vehicle Count vs Green Light Duration')
fig.tight_layout()
plt.grid(True)
plt.show()

#Getting the metrics associated with the lowest average wait time
optimal = min(results, key=lambda x: x['avgWaitTime'])

#Printing results
print("\nOptimal Traffic Light Schedule Based on Average Wait Time:")
print(f"Green Light: {optimal['green']}s")
print(f"Red Light: {optimal['red']}s")
print(f"Avg Wait Time: {optimal['avgWaitTime']:.2f} minutes")
print(f"Total Vehicles Processed: {optimal['vehicles']}")

