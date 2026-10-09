# /// script
# requires-python = ">=3.11"
# dependencies = ["fonttools>=4.50", "brotli>=1.1"]
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

from __future__ import annotations

import base64
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = REPO / "assets/hero.svg"
FONTS = HERE / "fonts"

W, H = 1280, 440

# site/src/styles/global.css
PAPER, INK, STONE, GRID, CONN, TRACK, MUTED = "#fbfaf8", "#1a1a1a", "#78716c", "#e7e5e1", "#d6d3cd", "#f1efeb", "#737373"

EYEBROW = "PROVENANCE FOR HUMAN–AI WORK"
TITLE = "MurphySig"
TAGLINE = "Sign your work."
# Each claim is the README's own (badges, "What it is", the benchmark table), qualified
# where the README qualifies it: the Claude row is cold→warm on one family; the README
# retired an unqualified "100% → 0%" headline, so no bare percentage appears here.
CHIPS = ["No tooling required", "A comment block, any language", "Spec v0.4", "Fabrication 11% → 0% (Claude)", "Unlicense"]

FILE_TAB = "retry.ts"
# The sample block, in the spec's documented shape (Signed / Format / Context /
# Confidence / Open, then a Reviews entry: "YYYY-MM-DD (Who): … Confidence now X.").
BAR = "{bar}"
SIGNATURE = [
    "// Signed: Kev + claude-opus-5-5, 2026-10-07",
    "// Format: MurphySig v0.4",
    "//",
    "// Context: retry with jitter, so the queue",
    "// drains before the socket closes.",
    "//",
    f"// Confidence: 0.7 {BAR}",
    "// Open: does the backoff cap hold on 3G?",
    "//",
    "// Reviews:",
    "// 2026-10-09 (Kev + claude-opus-5-5): cap",
    "// held on 3G. Confidence now 0.85.",
]
GLYPHS = ["//", "#", "--", "/*", ";;", "<!--", "%", "'", "*/", "-->", "REM"]

LOOP = 15.0          # seconds per cycle
CPS = 46             # typing speed, characters per second
LINE_GAP = 0.12      # pause after each line
START = 1.1          # the underline draws first
REVIEW_PAUSE = 0.9   # a beat before the Reviews entry arrives
FADE = 0.6           # the block fades out at the end of a cycle


# ── Fonts (from ~/.claude/skills/github-hero/herokit.py) ───────────────────
def font_face(path: Path, family: str, text: str, style: str = "normal"):
    from fontTools import subset  # only the writer needs fonttools + brotli
    from fontTools.ttLib import TTFont

    font = TTFont(path, recalcTimestamp=False)  # reproducible bytes
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["kern", "liga"]
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=text)
    subsetter.subset(font)
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
    for i, line in enumerate(lines):
        if line.startswith("// Reviews:"):
            t += REVIEW_PAUSE
        n = len(line.replace(BAR, ""))
        d = max(n, 1) / CPS
        out.append((t, t + d))
        t += d + LINE_GAP
    assert t < LOOP - FADE - 2.0, f"the typing ({t:.1f}s) must leave a hold before the loop ends"
    return out


def pct(seconds: float) -> str:
    return f"{100 * seconds / LOOP:.3f}%"


