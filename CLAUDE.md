# Clap — project guide for Claude

Clap is a mobile web app (PWA) that helps choose a film for tonight without scrolling streaming catalogs.
Owner: Ludo (freelance Senior Product Designer, Paris). Shared with his partner on two phones.

- Live app (V1): https://dolumino.github.io/clap/ — served by GitHub Pages from `main`
- Test app (V3): https://dolumino.github.io/clap/v3/ — same storage, installs as a separate "Clap V3"

## Working rules (from the owner — always follow)

1. **Preview before live.** Build an HTML preview of every change and show it first.
   Never update the live app without explicit confirmation. If a message says "publish",
   test quickly and publish directly.
2. **Every publish:** run `./bump.sh` (sets `APP_VERSION` in index.html and `version.json`,
   which triggers the in-app update card), commit, push to `main`.
   Commit identity: `git -c user.name="Ludovic Pochon" -c user.email="ludovicpochondesign@gmail.com" commit`.
3. **Keep the logo** unless asked. Toasts only for major changes (deletions with Undo, errors, new version).
4. Primary buttons are only active when something changed (`setPrimary`, `dlgSync`, `setupSync`).
5. Micro-interactions: no bounce, no size change ("ink" spreads from the touch point, `--ink` @property).
6. Interface must be **fully English or fully French** (one Language setting drives UI + TMDB content).
7. No zoom anywhere; mobile-first; touch targets ≥ 44 px; respect `prefers-reduced-motion`.

## Files

| Path | What |
|---|---|
| `index.html` | **The whole V1 app**: HTML + CSS + JS in one file (~250 KB). |
| `v3/skin.css` | V3 identity layer (Poster × Kodak). Visual only. |
| `v3/index.html` | **Generated** — `python3 tools/build-v3.py`. Never edit by hand. |
| `v3/manifest.webmanifest` | V3's own manifest (separate home-screen app). |
| `manifest.webmanifest`, `icon-*-v3.png`, `apple-touch-icon-v3.png` | PWA install. Icon files are versioned in their names to beat phone caches. |
| `version.json`, `bump.sh` | Update detection. |
| `tools/preview/build.py` | Wraps the app with a mock `fetch` (sample films, posters, cinemas) into a standalone `preview.html`. `CLAP_APP=… CLAP_OUT=… python3 tools/preview/build.py "note"`. Needs Pillow. |
| `tools/preview/shoot.py` | Taps through a preview at iPhone 15 size (393×852), saves 10 screenshots to `tools/preview/shots/`, fails on JavaScript errors. Options: `--dark`, `--fr`. |
| `tools/build-v3.py` | Builds V3 from `index.html` + `v3/skin.css`. |
| `tools/setup.sh` | Installs Pillow + Playwright (+ Chromium) if missing. Runs automatically at session start (`.claude/settings.json` hook). |
| `.claude/commands/` | `/preview [v1\|v3]` builds + screenshots a preview; `/publish [v1\|v3\|both]` bumps, commits, pushes (only after the owner says "publish"). |
| `design/icons/` | SVG sources of the app icon (cream clapperboard on brick). |

## Branches

- `main` — live. GitHub Pages serves it.
- `pending-v1-update` — **V1 changes not yet live** (results rows with % beside title + mood tags,
  Tonight's pick order title / year · director / duration, day + morning/afternoon/night label).
  V3 is built from this branch's `index.html`. When the owner says "replace" or approves V1:
  merge it into `main`, then `./bump.sh`, commit, push.
- `pending-update` — stale; safe to delete.

## Architecture (index.html)

- Two `<script>` blocks: a tiny no-zoom guard, then the app inside an IIFE (`"use strict"`).
- **i18n:** `UI_FR` (from saved `cfg.lang` or the phone language), `LOC`, `LANG2`. The UI is written in English;
  a MutationObserver translates text nodes and aria/placeholder attributes with the `FR` dictionary +
  `FRX` regex patterns. Data tables (genres, moods, fame, periods…) are translated at source when `UI_FR`.
  New UI strings → add the French to `FR` (or a pattern to `FRX`). Film titles etc. are protected by `NOTR` selectors.
- **Storage:** localStorage key `cesoir.tmdb.v1` → `{cfg:{key,region,lang}, s (filters), lists, meta, theme, themeMode, seen:{id:ISOdate}, place, radius}`.
  Filters are cleared at every launch. V1 and V3 share this key.
- **Views:** Discover (filters → results), Search, Lists (lists, list detail, Seen diary), In theatres, Settings (`openSetup(true)`), film detail overlay.
- **Data:** TMDB v3 (discover, movie details with `append_to_response=credits,watch/providers`, search, trending, now_playing, watch providers);
  Photon (komoot) geocoding; Overpass `amenity=cinema`. Showtimes = web search (no free showtimes API).
- **Ranking:** `scoreFilm` (mood genres, fame level, era, who's watching…). Results in rounds of 10 (`round`, `maxRound`, `pool`, de-duplicated by id and title+year).
  Surprise me guarantees 5–10 results by widening criteria.
- **Platforms:** `APPS` table → open the app if installed, else the store (Android intents / iOS schemes); website on desktop.
- **Limits:** moods max 3, genres max 5. Seen = id → date. Lists: Favorites (`fav`) + custom; remove from all lists when in ≥ 2.

## Design

**V1 (live, "Cinema editorial · Brick"):** Archivo (display, condensed) + Inter. Light bg `#f5ede4`, dark `#130d0b`,
accent brick `--amber` `#913220` / `#ad4428`, `--amber-text` `#913220` / `#f2a283`. Glass layer (`--glass*` tokens), soft brick gradients.

**V3 (test, "Poster × Kodak"):** Swiss mid-century print. Brand colours rust `#C74D1E`, mustard `#EBB83F`,
cream `#F9F2DA`, brown `#53413D`; small rust text uses `#A63E14` for AA contrast. Outfit ExtraBold (stand-in for Creo/Gilroy)
+ Geologica. Square corners, flat surfaces, light hairline dividers, numbered sections ("001" over a double rule),
big rank numerals, logo = three slanted bands + "clap." in a square, film-black tab bar.

Max 2 fonts, sans-serif only. Icons are inline SVG from the `ICONS` dictionary via `icon(name, filled)`.

## Testing

`python3 tools/preview/build.py "note" && python3 tools/preview/shoot.py` (or `/preview`). The preview is self-contained
(mock TMDB, Photon, Overpass); real TMDB calls need the owner's key, which lives only in his browser. Quick syntax check of the app scripts:

```bash
node -e "const s=require('fs').readFileSync('index.html','utf8');const re=/<script>([\s\S]*?)<\/script>/g;let m;while(m=re.exec(s)){new Function(m[1])}console.log('ok')"
```
