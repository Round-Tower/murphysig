# Signed: Kev + claude-opus-5-5, 2026-10-07
# Format: MurphySig v0.4 (https://murphysig.dev/spec)
# Prior: Unknown (new file)
#
# Context: Pins for build_hero.py and the committed assets/hero.svg — an SVG
# GitHub will actually animate inside <img>, a banner that says only what the
# README says (qualified the way the README qualifies it), and a sample
# signature in the spec's own shape. CI runs these with pytest alone; the
# byte-for-byte rebuild check needs fonttools + brotli and skips without them.
#
# Confidence: 0.85 - string-level pins on a generated file; the look itself is
# verified by eye (contact sheets), not here.
#
# Reviews:
#
# 2026-10-15 (claude-opus-5-5): the banner-link pin now parses the href and
# compares the host. The substring match CodeQL flagged
# (py/incomplete-url-substring-sanitization) passed a lookalike host such as
# murphysig.dev.example.com. The SVG is now parsed as XML, since a malformed
# one renders nothing in <img>. Its accessible name has to resolve too:
# <title> first, aria-labelledby naming real ids. Confidence now 0.9.
#
# 2026-10-15 (claude-opus-5-5): pre-push review fold. .hostname drops a port
# and a user@ prefix, so the pin compares (scheme, netloc) instead. The regex
# had also lost the old pin's "above the <h1>" guarantee; it searches only the
# text above the title again. Both mutants were green before, red now.
# Confidence now 0.9.

import re
from itertools import pairwise
from urllib.parse import urlsplit
from xml.etree import ElementTree

import build_hero as hero
import pytest

REPO = hero.REPO
README = (REPO / "README.md").read_text()


def svg() -> str:
    return hero.OUTPUT.read_text()


# ── GitHub-safe ────────────────────────────────────────────────────────────

def test_the_readme_shows_the_repo_hero():
    src = hero.OUTPUT.relative_to(REPO).as_posix()
    above_the_title = README.split("<h1")[0]
    banner = re.search(rf'<a href="([^"]+)">\s*<img src="{re.escape(src)}"', above_the_title)
    assert banner, "the hero is the README's banner: above the title, inside its link"
    link = urlsplit(banner.group(1))
    # the banner still links the site: compare the whole parsed authority, never a
    # substring. Not .hostname either, which drops a port or a user@ prefix.
    assert (link.scheme, link.netloc) == ("https", "murphysig.dev")


def test_the_svg_is_self_contained():
    s = svg()
    assert "<script" not in s                                   # stripped inside <img>
    assert not re.search(r'(href|src)\s*=\s*["\']https?:|url\(\s*["\']?https?:|@import', s)
    assert s.count("data:font/woff2;base64,") == 4               # serif, italic, sans, mono — inlined
    assert f'viewBox="0 0 {hero.W} {hero.H}"' in s


def test_the_svg_is_well_formed_and_names_itself():
    """A malformed SVG renders nothing inside <img>, so parse it rather than grep it.
    The accessible name must resolve: <title> first, aria-labelledby naming real ids."""
    root = ElementTree.fromstring(svg())
    ns = "{http://www.w3.org/2000/svg}"
    assert root.tag == f"{ns}svg" and root.get("role") == "img"
    assert root[0].tag == f"{ns}title"
    named = {el.get("id"): "".join(el.itertext()).strip() for el in root if el.tag in (f"{ns}title", f"{ns}desc")}
    assert root.get("aria-labelledby", "").split() == list(named)
    assert all(named.values())


def test_reduced_motion_shows_the_finished_block():
    s = svg()
    block = s[s.index("prefers-reduced-motion"):]
    assert "animation:none" in block
    assert ".cv,.ca{display:none}" in block     # every typewriter cover gone: the whole block reads


def test_the_svg_stays_light():
    assert hero.OUTPUT.stat().st_size < 150_000


def test_the_fonts_ship_with_their_licences():
    for font in hero.FONTS.glob("*.ttf"):
        family = font.stem.split("-")[0]
        assert (hero.FONTS / f"OFL-{family}.txt").exists(), font.name


# ── Says only what the README says ─────────────────────────────────────────

def test_every_chip_is_a_readme_claim():
    readme = README.lower()
    assert "no tooling required" in readme
    assert "in the language you already write in" in readme      # "a comment block, any language"
    assert "spec-v0.4" in readme                                   # the spec badge
    assert "11% → 0% fabrication" in README                        # the benchmark table's Claude row
    assert "license-unlicense" in readme
    assert (REPO / "LICENSE").read_text().startswith("This is free and unencumbered software")


def test_the_benchmark_chip_is_qualified():
    """The README retired an unqualified percentage headline; the banner never brings one back."""
    fabrication = [c for c in hero.CHIPS if "%" in c]
    assert fabrication and all("(Claude)" in c for c in fabrication)
    assert "100% → 0%" not in svg()


def test_the_committed_svg_carries_every_line_the_generator_writes():
    s = svg()
    for line in [hero.EYEBROW, hero.TAGLINE, hero.FILE_TAB, *hero.CHIPS]:
        assert line in s, line
    for line in hero.SIGNATURE:
        assert line.replace(hero.BAR, "").replace("&", "&amp;").replace("<", "&lt;") in s, line
    assert "Generated by scripts/hero/build_hero.py" in s


# ── The sample is a real MurphySig ─────────────────────────────────────────

def test_the_sample_signature_has_the_spec_shape():
    body = [line.removeprefix("//").strip() for line in hero.SIGNATURE]
    assert body[0].startswith("Signed: ") and re.search(r", \d{4}-\d{2}-\d{2}$", body[0])
    assert "Format: MurphySig v0.4" in body
    for field in ("Context: ", "Confidence: ", "Open: ", "Reviews:"):
        assert any(b.startswith(field) for b in body), field
    review = " ".join(body[body.index("Reviews:") + 1:])
    assert re.match(r"\d{4}-\d{2}-\d{2} \(.+\): .+ Confidence now \d\.\d+\.$", review)


def test_the_typing_leaves_a_hold_before_the_loop_restarts():
    times = hero.schedule(hero.SIGNATURE)
    assert all(e > s for s, e in times)
    assert all(b[0] >= a[1] for a, b in pairwise(times))   # one line at a time
    assert times[-1][1] < hero.LOOP - hero.FADE - 2.0


# ── Fresh ──────────────────────────────────────────────────────────────────

def test_the_committed_svg_is_exactly_what_the_generator_builds():
    """Byte-for-byte (the font subsets carry a pinned timestamp). Run after any edit:
    uv run scripts/hero/build_hero.py"""
    pytest.importorskip("fontTools")
    pytest.importorskip("brotli")
    assert hero.build() == svg()
