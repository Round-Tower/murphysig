# Project Memory — MurphySig

Durable context for AI-assisted work. Managed by /debrief.
Edit freely — the skill only appends new session blocks.

---

## Session — 2026-04-19 11:55 · main

**Shipped:**
- Spec v0.4 "The Narrowing" — `site/src/pages/spec.md`, `site/public/spec.txt`, `site/public/llms.txt`
- Four-theme empirical benchmark suite at `benchmark/` — 48 files, 5629 lines, 116 passing tests, flat CLI (`python -m src {run,tk-run,honesty-run,all}`)
- Three benchmark runs executed and reported — ICL v2a (90 reviews), TK (60 briefings), Honesty (36 signings), plus unified four-theme report
- `/benchmark` public page at `site/src/pages/benchmark.md` with editorial hero figures (`0.65 → 0.77` and `11% → 100%`)
- Site design refresh — Inter → Inter Tight swap, page-load settle animation (prefers-reduced-motion guarded), paper-grain noise overlay, journal-grade editorial tables (tabular-nums + double rules + mono small-caps headers), `.figure-hero` + `.figure-hero-pair` CSS components, footer v0.3.3 → v0.4 with Home + Benchmark links
- 5 clean commits on main, deployed to Netlify, verified live (`curl` returns v0.4 everywhere)

**In flight:**
- Nothing critical. Benchmark v3 planning is in `~/.claude/projects/.../memory/murphysig_expansions.md`.

**Decisions:**
- **Four themes > three themes.** Kev explicitly refined the philosophy mid-session: tacit knowledge + in-context learning + honesty/provenance + reflection (not my earlier 3-theme framing). Tacit knowledge is the load-bearing theme — it's what the Gallery Problem is a symptom OF. This reshaped the whitepaper argument and what v0.4 should lead with.
- **Commit CLI at v0.3.3, not v0.4.** `bin/sig` still generates v0.3.3 signatures. Intentional — v0.3.3 is a valid older Format version, and bumping would require updating every generated output + fixture. Spec-template examples got bumped to v0.4; historical dated examples preserved at their original version per the spec's own immutability rule.
- **Commit `.md` reports only, not raw JSONs.** `benchmark/.gitignore` excludes `results/**/*.json`. Reports (.md) are the source of narrative truth; raw response JSONs stay local. Reduces repo size and avoids committing full prompt-and-response content.
- **Skipped Sketch C phase 1 (src/ reshape into common/icl/tk/honesty subdirs).** New TK + Honesty live in their own subpackages; existing ICL code stays flat. Reshaping would touch 116 tests with zero user benefit. Revisit only if a concrete shared-client extraction appears.

**Blockers / gotchas:**
- **The ICL scorer was silently broken pre-2026-04-18.** `.format()` collided with literal JSON `{...}` in the judge prompt rubric, raising `KeyError: '\n "bug_detected"'` on every call. v1 fell back to heuristic scoring, which is why scrutiny was pinned at 5.0. Fix in `benchmark/src/scorer.py` uses `str.replace()` instead of `.format()` for the four real placeholders. Regression test at `tests/test_scorer.py::TestScoreResponse::test_template_with_literal_json_rubric`.
- **Enum sort ordering.** `sorted(dict_items_with_enum_keys)` fails with `TypeError: '<' not supported between instances of 'PromptCondition' and 'PromptCondition'`. Fixed in TK + Honesty reporters with explicit `key=lambda kv: (kv[0][0], kv[0][1].value)`. Any new reporter with Enum-keyed groupings needs the same.
- **Anthropic API "specified API usage limits"** is user-set (Console → Settings → Limits), not account cap. The `.env` file doesn't need replacing — just bump the limit.
- **Astro + dev server cwd**: `cd site && npm run dev` — if starting dev server, must be from `site/`. Bash tool doesn't persist cwd across calls cleanly on session restart.

