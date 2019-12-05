#!/bin/bash

if [ -z ${VIRTUAL_ENV+X} ]; then
    echo "Virtual environment is not activated"
    exit 1
fi
cd ${VIRTUAL_ENV}/../scripts
export PYTHONPATH=${VIRTUAL_ENV}/..

# TODO: Only set if not already set
KEY_SIZE=32

echo
echo "***** Scenario: Alice and Bob, Eve is absent *****"
echo

echo "Stopping old SimulaQron"
simulaqron stop
sleep 3

echo "killing old Alice, Bob, and Eve"
pkill -f alice.py
pkill -f bob.py
pkill -f eve.py
sleep 1

echo "Starting SimulaQron"
simulaqron start --force --nodes Alice,Bob --topology path
sleep 3

echo "Starting Alice"
python alice.py --report "$@" &
alice_pid=$!

echo "Starting Bob"
python bob.py --report --key-size ${KEY_SIZE} "$@" &
bob_pid=$!

echo "Waiting for Alice to finish"
wait $alice_pid

echo "Waiting for Bob to finish"
wait $bob_pid

echo "Stopping SimulaQron"
simulaqron stop
sleep 3
