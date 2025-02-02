import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from trader import Trader

# Constants
GENERATION_FILE = "generation.pkl"

class TradingEnvironment:
    def __init__(self, config):
        self.config = config
        self.dataset = None
        self.current_generation = 0
        self.population = []
        self.load_initial_generation()
        
    def load_initial_generation(self):
        """Load existing generation or create new population"""
        gen_path = os.path.join(self.config.save_dir, GENERATION_FILE)
        
        if os.path.exists(gen_path):
            print(f"Loading existing generation from {gen_path}")
            with open(gen_path, 'rb') as f:
                data = pickle.load(f)
                self.population = [Trader.deserialize(t) for t in data['traders']]
                self.current_generation = data['generation']
        else:
            print("Creating initial generation...")
            self.population = [Trader() for _ in range(self.config.population)]
            self.save_generation()

    def load_dataset(self):
        """Load and filter dataset"""
        try:
            df = pd.read_csv(self.config.dataset_path, parse_dates=['Date'])
            start_date = pd.to_datetime(self.config.start_date)
            end_date = pd.to_datetime(self.config.end_date)
            
            self.dataset = df[
                (df['Date'] >= start_date) & 
                (df['Date'] <= end_date)
            ].sort_values('Date').reset_index(drop=True)
            
            print(f"Loaded {len(self.dataset)} trading days")
            return True
        except Exception as e:
            print(f"Dataset error: {str(e)}")
            return False

    def run_generation(self):
        """Simulate one complete generation"""
        # Reset trader states
        for trader in self.population:
            trader.fiat_balance = 1000.0
            trader.btc_balance = 0.0
            trader.total_wealth = 1000.0
            trader.trade_history = []

        # Daily trading simulation
        for _, row in self.dataset.iterrows():
            price = row['Price_Float']
            features = {
                'sin_month': row['sin_month'],
                'cos_month': row['cos_month'],
                'sin_doy': row['sin_doy'],
                'cos_doy': row['cos_doy'],
                'sin_dow': row['sin_dow'],
                'cos_dow': row['cos_dow'],
                'year_scaled': row['Year_Scaled'],
                'fear_greed': row['FearGreed_Scaled']
            }

            for trader in self.population:
                action = trader.decide(features)
                trader.execute_trade(action, price)

        # Finalize by selling all BTC
        final_price = self.dataset.iloc[-1]['Price_Float']
        for trader in self.population:
            trader.sell_all(final_price)

    def evaluate_and_evolve(self):
        """Perform genetic algorithm operations"""
        # Sort by performance
        self.population.sort(key=lambda x: x.total_wealth, reverse=True)
        
        # Select survivors
        num_survivors = int(len(self.population) * self.config.survival_rate)
        survivors = self.population[:num_survivors]
        
        # Create new generation
        new_population = []
        while len(new_population) < self.config.population:
            parent = np.random.choice(survivors)
            child = self.clone_and_mutate(parent)
            new_population.append(child)

        self.population = new_population
        self.current_generation += 1

    def clone_and_mutate(self, parent):
        """Create mutated copy of a trader"""
        child = Trader.deserialize(parent.serialize())
        
        # Mutate neural network
        mutation_rate = 0.3 - (0.2 * (self.current_generation / 100))
        child.network.mutate(
            mutation_rate=min(0.5, mutation_rate),
            mutation_scale=0.2
        )
        return child

    def save_generation(self):
        """Save current generation state using constant"""
        data = {
            'traders': [t.serialize() for t in self.population],
            'generation': self.current_generation
        }
        
        os.makedirs(self.config.save_dir, exist_ok=True)
        gen_path = os.path.join(self.config.save_dir, GENERATION_FILE)
        
        with open(gen_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"Saved generation {self.current_generation} to {gen_path}")

    def run(self):
        """Main simulation loop"""
        if not self.load_dataset():
            return

        try:
            while True:
                print(f"\n=== Generation {self.current_generation} ===")
                
                # Run trading simulation
                self.run_generation()
                
                # Show performance stats
                wealths = [t.total_wealth for t in self.population]
                print(f"Best: ${max(wealths):.2f}")
                print(f"Average: ${np.mean(wealths):.2f}")
                print(f"Worst: ${min(wealths):.2f}")

                # Evolve population
                self.evaluate_and_evolve()
                
                # Save progress
                if self.current_generation % self.config.gen_save_interval == 0:
                    self.save_generation()

        except KeyboardInterrupt:
            self.save_generation()
            print("\nSimulation stopped. Current generation saved.")