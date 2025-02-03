import sys
from utils import Utilities
from simulation_engine import TradingEnvironment

def main():
    # Parse command line arguments
    parser = Utilities.setup_arg_parse()
    args = parser.parse_args()

    # Load configuration
    config = None
    if args.command in ('new', '-n'):
        config = Utilities.handle_new_simulation(args)
    elif args.command in ('load', '-l'):
        config = Utilities.handle_load_simulation(args.save_dir)
    

    test_phase = False
    if hasattr(args,'test_phase'):
        test_phase = Utilities.str_to_bool(args.test_phase)


    # Initialize and run environment
    if config:
        env = TradingEnvironment(config, test_phase)
        env.run()
        
if __name__ == "__main__":
    main()