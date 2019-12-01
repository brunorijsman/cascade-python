import argparse
import bb84

def main(observe_percentage):
    middle = bb84.Middle("Eve", "Alice", "Bob", observe_percentage)
    middle.pass_through(report=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Eve')
    parser.add_argument('-o', '--observe', type=int, default='0',
                        help='Percentage of observed qubits')
    args = parser.parse_args()
    main(args.observe)
