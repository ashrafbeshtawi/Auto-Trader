from utils import Utilities

def main():
    parser = Utilities.setup_arg_parse()
    args = parser.parse_args()

    if args.command in ('new', '-n'):
        Utilities.handle_new_simulation(args)
        
    elif args.command in ('load', '-l'):
        Utilities.handle_load_simulation(args.save_dir)

if __name__ == "__main__":
    main()