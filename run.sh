#!/bin/bash

# TODO: Add Eve the evesdropper

REQUIRED_KEY_BITS=5

echo "Stopping SimulaQron (in case it was still running from a previous test)"
simulaqron stop

echo
echo "***** Scenario 1: Alice and Bob, Eve is absent *****"
echo

echo "Starting SimulaQron"
simulaqron start --force --nodes Alice,Bob --topology path

echo "Starting Alice"
python alice.py --keysize ${REQUIRED_KEY_BITS} &
alice_pid=$!

echo "Starting Bob"
python bob.py --keysize ${REQUIRED_KEY_BITS} &
bob_pid=$!

echo "Waiting for Alice to finish"
wait $alice_pid

echo "Waiting for Bob to finish"
wait $bob_pid

echo "Stopping SimulaQron"
simulaqron stop

echo
echo "***** Scenario 2: Alice and Bob, Eve is present but does not observe qubits *****"
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
python eve.py &
eve_pid=$!

echo "Waiting for Alice to finish"
wait $alice_pid

echo "Waiting for Bob to finish"
wait $bob_pid

echo "Stopping SimulaQron"
simulaqron stop

echo
echo "***** Scenario 3: Alice and Bob, Eve is present and observes 50% of qubits *****"
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