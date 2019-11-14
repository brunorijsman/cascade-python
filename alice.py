import cqc.pythonLib as cqclib
import bb84

def main():

    with cqclib.CQCConnection("Alice") as simulaqron:
        _key = bb84.server_generate_key(simulaqron, "Bob", 10)

if __name__ == "__main__":
    main()
