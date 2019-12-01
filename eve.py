import argparse

def main(_observe_percentage):
    pass  # TODO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Eve')
    parser.add_argument('-o', '--observe', type=int, default='0',
                        help='Percentage of observed qubits')
    args = parser.parse_args()
    main(args.observe)
