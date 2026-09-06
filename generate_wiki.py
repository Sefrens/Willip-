from __future__ import annotations

import html
import re
import shutil
from pathlib import Path
from datetime import datetime, timezone
import json

import markdown
import yaml

ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "wiki_config.yaml"
OUTPUT = ROOT / "docs"

CATEGORY_NAMES = {
    "npc": "Personen",
    "location": "Orte",
    "faction": "Fraktionen",
    "session": "Sessions",
    "item": "Gegenstände",
    "creature": "Kreaturen",
    "phenomenon": "Phänomene",
}

def load_config():
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def should_ignore(path: Path, config: dict) -> bool:
    parts = set(path.parts)
    for folder in config.get("exclude_folders", []):
        if folder in parts:
            return True
    return False

def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not match:
        return {}, text
    data = yaml.safe_load(match.group(1)) or {}
    return data, match.group(2)

def filter_visibility(text: str, unlocks: set[str]) -> str:
    # :::gm ... ::: entfernen
    text = re.sub(r":::gm\s*\n.*?:::", "", text, flags=re.S | re.I)

    # :::player ... ::: Inhalt behalten, Marker entfernen
    text = re.sub(
        r":::player\s*\n(.*?):::",
        lambda m: m.group(1),
        text,
        flags=re.S | re.I,
    )

    # :::unlock id=name ... :::
    def unlock_replacer(match):
        unlock_id = match.group(1).strip()
        content = match.group(2)
        return content if unlock_id in unlocks else ""

    text = re.sub(
        r":::unlock\s+id=([A-Za-z0-9_.:-]+)\s*\n(.*?):::",
        unlock_replacer,
        text,
        flags=re.S | re.I,
    )

    # Unbekannte Sichtbarkeitsblöcke sicher entfernen.
    text = re.sub(r":::[A-Za-z].*?\n.*?:::", "", text, flags=re.S)
    return text.strip()

def extract_title(frontmatter: dict, body: str, fallback: str):
    if frontmatter.get("title"):
        return str(frontmatter["title"])
    match = re.search(r"^#\s+(.+)$", body, re.M)
    if match:
        return match.group(1).strip()
    return fallback

def slugify(value: str) -> str:
    value = value.lower().strip()
    replacements = {
        "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "artikel"

def convert_obsidian_links(md_text: str, title_to_url: dict[str, str]) -> str:
    def repl(match):
        target = match.group(1).split("|")[0].strip()
        label = match.group(2) or target
        url = title_to_url.get(target)
        if url:
            return f"[{label}]({url})"
        return label

    return re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", repl, md_text)

def build_nav(articles):
    categories = {}
    for article in articles:
        categories.setdefault(article["category"], []).append(article)

    parts = []
    for category, entries in sorted(categories.items()):
        label = CATEGORY_NAMES.get(category, category.title())
        links = "".join(
            f'<li><a href="{html.escape(a["url"])}">{html.escape(a["title"])}</a></li>'
            for a in sorted(entries, key=lambda x: x["title"].lower())
        )
        parts.append(f"<section><h3>{html.escape(label)}</h3><ul>{links}</ul></section>")
    return "\n".join(parts)

def render_page(site, article, content_html, nav_html):
    title = html.escape(article["title"])
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} – {html.escape(site["title"])}</title>
<link rel="stylesheet" href="assets/style.css">
<script defer src="assets/search.js"></script>
</head>
<body>
<header>
  <a class="brand" href="index.html">{html.escape(site["title"])}</a>
  <p>{html.escape(site.get("subtitle", ""))}</p>
</header>
<div class="layout">
<aside>
<input id="search" type="search" placeholder="Wiki durchsuchen...">
<div id="search-results"></div>
<nav>{nav_html}</nav>
</aside>
<main>
<article>
{content_html}
</article>
</main>
</div>
<footer>Stand: Session {site.get("campaign_session", "?")} · Generiert am {datetime.now().strftime("%d.%m.%Y %H:%M")}</footer>
</body>
</html>"""

def main():
    config = load_config()
    site = config.get("site", {})
    unlocks = set(config.get("unlocks", []))
    include_folders = config.get("include_folders", [])

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()

    source_files = []
    for folder in include_folders:
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue
        for path in folder_path.rglob("*.md"):
            if not should_ignore(path.relative_to(ROOT), config):
                source_files.append(path)

    raw_articles = []
    for path in source_files:
        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)

        if fm.get("published", True) is False:
            continue

        visible = filter_visibility(body, unlocks)
        if not visible:
            continue

        title = extract_title(fm, visible, path.stem)
        category = str(fm.get("type", "article")).lower()
        raw_articles.append({
            "path": path,
            "frontmatter": fm,
            "body": visible,
            "title": title,
            "category": category,
            "slug": slugify(title),
        })

    # Eindeutige Dateinamen
    used = set()
    for article in raw_articles:
        base = article["slug"]
        slug = base
        n = 2
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        used.add(slug)
        article["slug"] = slug
        article["url"] = f"{slug}.html"

    title_to_url = {a["title"]: a["url"] for a in raw_articles}

    articles = []
    for article in raw_articles:
        linked_md = convert_obsidian_links(article["body"], title_to_url)
        content_html = markdown.markdown(
            linked_md,
            extensions=["extra", "tables", "fenced_code"]
        )
        article["html"] = content_html
        articles.append(article)

    assets = OUTPUT / "assets"
    assets.mkdir()

    (assets / "style.css").write_text(STYLE, encoding="utf-8")
    (assets / "search.js").write_text(SEARCH_JS, encoding="utf-8")

    nav_html = build_nav(articles)

    search_index = [
        {
            "title": a["title"],
            "url": a["url"],
            "category": CATEGORY_NAMES.get(a["category"], a["category"].title()),
            "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", a["html"]))[:1500],
        }
        for a in articles
    ]
    (assets / "search-index.json").write_text(
        json.dumps(search_index, ensure_ascii=False),
        encoding="utf-8"
    )

    for article in articles:
        page = render_page(site, article, article["html"], nav_html)
        (OUTPUT / article["url"]).write_text(page, encoding="utf-8")

    grouped = {}
    for a in articles:
        grouped.setdefault(a["category"], []).append(a)

    sections = []
    for category, entries in sorted(grouped.items()):
        label = CATEGORY_NAMES.get(category, category.title())
        cards = "".join(
            f'<li><a href="{html.escape(a["url"])}">{html.escape(a["title"])}</a></li>'
            for a in sorted(entries, key=lambda x: x["title"].lower())
        )
        sections.append(f"<section><h2>{html.escape(label)}</h2><ul>{cards}</ul></section>")

    index_content = f"""
