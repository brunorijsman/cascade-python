import random
import cqc.pythonLib as cqclib

BASIS_COMPUTATIONAL = 0
BASIS_HADAMARD = 1

MSG_KEEP_DONE = b"KD"
MSG_KEEP_MORE = b"KM"
MSG_DISCARD = b"D"
MSG_EXPOSE_0 = b"E0"
MSG_EXPOSE_1 = b"E1"
MSG_FINISHED = b"F"

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

def percent_str(count, total):
    if total == 0:
        return f"{count} (-)"
    percentage = 100.0 * float(count) / float(total)
    return f"{percentage:.1f}%"

def report_statistics(header, key, qubits, keep_count, discard_count, exposed_count,
                      possibly_unobserverd_count, definitely_observered_count):
    print()
    print(f"{header}:\n"
          f"  key                       : {key}\n"
          f"  qubits                    : {qubits}\n"
          f"  keep count                : "
          f"{keep_count} "
          f"({percent_str(keep_count, qubits)})\n"
          f"  discard count             : "
          f"{discard_count} "
          f"({percent_str(discard_count, qubits)})\n"
          f"  exposed count             : "
          f"{exposed_count} "
          f"({percent_str(discard_count, qubits)})\n"
          f"    possibly unobserved count : "
          f"{possibly_unobserverd_count} "
          f"({percent_str(possibly_unobserverd_count, qubits)} of total) "
          f"({percent_str(possibly_unobserverd_count, exposed_count)} of exposed)\n"
          f"    definitely observed count : "
          f"{definitely_observered_count} "
          f"({percent_str(definitely_observered_count, qubits)} of total) "
          f"({percent_str(definitely_observered_count, exposed_count)} of exposed)\n")

def server_generate_key(simulaqron, client_node_name, required_key_length):

    key_done = False
    exposed_done = False
    wanted_exposed_bits = (required_key_length + 1) // 2
    key = []
    sent_qubits = 0
    keep_count = 0
    discard_count = 0
    exposed_count = 0
    possibly_unobserverd_count = 0
    definitely_observered_count = 0
    while not key_done:

        # Randomly choose a bit and an encoding basis
        bit = choose_random_bit()
        basis = choose_random_basis()

        # Encode the bit into a qubit (using the chosen basis) and send the qubit to the peer
        qubit = encode_key_bit_into_qubit(simulaqron, bit, basis)
        simulaqron.sendQubit(qubit, client_node_name)
        sent_qubits += 1

        # Wait for the peer to tell us what basis they chose
        msg = simulaqron.recvClassical()
        peer_basis = bytes_to_basis(msg)

        # Decide what to do with the bit, based on whether or not we chose the same basis
        if basis == peer_basis:
            # Same basis. Decide whether to keep or expose.
            if key_done:
                keep = False
            elif exposed_done:
                keep = True
            else:
                keep = random.randint(0, 1) == 0
            if keep:
                # Keep the bit as key material
                key.append(bit)
                keep_count += 1
                if len(key) == required_key_length:
                    key_done = True
                    msg = MSG_KEEP_DONE
                else:
                    msg = MSG_KEEP_MORE
            else:
                # Expose the bit value (as 0 or 1) to check for evesdroppers
                exposed_count += 1
                exposed_done = exposed_count >= wanted_exposed_bits
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

    report_statistics("Server", key, sent_qubits, keep_count, discard_count, exposed_count,
                      possibly_unobserverd_count, definitely_observered_count)

    return key

def client_generate_key(simulaqron, server_node_name, required_key_length):

    key_done = False
    key = []
    received_qubits = 0
    keep_count = 0
    discard_count = 0
    exposed_count = 0
    possibly_unobserverd_count = 0
    definitely_observered_count = 0
    while not key_done:

        # Choose a random basis
        basis = choose_random_basis()

        # Receive a qubit from the peer and decode it using our chosen basis
        qubit = simulaqron.recvQubit()
        received_qubits += 1
        bit = decode_key_bit_from_qubit(qubit, basis)

        # Tell the peer what basis we used to decode the qubit
        msg = basis_to_bytes(basis)
        simulaqron.sendClassical(server_node_name, msg)

        # Find out what the peer decided to do with the bit
        msg = simulaqron.recvClassical()
        if msg in [MSG_KEEP_DONE, MSG_KEEP_MORE]:
            # Keep the bit as key material, and check if we are done
            key.append(bit)
            keep_count += 1
            if msg == MSG_KEEP_DONE:
                assert len(key) == required_key_length
                key_done = True
            else:
                assert len(key) < required_key_length
        elif msg == MSG_DISCARD:
            # Discard the bit (we chose a different basis than the peer)
            discard_count += 1
        elif msg in [MSG_EXPOSE_0, MSG_EXPOSE_1]:
            # The bit was exposed. Look for evidence that an evesdropper observed it
            exposed_count += 1
            peer_bit = 0 if msg == MSG_EXPOSE_0 else 1
            if bit == peer_bit:
                simulaqron.sendClassical(server_node_name, MSG_POSSIBLY_UNOBSERVED)
                possibly_unobserverd_count += 1
            else:
                simulaqron.sendClassical(server_node_name, MSG_DEFINITELY_OBSERVED)
                definitely_observered_count += 1
        else:
            assert False, "Unrecognized disposition message from peer"

    report_statistics("Client", key, received_qubits, keep_count, discard_count, exposed_count,
                      possibly_unobserverd_count, definitely_observered_count)

    return key
