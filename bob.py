import cqc.pythonLib as cqclib
import bb84

def main():

    with cqclib.CQCConnection("Bob") as simulaqron:
        _key = bb84.client_generate_key(simulaqron, "Alice", 10)

if __name__ == "__main__":
    main()
