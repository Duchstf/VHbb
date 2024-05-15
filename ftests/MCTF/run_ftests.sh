#!/bin/bash

show_help() {
    cat <<'EOF'
Usage: ./myscript.sh <year>
Options:
    -h      Display this help message

This script runs the f-tests for VH MCTF.
EOF
}

# Check for help option
if [[ "$1" == "-h" ]]; then
    show_help
    exit 0
fi