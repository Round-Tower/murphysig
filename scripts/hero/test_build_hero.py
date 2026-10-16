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
#
# 2026-10-16 (claude-opus-5.5): The sample-shape pin went with the sample. The
# card's quote is now pinned to its source file line for line, and, where this
# clone has the pinned commit, pinned as a whole block with nothing cut. The SVG
# is parsed back to the same lines (xml:space kept, the file's own line numbers).
# The caption must cite repo, commit, path and lines, and the meter's values must
# come from the text. Alt and desc must name every field the quote carries (the
# missing Format the review flagged) and no field it lacks. A font-metric check
# keeps each line inside the card and the card clear of the title and chips.
# Confidence 0.9, held.
#
# 2026-10-16 (claude-opus-5.5): independent-verifier fold. The Context's "CI runs
# these with pytest alone" no longer holds. Three pins skipped in CI: the fit and
# rebuild checks (no fonttools), and the whole-at-commit check (depth-1 clone). So
# the quote was pinned only to the working tree. A skip now fails under CI=true,
# and CI installs the generator's exact fonttools/brotli pins (a test keeps the two
# in step). New pins: alt and desc account for every review the quote carries
# (they named one of two), and the inlined fonts are the woff2 they claim to be
# (they were raw TrueType). Each was red first. Confidence 0.9, held.

import base64
import importlib
import os
import re
import subprocess
from itertools import pairwise
from pathlib import PurePosixPath
from urllib.parse import urlsplit
from xml.etree import ElementTree

import build_hero as hero
import pytest
import tomllib

REPO = hero.REPO
README = (REPO / "README.md").read_text()
ALT = re.search(r'<img src="assets/hero\.svg" alt="([^"]+)"', README).group(1)


def svg() -> str:
    return hero.OUTPUT.read_text()


def desc() -> str:
    root = ElementTree.fromstring(svg())
    return "".join(root.find("{http://www.w3.org/2000/svg}desc").itertext())


def unrunnable(reason: str):
    """Skip on a laptop without the extras; fail in CI, where the hero job installs the
    generator's pins and fetches full history, so every pin has to run there."""
    if os.environ.get("CI"):
        pytest.fail(f"CI must run this pin: {reason}")
    pytest.skip(reason)


def require(module: str):
    try:
        return importlib.import_module(module)
    except ImportError:
        unrunnable(f"{module} is not installed")


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


def test_the_inlined_fonts_are_the_woff2_they_claim():
    """Each face is declared data:font/woff2 with format('woff2'), so the bytes must be
    WOFF2 (magic wOF2). Raw TrueType renders in Chrome but is a mislabelled hint, and it
    is the larger file."""
    blobs = re.findall(r"data:font/woff2;base64,([A-Za-z0-9+/=]+)", svg())
    assert len(blobs) == 4
    assert [base64.b64decode(blob)[:4] for blob in blobs] == [b"wOF2"] * 4


def test_ci_installs_the_generators_exact_pins():
    """The byte-for-byte rebuild only holds on the versions that wrote the file, so the
    generator pins fonttools and brotli exactly and the CI hero job installs the same."""
    script = (hero.HERE / "build_hero.py").read_text()
    block = re.search(r"^# /// script\n(.*?)^# ///$", script, re.MULTILINE | re.DOTALL).group(1)
    deps = tomllib.loads("\n".join(line.removeprefix("# ") for line in block.splitlines()))["dependencies"]
    assert sorted(dep.split("==")[0] for dep in deps) == ["brotli", "fonttools"]
    assert all(re.fullmatch(r"[a-z]+==\d+(\.\d+)+", dep) for dep in deps), deps
    ci = (REPO / ".github/workflows/ci.yml").read_text()
    job = re.search(r"^  hero:\n(.*?)(?=^  \S|\Z)", ci, re.MULTILINE | re.DOTALL)
    assert job, "ci.yml has a hero job"
    for dep in deps:
        assert dep in job.group(1), dep


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
    for line in [hero.EYEBROW, hero.TAGLINE, hero.FILE_TAB, hero.METER_LABEL, *hero.CHIPS]:
        assert line in s, line
    for line in [*hero.SIGNATURE, hero.CITE]:
        assert hero.esc(line) in s, line
    assert "Generated by scripts/hero/build_hero.py" in s


