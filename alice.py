import argparse
import bb84

def agree_key_with_client(client_name, key_size):
    server = bb84.Server("Alice", client_name, key_size)
    _key = server.agree_key(report=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Alice')
    parser.add_argument('-e', '--eve', action='store_true', help='Eve is present')
    parser.add_argument('-k', '--key-size', type=int, default='16', help='Key length in bits')
    args = parser.parse_args()
    if args.eve:
        agree_key_with_client("Eve", args.key_size)
    else:
        agree_key_with_client("Bob", args.key_size)
