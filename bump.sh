#!/usr/bin/env bash
# Run before each push: ./bump.sh
# Sets a new version in index.html and version.json so open copies of Clap show "New version available".
set -euo pipefail
cd "$(dirname "$0")"
V="$(date +%Y.%m.%d-%H%M)"
sed -i.bak -E "s/const APP_VERSION=\"[^\"]*\"/const APP_VERSION=\"$V\"/" index.html && rm -f index.html.bak
printf '{ "version": "%s" }\n' "$V" > version.json
echo "Clap version set to $V"
