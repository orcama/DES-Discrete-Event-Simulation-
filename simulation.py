import random
import numpy as np
import matplotlib.pyplot as plt
import simpy

# Simulation Parameters
RANDOM_SEED = 42
NUM_TELLERS = 3  # Modified number of tellers
ARRIVAL_RATE = 8  # Modified arrival rate to simulate peak hours
SERVICE_RATE = 7
SIM_TIME = 20

# Store waiting times and teller utilization
wait_times = []
teller_busy_time = []

teller_usage = {i: [] for i in range(NUM_TELLERS)}  # Track utilization over time

class BankQueueSimulation:
    def __init__(self, env, num_tellers, service_rate):
        self.env = env
        self.teller = simpy.PriorityResource(env, num_tellers)  # Priority queue for VIP customers
        self.service_rate = service_rate
        self.teller_busy = [0] * num_tellers  # Track individual teller usage
    
    def serve_customer(self, customer_id, teller_id):
        service_time = random.expovariate(self.service_rate)
        self.teller_busy[teller_id] += service_time
        teller_usage[teller_id].append((self.env.now, self.teller_busy[teller_id]))
        yield self.env.timeout(service_time)
        print(f"Customer {customer_id} finished service at {self.env.now:.2f} min.")

def customer_process(env, customer_id, bank, priority):
    arrival_time = env.now
    print(f"Customer {customer_id} (Priority {priority}) arrives at {arrival_time:.2f} min.")
    
    with bank.teller.request(priority=priority) as request:
        yield request  # Wait for an available teller
        wait_time = env.now - arrival_time
        wait_times.append(wait_time)

        print(f"Customer {customer_id} starts service after waiting {wait_time:.2f} min.")
        teller_id = random.randint(0, NUM_TELLERS - 1)
        yield env.process(bank.serve_customer(customer_id, teller_id))

def customer_arrivals(env, bank, arrival_rate):
    customer_id = 0
    while True:
        yield env.timeout(random.expovariate(arrival_rate))  # Time until next arrival
        customer_id += 1
        priority = 0 if random.random() < 0.2 else 1  # 20% chance of VIP customer
        env.process(customer_process(env, customer_id, bank, priority))

# Run Simulation
random.seed(RANDOM_SEED)
env = simpy.Environment()
bank = BankQueueSimulation(env, NUM_TELLERS, SERVICE_RATE)
env.process(customer_arrivals(env, bank, ARRIVAL_RATE))
env.run(until=SIM_TIME)

# Performance Analysis
print("\n=== Simulation Summary ===")
print(f"Average Wait Time: {np.mean(wait_times):.2f} minutes")

# Visualization
fig, axes = plt.subplots(2, 1, figsize=(10, 8))

# Histogram of Waiting Times
axes[0].hist(wait_times, bins=10, color='blue', alpha=0.7, label="Waiting Time Distribution")
axes[0].set_xlabel("Waiting Time (minutes)")
axes[0].set_ylabel("Number of Customers")
axes[0].set_title("Customer Waiting Time Distribution")
axes[0].legend()

# Teller Utilization Over Time
for teller_id, usage in teller_usage.items():
    times, busy_times = zip(*usage) if usage else ([], [])
    axes[1].plot(times, busy_times, label=f'Teller {teller_id}', linestyle='dashed')
axes[1].set_xlabel("Time (minutes)")
axes[1].set_ylabel("Busy Time (minutes)")
axes[1].set_title("Teller Utilization Over Time")
axes[1].legend()

plt.tight_layout()
plt.show()
