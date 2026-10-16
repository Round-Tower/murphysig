# /// script
# requires-python = ">=3.11"
# dependencies = ["fonttools==4.67.0", "brotli==1.2.0"]
# ///
# Signed: Kev + claude-opus-5-5, 2026-10-07
# Format: MurphySig v0.4 (https://murphysig.dev/spec)
# Prior: Unknown (new file)
#
# Context: Generates assets/hero.svg, the animated README banner: "Sign your
# work." in the site's printed-manifesto look (paper, ink, Instrument Serif),
# with a MurphySig block typing itself out in a code card — Signed, Context,
# Confidence with an ink bar, Open, then a Reviews entry arriving and the
# confidence bar moving. One self-contained SVG that GitHub animates inside an
# <img>: CSS keyframes only, no <script>, no external fetches; the three OFL
# faces in fonts/ are subset to the characters used and inlined as woff2.
# Method: ~/.claude/skills/github-hero (born on m1k3's README hero, #505).
#
#   uv run scripts/hero/build_hero.py      # writes assets/hero.svg
#
# Confidence: 0.8 - verified by eye in headless Chrome (page, <img>, reduced
# motion) and WebKit (Quick Look); Safari's live animation is unseen. The
# timings and the sample signature are taste.
# Open: should the banner also carry a dark variant via <picture>?
#
# Reviews:
#
# 2026-10-16 (claude-opus-5.5): Kev's call: the card quotes a real signature.
# The sample on a made-up retry.ts broke MurphySig's first rule (never fabricate
# provenance) on the project's own front door. It now shows benchmark/src/
# heuristic_scorer.py lines 6–25 at 39b539f, verbatim: signed in February asking
# to be validated, then the July review that measured it a coin flip and lowered
# its confidence to 0.4. Real lines run to 76 columns, so the code drops 15 → 13
# px, the card widens and the canvas grows to 1280×520. The confidence meter
# moved to the tab strip, so nothing is drawn inside the quote, and it reads its
# values from the text. The gutter numbers are the file's own and a caption cites
# repo, commit, path and lines. Typing 46 → 80 cps over a 26 s loop. Confidence
# 0.8, held: frames checked in headless Chrome; Safari's live animation is unseen.
#
# 2026-10-16 (claude-opus-5.5): independent-verifier fold. The entry above is
# loose in two places. "Signed in February" rests on the signature's own date
# (git first has the file 2026-04-19, in the benchmark's bulk import). The
# validation ran in June; the July review reports it, not measures it. The alt
# and desc named one review of the quote's two, missing the inline 2026-10-06
# lint pass; now both, pinned. They also said "code comment" for lines that sit
# in a module docstring; reworded. The fonts were raw TrueType declared as woff2:
# Subsetter ignores options.flavor, so font.flavor is set before save, and the
# file is lighter for it. fonttools and brotli are pinned exactly, so CI can run
# the byte-for-byte rebuild on the same versions. Confidence 0.8, held.

from __future__ import annotations

import base64
import io
import re
import sys
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = REPO / "assets/hero.svg"
FONTS = HERE / "fonts"

W, H = 1280, 520

# site/src/styles/global.css
PAPER, INK, STONE, GRID, CONN, TRACK, MUTED = "#fbfaf8", "#1a1a1a", "#78716c", "#e7e5e1", "#d6d3cd", "#f1efeb", "#737373"

EYEBROW = "PROVENANCE FOR HUMAN–AI WORK"
TITLE = "MurphySig"
TAGLINE = "Sign your work."
# Each claim is the README's own (badges, "What it is", the benchmark table), qualified
# where the README qualifies it: the Claude row is cold→warm on one family; the README
# retired an unqualified "100% → 0%" headline, so no bare percentage appears here.
CHIPS = ["No tooling required", "A comment block, any language", "Spec v0.4", "Fabrication 11% → 0% (Claude)", "Unlicense"]