# ── The signature is a real one, verbatim ──────────────────────────────────
# MurphySig's first rule is "never fabricate provenance", so the banner quotes a
# real signature from this repo rather than a sample written for it.

def test_the_signature_is_verbatim_from_its_source():
    """A contiguous run of the source file, character for character, from the line
    the gutter starts at. The tab names that file."""
    source = (REPO / hero.SOURCE_PATH).read_text().splitlines()
    start = hero.SOURCE_LINE - 1
    assert source[start:start + len(hero.SIGNATURE)] == hero.SIGNATURE
    assert hero.FILE_TAB == PurePosixPath(hero.SOURCE_PATH).name


def test_the_signature_is_whole_at_its_pinned_commit():
    """The caption cites a commit. Where this clone has it (CI checks out depth 1),
    the quote is that commit's text, from the Signed: line to the docstring's close:
    the whole block, so the card needs no elision mark."""
    shown = subprocess.run(["git", "-C", str(REPO), "show", f"{hero.SOURCE_COMMIT}:{hero.SOURCE_PATH}"],
                           capture_output=True, text=True, check=False)
    if shown.returncode != 0:
        unrunnable(f"{hero.SOURCE_COMMIT[:7]} is not in this clone")
    source = shown.stdout.splitlines()
    start, end = hero.SOURCE_LINE - 1, hero.SOURCE_LINE - 1 + len(hero.SIGNATURE)
    assert source[start:end] == hero.SIGNATURE
    assert hero.SIGNATURE[0].startswith("# Signed: Kev + ")
    assert source[end] == '"""'                                   # nothing cut from the end


def test_the_card_renders_the_quote_exactly():
    """Parse what the SVG draws, not what the generator meant: the code lines read back
    as the quote (whitespace kept), numbered with the source file's own line numbers."""
    root = ElementTree.fromstring(svg())
    ns, xml = "{http://www.w3.org/2000/svg}", "{http://www.w3.org/XML/1998/namespace}"
    code = [el for el in root.iter(f"{ns}text") if "code" in el.get("class", "").split()]
    assert [el.text or "" for el in code] == hero.SIGNATURE
    assert all(el.get(f"{xml}space") == "preserve" for el in code)   # the Context indent survives
    nums = [el.text for el in root.iter(f"{ns}text") if el.get("class") == "num"]
    assert nums == [str(hero.SOURCE_LINE + i) for i in range(len(hero.SIGNATURE))]


def test_the_caption_cites_the_source():
    last = hero.SOURCE_LINE + len(hero.SIGNATURE) - 1
    caption = re.search(r'<text class="cite"[^>]*>([^<]+)</text>', svg())
    assert caption, "the card carries its citation"
    for part in ("verbatim", hero.SOURCE_REPO, hero.SOURCE_COMMIT[:7], hero.SOURCE_PATH, f"{hero.SOURCE_LINE}–{last}"):
        assert part in caption.group(1), part
    assert re.fullmatch(r"[0-9a-f]{40}", hero.SOURCE_COMMIT)


def test_the_meter_reads_its_values_from_the_signature():
    """The confidence meter is never hand-set: it moves through the values the quote
    states, in order (signed 0.6, reviewed down to 0.4), and shows each as written."""
    marks = hero.confidence_marks(hero.SIGNATURE)
    assert [value for value, _, _ in marks] == ["0.6", "0.4"]
    for value, i, end in marks:
        assert hero.SIGNATURE[i][:end].endswith(value)
    s = svg()
    assert all(f">{value}</text>" in s for value, _, _ in marks)


