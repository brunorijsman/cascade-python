import argparse
import bb84

def agree_key_with_client(client_name,):
    server = bb84.Server("Alice", client_name)
    _key = server.agree_key(report=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Alice')
    parser.add_argument('-e', '--eve', action='store_true', help='Eve is present')
    args = parser.parse_args()
    if args.eve:
        agree_key_with_client("Eve")
    else:
        agree_key_with_client("Bob")
