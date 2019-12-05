import argparse
from .server import Server

def agree_key_with_client(client_name, trace, report):
    server = Server("Alice", client_name, trace=trace, report=report)
    _key = server.agree_key()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Alice')
    parser.add_argument('-e', '--eve', action='store_true', help='Eve is present')
    parser.add_argument('-r', '--report', action='store_true', help='Report statistics')
    parser.add_argument('-t', '--trace', action='store_true', help='Trace classical messages')
    args = parser.parse_args()
    if args.eve:
        agree_key_with_client("Eve", args.trace, args.report)
    else:
        agree_key_with_client("Bob", args.trace, args.report)
