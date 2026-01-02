#!/usr/bin/env sh

# Disable stdout if $1 is -s or --silent
SILENT=0
case "$1" in
  -s|--silent) SILENT=1 ;;
esac

if [ "$SILENT" -eq 1 ]; then
  exec >/dev/null
fi

INSTALL_DIR=$PWD/PyTree
echo "Creating directory at ${INSTALL_DIR}"
mkdir -p $INSTALL_DIR

BASE_URL="https://raw.githubusercontent.com/46Dimensions/PyTree/next"
COMMAND_URL=$BASE_URL/command.sh
MAIN_URL=$BASE_URL/main.py

# Download files
COMMAND_CONTENTS=$(curl -fsSL $COMMAND_URL) || { echo "Error downloading command script"; exit 1; }
curl -fsSL $MAIN_URL -o $INSTALL_DIR/main.py || { echo "Error downloading main script"; exit 1; }

echo "Configuring files..."

write_script_with_install_dir() {
    contents=$1
    out=$2


    printf '%s\n' "$contents" | awk -v install_dir="$INSTALL_DIR" '
        NR == 1 { print; next }
        NR == 2 && $0 ~ /^set -e/ {
        print
        print ""
        print "INSTALL_DIR=\"" install_dir "\""
        print ""
        next
        }
        { print }
    ' > "$out"

  chmod +x "$out"
}

write_script_with_install_dir "$COMMAND_CONTENTS" "$HOME/.local/bin/pytree"

echo "PyTree version 1.0.0 installed successfully"