**Empirical findings to treat as ground truth:**
- **TK strongly supported:** signatures measurably help AIs brief unfamiliar code. Coverage +0.12 (0.65 → 0.77) universal across all 5 cases. Hedging -0.4. 93% reference rate.
- **Honesty strongly supported:** "Never Fabricate" rule achieves perfect compliance. Cold 11% fabrication → warm 0%. Honest handling 11% → 100% (+89% delta — biggest effect in any MurphySig benchmark). `orphan_utility` case: 33% cold fabrication, 0% warm.
- **ICL partial:** signatures are read (85%+) but confidence direction does NOT polarize review behavior. The spec's "Confidence: 0.3 says scrutinize" claim was refuted and removed in v0.4.
- When pitching MurphySig, lead with TK + Honesty, not ICL.

**Next up:**
- **Replicate TK at n=10** — firm up the headline coverage finding. Cheapest path to a defensible "signatures help AIs read" claim.
- **Cross-family Honesty test** — does GPT fabricate at same rate as Claude? Does warm prompt work across families? This is where MurphySig goes from "interesting for Claude users" to "general AI hygiene rule."
- **Subtler ICL cases** — 4/5 current cases hit 100% detection ceiling. Need bugs that are actually missable (concurrency, subtle types, input-flow-dependent security).
- **v3 should test `Heuristic:` field priming.** Does asking AIs to write `Heuristic:` change their downstream self-disclosure? Untested.
- **Registry / badge** (`murphysig.dev/signed/<repo>`) is still the highest-leverage adoption move. Scan GitHub for `.murphysig` files, gallery view, linkable badge. Nothing exists yet.

---

## Session — 2026-04-19 12:50 · main

**Shipped:**
- Layer 1 install path — `site/public/init.sh` + Netlify `/init` redirect. Users run `curl -sL murphysig.dev/init | bash` in their repo root; script writes `.murphysig` seeded with git author + today's date, prepends `@.murphysig` to CLAUDE.md if present. Idempotent, shellcheck-clean.
- Manual alternative at `site/public/murphysig-template.txt` for users who won't pipe curl to bash.
- Homepage augmented with a new "Or set up a whole project" section — single curl command, source link to /init.sh, template alternative. Slots cleanly under the existing "Try it now" single-file example.

**Decisions:**
- **The `.murphysig` file IS the product.** Layer 1 is "zero install, just convention propagation" — the Honesty benchmark showed 100% compliance when the rule is in-context. Every other layer (MCP, hooks, CI) is scaffolding around this core.
- **Two paths, both documented.** `curl | bash` for speed; plain template at `/murphysig-template.txt` for users who (reasonably) distrust piping shell scripts. Same result, different trust model.
- **Skip Layer 2+ for now.** Kev explicitly said "other options for later" — MCP server, GitHub Action, Homebrew/npm/pip, registry/badge are ranked in `~/.claude/projects/.../memory/murphysig_expansions.md`. Layer 2 (MCP) is the next high-leverage move per that ranking.

**Blockers / gotchas:**
- None for Layer 1. Shipped clean.

**Next up:**
- **Layer 2: `@murphysig/mcp` MCP server.** Estimated afternoon of work. Wrap `bin/sig` commands as MCP tools, publish via npm. Claude Code users add one entry to settings.json and get native tool access.
- **GitHub Action** after that — public PR visibility is the adoption channel that doesn't require user install at all.

---

## Session — 2026-04-23 21:55 · main · 8 commits pushed

