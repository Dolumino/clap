#!/usr/bin/env python3
"""Tap through a Clap preview on an iPhone 15-sized screen, report JavaScript errors, save screenshots.

    python3 tools/preview/build.py "note"                       # → tools/preview/preview.html (V1)
    python3 tools/preview/shoot.py                              # screenshots → tools/preview/shots/
    python3 tools/preview/shoot.py tools/preview/preview-v3.html --dark --fr

Screens: discover, discover-filled, results, runners, film, lists, seen, search, theatres, settings.
Exit code 1 if the page raised a JavaScript error.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
args = [a for a in sys.argv[1:] if not a.startswith("--")]
SRC = Path(args[0]).resolve() if args else HERE / "preview.html"
DARK, FR = "--dark" in sys.argv, "--fr" in sys.argv
OUT = HERE / "shots"
OUT.mkdir(exist_ok=True)
errors, saved = [], []


def route(r):
    u = r.request.url
    # the preview is self-contained; let fonts through when the network allows it
    if u.startswith(("file:", "data:")) or "fonts.googleapis.com" in u or "fonts.gstatic.com" in u:
        return r.continue_()
    return r.abort()


def launch(p):
    """Playwright's own Chromium first, then any Chrome/Chromium already installed on the machine."""
    import shutil
    try:
        return p.chromium.launch()
    except Exception as first:
        for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
                     "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
            path = name if Path(name).exists() else shutil.which(name)
            if path:
                return p.chromium.launch(executable_path=path)
        sys.exit(f"shoot: no browser available ({first.__class__.__name__}). Run: python3 -m playwright install chromium")


with sync_playwright() as p:
    b = launch(p)
    pg = b.new_page(viewport={"width": 393, "height": 852}, device_scale_factor=2,
                    color_scheme="dark" if DARK else "light")
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.route("**/*", route)
    pg.goto(SRC.as_uri())
    pg.wait_for_timeout(900)
    if FR:
        pg.evaluate("""for (const k of ['clap.preview.v2','cesoir.tmdb.v1']) { const d = JSON.parse(localStorage.getItem(k) || 'null');
                       if (d) { d.cfg = Object.assign(d.cfg || {}, {lang: 'fr-FR'}); localStorage.setItem(k, JSON.stringify(d)); } }""")
        pg.reload()
        pg.wait_for_timeout(900)
    pg.evaluate("document.querySelector('.pv-band')?.remove(); document.getElementById('upd')?.remove()")

    def shot(name):
        path = OUT / f"{name}.png"
        pg.screenshot(path=str(path))
        saved.append(path.name)

    def tap(sel, wait=500):
        loc = pg.locator(sel).first
        if loc.count():
            loc.click()
            pg.wait_for_timeout(wait)
            return True
        return False

    shot("01-discover")
    tap("#who button >> nth=1", 200)
    tap("[data-mood] >> nth=0", 200)
    pg.evaluate("document.querySelector('#v-settings').scrollTop = 320")
    pg.wait_for_timeout(300)
    shot("02-discover-filled")
    if tap("#go", 1600):
        shot("03-results")
        pg.evaluate("document.querySelector('.runners')?.scrollIntoView({block:'start'})")
        pg.wait_for_timeout(300)
        shot("04-runners")
        if tap(".pick-more", 1200) or tap("#v-results [data-open]", 1200):
            shot("05-film")
            tap("#d-close", 400)
    tap("#nav-lists", 500)
    shot("06-lists")
    if tap("[data-list=__seen]", 500):
        shot("07-seen")
    tap("#nav-search", 1300)
    shot("08-search")
    tap("#nav-theatres", 1800)
    shot("09-theatres")
    tap("#nav-discover", 400)
    if tap(".topbar .icon-btn >> nth=-1", 700):
        shot("10-settings")
    b.close()

print(f"shoot: {len(saved)} screenshots in {OUT.relative_to(HERE.parent.parent)}/ ({'dark' if DARK else 'light'}{', French' if FR else ''})")
if errors:
    print("shoot: JavaScript errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("shoot: no JavaScript errors")