<h1>{html.escape(site.get("title", "Wiki"))}</h1>
<p class="lead">{html.escape(site.get("subtitle", ""))}</p>
<p>Dieses Wiki enthält ausschließlich Informationen, die für die Abenteurer freigegeben wurden.</p>
{''.join(sections)}
"""

    index_article = {"title": site.get("title", "Wiki")}
    (OUTPUT / "index.html").write_text(
        render_page(site, index_article, index_content, nav_html),
        encoding="utf-8"
    )

    print(f"Wiki erfolgreich erstellt: {OUTPUT}")
    print(f"Artikel exportiert: {len(articles)}")
    print(f"Freigeschaltete Informationsblöcke: {len(unlocks)}")

STYLE = r"""
:root {
  --bg: #181714;
  --panel: #24221d;
  --text: #e8e3d5;
  --muted: #aaa393;
  --accent: #c69b50;
  --line: #484338;
}
* { box-sizing: border-box; }
body {
  margin: 0; font-family: Georgia, serif; background: var(--bg);
  color: var(--text); line-height: 1.65;
}
header {
  padding: 2rem max(2rem, calc((100vw - 1200px)/2));
  border-bottom: 1px solid var(--line); background: var(--panel);
}
.brand { color: var(--accent); font-size: 1.8rem; text-decoration: none; }
header p { margin: .25rem 0 0; color: var(--muted); }
.layout { display: grid; grid-template-columns: 300px 1fr; max-width: 1400px; margin: auto; }
aside { padding: 1.5rem; border-right: 1px solid var(--line); min-height: 80vh; }
aside section { margin: 1.5rem 0; }
aside h3 { color: var(--accent); margin-bottom: .4rem; }
aside ul { padding-left: 1.2rem; margin: 0; }
main { padding: 2rem; max-width: 900px; }
article h1, article h2, article h3 { color: var(--accent); }
a { color: #d7b46e; }
input {
  width: 100%; padding: .7rem; background: #111; color: var(--text);
  border: 1px solid var(--line); border-radius: 4px;
}
.lead { color: var(--muted); font-size: 1.15rem; }
pre, code { background: #111; padding: .2rem .4rem; border-radius: 4px; }
pre { padding: 1rem; overflow-x: auto; }
footer { padding: 2rem; text-align: center; color: var(--muted); border-top: 1px solid var(--line); }
#search-results { margin-top: .8rem; }
#search-results a { display: block; padding: .4rem 0; }
@media (max-width: 800px) {
  .layout { grid-template-columns: 1fr; }
  aside { border-right: 0; border-bottom: 1px solid var(--line); min-height: auto; }
}
"""

SEARCH_JS = r"""
let wikiIndex = [];

fetch("assets/search-index.json")
  .then(r => r.text())
  .then(text => {
    // Die Datei wird vom Generator als YAML erzeugt, aber hier genügt
    // ein einfacher Fallback-Parser für die erzeugte Listenstruktur nicht.
    // Deshalb wird bei GitHub Pages eine JSON-Version bevorzugt.
  })
  .catch(() => {});

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("search");
  const results = document.getElementById("search-results");
  if (!input || !results) return;

  fetch("assets/search-index.json")
    .then(r => r.json())
    .then(data => wikiIndex = data)
    .catch(() => wikiIndex = []);

  input.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    if (!q) { results.innerHTML = ""; return; }

    const matches = wikiIndex.filter(item =>
      item.title.toLowerCase().includes(q) ||
      item.text.toLowerCase().includes(q)
    ).slice(0, 8);

    results.innerHTML = matches.map(item =>
      `<a href="${item.url}">${item.title}<br><small>${item.category}</small></a>`
    ).join("") || "<small>Keine Treffer</small>";
  });
});
"""

if __name__ == "__main__":
    main()
