#!/bin/bash

# TODO: Add Eve the evesdropper

echo "Starting SimulaQron"
simulaqron start --force --nodes Alice,Bob --topology path

echo "Starting Alice"
python alice.py &
alice_pid=$!

echo "Starting Bob"
python bob.py &
bob_pid=$!

echo "Waiting for Alice to finish"
wait $alice_pid

echo "Waiting for Bob to finish"
wait $bob_pid

echo "Stopping SimulaQron"
simulaqron stop