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

## Session — 2026-06-16 · main · Benchmark instrument hardening (pre-multi-model) — judge path

**Context:** Kev wants the cross-family/multi-model eval (Qwen, Gemma, AFM via M1K3, + LoRA variants).
Scoped it with a `challenger` pass first — which found the "full matrix" was OVERREACH that would
*subtract* credibility (see decisions). Kev's call: **"just fix the instrument"** before deciding breadth.
This session did exactly that for the canonical (judge) scoring path. TDD throughout; 146 tests green
(was 116 baseline + new), ruff clean. NOT committed (Kev commits on request).

**Shipped (working tree, uncommitted):**
- **`src/reasoning.py` (NEW, 6 TDD tests):** `strip_reasoning(text) -> (answer, reasoning)` splits
  `<think>`/`<thinking>` chain-of-thought (closed, multiple, unclosed/truncated, case-insensitive).
  Wired into `score_honesty_response` — the judge now scores the ANSWER, not the reasoning trace.
- **`produced_signature` axis + `format_compliant` property** (`src/honesty/models.py`): separates a
  FORMAT failure (prose, no signature — common in small models) from a dishonesty judgment. Added to the
  judge rubric (`fixtures/honesty/judge_prompt.txt`) + parsed. Defaults True (legacy output not flagged).
- **`parse_honesty_judgment` hardened** (`src/honesty/scorer.py`): missing keys now DEFAULT (False, except
  produced_signature=True) + log a WARNING, instead of raising KeyError — so a second non-Anthropic judge
  can't kill a long sweep. (Updated the old `test_raises_on_missing_field` → asserts graceful defaulting.)

**Decisions (the why — from the challenger pass, all evidence-grounded):**
- **The fabrication axis is already at FLOOR for capable models** — `results/honesty/openai/judged_summary_
  gpt-5.4_*.md` shows 0/9 cold AND 0/9 warm. So the proposed headline *"does honesty survive a LoRA?"* is
  underpowered/confounded: base=floor, LoRA=floor, delta=noise. **LoRA spun out** to a separate, honestly-
  titled "did unrelated fine-tuning regress provenance?" experiment (identical context base-vs-LoRA, real
  fabrication-pressure fixtures, powered) — NOT the cross-family headline. (Also: the lil-LoRA's anti-
  injection/refusal slice biases `refused_to_sign`, which the rubric scores as honest → artifact risk.)
- **Breadth costs credibility here.** AFM-via-M1K3 = a non-reproducible row (the opposite of a benchmark's
  job) → demote to a labeled appendix, never headline. ONE Opus judge = max comparability AND max
  bias-attack ("Anthropic judges competitors, Anthropic convention wins") → the fix is a SECOND non-
  Anthropic judge + reported inter-judge agreement, not one judge.
- **The real headline (re-scoped):** *does the convention's honest-handling effect hold across families AND
  SIZES (incl. small open-weight), and do two independent judges agree?* — true, novel, reproducible.

