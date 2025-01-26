import csv
from datetime import datetime
import math

# Input and output file paths
input_csv = 'Bitcoin Merged.csv'
output_csv = 'Bitcoin Normalized.csv'

# Define min/max year for scaling (update based on your data)
min_year = 2020  # Replace with your data's minimum year
max_year = 2023  # Replace with your data's maximum year

def normalize_date(date_str):
    date = datetime.strptime(date_str, '%d %b, %Y')
    year = date.year
    month = date.month
    day = date.day
    day_of_year = date.timetuple().tm_yday
    day_of_week = date.weekday() + 1  # Monday=1, Sunday=7

    # Handle leap year day 366 (treat as 365)
    day_of_year = 365 if day_of_year == 366 else day_of_year

    # Cyclical encoding for month, day_of_year, day_of_week
    sin_month = math.sin(2 * math.pi * month / 12)
    cos_month = math.cos(2 * math.pi * month / 12)
    sin_doy = math.sin(2 * math.pi * day_of_year / 365)
    cos_doy = math.cos(2 * math.pi * day_of_year / 365)
    sin_dow = math.sin(2 * math.pi * day_of_week / 7)
    cos_dow = math.cos(2 * math.pi * day_of_week / 7)

    # Normalize year (min-max scaling)
    year_scaled = (year - min_year) / (max_year - min_year)

    return [
        year, month, day, day_of_year, day_of_week,
        sin_month, cos_month, sin_doy, cos_doy, sin_dow, cos_dow, year_scaled
    ]

# Read input CSV and write to output CSV
with open(input_csv, 'r') as infile, open(output_csv, 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = [
        # Original columns
        'Date', 'Fear_Greed', 'Price',
        # Normalized columns
        'Year', 'Month', 'Day', 'Day_of_Year', 'Day_of_Week',
        'sin_month', 'cos_month', 'sin_doy', 'cos_doy', 'sin_dow', 'cos_dow',
        'Year_Scaled', 'FearGreed_Scaled', 'Price_Float'
    ]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        # Extract and normalize date components
        date_norm = normalize_date(row['Date'])
        
        # Normalize Fear/Greed (divide by 100)
        fear_greed = float(row['Fear_Greed'])
        fear_greed_scaled = fear_greed / 100

        # Convert price to float
        price = float(row['Price'].replace(',', ''))

        # Write to output CSV
        writer.writerow({
            # Original values
            'Date': row['Date'],
            'Fear_Greed': row['Fear_Greed'],
            'Price': row['Price'],
            # Normalized values
            'Year': date_norm[0],
            'Month': date_norm[1],
            'Day': date_norm[2],
            'Day_of_Year': date_norm[3],
            'Day_of_Week': date_norm[4],
            'sin_month': date_norm[5],
            'cos_month': date_norm[6],
            'sin_doy': date_norm[7],
            'cos_doy': date_norm[8],
            'sin_dow': date_norm[9],
            'cos_dow': date_norm[10],
            'Year_Scaled': date_norm[11],
            'FearGreed_Scaled': fear_greed_scaled,
            'Price_Float': price
        })