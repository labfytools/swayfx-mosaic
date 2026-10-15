#!/bin/sh
# Source assembly only; no installation or compositor launch.
set -eu
exec python3 -B "$(dirname "$0")/../assemble.py" "$@"