# The card quotes a real MurphySig, verbatim: the banner for a provenance convention
# must not fabricate provenance. Its signature (dated 2026-02-16) asks to be validated;
# the 2026-07-12 review reports the June validation (a coin flip) and lowers the
# confidence, and a 2026-10-06 lint pass follows. Never edit the lines by hand.
# Re-quote them from the file at a pinned main commit; the tests compare them line for
# line and parse them back out of the SVG.
SOURCE_REPO = "Round-Tower/murphysig"
SOURCE_PATH = "benchmark/src/heuristic_scorer.py"
SOURCE_COMMIT = "39b539fe823e88e034de29054e748eee704761a0"  # main, 2026-10-06 (#32): the last to touch it
SOURCE_LINE = 6                                             # the Signed: line; the gutter counts from here
FILE_TAB = PurePosixPath(SOURCE_PATH).name
SIGNATURE = [
    "# Signed: Kev + claude-opus-4-6, 2026-02-16",
    "# Format: MurphySig v0.3.3 (https://murphysig.dev/spec)",
    "#",
    "# Context: Fallback scorer when API limits are hit. Should be validated",
    "#          against LLM judge results when available.",
    "#",
    "# Confidence: 0.6 - heuristic approximation, not as good as LLM judge",
    "#",
    "# Reviews:",
    "#",
    "# 2026-07-12 (Kev + claude-fable-5): Closing the loop this signature opened.",
    "# The validation it asked for happened in June 2026: heuristic-vs-judge",
    "# agreement measured at 9/18 on the honesty benchmark — a coin flip. The",
    "# February suspicion was empirically confirmed; treat this scorer as",
    "# same-day directional signal only, never for reported numbers (the judge",
    "# is canonical, per project policy). Confidence now 0.4 — it runs, it's",
    "# fast, and it is measurably not a substitute for the judge.",
    "#",
    "# Review: Kev + claude-opus-5.5, 2026-10-06 — ruff 0.16 lint pass, no",
    "# behaviour change: set(generator) → set comprehension; import spacing.",
]
CITE = (f"verbatim · {SOURCE_REPO} @ {SOURCE_COMMIT[:7]} · {SOURCE_PATH}, "
        f"lines {SOURCE_LINE}–{SOURCE_LINE + len(SIGNATURE) - 1}")
METER_LABEL = "confidence"
GLYPHS = ["//", "#", "--", "/*", ";;", "<!--", "%", "'", "*/", "-->", "REM"]

LOOP = 26.0          # seconds per cycle
CPS = 80             # typing speed, characters per second
LINE_GAP = 0.12      # pause after each line
START = 1.1          # the underline draws first
REVIEW_PAUSE = 0.9   # a beat before each review arrives
FADE = 0.6           # the block fades out at the end of a cycle

TX, TITLE_SIZE = 88, 112    # the left column
MONO_SIZE, LINE_H = 13, 19  # the quote: 76 columns have to fit beside the title
CITE_SIZE = 11

CONFIDENCE = re.compile(r"Confidence(?::| now) ([01]\.\d+)")
REVIEW = re.compile(r"#\s*Reviews?:")


# ── Fonts (from ~/.claude/skills/github-hero/herokit.py) ───────────────────
def font_face(path: Path, family: str, text: str, style: str = "normal"):
    from fontTools import subset  # only the writer needs fonttools + brotli
    from fontTools.ttLib import TTFont

    font = TTFont(path, recalcTimestamp=False)  # reproducible bytes
    options = subset.Options()
    options.layout_features = ["kern", "liga"]
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=text)
    subsetter.subset(font)
    font.flavor = "woff2"  # Subsetter ignores options.flavor; without this, save() writes TrueType
    buf = io.BytesIO()
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    css = f"@font-face{{font-family:'{family}';font-style:{style};src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
    return css, TTFont(path)


def advance(font, text: str, size: float, tracking: float = 0) -> float:
    cmap, hmtx, upm = font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm
    return sum(hmtx[cmap[ord(ch)]][0] for ch in text) * size / upm + tracking * len(text)


# ── Timeline ───────────────────────────────────────────────────────────────
def schedule(lines: list[str]) -> list[tuple[float, float]]:
    """(start, end) seconds for each typed line; blank comment lines type too (fast)."""
    t, out = START, []
    for line in lines:
        if REVIEW.match(line):
            t += REVIEW_PAUSE
        d = max(len(line), 1) / CPS
        out.append((t, t + d))
        t += d + LINE_GAP
    assert t < LOOP - FADE - 2.0, f"the typing ({t:.1f}s) must leave a hold before the loop ends"
    return out


def confidence_marks(lines: list[str]) -> list[tuple[str, int, int]]:
    """Every confidence the quote states, in order: (value as written, line, end column).
    The meter moves through these values and no others."""
    return [(m.group(1), i, m.end(1)) for i, line in enumerate(lines) for m in CONFIDENCE.finditer(line)]


