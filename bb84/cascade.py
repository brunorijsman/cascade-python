import random

# TODO: For now, this is just futsing about to get familiar with the Cascade protocol.
# Eventually this will be integrated with the rest of the BB84 protocol.

KEY_LENGTH = 64

BIT_FLIP_PROBABILITY = 0.1

def random_key(key_length):
    key = []
    for _ in range(key_length):
        key.append(random.randint(0, 1))
    return key

def add_noise_to_key(key, bit_flip_probability):
    noisy_key = []
    for bit in key:
        if random.random() < bit_flip_probability:
            noisy_key.append(1 - bit)
        else:
            noisy_key.append(bit)
    return noisy_key

def key_str(key):
    string = ""
    for bit in key:
        string += str(bit)
    return string

def difference_str(key1, key2):
    string = ""
    count = 0
    for bit1, bit2 in zip(key1, key2):
        if bit1 == bit2:
            string += '.'
        else:
            string += 'X'
            count += 1
    return string + f" ({count})"

alice_key = random_key(KEY_LENGTH)
print(f"Alice key : {key_str(alice_key)}")

bob_key = add_noise_to_key(alice_key, BIT_FLIP_PROBABILITY)
print(f"Bob key   : {key_str(bob_key)}")

print(f"Difference: {difference_str(alice_key, bob_key)}")
