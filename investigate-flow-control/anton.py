import time
import cqc.pythonLib as cqclib

with cqclib.CQCConnection("Anton") as simulaqron:
    while True:
        qubit = cqclib.qubit(simulaqron)
        simulaqron.sendQubit(qubit, "Bart")
        print("[Anton] Sent qubit to Bart")
        time.sleep(0.1)
