"""Local layout approximation, not GitHub's sanitizer. Requires markdown-it-py.

python scripts/preview_readme.py
python -m http.server 8765 --bind 127.0.0.1
Open http://127.0.0.1:8765/output/profile-preview.html
"""
from pathlib import Path
from markdown_it import MarkdownIt

root = Path(__file__).resolve().parents[1]
body = MarkdownIt("commonmark", {"html": True}).enable("table").render(
    (root / "README.md").read_text(encoding="utf-8")
)
body = body.replace('<h2>Selected projects</h2>', '<h2 id="selected-projects">Selected projects</h2>')
body = body.replace('href="#', 'href="output/profile-preview.html#')
html = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<base href="../"><title>Davide Stefanelli · Profile preview</title>
<style>
:root{color-scheme:dark;--bg:#0d1117;--text:#e6edf3;--muted:#9198a1;--border:#3d444d;--stripe:#151b23;--link:#79c0ff}
body.light{color-scheme:light;--bg:#fff;--text:#1f2328;--muted:#59636e;--border:#d1d9e0;--stripe:#f6f8fa;--link:#0969da}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
nav{position:sticky;top:0;z-index:1;padding:12px 24px;background:var(--bg);border-bottom:1px solid var(--border);font-size:13px;display:flex;gap:16px;align-items:center}
button{background:var(--stripe);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:6px 12px;cursor:pointer}
article{max-width:896px;margin:24px auto;padding:32px;border:1px solid var(--border);border-radius:6px}
body.narrow article{max-width:390px;padding:16px}
p,table{margin-top:0;margin-bottom:16px}a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}
h2{font-size:24px;line-height:1.25;margin:24px 0 16px;padding-bottom:.3em;border-bottom:1px solid var(--border)}
h3{font-size:20px;line-height:1.25;margin:24px 0 16px}img{max-width:100%;height:auto}sub{font-size:12px}
table{border-collapse:collapse;display:block;width:max-content;max-width:100%;overflow:auto}td,th{border:1px solid var(--border);padding:6px 13px}tr:nth-child(2n){background:var(--stripe)}
td p:last-child{margin-bottom:0}hr{height:4px;border:0;background:var(--border);margin:24px 0}
@media(max-width:600px){article{margin:12px 8px;padding:16px}nav{padding:8px;font-size:11px}}
</style>
<nav>Local README preview · GitHub layout approximation <button onclick="document.body.classList.toggle('light')">Light / dark</button><button onclick="document.body.classList.toggle('narrow')">390px / desktop</button></nav>
<article>__BODY__</article></html>'''
output = root / "output" / "profile-preview.html"
output.parent.mkdir(exist_ok=True)
output.write_text(html.replace("__BODY__", body), encoding="utf-8")
print(output)
