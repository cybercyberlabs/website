#!/usr/bin/env python3
"""Rebuild the site feed from publications.json.

Edit publications.json when a report is published, then run this script.
It rewrites feed.xml and publications.js, which the home page loads.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "publications.json"
FEED = ROOT / "feed.xml"
PAGE_DATA = ROOT / "publications.js"
REQUIRED = ("label", "title", "summary", "published", "html", "pdf")


def xml_text(value):
    return escape(str(value), {'"': "&quot;", "'": "&apos;"})


def rfc822(date_str):
    published = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return published.strftime("%a, %d %b %Y %H:%M:%S GMT")


def load_catalog():
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    site = data["site"]
    publications = data["publications"]
    if not publications:
        raise SystemExit("publications.json has no publications")

    seen = set()
    for item in publications:
        missing = [field for field in REQUIRED if not item.get(field)]
        if missing:
            raise SystemExit(f"{item.get('title', 'publication')} is missing {', '.join(missing)}")
        datetime.strptime(item["published"], "%Y-%m-%d")
        for field in ("html", "pdf"):
            path = ROOT / item[field]
            if not path.is_file():
                raise SystemExit(f"missing file for {item['title']}: {item[field]}")
        if item["html"] in seen:
            raise SystemExit(f"duplicate report path: {item['html']}")
        seen.add(item["html"])

    publications.sort(key=lambda item: item["published"], reverse=True)
    return site, publications


def absolute(site_url, path):
    return site_url.rstrip("/") + "/" + path.lstrip("/")


def render_feed(site, publications):
    site_url = site["url"]
    feed_url = absolute(site_url, site["feedPath"])
    newest = rfc822(publications[0]["published"])
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        f"    <title>{xml_text(site['title'])}</title>",
        f"    <link>{xml_text(site_url)}</link>",
        f"    <description>{xml_text(site['description'])}</description>",
        f"    <language>{xml_text(site['language'])}</language>",
        f"    <lastBuildDate>{newest}</lastBuildDate>",
        f'    <atom:link href="{xml_text(feed_url)}" rel="self" type="application/rss+xml"/>',
    ]
    for item in publications:
        page = absolute(site_url, item["html"])
        pdf = ROOT / item["pdf"]
        lines.extend([
            "    <item>",
            f"      <title>{xml_text(item['title'])}</title>",
            f"      <link>{xml_text(page)}</link>",
            f'      <guid isPermaLink="true">{xml_text(page)}</guid>',
            f"      <pubDate>{rfc822(item['published'])}</pubDate>",
            f"      <description>{xml_text(item['summary'])}</description>",
            (
                f'      <enclosure url="{xml_text(absolute(site_url, item["pdf"]))}" '
                f'length="{pdf.stat().st_size}" type="application/pdf"/>'
            ),
            "    </item>",
        ])
    lines.extend(["  </channel>", "</rss>", ""])
    return "\n".join(lines)


def render_page_data(publications):
    payload = json.dumps(publications, indent=2, ensure_ascii=False)
    return (
        "// Generated from publications.json by scripts/build_feed.py. Do not edit.\n"
        f"const publications = {payload};\n"
    )


def main():
    check = "--check" in sys.argv[1:]
    site, publications = load_catalog()
    feed = render_feed(site, publications)
    page_data = render_page_data(publications)
    if check:
        current_feed = FEED.read_text(encoding="utf-8") if FEED.exists() else ""
        current_page = PAGE_DATA.read_text(encoding="utf-8") if PAGE_DATA.exists() else ""
        if current_feed != feed or current_page != page_data:
            raise SystemExit("feed is out of date. Run: python3 scripts/build_feed.py")
        return
    FEED.write_text(feed, encoding="utf-8")
    PAGE_DATA.write_text(page_data, encoding="utf-8")
    print(f"wrote {FEED.relative_to(ROOT)} and {PAGE_DATA.relative_to(ROOT)} ({len(publications)} reports)")


if __name__ == "__main__":
    main()