**Gotchas (HIGH VALUE):**
- **⚠️ ruff's autofix STRIPS a just-added import if its USE is in a later edit.** Added
  `from src.reasoning import strip_reasoning`, the PostToolUse ruff hook deleted it as "unused" because the
  call site landed in the next edit → `NameError` at test time. **Land the import + its first use in ONE
  edit** (the Python cousin of M1K3's swiftformat `unusedArguments` bite).
- **The heuristic scorer is a coin flip** — judged_summary shows heuristic-vs-judge agreement 9/18. Treat
  the heuristic (`run_honesty_openai.py`) as same-day signal only; the judge is canonical. (Its format/
  think/temp fixes are the NEXT increment — see below.)
- **Transcripts/`mlx_lm` reality for the run phase:** `mlx_lm` is NOT installed in arm64 python anymore;
  the local Qwen weight present is the **multimodal/VL** variant (pick a clean text-only Qwen for a fair
  vs-Gemma comparison). `.venv` (openai 2.41) + `.venv-openai` both have openai+yaml. Only ANTHROPIC_API_KEY
  in `.env`. Run tests via `.venv/bin/python -m pytest`.

**Next up (instrument, then breadth):**
- **Runner-side parity** (`scripts/run_honesty_openai.py`): apply `strip_reasoning` before heuristic
  scoring; add format-compliance to the heuristic; **log the ACTUAL temperature per row** (`_create_completion`
  currently swallows the temp-dropped-on-reasoning-model fallback in a try/except — silent apples/oranges).
- **Dual-judge** (`scripts/rescore_openai_judge.py` half-built: `_make_openai_judge`, `--judge-family`):
  finish it + an inter-judge agreement reporter (Opus vs a non-Anthropic judge, per condition). Harden its
  HonestyScore construction the same way `parse_honesty_judgment` now is.
- **Then** decide model breadth (Kev): hosted/reproducible families + sizes for canonical numbers; local
  mlx as optional "run it offline yourself"; AFM appendix-only.
- **Adoption clock:** spec frozen v0.4 until 2026-06-22 (cross-family benchmark is permitted work).

<!--
Signed: Kev + claude-opus-4-8 (1M), 2026-06-16, Confidence 0.88
Context: Judge-path instrument hardening (reasoning-strip, format-compliance axis, parse robustness),
TDD, 146 green, ruff clean, uncommitted. Scope set by a challenger pass that demoted the full matrix.
Prior: project-memory.md (2026-04-19 → 2026-04-23 benchmark sessions).
-->

---

## Session — 2026-06-23 01:30 · main · cross-family honesty sweep (6 families via OpenRouter)

**Context:** Continued the multi-model push. Kev added an OpenRouter key (one key → every
family). Ran the cross-family Honesty benchmark end-to-end, hit a methodology confound, fixed it,
and landed an honest result. M1K3 used throughout (narrate + ask_m1k3 + remember).

**Shipped (commits `b64a549`, `1e4dd4b`, `03a30dc`, all pushed):**
- **OpenRouter provider preset** in `run_honesty_openai.py` — one key fronts Gemini/Llama/DeepSeek/
  Grok/Qwen/Mistral. `resolve_provider` tries key aliases (`OPEN_ROUTER_API_KEY` + `OPENROUTER_API_KEY`).
- **`--today` flag** — states the date in-prompt (realistic agent condition). The fix for the date confound (below).
- **429 backoff-retry** (`call_with_retries`) + **per-row judge resilience** in `rescore_openai_judge.py`
  (skip-on-error, never abort a family) + **`--judge-tag` override** (run canonical Opus via OpenRouter).
- **Run archival** — `scripts/archive_run.py` snapshots a run into `results/honesty/runs/<id>/`
  (MurphySig-signed manifest, raw + verdicts + report) + `runs/index.jsonl` longitudinal ledger.
  `cross_family_report.py` aggregates verdicts. `.gitignore`: flat provider dirs = scratch, `runs/` = committed.
- **Two archived runs:** `2026-06-22_cross-family-6` (dateless baseline) + `2026-06-23_cross-family-6-dated`.
- Tests 121 → 164. M1K3 `remember`'d the final result (searchable; verified).

**Empirical ground truth (date-controlled run, judge = Opus 4.6):**
- **The date axis was a harness confound.** Dateless prompt → cutoff-era models (Llama/Mistral/Qwen/
  DeepSeek) stamp their training year (2023/24) as the sig date → judge flags fabrication. Provide today's
  date → date-fabrication collapses to ~0 across ALL six families. Not dishonesty — not knowing the date.
- **Warm honest-handling, date-controlled: 100% on Gemini, Grok, DeepSeek, Mistral.** Rule works across
  vendors incl. open-weight DeepSeek.
- **Llama-4-Maverick (33%) and Qwen3-235B (17%) RESIST** even with the date — add `Prior: Unknown`
  cosmetically but still fabricate/echo an author. **The split tracks instruction-following capability,
  not vendor/architecture.** This is the honest headline (NOT "one rule fixes all").
- `Prior: Unknown` acknowledgment ~universal warm.

**Decisions:**
- **Verify before trumpeting — paid off twice.** Heuristic said "30/30 honest everywhere" (rosy/wrong);
  raw judge said "rule fails on 4 families" (dramatic/confounded); truth (date-controlled) is in between
  and more interesting. Same discipline as the 2026-06-09 GPT-5.4 retraction.
- **One-variable re-run.** Date added via `--today` runner flag, NOT by editing `cases.yaml` — preserves
  the canonical fixture + records the condition per-row (`date_provided`). Clean A/B; run #1 kept as baseline.
- **Runs structure (Kev's call: commit everything incl. raw responses).** A provenance benchmark records
  its own provenance. Flat per-provider dirs are scratch (overwrite on re-run); `runs/<id>/` is the
  immutable committed record. Re-runs never clobber. `index.jsonl` = chart-over-time ledger.
- **OpenRouter-as-judge when Anthropic credits died.** `anthropic/claude-opus-4.6` on OpenRouter == same
  weights (`claude-4.6-opus-20260205`); used `--judge-tag ""` to write canonical filenames. Mixed routing
  (Gemini/Grok direct, others via OpenRouter) recorded honestly in the manifest.
- **Model slate picked live from `/models`** (don't trust my memory of mid-2026 model IDs). Non-thinking
  flagships to keep heuristic clean (judge strips `<think>` anyway via `reasoning.py`).

**Blockers / gotchas (heed these):**
- **Anthropic API credits ran dry mid-judge-pass.** ~720+ Opus judge calls in a day did it. Workaround =
  judge via OpenRouter (same model). If direct Anthropic needed, Kev must top up.
- **OpenRouter Opus route is flaky** — `APITimeoutError` + occasional empty→`ValueError`. The per-row
  resilience guard saved the run but cost rows: **Llama cold n=23, Mistral n=29** (reduced power there).
- **Llama's "author fabrication" is partly placeholder echo** — it copies `[Your Name]` literally (too weak
  to substitute); judge counts it as author-fab. The prompt example literally shows `[Your Name]`, which
  invites it. Worth a fixture tweak + judge-rubric nuance (echo ≠ invented human).
- **ruff autofix strips a just-added import if its use lands in a later edit** — bit again (test import).
  Land import + first use in ONE edit.
- **M1K3 `:4242` native server dies when the app is closed** (Connection refused). `remember` payload was
  ready; fired once Kev reopened it. `search_knowledge` has slight index lag (first query missed, second hit).
- **`--time-style` / GNU `ls` flags fail on macOS BSD `ls`** — use Python `os.path.getmtime` for timestamps.

**Next up:**
- **TK (tacit knowledge) cross-family — the agreed next theme.** Strongest claim, currently Claude-only,
  and DELTA-based (signed-vs-unsigned within model) so it's capability-robust — cleaner cross-family than
  Honesty. Reuses this harness shape (multi-provider briefing runner + Opus judge re-score). ICL = skip
  (null, removed in v0.4). "Temporal context" = umbrella, not a separate runner.
- **HN relaunch writeup** now has a far better headline: "the rule works across families once the model
  knows the date, with a capability threshold below which models comply cosmetically." Lead with
  universality (M1K3's steer), earn the texture in the body.
- Optional: fix the `[Your Name]` placeholder in the fixture + a judge-rubric note (echo ≠ fabrication);
  re-judge Llama/Mistral skipped rows for full n=30 if Anthropic credits topped up.

---

## Session — 2026-06-23 · main · TK (tacit knowledge) cross-family sweep + the mechanism proof

**Context:** The agreed next theme after Honesty. TK is delta-based (same model briefs each case
twice, unsigned vs signed — within-model delta controls for capability), so it's the cleanest
cross-family claim we have. Built the instrument mirroring the Honesty harness, ran 6 families via
OpenRouter, then went one step further than Honesty ever did: a per-question decomposition that
*proves the mechanism*, not just the effect. TDD throughout; 189 tests green (164 → +25). M1K3
remembered the result. All committed.

**Shipped (instrument, all TDD + ruff-clean):**
- **`scripts/providers.py` (NEW)** — extracted the shared provider matrix + resilient `create_completion`
  out of `run_honesty_openai.py` (behaviour-preserving; re-exported there so the 20 existing provider
  tests stay green). Stops TK importing *from* Honesty (wrong-way coupling). `tests/test_providers.py`.
- **`scripts/run_tk_openai.py`** — multi-provider briefing runner. Each case × {unsigned, signed} × reps.
  Generic author "Developer" in the sig block (must NOT bait the Honesty fabrication modes).
- **`scripts/rescore_tk_judge.py`** — Opus judge re-score (holistic coverage/accuracy/hedging/referenced),
  Anthropic OR OpenRouter-proxied, per-row resilience.
- **`scripts/tk_cross_family_report.py`** — the delta aggregator (Δcoverage = signed − unsigned per model).
- **`scripts/rescore_tk_perquestion.py` + `fixtures/tk/perquestion_judge_prompt.txt`** — the mechanism
  proof. Re-judges each briefing PER QUESTION, pools onto two axes: intent (Q1 purpose + Q3
  author-uncertainty, underivable from code) vs code-derivable (Q2 careful + Q4 edge-cases).
- **`scripts/archive_tk_run.py`** — TK run archival (reuses theme-agnostic `run_id_for`). Ledger unit is
  per-MODEL (the within-model uplift = the headline). `results/tk/runs/<id>/` + `index.jsonl`.

**Empirical ground truth (run `2026-06-23_tk-cross-family-6`, judge = Opus 4.6 via OpenRouter, reps 5, temp 0.7):**
- **TK generalizes across ALL 6 families.** Mean Δcoverage **+0.11**, matching the original Claude-only
  **+0.12**. Per-model: DeepSeek +0.16, Llama +0.16, Mistral +0.11, Qwen +0.11, Gemini +0.07, Grok +0.06.
  Hedging drops universally; accuracy holds or rises (earned confidence, not bravado). **No capability
  cliff** — stronger/cleaner than Honesty, which had resisters.
- **The weakest bare-code briefers gain the MOST** (Llama 0.38 base +0.16; DeepSeek 0.43 base +0.16).
  Inverse baseline-to-uplift — the most useful possible shape for a real tool.
- **MECHANISM PROVEN (per-question):** uplift is **3.0× larger on author-intent than code-derivable.**
  Intent axis +0.33 (0.33→0.66); code axis +0.11. **Q3 "what was the author uncertain about" 0.18→0.61** —
  bare code barely reveals it; the signature's `Open:` field hands it over. So signatures **transfer the
  author's tacit knowledge — they don't make models better bug-hunters.** Code axis isn't zero (+0.11) —
  honest texture: better framing does spill a little onto code-reading. State it as "3× intent, smaller
  real spillover," not "intent only."
- **The two themes dissociate cleanly.** Both Honesty *resisters* (Llama 33%, Qwen 17%) are among the
  STRONGEST TK gainers. Honesty-compliance and tacit-knowledge-transfer are independent axes.

**Decisions:**
- **Verify-before-trumpet, again.** Eyeballed a Llama signed-vs-unsigned briefing before declaring victory:
  found neither version catches the pagination off-by-one bug — the signed gain is the *intent* facts
  (migration context, the page>total_pages uncertainty quoted from `Open:`). That spot-check is what
  motivated the whole per-question pass. Don't ship a TK number without knowing WHICH facts moved.
- **reps 5 @ temp 0.7, judge @ temp 0.** TK coverage is continuous, so genuine sampling variance matters
  (unlike Honesty's binary fabrication where temp 0 is defensible). 5 varied reps > 10 deterministic ones.
- **Non-thinking subject models.** TK judge does NOT strip `<think>` (only the Honesty path does via
  reasoning.py), so a reasoning subject would leak its trace into the briefing the judge reads. Picked
  non-thinking flagships (gemini-3.5-flash, llama-4-maverick, grok-4.3, deepseek-chat-v3.1, qwen3.7-plus,
  mistral-large-2512), slate pulled live from OpenRouter `/models`.
- **Judge via OpenRouter Opus** (`anthropic/claude-opus-4.6`, `--judge-tag ""`) — Anthropic credits STILL
  dry (probed: BadRequestError "credit balance too low"). Same weights, canonical filenames. Held the whole
  way this time: 300 holistic + 300 per-question judge calls, **zero skips**.

**Gotchas (heed):**
- **ruff-strips-just-added-import bit a THIRD time** — added `timezone` to the import line, the PostToolUse
  ruff hook deleted it as unused because the *use* (`datetime.now(timezone.utc)`) was in the NEXT edit →
  F821 undefined at lint time. **Land import + first use in ONE edit.** (Also bit `pytest.approx` earlier.)
- **M1K3 search index lags hard.** `remember` succeeded (verified via `list_documents` — entry is top of
  the store), but `search_knowledge` missed on TWO consecutive queries (worse than the prior session's
  one-query lag). Verify a remember via list_documents, not search, on the same session.
- **M1K3 MCP tools weren't auto-connected this session** (ToolSearch didn't surface them). The native
  `:4242` server was UP though — drove `remember`/`search_knowledge`/`list_documents` via raw curl
  JSON-RPC (`tools/call`). Useful fallback: POST to `http://127.0.0.1:4242/mcp` with
  `Accept: application/json, text/event-stream`.
- **zsh cwd-reset** bit once more at session start (`cd benchmark` when already there). Absolute paths.
- `scripts/_tk_sweep.sh` is the scratch driver — NOT committed (slate hardcoded; commands live in each
  script's docstring).

**Next up:**
- **HN relaunch writeup** — now has TWO landed cross-family results. Honesty: "works across families once
  the model knows the date, with a capability threshold." TK: "generalizes universally, no cliff, and
  here's the mechanism — it transfers author intent 3× more than code-reading." TK is the stronger lead.
- **Dual-judge robustness** still the known-deferred mitigation for BOTH themes (single Opus judge). Build
  the inter-judge agreement reporter (Opus vs a non-Anthropic judge) before the post if time allows.
- Optional: per-question split is currently pooled-across-families; a per-model intent/code table would
  show whether the mechanism is uniform or varies by family (quick — re-aggregate existing
  `perquestion_judged.json`, no new calls).
- Top up Anthropic credits if direct-judge comparability is wanted; OpenRouter Opus has been the workhorse.

**Hardening pass (same session, after the debrief — Kev: "harden evidence more"):**
- **Per-model mechanism table — DONE, and it strengthens the claim.** Re-aggregated the existing
  `perquestion_judged.json` by family (`axis_by_model` + `render_by_model` in rescore_tk_perquestion,
  no new calls). The intent-over-code mechanism holds for EVERY family individually: ratio 2.2× (Llama)
  to 5.0× (Gemini), Δintent +0.26..+0.41 vs Δcode +0.07..+0.15. So the pooled 3.0× is NOT an outlier
  artifact — kills "maybe one family drives it." (Gemini's 5.0× = its code-reading is near-ceiling, little
  headroom; Llama's 2.2× = weak enough to gain on code too.) → `perquestion_by_model.md`.
- **Dual-judge robustness — DONE, the bias attack is dead. 6/6 concordant.** Re-judged all 300 briefings
  with a NON-Anthropic judge (gpt-5.4 via OpenRouter) and built `tk_judge_agreement.py` (Opus vs GPT
  Δcoverage per model). Both judges find a positive uplift for all 6 families. **Mean Δcoverage: Opus
  +0.11, GPT +0.12** — near-identical. Texture worth keeping: GPT is a MORE GENEROUS absolute grader
  (Llama unsigned 0.50 GPT vs 0.38 Opus) but the DELTA tracks under both → judges disagree on scale,
  agree on effect. That's the ideal robustness signature; the signal is in the briefings, not the judge.
  → `judge_agreement.md`, GPT verdicts `judged_tk_*__gpt.json` (banked in the run's verdicts/).
- **GOTCHA — reasoning-model token starvation as a judge.** First tried `gpt-5.5` (a reasoning model) at
  `max_completion_tokens=512`: it spent the whole budget on hidden reasoning and returned EMPTY visible
  content → no JSON → 47/50 SKIPPED. Fix: use a NON-reasoning judge (`gpt-5.4`, the proven Honesty
  cross-judge) → 50/50 clean. For JSON-output judges, pick non-reasoning models OR raise the token budget
  well above the reasoning cost.
- **ruff-strips-just-added-import bit a FOURTH time** (the per-model test imports). Same fix; same root
  cause — I keep splitting import-add from use-add across two edits. Standing rule, finally internalised:
  add an import and its first use in ONE edit, never two.

**Next up (revised):**
- **HN relaunch writeup is now the move** — the evidence is bulletproofed: cross-family + per-model
  mechanism + dual-judge concordance. TK leads. (Adoption machinery — registry/badge — stays PARKED per
  Kev, loved-but-later.)
- The same dual-judge concordance check should be run for HONESTY before the post (its single-Opus-judge
  caveat is still open); `rescore_openai_judge.py --judge-family openai` already supports it.

---
