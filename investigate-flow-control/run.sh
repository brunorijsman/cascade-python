#!/bin/bash

echo "Stopping SimulaQron (in case it was still running from a previous test)"
simulaqron stop

echo "Starting SimulaQron"
simulaqron start --force --nodes Anton,Bart --topology path

echo "Starting Anton"
python anton.py &
anton_pid=$!

echo "Starting Bart"
python bart.py &
bart_pid=$!

echo "Waiting for Anton to finish"
wait $anton_pid

echo "Waiting for Bart to finish"
wait $bart_pid

echo "Stopping SimulaQron"
simulaqron stop
