#!/usr/bin/env python3
"""Build Clap V3 (v3/index.html) from the V1 app (index.html) + the V3 identity layer (v3/skin.css).

V3 is not a separate codebase: it is the V1 app with a different look. Any feature or logic
change goes into index.html; any visual change for V3 goes into v3/skin.css. Then run:

    python3 tools/build-v3.py            # uses ./index.html
    python3 tools/build-v3.py path.html  # uses another source (e.g. a branch export)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "index.html"
s = src.read_text()
skin = (ROOT / "v3" / "skin.css").read_text()


def rep(old, new):
    global s
    if old not in s:
        sys.exit(f"build-v3: expected text not found in {src.name}: {old[:70]}…")
    s = s.replace(old, new, 1)


# Fonts: Outfit (display) + Geologica (interface)
rep("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&family=Inter:wght@400..700&display=swap",
    "https://fonts.googleapis.com/css2?family=Outfit:wght@400..900&family=Geologica:wght@300..800&display=swap")
rep("<title>Clap</title>", "<title>Clap V3</title>")
# V3 has its own manifest (v3/manifest.webmanifest) so it installs as a separate home-screen app
rep('href="manifest.webmanifest?v=3"', 'href="manifest.webmanifest?v=1"')
# Shared icons live one folder up
rep('href="icon-192-v3.png"', 'href="../icon-192-v3.png"')
rep('href="apple-touch-icon-v3.png"', 'href="../apple-touch-icon-v3.png"')
rep('<meta name="apple-mobile-web-app-title" content="Clap">', '<meta name="apple-mobile-web-app-title" content="Clap V3">')
rep('content="#f5ede4" media="(prefers-color-scheme: light)"', 'content="#F9F2DA" media="(prefers-color-scheme: light)"')
rep('content="#130d0b" media="(prefers-color-scheme: dark)"', 'content="#1d1614" media="(prefers-color-scheme: dark)"')
# The identity layer goes last so it wins over the V1 styles
rep("</style>", "\n" + skin + "\n</style>")

out = ROOT / "v3" / "index.html"
out.write_text(s)
print(f"build-v3: wrote {out.relative_to(ROOT)} from {src.name} ({len(s)//1024} KB)")
