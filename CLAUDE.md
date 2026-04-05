# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

MurphySig is a human-readable provenance standard for signing creative work — a convention for documenting who made what, when, with what confidence, and what remains uncertain. No tooling required, just structured comment blocks.

Live at **https://murphysig.dev** (hosted on Netlify).

## Build & Development

All site commands run from the `site/` directory:

```bash
cd site
npm install          # Install dependencies
npm run dev          # Local dev server (Astro)
npm run build        # Production build → site/dist/
npm run preview      # Preview production build locally
```

Deploy is via Netlify (configured in `netlify.toml` — base is `site/`, publish is `site/dist/`, Node 20). There's also `site/deploy.sh` for manual Netlify CLI deploys.

The CLI tool lives at `bin/sig` (bash script, run with `./bin/sig help`).

## Architecture

### Two distinct parts:

1. **`site/`** — Astro 5 static site with Tailwind CSS v4 and `@tailwindcss/typography`
2. **`bin/sig`** — Standalone bash CLI for signing files, adding reviews, and viewing a gallery of signed work

### Site structure

- **Layouts**: `ArtLayout.astro` is the base layout (SEO, fonts, footer nav). `MarkdownLayout.astro` wraps it for long-form prose pages (spec, whitepaper).
- **Pages**: `index.astro` (homepage), `spec.md` and `whitepaper.md` (markdown pages using `MarkdownLayout`), `404.astro`
- **Styles**: `global.css` — Tailwind imports, typography plugin, CSS custom properties for the "printed manifesto" aesthetic. Fonts: Instrument Serif (headings), Inter (body), JetBrains Mono (code).
- **Public**: `llms.txt` (AI-optimized summary), `spec.txt` (plain text spec), `robots.txt`, `sitemap.xml`, `favicon.svg`

### Design language

Typography-first, "printed manifesto" feel. Paper-tone background (`#fbfaf8`), ink-dark text (`#1a1a1a`). All design tokens are CSS custom properties in `global.css`.

## MurphySig Convention (This Repo Practices What It Preaches)

This repo uses MurphySig v0.1. See `murphysig.claude.md` at project root for the full AI instruction set.

**Quick version:** When you create or modify a significant file, add an L0 credit line at the top:

```
# Drafted by [Human] with [Your Model + Version], [Date].
```

For critical code, use an L1 structured block (`---murphysig v0.1` delimiters). When modifying signed files, add a `reviews` entry rather than replacing the block. Never fabricate provenance.

Full spec: https://murphysig.dev/spec

## Key Files

| File | What it is |
|------|-----------|
| `MURPHYSIG_WHITEPAPER-v0.0.2.md` | Foundational philosophy (The Gallery Problem, in-context learning) |
| `.murphysig` | Project-level MurphySig declaration for AI discovery |
| `reviews/` | External reviews of MurphySig (from Gemini, GPT-5, Sonnet) |
| `bin/sig` | CLI tool — `init`, `add`, `review`, `gallery`, `questions` commands |

## Content Relationship

The spec and whitepaper exist in two forms each:
- **Rendered pages**: `site/src/pages/spec.md` and `whitepaper.md` (served as HTML via Astro)
- **Plain text**: `site/public/spec.txt` and root `MURPHYSIG_WHITEPAPER-v0.0.2.md`
- **AI summary**: `site/public/llms.txt`

Changes to spec content need to be kept in sync across these formats.
