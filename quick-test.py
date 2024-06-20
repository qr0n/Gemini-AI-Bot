import random

# Number of trials to demonstrate the 20% chance
trials = 1000000
condition_met_count = 0

for _ in range(trials):
    if random.random() == 0.20:
        condition_met_count += 1

print(f"The condition was met {condition_met_count} times out of {trials} trials.")
print(f"Approximate probability: {condition_met_count / trials * 100:.2f}%")