**Shipped** (`92ebcd8` → `bdd81c7`, all on origin):
- `92ebcd8` CLI fixes from 6-month audit: emit Format v0.4 (was v0.3.3); `get_author` honours `MURPHYSIG_AUTHOR` env > `.murphysig.author` file > git config; `cmd_add` prompts separately for confidence rationale; tab-separator in `get_signature_info` (pipes in single-line shorthand sigs were scrambling gallery columns); `cmd_review` inserts ". " before "Confidence now" + strips trailing period from text. Pure-bash test suite at `tests/test_sig.sh` (9 assertions, no deps).
- `f4822f6` `CLAUDE.md` + `README.md` aligned to spec v0.4 (older sigs not back-bumped — bump-on-edit only per spec immutability rule).
- `398283a` `site/src/pages/launch.md` — 90-day HN field report. Anchored on Honesty finding + 90d adoption numbers + explicit ask for cross-family validation.
- `63e534f` `benchmark/scripts/run_honesty_openai.py` (standalone, separate from production async-Anthropic runner) + GPT-5.4 results. **100% → 0% fabrication** cold→warm, n=18. Stronger than original Claude (11→0%). Different failure mode — GPT signs as itself ("ChatGPT + GPT-5") not lifting "John"/"ACME" from comments. Same rule fixes both.
- Repo flipped **PUBLIC** via `gh repo edit`, description + homepage + 10 topics set, `git gc` shrunk repo 170M → 540K.
- `096c8bf` `README.md` rewritten — OG image, badges, evidence table including GPT-5.4 cross-family row, three quick-start paths, specific contributing ask.
- `bdd81c7` SEO audit fixes: `pre { max-width: 100% }` (mobile horizontal scroll on /launch/), footer `text-neutral-500 → text-neutral-600` (WCAG AA contrast), per-page Schema.org via `MarkdownLayout.astro` (TechArticle/Dataset/BlogPosting/ScholarlyArticle), whitepaper staleness banner, homepage hero figure-pair surfaces 11→0% + 0.65→0.77 above the fold.

