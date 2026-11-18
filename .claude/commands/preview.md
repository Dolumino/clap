---
description: Build the Clap preview (V1 or V3), tap through it on an iPhone 15 screen and show the screenshots
argument-hint: "[v1|v3] [note]"
---

Build and check a preview of Clap. Argument: $ARGUMENTS (default: v1).

1. If the argument mentions v3: run `python3 tools/build-v3.py` first, then
   `CLAP_APP=v3/index.html CLAP_OUT=tools/preview/preview-v3.html python3 tools/preview/build.py "<note>"`.
   Otherwise: `python3 tools/preview/build.py "<note>"` (→ `tools/preview/preview.html`).
2. Run `python3 tools/preview/shoot.py <the preview file>` (add `--dark` and/or `--fr` when relevant).
   Fix any JavaScript error it reports before going on.
3. Look at the screenshots in `tools/preview/shots/` that matter for the change, and show them to me.
4. Tell me in a few lines what changed and what I should look at. Do not publish: wait for my "publish".
