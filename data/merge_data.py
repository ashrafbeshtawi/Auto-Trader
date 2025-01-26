import csv
from datetime import datetime

# Define file names
file1 = "Bitcoin Price.csv"
file2 = "Bitcoin Fear Gread.csv"
output_file = "Bitcoin Merged.csv"

# Read data from the first file
data1 = {}
with open(file1, mode="r",encoding="utf-8-sig") as f1:
    reader = csv.DictReader(f1)
    for row in reader:
        # Use the date as the key and store the price
        data1[row["Date"]] = row["Price"]



# Open the second file and match the dates
with open(file2, mode="r") as f2, open(output_file, mode="w", newline="") as out:
    reader = csv.DictReader(f2)
    writer = csv.writer(out)
    # Write the header
    writer.writerow(["Date", "Price", "Fear_Greed"])

    for row in reader:
        date = row["Date"]
        date_object = datetime.strptime(date, "%d %b, %Y")
        formatted_date = date_object.strftime("%m/%d/%Y")
        if formatted_date in data1:
            # Write the matching date, price from file1, and value from file2
            writer.writerow([date, data1[formatted_date], row["Value"]])

print(f"Data successfully merged into {output_file}")
