from html.parser import HTMLParser
from pathlib import Path


EXPECTED_YEARS = {
    "projects/eyemaps.html": "2013–2017",
    "projects/crealogix.html": "2019–2022",
    "projects/bity.html": "2022–2026",
    "projects/icpkit.html": "2022–2025",
}


class YearParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.project_card = None
        self.in_card_year = False
        self.card_years = {}
        self.in_case_year = False
        self.case_years = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set(attributes.get("class", "").split())
        if tag == "a" and "project-card" in classes:
            self.project_card = attributes.get("href")
        if "project-years" in classes and self.project_card:
            self.in_card_year = True
        if "case-years" in classes:
            self.in_case_year = True

    def handle_endtag(self, tag):
        if self.in_card_year and tag == "span":
            self.in_card_year = False
        if self.in_case_year and tag == "span":
            self.in_case_year = False
        if tag == "a" and self.project_card:
            self.project_card = None

    def handle_data(self, data):
        text = data.strip()
        if self.in_card_year and text:
            self.card_years[self.project_card] = text
        if self.in_case_year and text:
            self.case_years.append(text)


index_parser = YearParser()
index_parser.feed(Path("index.html").read_text())
assert index_parser.card_years == EXPECTED_YEARS, index_parser.card_years

for page, expected_years in EXPECTED_YEARS.items():
    parser = YearParser()
    parser.feed(Path(page).read_text())
    assert parser.case_years == [expected_years], (page, parser.case_years)
