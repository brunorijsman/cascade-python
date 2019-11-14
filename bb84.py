import random
import cqc.pythonLib as cqclib

BASIS_COMPUTATIONAL = 0
BASIS_HADAMARD = 1

MSG_KEEP = b"K"
MSG_DISCARD = b"D"
MSG_EXPOSE_0 = b"E0"
MSG_EXPOSE_1 = b"E1"

MSG_POSSIBLY_UNOBSERVED = b"U"
MSG_DEFINITELY_OBSERVED = b"O"

def basis_to_str(basis):
    if basis == BASIS_COMPUTATIONAL:
        return "+"
    assert basis == BASIS_HADAMARD
    return "x"

def basis_to_bytes(basis):
    if basis == BASIS_COMPUTATIONAL:
        return b"+"
    assert basis == BASIS_HADAMARD
    return b"x"

def bytes_to_basis(msg):
    if msg == b"+":
        return BASIS_COMPUTATIONAL
    assert msg == b"x"
    return BASIS_HADAMARD

def choose_random_bit():
    return random.randint(0, 1)

def choose_random_basis():
    return random.randint(0, 1)

def encode_key_bit_into_qubit(connection, bit, basis):
    qubit = cqclib.qubit(connection)
    if basis == BASIS_COMPUTATIONAL:
        if bit == 0:
            pass
        elif bit == 1:
            qubit.X()
        else:
            assert False, "Unknown bit value"
    elif basis == BASIS_HADAMARD:
        if bit == 0:
            qubit.H()
        elif bit == 1:
            qubit.X()
            qubit.H()
        else:
            assert False, "Unknown bit value"
    else:
        assert False, "Unknown basis"
    return qubit

def decode_key_bit_from_qubit(qubit, basis):
    if basis == BASIS_COMPUTATIONAL:
        pass
    elif basis == BASIS_HADAMARD:
        qubit.H()
    else:
        assert False, "Unknown basis"
    bit = qubit.measure()
    return bit

def server_generate_key(simulaqron, client_node_name, required_key_length):

    key = []
    discard_count = 0
    possibly_unobserverd_count = 0
    definitely_observered_count = 0
    while len(key) < required_key_length:

        # Randomly choose a bit and an encoding basis
        bit = choose_random_bit()
        basis = choose_random_basis()

        # Encode the bit into a qubit (using the chosen basis) and send the qubit to the peer
        qubit = encode_key_bit_into_qubit(simulaqron, bit, basis)
        simulaqron.sendQubit(qubit, client_node_name)

        # Wait for the peer to tell us what basis they chose
        msg = simulaqron.recvClassical()
        peer_basis = bytes_to_basis(msg)

        # Decide what to do with the bit, based on whether or not we chose the same basis
        if basis == peer_basis:
            if random.randint(0, 1) == 0:
                # Keep the bit as key material
                msg = MSG_KEEP
                key.append(bit)
            else:
                # Expose the bit value (as 0 or 1) to check for evesdroppers
                if bit == 0:
                    msg = MSG_EXPOSE_0
                else:
                    msg = MSG_EXPOSE_1
        else:
            # Discard the bit (we chose a different basis than the peer)
            msg = MSG_DISCARD
            discard_count += 1
        simulaqron.sendClassical(client_node_name, msg)

        # If we exposed our bit, look for evidence that an evesdropper observed it
        if msg in [MSG_EXPOSE_0, MSG_EXPOSE_1]:
            msg = simulaqron.recvClassical()
            if msg == MSG_POSSIBLY_UNOBSERVED:
                possibly_unobserverd_count += 1
            elif msg == MSG_DEFINITELY_OBSERVED:
                definitely_observered_count += 1
            else:
                assert False, "Unrecognized observation message"

    print()
    print(f"[Server] key                       : {key}\n"
          f"[Server] discard count             : {discard_count}\n"
          f"[Server] possibly unobserved count : {possibly_unobserverd_count}\n"
          f"[Server] definitely observed count : {definitely_observered_count}")

    return key

def client_generate_key(simulaqron, server_node_name, required_key_length):

    key = []
    discard_count = 0
    possibly_unobserverd_count = 0
    definitely_observered_count = 0
    while len(key) < required_key_length:

        # Choose a random basis
        basis = choose_random_basis()

        # Receive a qubit from the peer and decode it using our chosen basis
        qubit = simulaqron.recvQubit()
        bit = decode_key_bit_from_qubit(qubit, basis)

        # Tell the peer what basis we used to decode the qubit
        msg = basis_to_bytes(basis)
        simulaqron.sendClassical(server_node_name, msg)

        # Find out what the peer decided to do with the bit
        msg = simulaqron.recvClassical()
        if msg == MSG_KEEP:
            # Keep the bit as key material
            key.append(bit)
        elif msg == MSG_DISCARD:
            # Discard the bit (we chose a different basis than the peer)
            discard_count += 1
        elif msg in [MSG_EXPOSE_0, MSG_EXPOSE_1]:
            # The bit was exposed. Look for evidence that an evesdropper observed it
            peer_bit = 0 if msg == MSG_EXPOSE_0 else 1
            if bit == peer_bit:
                simulaqron.sendClassical(server_node_name, MSG_POSSIBLY_UNOBSERVED)
                possibly_unobserverd_count += 1
            else:
                simulaqron.sendClassical(server_node_name, MSG_DEFINITELY_OBSERVED)
                definitely_observered_count += 1
        else:
            assert False, "Unrecognized disposition message from peer"

    print()
    print(f"[Client] key                       : {key}\n"
          f"[Client] discard count             : {discard_count}\n"
          f"[Client] possibly unobserved count : {possibly_unobserverd_count}\n"
          f"[Client] definitely observed count : {definitely_observered_count}")

    return key
