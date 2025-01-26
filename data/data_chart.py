import csv
from datetime import datetime
import matplotlib.pyplot as plt

# Define input CSV file
input_file = "Bitcoin Complete.csv"

# Initialize lists to store data
date_numbers = []
prices = []
fear_greed = []

# Read the CSV file
with open(input_file, mode="r") as file:
    reader = csv.DictReader(file)
    for idx, row in enumerate(reader, start=1):
        # Replace date with sequential numbers
        date_numbers.append(idx)

        # Convert price to float (removing commas)
        price = float(row["Price"].replace(",", ""))
        prices.append(price)

        # Append Fear/Greed index
        fear_greed.append(int(row["Fear/Greed"]))

# Plot Price over Time
plt.figure(figsize=(10, 5))
plt.plot(date_numbers, prices, marker="o", label="Price", color="blue")
plt.xlabel("Time (Sequential Number)")
plt.ylabel("Price (USD)")
plt.title("Price over Time")
plt.legend()
plt.tight_layout()
plt.show()

# Plot Fear/Greed Index over Time
plt.figure(figsize=(10, 5))
plt.plot(date_numbers, fear_greed, marker="o", label="Fear/Greed Index", color="green")
plt.xlabel("Time (Sequential Number)")
plt.ylabel("Fear/Greed Index")
plt.title("Fear/Greed Index over Time")
plt.legend()
plt.tight_layout()
plt.show()
