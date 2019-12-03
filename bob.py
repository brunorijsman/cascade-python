import argparse
import bb84

def agree_key_with_server(server_name, key_size, window_size, block_size):
    client = bb84.Client("Bob", server_name, key_size, window_size, block_size)
    _key = client.agree_key(report=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bob')
    parser.add_argument('-e', '--eve', action='store_true', help='Eve is present')
    parser.add_argument('-k', '--key-size', type=int, default='128', help='Key length in bits')
    parser.add_argument('-w', '--window-size', type=int, default='8', help='Window size in bits')
    parser.add_argument('-b', '--block-size', type=int, default='64', help='Block size in bits')
    args = parser.parse_args()
    if args.eve:
        agree_key_with_server("Eve", args.key_size, args.window_size, args.block_size)
    else:
        agree_key_with_server("Alice", args.key_size, args.window_size, args.block_size)