def test_the_descriptions_name_only_fields_the_signature_has():
    """The review caught the alt text dropping Format. Pin both ways: the README alt and
    the SVG <desc> name every field label the quote carries, and no spec field it lacks."""
    labels = {m.group(1) for line in hero.SIGNATURE if (m := re.match(r"#\s*([A-Z][a-z]+):", line))}
    assert labels >= {"Signed", "Format", "Context", "Confidence", "Reviews"}
    for text in (ALT, desc()):
        assert hero.FILE_TAB in text
        for label in labels:
            assert label in text, label
        for absent in {"Open", "Prior"} - labels:
            assert f"{absent}," not in text and f"{absent} " not in text, absent


def test_the_descriptions_account_for_every_review():
    """The quote carries two reviews: the 2026-07-12 entry and an inline 2026-10-06
    lint pass. A verifier caught the alt and the desc summary naming only the first;
    a screen reader hears only the alt. Each review's date is in both summaries
    (the desc's summary is the text before its verbatim copy of the quote)."""
    entry = re.compile(r"#\s*(?:(\d{4}-\d{2}-\d{2}) \(|Review: [^,]+, (\d{4}-\d{2}-\d{2}))")
    dates = [m.group(1) or m.group(2) for line in hero.SIGNATURE if (m := entry.match(line))]
    assert dates == ["2026-07-12", "2026-10-06"]
    verbatim_start = hero.SIGNATURE[0].lstrip("#").strip()
    summary = desc().split(verbatim_start)[0]
    assert summary != desc(), "the desc quotes the signature after its summary"
    for text in (ALT, summary):
        for date in dates:
            assert date in text, date


def test_everything_fits_its_box():
    """A real signature runs to ~76 columns, not the old sample's ~45. Every code line
    ends inside the card, the card clears the title and the chips, the meter clears the
    file tab, and the card and its caption sit inside the canvas."""
    require("fontTools")
    from fontTools.ttLib import TTFont

    font = {name: TTFont(hero.FONTS / f"{name}.ttf") for name in
            ("JetBrainsMono-Regular", "InstrumentSerif-Regular", "InstrumentSerif-Italic")}
    mono = font["JetBrainsMono-Regular"]
    root = ElementTree.fromstring(svg())
    ns = "{http://www.w3.org/2000/svg}"

    def first(tag, cls):
        return next(el for el in root.iter(f"{ns}{tag}") if cls in el.get("class", "").split())

    def box(el):
        return tuple(float(el.get(k)) for k in ("x", "y", "width", "height"))

    cx, cy, cw, ch = box(first("rect", "card"))
    for el in root.iter(f"{ns}text"):
        if "code" in el.get("class", "").split():
            assert float(el.get("x")) + hero.advance(mono, el.text or "", hero.MONO_SIZE) <= cx + cw - 8, el.text
    title_right = hero.TX - 4 + hero.advance(font["InstrumentSerif-Regular"], "Murphy", hero.TITLE_SIZE) \
        + hero.advance(font["InstrumentSerif-Italic"], "Sig", hero.TITLE_SIZE)
    chip_right = max(box(r)[0] + box(r)[2] for g in root.iter(f"{ns}g") if g.get("class") == "chip"
                     for r in g if r.tag == f"{ns}rect")
    assert max(title_right, chip_right) < cx - 24
    tab_x, _, tab_w, _ = box(first("rect", "tab"))
    assert tab_x + tab_w + 16 < float(first("text", "meterlabel").get("x"))
    cite = first("text", "cite")
    assert float(cite.get("x")) + hero.advance(mono, cite.text, hero.CITE_SIZE) <= cx + cw
    assert cy > 0 and cy + ch + 12 < float(cite.get("y")) < hero.H - 4


def test_the_typing_leaves_a_hold_before_the_loop_restarts():
    times = hero.schedule(hero.SIGNATURE)
    assert all(e > s for s, e in times)
    assert all(b[0] >= a[1] for a, b in pairwise(times))   # one line at a time
    assert times[-1][1] < hero.LOOP - hero.FADE - 2.0


# ── Fresh ──────────────────────────────────────────────────────────────────

def test_the_committed_svg_is_exactly_what_the_generator_builds():
    """Byte-for-byte (the font subsets carry a pinned timestamp). Run after any edit:
    uv run scripts/hero/build_hero.py"""
    require("fontTools")
    require("brotli")
    assert hero.build() == svg()
