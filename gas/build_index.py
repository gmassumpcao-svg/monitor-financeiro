#!/usr/bin/env python3
"""Build gas/Index.html with docs/styles.css + docs/js/*.js inlined."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = ROOT / "gas" / "Index.html"

CSS = (DOCS / "styles.css").read_text(encoding="utf-8")
JS_FILES = [
    DOCS / "js" / "api.js",
    DOCS / "js" / "summary.js",
    DOCS / "js" / "agent.js",
    DOCS / "js" / "app.js",
]
HTML = (DOCS / "index.html").read_text(encoding="utf-8")

# Drop external stylesheet; inject inline CSS + base for Apps Script iframe.
HTML = HTML.replace(
    '  <link rel="stylesheet" href="./styles.css" />\n',
    '  <base target="_top" />\n  <style>\n' + CSS + "\n  </style>\n",
)

# Replace external scripts with inlined bundles (keep MONITOR_CONFIG).
old_scripts = """  <script src="./js/config.js"></script>
  <script src="./js/api.js"></script>
  <script src="./js/summary.js"></script>
  <script src="./js/agent.js"></script>
  <script src="./js/app.js"></script>
"""

parts = [
    '  <script>\n    window.MONITOR_CONFIG = { apiUrl: "", apiToken: "" };\n  </script>\n'
]
for path in JS_FILES:
    parts.append("  <script>\n" + path.read_text(encoding="utf-8") + "\n  </script>\n")

if old_scripts not in HTML:
    raise SystemExit("docs/index.html script block not found — update build_index.py")

HTML = HTML.replace(old_scripts, "".join(parts))
OUT.write_text(HTML, encoding="utf-8")
print(f"Wrote {OUT} ({len(HTML.splitlines())} lines)")
