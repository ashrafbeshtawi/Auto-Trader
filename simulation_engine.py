import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from trader import Trader
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Constants
GENERATION_FILE = "generation.pkl"

class TradingEnvironment:
    def __init__(self, config):
        self.config = config
        self.dataset = None
        self.current_generation = 0
        self.population = []
        self.best_trader_history = []
        self.load_initial_generation()
        self.setup_visualization()

    def setup_visualization(self):
        """Initialize interactive plot"""
        plt.ion()  # Turn on interactive mode
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.price_line, = self.ax.plot([], [], label='Price', color='#1f77b4')
        self.buy_scatter = self.ax.scatter([], [], c='green', label='Buys')
        self.sell_scatter = self.ax.scatter([], [], c='red', label='Sells')
        
        self.ax.set_title('Best Trader Actions - Generation 0')
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('Price (USD)')
        self.ax.legend()
        plt.tight_layout()

    def update_visualization(self):
        """Update plot with latest best trader data"""
        if not self.best_trader_history:
            return

        # Get latest best trader
        best_trader = self.best_trader_history[-1]
        # Extract trade data
        dates = [t['date'] for t in best_trader.trade_history]
        prices = [t['price'] for t in best_trader.trade_history]
        actions = [t['action'] for t in best_trader.trade_history]


        # Convert dates to matplotlib format
        dates = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
        
        # Update plot data
        self.price_line.set_data(dates, prices)
        self.ax.relim()
        self.ax.autoscale_view()
        
        # Update buy/sell markers
        buy_dates = [d for d, a in zip(dates, actions) if a > 0]
        buy_prices = [p for p, a in zip(prices, actions) if a > 0]
        sell_dates = [d for d, a in zip(dates, actions) if a < 0]
        sell_prices = [p for p, a in zip(prices, actions) if a < 0]

        if buy_dates and buy_prices:  # Only update if there are buys
            self.buy_scatter.set_offsets(np.array(list(zip(buy_dates, buy_prices))))
        if sell_dates and sell_prices:  # Only update if there are sells
            self.sell_scatter.set_offsets(np.array(list(zip(sell_dates, sell_prices))))

        # Update title
        self.ax.set_title(f'Best Trader Actions - Generation {self.current_generation}')
        
        # Redraw
        self.fig.canvas.draw_idle()
        plt.pause(0.1)  # Small pause to allow GUI update

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
            date = row['Date']
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
                trader.execute_trade(action, price, date)

        # Finalize by selling all BTC
        final_price = self.dataset.iloc[-1]['Price_Float']
        final_date = self.dataset.iloc[-1]['Date']
        for trader in self.population:
            trader.sell_all(final_price, final_date)

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
        child = Trader.deserialize(parent.serialize())
        
        # Dynamic mutation based on diversity
        current_diversity = np.std([t.total_wealth for t in self.population])
        base_rate = 0.5 if current_diversity < 100 else 0.3
        mutation_rate = base_rate * (1 - (self.current_generation / 200))
        
        child.network.mutate(
            mutation_rate=max(0.1, mutation_rate),  # Never drop below 10%
            mutation_scale=0.2 + (0.3 * (current_diversity < 100))  # Boost scale when diversity low
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

                # update animation
                best_trader = max(self.population, key=lambda x: x.total_wealth)
                self.best_trader_history.append(best_trader)
                self.update_visualization()


                # Evolve population
                self.evaluate_and_evolve()
                
                # Save progress
                if self.current_generation % self.config.gen_save_interval == 0:
                    self.save_generation()

        except KeyboardInterrupt:
            self.save_generation()
            print("\nSimulation stopped. Current generation saved.")