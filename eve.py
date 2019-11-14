import argparse
import random
import cqc.pythonLib as cqclib
import bb84

def main(observe_percentage):

    with cqclib.CQCConnection("Eve") as simulaqron:

        done = False
        qubits_count = 0
        unobserved_count = 0
        observed_count = 0
        while not done:

            # Receive qubit from Aliced
            qubit = simulaqron.recvQubit()
            qubits_count += 1

            # Does Eve observe the qubit?
            if random.randint(1, 100) <= observe_percentage:

                # Observe the qubit
                qubit.measure()
                observed_count += 1

                # Create a new random qubit and send to Bob
                bit = bb84.choose_random_bit()
                basis = bb84.choose_random_basis()
                new_qubit = bb84.encode_key_bit_into_qubit(simulaqron, bit, basis)
                simulaqron.sendQubit(new_qubit, "Bob")

            else:

                # Forward qubit (without observing it) to Bob
                simulaqron.sendQubit(qubit, "Bob")
                unobserved_count += 1

            # Forward basis message from Bob to Alice
            basis_msg = simulaqron.recvClassical()
            simulaqron.sendClassical("Alice", basis_msg)

            # Forward disposition message from Alice to Bob
            disposition_msg = simulaqron.recvClassical()
            simulaqron.sendClassical("Bob", disposition_msg)

            if disposition_msg == bb84.MSG_KEEP_DONE:

                # Disposition was keep done, we are finished
                done = True

            elif disposition_msg in [bb84.MSG_EXPOSE_0, bb84.MSG_EXPOSE_1]:

                # Disposition was expose, forward observation message from Bob to Alice
                observation_msg = simulaqron.recvClassical()
                simulaqron.sendClassical("Alice", observation_msg)

    print()
    print(f"Eve:\n"
          f"  un-observerd qubits : "
          f"{unobserved_count} "
          f"{bb84.percent_str(unobserved_count, qubits_count)}\n"
          f"  observed qubits     : "
          f"{observed_count} "
          f"{bb84.percent_str(observed_count, qubits_count)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Eve')
    parser.add_argument('-o', '--observe', type=int, default='0',
                        help='Percentage of observed qubits')
    args = parser.parse_args()
    main(args.observe)
