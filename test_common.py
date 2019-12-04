import subprocess
import threading
import time
import bb84

def start_simulaqron(eve_present=False):

    print("Killing old simulaqron processes...")
    subprocess.call(["pkill", "-f", "simulaqron"])
    time.sleep(1)
    print("Old simulaqron processes killed")

    print("Starting Simulaqron...")
    nodes = 'Alice,Eve,Bob' if eve_present else 'Alice,Bob'
    subprocess.call(['simulaqron', 'start', '--force', '--nodes', nodes, '--topology', 'path'])
    time.sleep(3)
    print("Simulaqron started")

def stop_simulaqron():

    print("Stopping Simulaqron...")
    subprocess.call(['simulaqron', 'stop'])
    time.sleep(3)
    print("Simulaqron stopped")

def run_nodes(key_size, block_size, window_size, eve_present=False, eve_observe_percentage=0):

    print("Creating Alice...")
    neighbor = "Eve" if eve_present else "Bob"
    alice = bb84.Server("Alice", neighbor, trace=True, report=True)
    print("Alice created")

    print("Starting Alice...")
    alice_thread = threading.Thread(target=alice.agree_key)
    alice_thread.start()
    print("Alice started")

    print("Creating Bob...")
    neighbor = "Eve" if eve_present else "Alice"
    bob = bb84.Client("Bob", neighbor, key_size, window_size, block_size, trace=True, report=True)
    print("Bob created")

    print("Starting Bob...")
    bob_thread = threading.Thread(target=bob.agree_key)
    bob_thread.start()
    print("Bob started")

    if eve_present:

        print("Creating Eve...")
        eve = bb84.Middle("Eve", "Alice", "Bob", eve_observe_percentage, trace=True, report=True)
        print("Eve created")

        print("Starting Eve...")
        eve_thread = threading.Thread(target=eve.pass_through)
        eve_thread.start()
        print("Eve started")

    print("Waiting for Alice to finish...")
    alice_thread.join()
    print("Alice finished")

    print("Waiting for Bob to finish...")
    bob_thread.join()
    print("Bob finished")

    if eve_present:

        print("Waiting for Eve to finish...")
        eve_thread.join()
        print("Eve finished")

        return (alice, bob, eve)

    return (alice, bob)
