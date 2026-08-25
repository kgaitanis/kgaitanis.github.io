#!/bin/sh
set -eu

max_bytes=15360

check_logo() {
  page=$1
  logo=$2
  alt=$3

  grep -Fq "class=\"case-logo" "$page"
  grep -Fq "src=\"../$logo\"" "$page"
  grep -Fq "alt=\"$alt\"" "$page"
  test -s "$logo"

  bytes=$(wc -c < "$logo")
  test "$bytes" -le "$max_bytes"
}

check_logo projects/eyemaps.html assets/images/logos/eyemaps.webp "eyeMaps logo"
grep -Fq 'class="case-logo case-logo-wide"' projects/eyemaps.html
eyemaps_width=$(sips -g pixelWidth assets/images/logos/eyemaps.webp 2>/dev/null | awk '/pixelWidth/ { print $2 }')
eyemaps_height=$(sips -g pixelHeight assets/images/logos/eyemaps.webp 2>/dev/null | awk '/pixelHeight/ { print $2 }')
test "$eyemaps_width" -gt $((eyemaps_height * 3))
check_logo projects/crealogix.html assets/images/logos/crealogix.webp "CREALOGIX logo"
check_logo projects/bity.html assets/images/logos/bity.webp "Bity logo"
check_logo projects/icpkit.html assets/images/logos/internet-computer.svg "Internet Computer logo"
check_logo projects/icpkit.html assets/images/logos/icpkit.webp "IcpKit logo"
grep -Fq 'class="case-logo-row"' projects/icpkit.html

grep -Fq ".case-logo" assets/styles.css
grep -Fq ".case-logo-row" assets/styles.css

grep -Fq 'class="project-title"' index.html
grep -Fq 'src="assets/images/logos/eyemaps.webp"' index.html
grep -Fq 'src="assets/images/logos/crealogix.webp"' index.html
grep -Fq 'src="assets/images/logos/bity.webp"' index.html
grep -Fq 'src="assets/images/logos/internet-computer.svg"' index.html
grep -Fq ".project-title" assets/styles.css
grep -Fq '<a class="project-card hero-project" href="projects/eyemaps.html">' index.html
grep -Fq '<a class="project-card side-project" href="projects/crealogix.html">' index.html
test "$(rg -o '<a class="project-card" href="projects/' index.html | wc -l | tr -d ' ')" = 2
if grep -Fq '<a class="project-title' index.html; then
  exit 1
fi
grep -Fq '<h3>eyeMaps</h3>' index.html
grep -Fq '<h3>Mobile Banking</h3>' index.html
grep -Fq '<h3>IcpKit</h3>' index.html
if grep -Fq 'src="assets/images/logos/icpkit.webp"' index.html; then
  exit 1
fi

grep -Fq 'src="../assets/images/bity-swiftui.webp"' projects/bity.html
test -s assets/images/bity-swiftui.webp
grep -Fq 'src="../assets/images/bity-flutter.webp"' projects/bity.html
test -s assets/images/bity-flutter.webp
grep -Fq 'src="../assets/images/eyemaps-hero.webp"' projects/eyemaps.html
test -s assets/images/eyemaps-hero.webp
test "$(wc -c < assets/images/eyemaps-hero.webp | tr -d ' ')" -le 262144
if rg -q 'src="https?://' projects/*.html index.html; then
  exit 1
fi

test "$(rg -o '<b>↔</b>' projects/icpkit.html | wc -l | tr -d ' ')" = 2
