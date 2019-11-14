import argparse
import cqc.pythonLib as cqclib
import bb84

def agree_key_with_client(client, required_key_size):
    with cqclib.CQCConnection("Alice") as simulaqron:
        _key = bb84.server_generate_key(simulaqron, client, required_key_size)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Alice')
    parser.add_argument('-e', '--eve', action='store_true', help='Eve is present')
    parser.add_argument('-k', '--keysize', type=int, default='16', help='Required key size in bits')
    args = parser.parse_args()
    if args.eve:
        agree_key_with_client("Eve", args.keysize)
    else:
        agree_key_with_client("Bob", args.keysize)
