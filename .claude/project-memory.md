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
