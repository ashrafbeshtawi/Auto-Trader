from utils import Utilities

def main():
    parser = Utilities.setup_arg_parse()
    args = parser.parse_args()

    config = None
    
    if args.command in ('new', '-n'):
        config = Utilities.handle_new_simulation(args)
        
    elif args.command in ('load', '-l'):
        config = Utilities.handle_load_simulation(args.save_dir)

    if config:
        # Now pass config to simulation engine
        print("\nStarting simulation with config:")
        print(f"-> First training date: {config.start_date}")
        print(f"-> Population size: {config.population}")
        # Add simulation.run(config) here
        
if __name__ == "__main__":
    main()