**Decisions:**
- **Held GPT-5.4 result for next-week relaunch, NOT a follow-up comment** on tonight's HN thread. Launch sank under GPT-5.5 release (1pt/0c after 3h). The cross-family number deserves a clean post on a quieter day.
- **CLI emits v0.4, benchmark/* fixtures stay frozen at v0.3.3.** Benchmark fixtures are reproducibility artefacts for runs that happened at v0.3.3; bumping would break the experiment record. Different lifecycle from the live emit path.
- **Per-page Schema in `MarkdownLayout.astro` via inline objects, not imports.** Simpler than separate JSON files + import + tree-shake; small enough to inline. ArtLayout accepts optional `schemaJson` prop, falls back to WebSite default for `/`.
- **Author resolution order in `bin/sig`:** env > `.murphysig.author` file > git config > $USER. Env wins so users have one global preference (`export MURPHYSIG_AUTHOR=Kev` in `.zshrc`); file wins next so projects can use a pen-name persona.
- **Inlined the canonical short author/model token form** in `~/.claude/skills/murphysig/SKILL.md`: never invent dated suffixes when Anthropic only publishes the family alias (`claude-opus-4-7`, not `claude-opus-4-7-20260315`). Caught myself fabricating a date mid-edit.
- **60-day adoption clock starts now (until 2026-06-22).** Spec frozen at v0.4. Only adoption-surface work allowed (registry/badge, MCP, cross-family benchmark). Stop conditions documented in `~/.claude/projects/-Users-kevinmurphy/memory/project_murphysig_launch.md`.

**Gotchas (future-me, heed these):**
- **Local `rg` for adoption audits is wildly unreliable.** Initial sweep found 21 sigs across `~/Development/`. GH commit-message search (`gh api search/commits?q=author:kpmmmurphy+MurphySig`) found **137+ in 90d across 7 repos**. Truth lives on GitHub, not local clones. For any adoption-or-usage question: `gh api search/commits` first, ripgrep never.
- **`bin/sig` self-signs at v0.3.3 in its own header** — that's the historical version when it was originally signed; do NOT bump in-place. Add a Reviews entry instead. Same applies to all in-repo old sigs (only bump on substantive edit; preserve historical Format value).
- **`/llms.txt` "prompt-injection" alarm from `seo-technical` was a false positive.** The agent saw context-leak from its own fetch chain, not actual served content. Verified directly: `/llms.txt` is clean. If a future audit flags injection-looking text in served files, **`curl` the file yourself before panicking**.
- **GPT-5 family API gotchas:** uses `max_completion_tokens` not `max_tokens`; rejects explicit `temperature` parameter on reasoning models (try-except fallback in `run_honesty_openai.py:140`).
- **Mac Python 3.9 pip-install is x86_64; arm64 binaries needed for openai/pydantic_core.** Use `/opt/homebrew/bin/python3.12` and a per-task venv. Pattern: `python3.12 -m venv .venv-openai`. Added `.venv*/` to `benchmark/.gitignore`.
- **Subprocesses don't inherit interactive shell exports.** When Kev `export OPENAI_API_KEY=...`, my Bash tool calls don't see it. Pass inline as env to the subprocess invocation: `OPENAI_API_KEY=... .venv-openai/bin/python ...`.
- **`!` prefix in chat does NOT prevent text from landing in the transcript.** Kev pasted his OpenAI key thinking it would stay local; it went into conversation context. Rotated immediately. **Future: never instruct the user to `!`-paste a secret. Use `.env` or have them set it in their shell directly without confirming the value to me.**
- **gemba and dyslexia-ai had heavy MurphySig adoption in commits but no `.murphysig` file at root** — pure discovery-layer gap. Provisioned 5 active repos tonight (gemba/Dyslexia-ai-Server/Cartogram/clair pushed; dyslexia-ai-ios committed locally on `version/3.4` since branch was 7 ahead — Kev to push when ready).
- **Homepage was contradicting v0.4 spec.** Said `Confidence: 0.75 says "scrutinize this"` — the exact claim "The Narrowing" deleted. Found while doing the SEO sweep, fixed in the same commit. **Always grep the homepage when bumping the spec; refuted-claim residue is the credibility leak you'll never notice yourself.**

**In flight (NOT this session, but worth noting):**
- HN post `47880139` flat at 1pt/0c after ~3h. Watcher logging at `/tmp/hn-watch/47880139.log` until self-terminates.
- 2 untracked: `screenshots/` (visual agent output) and `site/public/.!69663!og-image.png` (macOS Finder partial-write turd, safe to `rm`).
- `dyslexia-ai-ios` commit `48628e24` is local-only on `version/3.4` (was already 7 ahead of origin).

**Next up (in order of leverage):**
- **Build the registry/badge** (`/signed/<owner>/<repo>` + SVG endpoint). Acceptance criteria + tech sketch in `~/.claude/projects/-Users-kevinmurphy/memory/project_murphysig_launch.md` under "Next concrete deliverable." Critical detail: **never call GitHub from the badge endpoint** (30 req/min cap will DoS instantly) — nightly Action commits `data/registry.json` to repo, badge serves from static.
- **Next-week HN relaunch** of GPT-5.4 cross-family finding. Best window: Tue–Thu of week beginning 2026-04-27, 13:00–15:00 UTC. Re-score with Opus judge first for direct comparability with original Claude benchmark, then write the post.
- **Author/about page** at `/about/` — caps E-E-A-T authoritativeness ceiling per Sept-2025 QRG update. Bio + prior work + GitHub/LinkedIn `sameAs`.
- **Self-host fonts** via `@fontsource` (Inter Tight, Instrument Serif, JetBrains Mono) — closes both High Performance and the third-party privacy hop. ~300-600ms LCP win on slow networks.
- Mediums from the SEO audit (CSP header, `og:type=article` on /launch and /whitepaper, sitemap `lastmod` cascade via `@astrojs/sitemap`, IndexNow). All 1-2 weeks-of-polish, none blocking.
- Cross-family Honesty re-runs against Gemini + Llama — strongest empirical extension. Runner is ready (`benchmark/scripts/run_honesty_openai.py`); needs adapter for non-OpenAI APIs.
- `bin/sig` would benefit from `--author` CLI flag in addition to env var (skipped tonight per "no abstraction beyond what's needed" rule; revisit if a real user complains).

---
