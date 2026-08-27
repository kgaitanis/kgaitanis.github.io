#!/usr/bin/env python3

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = {
    "projects/eyemaps.html": "2013–2017",
    "projects/crealogix.html": "2019–2022",
    "projects/bity.html": "2022–Mar 2026",
    "projects/icpkit.html": "2022–Present",
}
PAGES = [ROOT / "index.html", *(ROOT / page for page in PROJECTS)]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.hrefs = []
        self.sources = []
        self.json_ld = []
        self.in_json_ld = False
        self.h1_count = 0
        self.main_count = 0
        self.title_count = 0
        self.favicons = []
        self.downloads = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            self.ids.append(values["id"])
        if "href" in values:
            self.hrefs.append(values["href"])
        if "src" in values:
            self.sources.append(values["src"])
        if tag == "h1":
            self.h1_count += 1
        if tag == "main":
            self.main_count += 1
        if tag == "title":
            self.title_count += 1
        if tag == "link" and "icon" in values.get("rel", "").split():
            self.favicons.append(values.get("href"))
        if tag == "a" and "download" in values:
            self.downloads.append(values.get("href"))
        if tag == "script" and values.get("type") == "application/ld+json":
            self.in_json_ld = True
            self.json_ld.append("")

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_json_ld = False

    def handle_data(self, data):
        if self.in_json_ld:
            self.json_ld[-1] += data


def local_target(page, reference):
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    return (page.parent / unquote(parsed.path)).resolve()


def check_page(page):
    source = page.read_text()
    assert source.lower().startswith("<!doctype html>"), f"{page}: missing doctype"
    assert '<html lang="en"' in source, f"{page}: missing language"

    parser = PageParser()
    parser.feed(source)

    assert parser.title_count == 1, f"{page}: expected one title"
    assert parser.main_count == 1, f"{page}: expected one main element"
    assert parser.h1_count == 1, f"{page}: expected one h1"
    assert len(parser.ids) == len(set(parser.ids)), f"{page}: duplicate IDs"
    assert len(parser.favicons) == 1, f"{page}: expected one favicon"

    for reference in [*parser.hrefs, *parser.sources]:
        target = local_target(page, reference)
        if target is not None:
            assert target.is_file(), f"{page}: missing local asset {reference}"

    for source_reference in parser.sources:
        assert not urlsplit(source_reference).scheme, (
            f"{page}: images and media should be served locally"
        )

    return parser


def check_person_metadata(parser):
    blocks = [json.loads(block) for block in parser.json_ld]
    people = [block for block in blocks if block.get("@type") == "Person"]
    assert len(people) == 1, "index.html: expected one Person JSON-LD block"

    person = people[0]
    required = {"@context", "name", "url", "jobTitle", "email", "sameAs"}
    assert required <= person.keys(), "index.html: incomplete Person metadata"
    assert person["@context"] == "https://schema.org"
    assert urlsplit(person["url"]).scheme == "https"
    assert person["email"].startswith("mailto:")
    assert all(urlsplit(url).scheme == "https" for url in person["sameAs"])


def check_project_dates():
    index = (ROOT / "index.html").read_text()
    for relative_page, years in PROJECTS.items():
        assert f'href="{relative_page}"' in index
        assert years in index
        assert years in (ROOT / relative_page).read_text()


def main():
    assert all(page.is_file() for page in PAGES), "required page missing"
    parsers = {page: check_page(page) for page in PAGES}
    check_person_metadata(parsers[ROOT / "index.html"])
    check_project_dates()

    index_downloads = parsers[ROOT / "index.html"].downloads
    assert len(index_downloads) >= 1, "index.html: missing CV download"
    assert any(reference.lower().endswith(".pdf") for reference in index_downloads)

    print(f"Site integrity checks passed for {len(PAGES)} pages.")


if __name__ == "__main__":
    main()
