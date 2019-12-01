#!/bin/bash

# TODO: Only set if not already set
KEY_SIZE=32

echo
echo "***** Scenario: Alice and Bob, Eve is present but does not observe qubits *****"
echo

# In case it was still running from a previous test
echo "Stopping SimulaQron"
simulaqron stop

echo "Starting SimulaQron"
simulaqron start --force --nodes Alice,Eve,Bob --topology path

echo "Starting Alice"
python alice.py --eve --key-size ${KEY_SIZE} &
alice_pid=$!

echo "Starting Bob"
python bob.py --eve --key-size ${KEY_SIZE} &
bob_pid=$!

echo "Starting Eve"
python eve.py &
eve_pid=$!

echo "Waiting for Alice to finish"
wait $alice_pid

echo "Waiting for Bob to finish"
wait $bob_pid

echo "Stopping SimulaQron"
simulaqron stop
