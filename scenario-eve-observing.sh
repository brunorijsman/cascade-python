#!/bin/bash

# TODO: Only set if not already set
REQUIRED_KEY_BITS=32

echo
echo "***** Scenario: Alice and Bob, Eve is present and observes 50% of qubits *****"
echo

echo "Starting SimulaQron"
simulaqron start --force --nodes Alice,Eve,Bob --topology path

echo "Starting Alice"
python alice.py --eve --keysize ${REQUIRED_KEY_BITS} &
alice_pid=$!

echo "Starting Bob"
python bob.py --eve --keysize ${REQUIRED_KEY_BITS} &
bob_pid=$!

echo "Starting Eve"
python eve.py --observe 50 &
eve_pid=$!

echo "Waiting for Alice to finish"
wait $alice_pid

echo "Waiting for Bob to finish"
wait $bob_pid

echo "Stopping SimulaQron"
simulaqron stop