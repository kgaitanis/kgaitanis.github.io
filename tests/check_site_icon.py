#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / "index.html", *sorted((ROOT / "projects").glob("*.html"))]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.favicons = []
        self.brand_icons = []
        self.in_brand = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        classes = values.get("class", "").split()
        if tag == "a" and "brand" in classes:
            self.in_brand = True
        if tag == "link" and "icon" in values.get("rel", "").split():
            self.favicons.append(values)
        if tag == "img" and self.in_brand:
            self.brand_icons.append(values)

    def handle_endtag(self, tag):
        if tag == "a" and self.in_brand:
            self.in_brand = False


def expected_asset_path(page, href):
    return (page.parent / href).resolve()


def test_svg_asset():
    icon = ROOT / "assets" / "images" / "kg-icon.svg"
    svg = ET.parse(icon).getroot()
    assert svg.attrib["viewBox"] == "0 0 64 64"
    assert svg.attrib["role"] == "img"
    assert svg.find("{http://www.w3.org/2000/svg}title").text == "KG"
    namespace = "{http://www.w3.org/2000/svg}"
    rectangles = svg.findall(f"{namespace}rect")
    lettering = svg.find(f"{namespace}g")
    assert len(rectangles) == 1, "the icon should have no separate accent bar"
    assert rectangles[0].attrib["fill"] == "#0b0d0f"
    assert lettering.attrib["stroke"] == "#c4ff72"
    assert len(lettering.findall(f"{namespace}path")) == 2
    assert "#f4f5f3" not in icon.read_text()


def test_every_page_exposes_the_same_icon():
    icon = (ROOT / "assets" / "images" / "kg-icon.svg").resolve()
    for page in PAGES:
        parser = PageParser()
        parser.feed(page.read_text())
        assert len(parser.favicons) == 1, f"{page}: missing or duplicate favicon"
        assert expected_asset_path(page, parser.favicons[0]["href"]) == icon
        assert parser.favicons[0].get("type") == "image/svg+xml"
        assert len(parser.brand_icons) == 1, f"{page}: missing or duplicate brand icon"
        brand_icon = parser.brand_icons[0]
        assert expected_asset_path(page, brand_icon["src"]) == icon
        assert brand_icon.get("alt") == ""
        assert brand_icon.get("width") == "32"
        assert brand_icon.get("height") == "32"


if __name__ == "__main__":
    test_svg_asset()
    test_every_page_exposes_the_same_icon()
    print(f"Site icon checks passed for {len(PAGES)} pages.")
