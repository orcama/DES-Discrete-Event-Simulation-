import simpy
import random
import matplotlib.pyplot as plt
import numpy as np

RANDOM_SEED = 42
NUM_TELLERS = 3  # Jumlah teller
SIM_TIME = 10  # Waktu simulasi dalam menit
ARRIVAL_RATE = 0.5  # Rata-rata waktu antar kedatangan pelanggan
VIP_PROB = 0.2  # Peluang pelanggan VIP

time_waiting = []  
server_utilization = []  
time_points = []  

class Bank:
    def __init__(self, env, num_tellers):
        self.env = env
        self.teller = simpy.PriorityResource(env, capacity=num_tellers)
    
    def serve(self, customer_id):
        service_time = random.uniform(0.1, 0.3)  # Durasi layanan acak
        yield self.env.timeout(service_time)
        return service_time

def customer(env, name, bank, arrival_time, is_vip):
    global time_waiting
    arrival = env.now
    priority = 0 if is_vip else 1  # VIP memiliki prioritas lebih tinggi
    
    with bank.teller.request(priority=priority) as request:
        yield request  
        wait_time = env.now - arrival
        time_waiting.append(wait_time)
        print(f"{name} starts service after waiting {wait_time:.2f} min.")
        yield env.process(bank.serve(name))
        print(f"{name} finished service at {env.now:.2f} min.")

def generate_customers(env, bank):
    customer_id = 1
    while env.now < SIM_TIME:
        inter_arrival = random.expovariate(1.0 / ARRIVAL_RATE)
        yield env.timeout(inter_arrival)
        is_vip = random.random() < VIP_PROB
        env.process(customer(env, f"Customer {customer_id}", bank, env.now, is_vip))
        customer_id += 1

def monitor_utilization(env, bank):
    while True:
        utilization = len(bank.teller.queue) / NUM_TELLERS
        server_utilization.append(utilization)
        time_points.append(env.now)
        yield env.timeout(0.1)  # Update setiap 0.1 menit

def run_simulation():
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    bank = Bank(env, NUM_TELLERS)
    env.process(generate_customers(env, bank))
    env.process(monitor_utilization(env, bank))
    env.run(until=SIM_TIME)

    # Visualisasi hasil
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.hist(time_waiting, bins=10, edgecolor='black')
    plt.xlabel("Waiting Time (min)")
    plt.ylabel("Number of Customers")
    plt.title("Histogram of Waiting Times")

    plt.subplot(1, 2, 2)
    plt.plot(time_points, server_utilization, label="Teller Utilization")
    plt.xlabel("Time (min)")
    plt.ylabel("Utilization")
    plt.title("Teller Utilization Over Time")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    run_simulation()
