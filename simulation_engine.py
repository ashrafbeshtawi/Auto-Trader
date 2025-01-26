import pandas as pd
from datetime import datetime
import os
import pickle

GENERATION_FILE = "generation.pkl"

class TradingEnvironment:
    def __init__(self, config):
        self.config = config
        self.dataset = None
        self.current_generation = 0
        self.population = []
        
        # Load existing generation or create new
        self.generation_path = os.path.join(config.save_dir, GENERATION_FILE)
        self.load_generation()

    def load_generation(self):
        """Load generation state if exists"""
        if os.path.exists(self.generation_path):
            print(f"Loading existing generation from {self.generation_path}")
            with open(self.generation_path, 'rb') as f:
                data = pickle.load(f)
                # Handle both list and dict formats for backward compatibility
                if isinstance(data, dict):
                    self.population = data['population']
                    self.current_generation = data['generation'] + 1
                else:  # Legacy list format
                    self.population = data[0]
                    self.current_generation = data[1] + 1
            print(f"Resuming from generation {self.current_generation - 1}")
        else:
            print("Creating new generation")
            self.current_generation = 0
            self.population = [f"Trader-{i}" for i in range(self.config.population)]

    def save_generation(self):
        """Save current generation state with proper dictionary format"""
        data = {
            'population': self.population,
            'generation': self.current_generation
        }
        with open(self.generation_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"Saved generation {self.current_generation} to {self.generation_path}")

    def load_dataset(self):
        """Load and validate the dataset"""
        try:
            # Load CSV with proper date parsing
            df = pd.read_csv(
                self.config.dataset_path,
                parse_dates=['Date'],
                dayfirst=False  # Change if using non-US date formats
            )
            
            # Convert string dates to datetime objects for filtering
            start_date = datetime.strptime(self.config.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(self.config.end_date, "%Y-%m-%d")
            
            # Filter and sort data
            self.dataset = df[
                (df['Date'] >= start_date) & 
                (df['Date'] <= end_date)
            ].sort_values('Date').reset_index(drop=True)
            
            # Validate required columns
            required_columns = {
                'Date', 'FearGreed_Scaled', 'Price_Float',
                'sin_month', 'cos_month', 'sin_doy', 'cos_doy',
                'sin_dow', 'cos_dow', 'Year_Scaled'
            }
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise ValueError(f"Missing columns: {missing}")
            
            print(f"Successfully loaded {len(self.dataset)} trading days")
            return True
            
        except Exception as e:
            print(f"Dataset loading failed: {str(e)}")
            return False

    def run(self):
        """Main simulation loop with periodic saving"""
        if not self.load_dataset():
            return

        try:
            while True:
                print(f"\n=== Generation {self.current_generation} ===")
                print(f"Traders: {len(self.population)}")
                
                # Simulate market days (mock)
                print(f"Processing {len(self.dataset)} trading days...")
                
                # Save if at interval
                if self.current_generation % self.config.gen_save_interval == 0:
                    self.save_generation()
                
                # Prepare next generation (mock)
                self.current_generation += 1
                print("Creating next generation...")

        except KeyboardInterrupt:
            print("\nSimulation interrupted - saving final state")
            self.save_generation()
            print("Exit")