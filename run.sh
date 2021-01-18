#!/bin/bash

cd "$(dirname "$0")"

if command -v python3 &>/dev/null; then
    python3 monitor.py $@
else
    python monitor.py $@
fi
