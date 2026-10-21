#!/usr/bin/env bash
# Lanzador para Linux: ./eva.sh ejemplos/01_primera_prueba.eva
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -x "$DIR/.venv/bin/python" ]; then
    exec "$DIR/.venv/bin/python" "$DIR/run.py" "$@"
else
    exec python3 "$DIR/run.py" "$@"
fi
