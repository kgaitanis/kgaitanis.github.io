import json
from html.parser import HTMLParser
from pathlib import Path


TECHNOLOGIES = [
    "Swift 6",
    "SwiftUI",
    "UIKit",
    "Swift Concurrency",
    "Mobile Architecture",
    "CI/CD",
    "Automated Testing",
    "Cryptography",
]


class EngineeringParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_engineering = False
        self.in_heading = False
        self.in_item = False
        self.heading = ""
        self.items = []
        self.json_ld = []
        self.in_json_ld = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "section" and attributes.get("id") == "engineering":
            self.in_engineering = True
        if self.in_engineering and tag == "h2":
            self.in_heading = True
        if self.in_engineering and tag == "li":
            self.in_item = True
            self.items.append("")
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self.in_json_ld = True
            self.json_ld.append("")

    def handle_endtag(self, tag):
        if tag == "section" and self.in_engineering:
            self.in_engineering = False
        if tag == "h2":
            self.in_heading = False
        if tag == "li":
            self.in_item = False
        if tag == "script" and self.in_json_ld:
            self.in_json_ld = False

    def handle_data(self, data):
        if self.in_heading:
            self.heading += data
        if self.in_item:
            self.items[-1] += data
        if self.in_json_ld:
            self.json_ld[-1] += data


parser = EngineeringParser()
parser.feed(Path("index.html").read_text())

assert parser.heading.strip() == "Engineering"
assert [item.strip() for item in parser.items] == TECHNOLOGIES

person = next(
    block
    for block in map(json.loads, parser.json_ld)
    if block.get("@type") == "Person"
)
structured_terms = ["Swift" if technology == "Swift 6" else technology for technology in TECHNOLOGIES]
assert all(technology in person["knowsAbout"] for technology in structured_terms)
