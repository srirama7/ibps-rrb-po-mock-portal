from pathlib import Path

portal_dir = Path(__file__).resolve().parents[1]
css = (portal_dir / "styles.css").read_text(encoding="utf-8")
js = (portal_dir / "app.js").read_text(encoding="utf-8")
data_json = (portal_dir / "data" / "tests.json").read_text(encoding="utf-8")

html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#0f2d4a">
  <meta name="description" content="20 Authentic IBPS RRB Officer Scale I (PO) Prelims Mock Tests based on 2021-2025 previous years exam trends. Complete with real sectional timers and full solutions.">
  <title>IBPS RRB Officer Scale I (PO) Prelims – 20 Authentic Mocks</title>
  <style>
REPLACE_CSS
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand">
      <div class="brand-mark">IB</div>
      <div class="brand-text">
        <strong>IBPS RRB Officer Scale I (PO) Prelims</strong>
        <small>Official Pattern 2026 Practice Portal • 20 Full Mocks</small>
      </div>
    </div>
    <div class="header-right">
      <div class="candidate-badge">
        <div class="candidate-avatar">AB</div>
        <div class="candidate-info">
          <b>Amogha Bhat</b>
          <span>Roll No: 2026-RRB-08492</span>
        </div>
      </div>
      <button id="homeButton" class="btn btn-ghost">All Mocks</button>
    </div>
  </header>
  <main id="app" class="main">
    <div style="text-align:center; padding: 60px 20px; font-size: 16px; color: #64748b;">
      Loading 20 Authentic IBPS RRB PO Mock Papers…
    </div>
  </main>
  <script>
    window.__IBPS_MOCK_DATA__ = REPLACE_DATA;
  </script>
  <script>
REPLACE_JS
  </script>
</body>
</html>
"""

html = html.replace("REPLACE_CSS", css).replace("REPLACE_DATA", data_json).replace("REPLACE_JS", js)

dest = portal_dir / "standalone.html"
dest.write_text(html, encoding="utf-8")
print(f"Successfully compiled standalone HTML to {dest} ({dest.stat().st_size} bytes)")
