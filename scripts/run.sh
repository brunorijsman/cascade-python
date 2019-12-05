#!/bin/bash

if [ -z ${VIRTUAL_ENV+X} ]; then
    echo "Virtual environment is not activated"
    exit 1
fi
SCRIPTS=${VIRTUAL_ENV}/../scripts

${SCRIPTS}/scenario-eve-absent.sh
${SCRIPTS}/scenario-eve-not-observing.sh
${SCRIPTS}/scenario-eve-observing.sh