def pct(seconds: float) -> str:
    return f"{100 * seconds / LOOP:.3f}%"


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;")


# ── Compose ────────────────────────────────────────────────────────────────
def build() -> str:
    lines = SIGNATURE
    marks = confidence_marks(lines)
    mono_text = "".join(lines) + "".join(GLYPHS) + FILE_TAB + "0123456789" + CITE + METER_LABEL
    serif_css, serif = font_face(FONTS / "InstrumentSerif-Regular.ttf", "Serif", TITLE)
    italic_css, italic = font_face(FONTS / "InstrumentSerif-Italic.ttf", "SerifItalic", TAGLINE + TITLE, "italic")
    sans_css, sans = font_face(FONTS / "InterTight-Medium.ttf", "Sans", EYEBROW + "".join(CHIPS))
    mono_css, mono = font_face(FONTS / "JetBrainsMono-Regular.ttf", "Mono", mono_text)

    # The card: as wide as the quote's longest line, on the right, centred with its caption.
    tab_h, tab_size, pad_top, pad_bottom, pad_right, cite_gap = 34, 12.5, 14, 12, 16, 24
    card_w = round(42 + max(advance(mono, line, MONO_SIZE) for line in lines) + pad_right)
    card_x = W - 56 - card_w
    card_h = tab_h + pad_top + LINE_H * len(lines) + pad_bottom
    card_y = round((H - card_h - cite_gap) / 2)
    body_y = card_y + tab_h + pad_top
    gutter_x, text_x = card_x + 30, card_x + 42

    # The left column, centred on the canvas.
    tx, title_size = TX, TITLE_SIZE
    title_y = round(H / 2 - 38)
    murphy_w = advance(serif, "Murphy", title_size)
    title_w = murphy_w + advance(italic, "Sig", title_size)

    # Hand-drawn underline: a slightly wandering ink stroke under the title.
    uy = title_y + 26
    under = (f"M{tx + 2} {uy + 3} C {tx + title_w * 0.25:.0f} {uy - 5}, {tx + title_w * 0.55:.0f} {uy + 6}, "
             f"{tx + title_w * 0.8:.0f} {uy - 1} S {tx + title_w + 6:.0f} {uy - 6}, {tx + title_w + 18:.0f} {uy - 2}")

    tag_y = title_y + 84
    chip_size, chip_h, chip_pad, chip_gap = 14.5, 32, 15, 9
    chips, cx, cy = [], tx, tag_y + 34
    for label in CHIPS:
        w = advance(sans, label, chip_size) + chip_pad * 2
        if cx + w > card_x - 32:
            cx, cy = tx, cy + chip_h + chip_gap
        chips.append(f'<g class="chip"><rect x="{cx:.1f}" y="{cy}" width="{w:.1f}" height="{chip_h}" rx="{chip_h / 2}"/>'
                     f'<text x="{cx + chip_pad:.1f}" y="{cy + chip_h / 2 + 5:.1f}">{label}</text></g>')
        cx += w + chip_gap

    times = schedule(lines)
    end_typing = times[-1][1]
    review_i = next(i for i, ln in enumerate(lines) if REVIEW.match(ln))
    review_start = times[review_i][0]
    rows, covers, cover_css = [], [], []
    for i, (line, (s, e)) in enumerate(zip(lines, times)):
        y = body_y + i * LINE_H + MONO_SIZE
        width = advance(mono, line, MONO_SIZE) + 4
        # The gutter carries the source file's own line numbers; xml:space keeps the
        # quote's indentation in renderers that ignore CSS white-space.
        rows.append(f'<text class="num" x="{gutter_x}" y="{y:.1f}" text-anchor="end">{SOURCE_LINE + i}</text>'
                    f'<text class="code{" rev" if i >= review_i else ""}" x="{text_x}" y="{y:.1f}" xml:space="preserve">{esc(line)}</text>')
        # A paper-coloured cover slides right in character steps: the typewriter. Its
        # transform ATTRIBUTE is the revealed position, so a renderer that ignores CSS
        # animation shows the finished block; the keyframes override it in browsers.
        n = max(len(line), 1)
        covers.append(f'<rect class="cv cv{i}{" cvr" if i >= review_i else ""}" x="{text_x - 2}" y="{y - MONO_SIZE + 1:.1f}" width="{width:.1f}" height="{LINE_H}" transform="translate({width:.1f} 0)"/>'
                      f'<rect class="ca ca{i}" x="{text_x - 1}" y="{y - MONO_SIZE + 2:.1f}" width="7" height="{MONO_SIZE + 3:.1f}"/>')
        cover_css.append(
            f".cv{i}{{animation:cv{i} {LOOP}s infinite{f',cvr {LOOP}s infinite' if i >= review_i else ''}}}"
            f"@keyframes cv{i}{{0%,{pct(s)}{{transform:translateX(0);animation-timing-function:steps({n},end)}}"
            f"{pct(e)},100%{{transform:translateX({width:.1f}px)}}}}"
            f".ca{i}{{opacity:0;animation:ca{i} {LOOP}s infinite}}"
            f"@keyframes ca{i}{{0%,{pct(s)}{{opacity:0;transform:translateX(0);animation-timing-function:steps({n},end)}}"
            f"{pct(s + 0.001)}{{opacity:1;transform:translateX(0);animation-timing-function:steps({n},end)}}"
            f"{pct(e)}{{opacity:1;transform:translateX({width:.1f}px);animation-timing-function:step-end}}"
            f"{pct(e + LINE_GAP)},100%{{opacity:0;transform:translateX({width:.1f}px)}}}}"
        )

    last_y = body_y + (len(lines) - 1) * LINE_H + MONO_SIZE
    last_x = text_x + advance(mono, lines[-1], MONO_SIZE) + 3

    # The confidence meter sits in the tab strip, outside the quote, and moves through
    # the values the quote states at the moment each one is typed.
    reveal = [times[i][0] + end / CPS for _, i, end in marks]
    final = float(marks[-1][0])
    meter_w, meter_h = 88, 8
    value_x = card_x + card_w - 16 - max(advance(mono, v, tab_size) for v, _, _ in marks)
    bar_x = value_x - 10 - meter_w
    label_x = bar_x - 10 - advance(mono, METER_LABEL, tab_size)
    bar_y = card_y + 16
    ease = "animation-timing-function:cubic-bezier(.2,.8,.2,1)"
    bar_frames = [f"0%,{pct(reveal[0])}{{transform:scaleX(0);{ease}}}"]
    values, value_css = [], []
    for k, (value, _, _) in enumerate(marks):
        last = k == len(marks) - 1
        scale = f"transform:scaleX({float(value) / final:.4f})"
        settle = pct(reveal[k] + (0.7 if k == 0 else 0.8))
        bar_frames.append(f"{settle},100%{{{scale}}}" if last else f"{settle},{pct(reveal[k + 1])}{{{scale};{ease}}}")
        # Without CSS (or with reduced motion) only the final value shows.
        hidden = "" if last else ' opacity="0"'
        values.append(f'<text class="cval cval{k}" x="{value_x:.1f}" y="{card_y + 25}"{hidden}>{value}</text>')
        off = "" if last else f"{pct(reveal[k + 1])}{{opacity:0}}"
        value_css.append(f".cval{k}{{animation:cval{k} {LOOP}s step-end infinite}}"
                         f"@keyframes cval{k}{{0%{{opacity:0}}{pct(reveal[k])}{{opacity:1}}{off}100%{{opacity:{int(last)}}}}}")

    # Background: ledger rules, the margin rule, and a scatter of comment glyphs.
    rules = "".join(f"M0 {y}h{W}" for y in range(36, H, 28))
    glyphs = []
    k = 0
    for gy in range(44, H - 10, 56):
        for gx in range(24, W, 92):
            jitter = ((k * 37) % 23) - 11
            glyph = GLYPHS[(k * 7 + gy // 56) % len(GLYPHS)]
            glyphs.append(f'<text x="{gx + jitter}" y="{gy + (k * 13) % 17}">{glyph.replace("<", "&lt;")}</text>')
            k += 1
    edge = card_x / W  # the glyphs come back at the card's edge

    hold_from = end_typing + 0.2
    hl_y = body_y + review_i * LINE_H + 1  # flush with the review covers' top edge
    hl_h = LINE_H * (len(lines) - review_i) + 2
    css = f"""{serif_css}{italic_css}{sans_css}{mono_css}
.eyebrow{{font-family:'Sans',Inter,sans-serif;font-size:13px;letter-spacing:3.6px;fill:{STONE}}}
.title{{font-family:'Serif',serif;font-size:{title_size}px;fill:{INK}}}
.titleit{{font-family:'SerifItalic',serif;font-style:italic}}
.tag{{font-family:'SerifItalic',serif;font-style:italic;font-size:40px;fill:{INK}}}
.chip rect{{fill:#ffffff;stroke:{CONN};stroke-width:1}}
.chip text{{font-family:'Sans',Inter,sans-serif;font-size:{chip_size}px;fill:{INK}}}
.glyphs text{{font-family:'Mono',monospace;font-size:15px;fill:{STONE}}}
.code{{font-family:'Mono',monospace;font-size:{MONO_SIZE}px;fill:#3f3c39;white-space:pre}}
.code.rev{{fill:{INK}}}
.num{{font-family:'Mono',monospace;font-size:11px;fill:#b8b3ad}}
.tabtext{{font-family:'Mono',monospace;font-size:{tab_size}px;fill:{STONE}}}
.meterlabel{{font-family:'Mono',monospace;font-size:{tab_size}px;fill:{STONE}}}
.cval{{font-family:'Mono',monospace;font-size:{tab_size}px;fill:{INK}}}
.cite{{font-family:'Mono',monospace;font-size:{CITE_SIZE}px;fill:{STONE}}}
.cv{{fill:#ffffff}}
.ca{{fill:{INK}}}
.ink{{fill:none;stroke:{INK};stroke-width:3.2;stroke-linecap:round;stroke-dasharray:101;stroke-dashoffset:0;animation:ink {LOOP}s infinite}}
@keyframes ink{{0%{{stroke-dashoffset:101;opacity:1;animation-timing-function:cubic-bezier(.6,0,.3,1)}}{pct(START - 0.1)},{pct(LOOP - FADE)}{{stroke-dashoffset:0;opacity:1}}{pct(LOOP - 0.05)},100%{{stroke-dashoffset:0;opacity:0}}}}
.block{{animation:block {LOOP}s infinite}}
@keyframes block{{0%,{pct(LOOP - FADE)}{{opacity:1}}{pct(LOOP - 0.05)},100%{{opacity:0}}}}
.barfill{{transform-box:fill-box;transform-origin:left center;animation:bar {LOOP}s infinite}}
@keyframes bar{{{"".join(bar_frames)}}}
{"".join(value_css)}
.mark{{opacity:0;animation:mark {LOOP}s infinite}}
@keyframes mark{{0%,{pct(review_start - 0.55)}{{opacity:0}}{pct(review_start - 0.15)},100%{{opacity:1}}}}
@keyframes cvr{{0%,{pct(review_start - 0.55)}{{fill:#ffffff}}{pct(review_start - 0.15)},100%{{fill:{TRACK}}}}}
.caret{{opacity:0;animation:caret {LOOP}s step-end infinite}}
@keyframes caret{{0%,{pct(hold_from)}{{opacity:0}}{pct(hold_from + 0.01)}{{opacity:1}}{pct(hold_from + 0.55)}{{opacity:0}}{pct(hold_from + 1.1)}{{opacity:1}}{pct(hold_from + 1.65)}{{opacity:0}}{pct(hold_from + 2.2)}{{opacity:1}}{pct(hold_from + 2.75)}{{opacity:0}}{pct(hold_from + 3.3)}{{opacity:1}}{pct(LOOP - FADE)},100%{{opacity:0}}}}
{"".join(cover_css)}
@media (prefers-reduced-motion:reduce){{
.cv,.ca,.ink,.block,.barfill,.cval,.caret,.mark{{animation:none}}
.cv,.ca{{display:none}}.caret,.mark{{opacity:1}}
}}"""

    first = marks[0][0]
    said = " ".join(text for line in lines if (text := line.lstrip("#").strip()))
    final_said = marks[-1][0]
    desc = (f"A real MurphySig types itself out in a code card, quoted verbatim from {FILE_TAB} "
            f"({SOURCE_PATH}, lines {SOURCE_LINE}–{SOURCE_LINE + len(lines) - 1} of its module docstring, "
            f"in {SOURCE_REPO} at commit {SOURCE_COMMIT[:7]}): Signed, Format, Context and Confidence {first}, "
            f"then its Reviews: a 2026-07-12 entry that reports the validation the signature asked for "
            f"(a coin flip) and lowers the confidence to {final_said}, and a 2026-10-06 lint pass with no "
            f"behaviour change. A confidence meter fills to {first} and drops to {final_said}. "
            f"The signature, its # markers dropped: {said} "
            f"Beside it: MurphySig. Sign your work. No tooling required; a comment block, any language; spec v0.4; "
            f"fabrication 11% to 0% on Claude in the benchmark; Unlicense.")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">MurphySig — sign your work</title>
<desc id="d">{esc(desc)}</desc>
<!-- Generated by scripts/hero/build_hero.py — edit that, not this. Fonts: Instrument Serif, Inter Tight, JetBrains Mono (SIL OFL 1.1). -->
<style>{css}</style>
<defs>
<linearGradient id="fade" x1="0" x2="1"><stop offset=".08" stop-color="#fff" stop-opacity=".9"/><stop offset=".24" stop-color="#fff" stop-opacity=".18"/><stop offset="{edge - 0.06:.3f}" stop-color="#fff" stop-opacity=".18"/><stop offset="{edge:.3f}" stop-color="#fff" stop-opacity=".9"/></linearGradient>
<mask id="glyphmask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
<clipPath id="cardclip"><rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h:.1f}" rx="10"/></clipPath>
<filter id="shadow" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#1a1a1a" flood-opacity=".08"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="{PAPER}"/>
<path d="{rules}" stroke="{GRID}" stroke-width="1" opacity=".75"/>
<path d="M56 0V{H}" stroke="{STONE}" stroke-width="1" opacity=".22"/>
<g class="glyphs" opacity=".16" mask="url(#glyphmask)">{"".join(glyphs)}</g>
<text class="eyebrow" x="{tx}" y="{title_y - 104}">{EYEBROW}</text>
<text class="title" x="{tx - 4}" y="{title_y}">Murphy<tspan class="titleit">Sig</tspan></text>
<path class="ink" d="{under}" pathLength="100"/>
<text class="tag" x="{tx}" y="{tag_y}">{TAGLINE}</text>
{"".join(chips)}
<g filter="url(#shadow)"><rect class="card" x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h:.1f}" rx="10" fill="#ffffff" stroke="{GRID}"/></g>
<g clip-path="url(#cardclip)">
<rect x="{card_x}" y="{card_y}" width="{card_w}" height="{tab_h}" fill="{TRACK}"/>
<path d="M{card_x} {card_y + tab_h}h{card_w}" stroke="{GRID}"/>
<rect class="tab" x="{card_x + 14}" y="{card_y + 7}" width="{advance(mono, FILE_TAB, tab_size) + 26:.1f}" height="{tab_h - 7}" rx="5" fill="#ffffff"/>
<text class="tabtext" x="{card_x + 27}" y="{card_y + 25}">{FILE_TAB}</text>
<g class="block">
<text class="meterlabel" x="{label_x:.1f}" y="{card_y + 25}">{METER_LABEL}</text>
<rect x="{bar_x:.1f}" y="{bar_y}" width="{meter_w}" height="{meter_h}" rx="2" fill="#ffffff" stroke="{CONN}" stroke-width=".8"/>
<rect class="barfill" x="{bar_x:.1f}" y="{bar_y}" width="{meter_w * final:.1f}" height="{meter_h}" rx="2" fill="{INK}"/>
{"".join(values)}
<rect class="mark" x="{card_x + 1}" y="{hl_y:.1f}" width="{card_w - 2}" height="{hl_h:.1f}" fill="{TRACK}"/>
<path class="mark" d="M{card_x + 1.5} {hl_y:.1f}v{hl_h:.1f}" stroke="{INK}" stroke-width="3"/>
{"".join(rows)}
{"".join(covers)}
<rect class="caret" x="{last_x:.1f}" y="{last_y - MONO_SIZE + 2:.1f}" width="7" height="{MONO_SIZE + 3:.1f}" fill="{INK}"/>
</g>
</g>
<text class="cite" x="{card_x + 2}" y="{card_y + card_h + cite_gap:.1f}">{esc(CITE)}</text>
</svg>
"""


def main() -> None:
    svg = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg)
    print(f"wrote {OUTPUT.relative_to(REPO)} ({len(svg.encode()) / 1024:.0f} KB)", file=sys.stderr)


if __name__ == "__main__":
    main()
