#!/usr/bin/env sh
set -eu
python_command="${PYTHON:-python3}"
exec "$python_command" software/run_all.py
