#!/usr/bin/env bash
# Clap — one-time tool setup. Runs automatically at the start of each Claude Code session
# (see .claude/settings.json). Safe to run again: it only installs what is missing.
#   Pillow     → draws the sample posters for the preview (tools/preview/build.py)
#   Playwright → drives a real Chromium to tap through the app and take screenshots (tools/preview/shoot.py)
set -u
cd "$(dirname "$0")/.." || exit 0

pip_install() {
  python3 -m pip install --quiet --disable-pip-version-check "$@" 2>/dev/null \
  || python3 -m pip install --quiet --disable-pip-version-check --user "$@" 2>/dev/null \
  || python3 -m pip install --quiet --disable-pip-version-check --break-system-packages "$@" 2>/dev/null
}

command -v python3 >/dev/null 2>&1 || { echo "setup: python3 not found — install Python 3 first."; exit 0; }

python3 -c "import PIL" 2>/dev/null || { echo "setup: installing Pillow…"; pip_install pillow; }
python3 -c "import playwright" 2>/dev/null || { echo "setup: installing Playwright…"; pip_install playwright; }

# A browser for Playwright (skipped when one already works, e.g. a preinstalled Chromium)
if python3 -c "import playwright" 2>/dev/null; then
  if ! python3 - <<'EOF' 2>/dev/null
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    p.chromium.launch().close()
EOF
  then
    echo "setup: installing Chromium for Playwright…"
    python3 -m playwright install chromium >/dev/null 2>&1 \
    || { command -v google-chrome >/dev/null 2>&1 || command -v chromium >/dev/null 2>&1 || command -v chromium-browser >/dev/null 2>&1; } \
    && true \
    || echo "setup: could not download Chromium (network?) — previews still build; screenshots use any Chrome found on the machine."
  fi
fi

python3 -c "import PIL, playwright" 2>/dev/null && echo "setup: Pillow + Playwright ready." || echo "setup: some tools are missing — see messages above."
exit 0
