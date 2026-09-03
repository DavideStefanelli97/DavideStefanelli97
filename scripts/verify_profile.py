"""Validate the profile and optionally render it with GitHub's Markdown API.

--links checks public URLs without authentication.
--render sends README text to GitHub's stateless rendering endpoint and caches
the resulting HTML plus GitHub's public stylesheets under ignored tmp/readme-qa.
--serve exposes only that preview and the README's referenced images on loopback.
Nothing is committed, published or changed remotely.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
from html import escape
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import runpy
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "tmp" / "readme-qa"
PROFILE = "https://github.com/DavideStefanelli97"
HEADERS = {"User-Agent": "DavideStefanelli97-profile-validation"}


class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def request(url: str, data: bytes | None = None, method: str | None = None):
    headers = dict(HEADERS)
    if data is not None:
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "text/html"
    return urlopen(Request(url, data=data, headers=headers, method=method), timeout=30)


def luminance(colour: str) -> float:
    rgb = [int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
    return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))


def local_checks(markdown: str) -> list[str]:
    from PIL import Image

    assert not re.search(
        r"example\.com|your-handle|calibration\s+map|\{\{|\}\}|file://|[A-Z]:\\",
        markdown, re.I,
    ), "Placeholder or local-machine path in README"
    assert len(re.findall(r"^# ", markdown, re.M)) == 1, "One identity heading required"
    parser = Elements()
    parser.feed(markdown)
    assert not any(t in {"table", "script", "iframe", "style"} for t, _ in parser.tags)
    images = [a for t, a in parser.tags if t == "img"]
    assert len(images) == 4, "Expected one hero and three proof previews"
    paths = []
    total = 0
    for img in images:
        src = img["src"]
        assert not urlparse(src).scheme, f"Remote image dependency: {src}"
        path = (ROOT / src).resolve()
        assert path.is_relative_to(ROOT / "assets") and path.is_file(), src
        assert len(img.get("alt", "")) >= 30, f"Missing descriptive alt text: {src}"
        assert img.get("width") == "100%", f"Image must scale with content: {src}"
        paths.append(src)
        total += path.stat().st_size
        if path.suffix == ".svg":
            raw = path.read_text(encoding="utf-8")
            tree = ET.fromstring(raw)
            ns = {"s": "http://www.w3.org/2000/svg"}
            assert tree.find("s:title", ns) is not None
            assert tree.find("s:desc", ns) is not None
            assert "prefers-reduced-motion: reduce" in raw
            assert not re.search(r"<(?:script|foreignObject|image)\b|@import|onload=|onclick=", raw)
            for element in tree.iter():
                for attr, value in element.attrib.items():
                    if attr.rsplit("}", 1)[-1] in {"href", "src"}:
                        assert value.startswith("#"), f"External SVG reference: {value}"
            assert all(value.startswith("#") for value in re.findall(r"url\(([^)]+)\)", raw))
            animations = tree.findall(".//s:animateMotion", ns)
            assert len(animations) == 1
            assert animations[0].get("repeatCount") == "1"
            assert float(animations[0].get("dur", "0s").removesuffix("s")) <= 5
            assert animations[0].get("fill") == "freeze"
            print(f"PASS {src}: vector, one finite 4.5s motion, reduced-motion rule")
        else:
            with Image.open(path) as image:
                assert image.format == "WEBP" and image.n_frames == 1
                assert not image.getexif() and not image.info.get("xmp")
                assert image.width == 1200
                print(f"PASS {src}: {image.size}, one frame, no EXIF/XMP")
    assert total <= 4 * 1024 * 1024, f"Image budget exceeded: {total}"
    print(f"PASS referenced image payload: {total:,} bytes ({total / 1024:.1f} KiB)")
    for colour in ("#D5E7F4", "#6EE7F9", "#58C7B1", "#8FAABD"):
        ratio = (luminance(colour) + .05) / (luminance("#0B1320") + .05)
        assert ratio >= 4.5
        print(f"PASS hero contrast {colour} on #0B1320: {ratio:.2f}:1")
    generator = runpy.run_path(str(ROOT / "scripts" / "generate_assets.py"))
    expected = generator["hero_svg"]().encode("utf-8")
    actual = (ROOT / paths[0]).read_bytes()
    assert expected == actual, "Generated hero differs from its source"
    print("PASS deterministic SVG matches the generator")
    for url in urls(markdown):
        if url.startswith("#"):
            headings = re.findall(r"^#{1,6}\s+(.+)$", markdown, re.M)
            assert url[1:] in [slug(h) for h in headings], f"Missing anchor: {url}"
        elif not urlparse(url).scheme:
            assert (ROOT / unquote(url)).is_file(), f"Missing local link: {url}"
    return paths


def urls(markdown: str) -> list[str]:
    parser = Elements()
    parser.feed(markdown)
    return sorted(set(
        re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", markdown)
        + [a["href"] for t, a in parser.tags if t == "a" and "href" in a]
    ))


def slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text).lower()
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def check_link(url: str) -> tuple[str, bool]:
    try:
        with request(url, method="HEAD") as response:
            return f"PASS {response.status} {url}", True
    except (HTTPError, URLError, TimeoutError) as exc:
        # LinkedIn commonly rejects unauthenticated automated requests.
        # Its exact contact URL is independently verified in the definitive CV.
        if (isinstance(exc, HTTPError) and urlparse(url).hostname == "www.linkedin.com"
                and exc.code in {403, 405, 429, 999}):
            return f"MANUAL LinkedIn rejects automated validation: {url} ({exc})", True
        return f"FAIL {url} ({exc})", False


def render(markdown: str) -> None:
    QA.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({
        "text": markdown,
        "mode": "gfm",
        "context": "DavideStefanelli97/DavideStefanelli97",
    }).encode("utf-8")
    with request("https://api.github.com/markdown", data=payload) as response:
        rendered = response.read().decode("utf-8")
    (QA / "github-render.html").write_text(rendered, encoding="utf-8")
    # API output lacks the page-level heading anchors GitHub adds to a README.
    rendered = re.sub(
        r"<(h[1-6])([^>]*)>(.*?)</\1>",
        lambda m: f'<{m[1]} id="{escape(slug(m[3]))}"{m[2]}>{m[3]}</{m[1]}>',
        rendered, flags=re.S,
    )
    (QA / "preview-body.html").write_text(rendered, encoding="utf-8")
    with request(PROFILE) as response:
        profile_html = response.read().decode("utf-8")
    parser = Elements()
    parser.feed(profile_html)
    styles = [
        a["href"] for t, a in parser.tags
        if t == "link" and a.get("rel") == "stylesheet"
        and a.get("href", "").startswith("https://github.githubassets.com/assets/")
        and a.get("data-color-theme", "") in ("", "light", "dark")
    ]
    assert styles, "No GitHub stylesheets found; refusing an unstyled preview"
    for index, url in enumerate(dict.fromkeys(styles)):
        with request(url) as response:
            css = response.read()
        (QA / f"github-{index}.css").write_bytes(css)
    (QA / "render-manifest.json").write_text(json.dumps({
        "renderer": "GitHub REST /markdown, mode=gfm; no authentication",
        "readme_sha256": hashlib.sha256(markdown.encode("utf-8")).hexdigest(),
        "stylesheets": list(dict.fromkeys(styles)),
        "note": "Only preview heading IDs and a local responsive shell are added.",
    }, indent=2), encoding="utf-8")
    print(f"PASS GitHub GFM rendering; {len(set(styles))} GitHub stylesheets cached")


def serve(image_paths: list[str], port: int) -> None:
    manifest = json.loads((QA / "render-manifest.json").read_text(encoding="utf-8"))
    styles = [QA / f"github-{i}.css" for i in range(len(manifest["stylesheets"]))]
    assert styles and (QA / "preview-body.html").is_file()
    css_links = "".join(f'<link rel="stylesheet" href="/{p.name}">' for p in styles)
    allowed = {"/" + p: ROOT / p for p in image_paths}
    allowed.update({"/" + p.name: p for p in styles})

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/":
                current = (ROOT / "README.md").read_text(encoding="utf-8")
                manifest = json.loads((QA / "render-manifest.json").read_text(encoding="utf-8"))
                if hashlib.sha256(current.encode("utf-8")).hexdigest() != manifest["readme_sha256"]:
                    self.send_error(503, "README changed: run verify_profile.py --render first")
                    return
                body = (QA / "preview-body.html").read_text(encoding="utf-8")
                theme = "dark" if parsed.query == "theme=dark" else "light"
                content = (
                    '<!doctype html><html lang="en" data-color-mode="' + theme
                    + '" data-light-theme="light" data-dark-theme="dark"><head>'
                    + '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                    + '<title>Davide Stefanelli — GitHub README preview</title>' + css_links
                    + '<style>body{margin:0;background:var(--bgColor-default);color:var(--fgColor-default)}'
                    + '.qa-shell{box-sizing:border-box;max-width:900px;margin:32px auto;padding:32px;'
                    + 'border:1px solid var(--borderColor-default);border-radius:6px}'
                    + '@media(max-width:767px){.qa-shell{margin:16px;padding:16px}}</style>'
                    + '</head><body><main class="qa-shell"><article class="markdown-body">'
                    + body + '</article></main></body></html>'
                ).encode("utf-8")
                kind = "text/html; charset=utf-8"
            elif parsed.path in allowed:
                path = allowed[parsed.path]
                content = path.read_bytes()
                kind = {".css": "text/css", ".svg": "image/svg+xml", ".webp": "image/webp"}[path.suffix]
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Preview: http://127.0.0.1:{port}/?theme=light", flush=True)
    print(f"Dark:    http://127.0.0.1:{port}/?theme=dark", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--links", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    markdown = (ROOT / "README.md").read_text(encoding="utf-8")
    images = local_checks(markdown)
    guide = (ROOT / "assets" / "ASSET_GUIDE.md").read_text(encoding="utf-8")
    for url in urls(guide):
        if not urlparse(url).scheme and not url.startswith("#"):
            target = (ROOT / "assets" / unquote(url)).resolve()
            assert target.is_relative_to(ROOT) and target.is_file(), f"Missing guide link: {url}"
    print("PASS all local asset-guide links")
    if args.links:
        targets = sorted({url for url in urls(markdown) + urls(guide) if url.startswith("https://")})
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(check_link, targets))
        for message, _ in results:
            print(message)
        assert all(ok for _, ok in results), "Public links failed verification"
    if args.render:
        render(markdown)
    if args.serve:
        serve(images, args.port)


if __name__ == "__main__":
    main()
