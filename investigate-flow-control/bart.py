import time
import cqc.pythonLib as cqclib

with cqclib.CQCConnection("Bart") as simulaqron:
    while True:
        qubit = simulaqron.recvQubit()
        bit = qubit.measure()
        print(f"[Bart] Received qubit {bit} from Anton")
        time.sleep(0.2)
