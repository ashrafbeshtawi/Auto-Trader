import os
import pickle
from datetime import datetime
import argparse
import sys

CONFIG_FILE = "simulation_config.pkl"

class SimulationConfig:
    def __init__(self, args):
        self.dataset_path = args.dataset
        self.start_date = args.start_date
        self.end_date = args.end_date
        self.save_dir = args.save_dir
        self.gen_save_interval = args.gen_save_interval
        self.population = args.population
        self.survival_rate = args.survival_rate

class Utilities:
    @staticmethod
    def validate_directory(path):
        if not os.path.exists(path):
            os.makedirs(path)
        elif not os.path.isdir(path):
            raise ValueError(f"Path exists but is not a directory: {path}")
        return path

    @staticmethod
    def validate_dates(start_str, end_str):
        try:
            start = datetime.strptime(start_str, "%Y-%m-%d")
            end = datetime.strptime(end_str, "%Y-%m-%d")
            if start >= end:
                raise ValueError("End date must be after start date")
            return start, end
        except ValueError as e:
            raise ValueError(f"Date validation failed: {e}")

    @staticmethod
    def validate_survival_rate(rate):
        if not 0 < rate < 1:
            raise ValueError("Survival rate must be between 0 and 1")

    @staticmethod
    def setup_arg_parse():
        parser = argparse.ArgumentParser(description="Bitcoin Trading Evolution Simulator")
        subparsers = parser.add_subparsers(dest='command', required=True)

        # New simulation parser
        new_parser = subparsers.add_parser('new', aliases=['-n'], help='Start new simulation')
        new_parser.add_argument('-d', '--dataset', required=True, help='Path to dataset CSV')
        new_parser.add_argument('-s', '--start-date', required=True, help='Start date (YYYY-MM-DD)')
        new_parser.add_argument('-e', '--end-date', required=True, help='End date (YYYY-MM-DD)')
        new_parser.add_argument('-sd', '--save-dir', required=True, help='Directory to save simulation data')
        new_parser.add_argument('-p', '--population', type=int, default=100, help='Number of traders per generation')
        new_parser.add_argument('-sr', '--survival-rate', type=float, default=0.2, help='Top percentage to survive')
        new_parser.add_argument('-si', '--save-interval', type=int, default=10, dest='gen_save_interval',
                              help='Save every N generations')

        # Load simulation parser
        load_parser = subparsers.add_parser('load', aliases=['-l'], help='Load existing simulation')
        load_parser.add_argument('save_dir', help='Directory containing simulation data')

        return parser

    @staticmethod
    def handle_new_simulation(args):
        try:
            Utilities.validate_directory(args.save_dir)
            Utilities.validate_dates(args.start_date, args.end_date)
            Utilities.validate_survival_rate(args.survival_rate)
            
            if args.population <= 0:
                raise ValueError("Population size must be positive")

            config = SimulationConfig(args)
            config_path = os.path.join(args.save_dir, CONFIG_FILE)
            
            with open(config_path, 'wb') as f:
                pickle.dump(config, f)
            
            print(f"New simulation initialized in: {args.save_dir}")
            print(f"Configuration saved to: {config_path}")
            return config  # Return created config

        except Exception as e:
            print(f"Error creating simulation: {str(e)}")
            sys.exit(1)

    @staticmethod
    def handle_load_simulation(save_dir):
        try:
            config_path = os.path.join(save_dir, CONFIG_FILE)
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Missing config file: {CONFIG_FILE}")

            with open(config_path, 'rb') as f:
                config = pickle.load(f)
            
            print(f"Loaded simulation from: {save_dir}")
            print(f"Dataset: {config.dataset_path}")
            print(f"Date Range: {config.start_date} to {config.end_date}")
            print(f"Population: {config.population} traders")
            print(f"Survival Rate: {config.survival_rate*100}%")
            return config  # Return loaded config

        except Exception as e:
            print(f"Error loading simulation: {str(e)}")
            sys.exit(1)