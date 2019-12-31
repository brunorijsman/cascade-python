import argparse
from middle import Middle

def main(observe_percentage, trace, report):
    middle = Middle("Eve", "Alice", "Bob", observe_percentage, trace=trace, report=report)
    middle.pass_through()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Eve')
    parser.add_argument('-o', '--observe', type=int, default='0',
                        help='Percentage of observed qubits')
    parser.add_argument('-r', '--report', action='store_true', help='Report statistics')
    parser.add_argument('-t', '--trace', action='store_true', help='Trace classical messages')
    args = parser.parse_args()
    main(args.observe, args.trace, args.report)
