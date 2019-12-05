#!/bin/bash
kill $(lsof -nP -i4 -i6 | grep LISTEN | grep Python | awk '{print $2}')