#!/bin/bash

# TODO: Only set if not already set
KEY_SIZE=32

echo
echo "***** Scenario: Alice and Bob, Eve is present but does not observe qubits *****"
echo

echo "killing old SimulaQron"
pkill -f simulaqron

echo "killing old Alice, Bob, and Eve"
pkill -f alice.py
pkill -f bob.py
pkill -f eve.py

echo "Starting SimulaQron"
simulaqron start --force --nodes Alice,Eve,Bob --topology path

echo "Starting Alice"
python alice.py --eve "$@" &
alice_pid=$!

echo "Starting Bob"
###@@@ python bob.py --eve --key-size ${KEY_SIZE} "$@" &
python bob.py --eve --key-size 8 --window-size 2 --block-size 2 "$@" &
bob_pid=$!

echo "Starting Eve"
python eve.py "$@" &
eve_pid=$!

echo "Waiting for Alice to finish"
wait $alice_pid

echo "Waiting for Bob to finish"
wait $bob_pid

echo "Stopping SimulaQron"
simulaqron stop
