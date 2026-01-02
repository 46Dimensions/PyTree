#!/usr/bin/env sh
dir=""
flags=""

# Parse arguments to separate directory from flags
for arg in "$@"; do
    case "$arg" in
        -*)
            # It's a flag
            flags="$flags $arg"
            ;;
        *)
            # It's the directory (first non-flag argument)
            if [ -z "$dir" ]; then
                dir="$arg"
            else
                flags="$flags $arg"
            fi
            ;;
    esac
done

# Use current directory if none specified
if [ -z "$dir" ]; then
    dir="$PWD"
fi

python $INSTALL_DIR/main.py "$dir" $flags