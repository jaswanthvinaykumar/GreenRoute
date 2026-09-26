#!/usr/bin/env bash
# GreenRoute — Sustainable Server Log Optimizer
# Quick launcher script

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=================================================================="
echo "  🌱 GreenRoute — Sustainable Server Log Optimizer"
echo "  Hackathon Edition • Carbon Abatement & Energy Conservation"
echo "=================================================================="

if [ "$1" == "cli" ]; then
    shift
    python3 app.py optimize "$@"
elif [ "$1" == "test" ]; then
    python3 -m unittest discover -s tests
    python3 tests/test_asgi_inprocess.py
elif [ "$1" == "sample" ]; then
    shift
    python3 app.py sample "$@"
else
    echo "Starting GreenRoute Local Desktop Dashboard..."
    echo "Opening your default browser..."
    python3 app.py gui "$@"
fi
