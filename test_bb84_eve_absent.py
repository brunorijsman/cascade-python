import subprocess
import threading
import time
import bb84

def eve_absent(key_size, block_size, window_size):

    print("Starting Simulaqron...")
    subprocess.call(['simulaqron', 'start', '--force', '--nodes', 'Alice,Bob', '--topology',
                     'path'])
    time.sleep(1)
    print("Simulaqron started")

    print("Creating Alice...")
    alice = bb84.Server("Alice", "Bob", trace=True, report=True)
    print("Alice created")

    print("Starting Alice...")
    alice_thread = threading.Thread(target=alice.agree_key)
    alice_thread.start()
    print("Alice started")

    print("Creating Bob...")
    bob = bb84.Client("Bob", "Alice", key_size, window_size, block_size, trace=True, report=True)
    print("Bob created")

    print("Starting Bob...")
    bob_thread = threading.Thread(target=bob.agree_key)
    bob_thread.start()
    print("Bob started")

    print("Waiting for Alice to finish...")
    alice_thread.join()
    print("Alice finished")

    print("Waiting for Bob to finish...")
    bob_thread.join()
    print("Bob finished")

    alice_key = alice.key_str()
    print(f"Alice key: {alice_key}")
    assert len(alice_key) == key_size
    for c in alice_key:
        assert c in ['0', '1']

    bob_key = bob.key_str()
    print(f"Bob key: {bob_key}")
    assert len(bob_key) == key_size
    for c in alice_key:
        assert c in ['0', '1']

    assert alice_key == bob_key

    print("Stopping Simulaqron...")
    subprocess.call(['simulaqron', 'stop'])
    time.sleep(1)
    print("Simulaqron stopped")

def test_key_16_block_4_window_2():
    eve_absent(key_size=16, block_size=4, window_size=2)

def test_key_64_block_32_window_8():
    eve_absent(key_size=64, block_size=32, window_size=8)

def test_key_16_block_4_window_1():
    # Window size is degenerate value of 1
    eve_absent(key_size=16, block_size=4, window_size=1)

def test_key_16_block_4_window_4():
    # Block size is same as window size
    eve_absent(key_size=16, block_size=4, window_size=4)

def test_key_8_block_8_window_4():
    # Key size is same as block size
    eve_absent(key_size=8, block_size=8, window_size=4)

def test_key_8_block_8_window_8():
    # Key size, block size, and window size are all the same
    eve_absent(key_size=8, block_size=8, window_size=8)

def test_key_27_block_8_window_4():
    # Key size is not a multiple of block size
    eve_absent(key_size=27, block_size=8, window_size=4)
