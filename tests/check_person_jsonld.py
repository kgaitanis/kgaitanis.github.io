import json
from html.parser import HTMLParser
from pathlib import Path


class JsonLdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_json_ld = False
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self.in_json_ld = True
            self.blocks.append("")

    def handle_endtag(self, tag):
        if tag == "script" and self.in_json_ld:
            self.in_json_ld = False

    def handle_data(self, data):
        if self.in_json_ld:
            self.blocks[-1] += data


parser = JsonLdParser()
parser.feed(Path("index.html").read_text())
people = [
    json.loads(block)
    for block in parser.blocks
    if json.loads(block).get("@type") == "Person"
]

assert len(people) == 1, people
person = people[0]
assert person["@context"] == "https://schema.org"
assert person["name"] == "Konstantinos Gaitanis"
assert person["url"] == "https://kgaitanis.github.io/"
assert person["jobTitle"] == "Mobile Architect and Senior iOS Engineer"
assert person["email"] == "mailto:k.gaitanis@protonmail.com"
assert person["telephone"] == "+41765728189"
assert person["sameAs"] == [
    "https://www.linkedin.com/in/gaitanis",
    "https://github.com/kgaitanis",
]
assert person["address"] == {
    "@type": "PostalAddress",
    "addressLocality": "Zürich",
    "addressCountry": "CH",
}
assert set(person["knowsAbout"]) == {
    "Swift",
    "SwiftUI",
    "UIKit",
    "Swift Concurrency",
    "Mobile Architecture",
    "CI/CD",
    "Automated Testing",
    "Fintech",
    "Cryptography",
    "Blockchain",
    "3D mapping",
}