# ── Compose ────────────────────────────────────────────────────────────────
def build() -> str:
    lines = SIGNATURE
    mono_text = "".join(lines) + "".join(GLYPHS) + FILE_TAB + "0123456789"
    serif_css, serif = font_face(FONTS / "InstrumentSerif-Regular.ttf", "Serif", TITLE)
    italic_css, italic = font_face(FONTS / "InstrumentSerif-Italic.ttf", "SerifItalic", TAGLINE + TITLE, "italic")
    sans_css, sans = font_face(FONTS / "InterTight-Medium.ttf", "Sans", EYEBROW + "".join(CHIPS))
    mono_css, mono = font_face(FONTS / "JetBrainsMono-Regular.ttf", "Mono", mono_text.replace(BAR, ""))

    tx = 88
    title_size, title_y = 112, 226
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
        if cx + w > 690:
            cx, cy = tx, cy + chip_h + chip_gap
        chips.append(f'<g class="chip"><rect x="{cx:.1f}" y="{cy}" width="{w:.1f}" height="{chip_h}" rx="{chip_h / 2}"/>'
                     f'<text x="{cx + chip_pad:.1f}" y="{cy + chip_h / 2 + 5:.1f}">{label}</text></g>')
        cx += w + chip_gap

    # The card.
    card_x, card_y, card_w = 716, 50, 500
    tab_h, line_h, mono_size = 34, 24.5, 15
    body_y = card_y + tab_h + 18
    card_h = tab_h + 18 + line_h * len(lines) + 14
    gutter_x, text_x = card_x + 34, card_x + 50
    times = schedule(lines)
    end_typing = times[-1][1]

    review_i = next(i for i, ln in enumerate(lines) if ln.startswith("// Reviews:"))
    review_start = times[review_i][0]
    rows, covers, cover_css = [], [], []
    bar_x = bar_w = 0.0
    for i, (line, (s, e)) in enumerate(zip(lines, times)):
        y = body_y + i * line_h + mono_size
        shown = line.replace(BAR, "")
        width = advance(mono, shown, mono_size) + 4
        if BAR in line:
            bar_x = text_x + advance(mono, shown, mono_size) + 2
            bar_w = 120
            width += bar_w + 4
        rows.append(f'<text class="num" x="{gutter_x}" y="{y:.1f}" text-anchor="end">{i + 1}</text>'
                    f'<text class="code{" rev" if i >= len(lines) - 3 else ""}" x="{text_x}" y="{y:.1f}">{shown.replace("&", "&amp;").replace("<", "&lt;")}</text>')
        # A paper-coloured cover slides right in character steps: the typewriter. Its
        # transform ATTRIBUTE is the revealed position, so a renderer that ignores CSS
        # animation shows the finished block; the keyframes override it in browsers.
        n = max(len(shown), 1)
        covers.append(f'<rect class="cv cv{i}{" cvr" if i >= review_i else ""}" x="{text_x - 2}" y="{y - mono_size + 1:.1f}" width="{width:.1f}" height="{line_h}" transform="translate({width:.1f} 0)"/>'
                      f'<rect class="ca ca{i}" x="{text_x - 1}" y="{y - mono_size + 2:.1f}" width="8" height="{mono_size + 3:.1f}"/>')
        step = (width - (bar_w + 4 if BAR in line else 0)) / n
        cover_css.append(
            f".cv{i}{{animation:cv{i} {LOOP}s infinite{f',cvr {LOOP}s infinite' if i >= review_i else ''}}}"
            f"@keyframes cv{i}{{0%,{pct(s)}{{transform:translateX(0);animation-timing-function:steps({n},end)}}"
            f"{pct(e)},100%{{transform:translateX({width:.1f}px)}}}}"
            f".ca{i}{{opacity:0;animation:ca{i} {LOOP}s infinite}}"
            f"@keyframes ca{i}{{0%,{pct(s)}{{opacity:0;transform:translateX(0);animation-timing-function:steps({n},end)}}"
            f"{pct(s + 0.001)}{{opacity:1;transform:translateX(0);animation-timing-function:steps({n},end)}}"
            f"{pct(e)}{{opacity:1;transform:translateX({step * n:.1f}px);animation-timing-function:step-end}}"
            f"{pct(e + LINE_GAP)},100%{{opacity:0;transform:translateX({step * n:.1f}px)}}}}"
        )

    last_y = body_y + (len(lines) - 1) * line_h + mono_size
    last_x = text_x + advance(mono, lines[-1], mono_size) + 3
    conf_i = next(i for i, ln in enumerate(lines) if BAR in ln)
    conf_end = times[conf_i][1]
    bar_y = body_y + conf_i * line_h + mono_size - 9
    review_end = end_typing

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

    hold_from = review_end + 0.2
    hl_y = body_y + review_i * line_h + 1  # flush with the review covers' top edge
    hl_h = line_h * (len(lines) - review_i) + 2
    css = f"""{serif_css}{italic_css}{sans_css}{mono_css}
.eyebrow{{font-family:'Sans',Inter,sans-serif;font-size:13px;letter-spacing:3.6px;fill:{STONE}}}
.title{{font-family:'Serif',serif;font-size:{title_size}px;fill:{INK}}}
.titleit{{font-family:'SerifItalic',serif;font-style:italic}}
.tag{{font-family:'SerifItalic',serif;font-style:italic;font-size:40px;fill:{INK}}}
.chip rect{{fill:#ffffff;stroke:{CONN};stroke-width:1}}
.chip text{{font-family:'Sans',Inter,sans-serif;font-size:{chip_size}px;fill:{INK}}}
.glyphs text{{font-family:'Mono',monospace;font-size:15px;fill:{STONE}}}
.code{{font-family:'Mono',monospace;font-size:{mono_size}px;fill:#3f3c39;white-space:pre}}
.code.rev{{fill:{INK}}}
.num{{font-family:'Mono',monospace;font-size:12px;fill:#b8b3ad}}
.tabtext{{font-family:'Mono',monospace;font-size:12.5px;fill:{STONE}}}
.cv{{fill:#ffffff}}
.ca{{fill:{INK}}}
.ink{{fill:none;stroke:{INK};stroke-width:3.2;stroke-linecap:round;stroke-dasharray:101;stroke-dashoffset:0;animation:ink {LOOP}s infinite}}
@keyframes ink{{0%{{stroke-dashoffset:101;opacity:1;animation-timing-function:cubic-bezier(.6,0,.3,1)}}{pct(START - 0.1)},{pct(LOOP - FADE)}{{stroke-dashoffset:0;opacity:1}}{pct(LOOP - 0.05)},100%{{stroke-dashoffset:0;opacity:0}}}}
.block{{animation:block {LOOP}s infinite}}
@keyframes block{{0%,{pct(LOOP - FADE)}{{opacity:1}}{pct(LOOP - 0.05)},100%{{opacity:0}}}}
.barfill{{transform-box:fill-box;transform-origin:left center;animation:bar {LOOP}s infinite}}
@keyframes bar{{0%,{pct(conf_end)}{{transform:scaleX(0);animation-timing-function:cubic-bezier(.2,.8,.2,1)}}{pct(conf_end + 0.7)},{pct(review_end)}{{transform:scaleX({0.7 / 0.85:.4f});animation-timing-function:cubic-bezier(.2,.8,.2,1)}}{pct(review_end + 0.8)},100%{{transform:scaleX(1)}}}}
.mark{{opacity:0;animation:mark {LOOP}s infinite}}
@keyframes mark{{0%,{pct(review_start - 0.55)}{{opacity:0}}{pct(review_start - 0.15)},100%{{opacity:1}}}}
@keyframes cvr{{0%,{pct(review_start - 0.55)}{{fill:#ffffff}}{pct(review_start - 0.15)},100%{{fill:{TRACK}}}}}
.caret{{opacity:0;animation:caret {LOOP}s step-end infinite}}
@keyframes caret{{0%,{pct(hold_from)}{{opacity:0}}{pct(hold_from + 0.01)}{{opacity:1}}{pct(hold_from + 0.55)}{{opacity:0}}{pct(hold_from + 1.1)}{{opacity:1}}{pct(hold_from + 1.65)}{{opacity:0}}{pct(hold_from + 2.2)}{{opacity:1}}{pct(hold_from + 2.75)}{{opacity:0}}{pct(hold_from + 3.3)}{{opacity:1}}{pct(LOOP - FADE)},100%{{opacity:0}}}}
{"".join(cover_css)}
@media (prefers-reduced-motion:reduce){{
.cv,.ca,.ink,.block,.barfill,.caret,.mark{{animation:none}}
.cv,.ca{{display:none}}.caret,.mark{{opacity:1}}
}}"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">MurphySig — sign your work</title>
<desc id="d">A MurphySig block types itself into a code comment: Signed, Format, Context, Confidence with an ink bar, Open, then a Reviews entry that raises the confidence. Beside it: MurphySig. Sign your work. No tooling required; a comment block, any language; spec v0.4; fabrication 11% to 0% on Claude in the benchmark; Unlicense.</desc>
<!-- Generated by scripts/hero/build_hero.py — edit that, not this. Fonts: Instrument Serif, Inter Tight, JetBrains Mono (SIL OFL 1.1). -->
<style>{css}</style>
<defs>
<linearGradient id="fade" x1="0" x2="1"><stop offset=".08" stop-color="#fff" stop-opacity=".9"/><stop offset=".3" stop-color="#fff" stop-opacity=".18"/><stop offset=".5" stop-color="#fff" stop-opacity=".18"/><stop offset=".56" stop-color="#fff" stop-opacity=".9"/></linearGradient>
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
<g filter="url(#shadow)"><rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h:.1f}" rx="10" fill="#ffffff" stroke="{GRID}"/></g>
<g clip-path="url(#cardclip)">
<rect x="{card_x}" y="{card_y}" width="{card_w}" height="{tab_h}" fill="{TRACK}"/>
<path d="M{card_x} {card_y + tab_h}h{card_w}" stroke="{GRID}"/>
<rect x="{card_x + 14}" y="{card_y + 7}" width="{advance(mono, FILE_TAB, 12.5) + 26:.1f}" height="{tab_h - 7}" rx="5" fill="#ffffff"/>
<text class="tabtext" x="{card_x + 27}" y="{card_y + 25}">{FILE_TAB}</text>
<g class="block">
<rect class="mark" x="{card_x + 1}" y="{hl_y:.1f}" width="{card_w - 2}" height="{hl_h:.1f}" fill="{TRACK}"/>
<path class="mark" d="M{card_x + 1.5} {hl_y:.1f}v{hl_h:.1f}" stroke="{INK}" stroke-width="3"/>
{"".join(rows)}
<rect x="{bar_x:.1f}" y="{bar_y:.1f}" width="{bar_w}" height="9" rx="2" fill="{TRACK}" stroke="{CONN}" stroke-width=".8"/>
<rect class="barfill" x="{bar_x:.1f}" y="{bar_y:.1f}" width="{bar_w * 0.85:.1f}" height="9" rx="2" fill="{INK}"/>
{"".join(covers)}
<rect class="caret" x="{last_x:.1f}" y="{last_y - mono_size + 2:.1f}" width="8" height="{mono_size + 3:.1f}" fill="{INK}"/>
</g>
</g>
</svg>
"""


def main() -> None:
    svg = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg)
    print(f"wrote {OUTPUT.relative_to(REPO)} ({len(svg.encode()) / 1024:.0f} KB)", file=sys.stderr)


if __name__ == "__main__":
    main()
