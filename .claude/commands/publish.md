---
description: Publish the current Clap changes to the live app (only after the owner's go)
argument-hint: "[v1|v3|both]"
---

Publish Clap. Target: $ARGUMENTS (default: v1, the live app on `main`).

Only run this when I have explicitly said "publish" for these changes.

1. Syntax-check every `<script>` block of `index.html` (see CLAUDE.md › Testing). Stop if anything fails.
2. For v3 or both: `python3 tools/build-v3.py` to regenerate `v3/index.html`.
3. For v1 or both: `./bump.sh` (new APP_VERSION + version.json → phones show the update card).
4. Commit with `git -c user.name="Ludovic Pochon" -c user.email="ludovicpochondesign@gmail.com" commit`
   and a short, plain message, then push to `main`.
5. Tell me the new version number, what went live, and that phones get it by tapping Refresh on the update card.
