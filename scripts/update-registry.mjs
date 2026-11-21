#!/usr/bin/env node
// Signed: Kev + claude-fable-5, 2026-06-09
// Format: MurphySig v0.4 (https://murphysig.dev/spec)
// Prior: Unknown (new file)
//
// Context: Nightly registry discovery for murphysig.dev/signed/.
// Searches GitHub code search for root-level `.murphysig` files,
// fetches each declaration, and writes site/src/data/registry.json.
// The badge and /signed/ pages are rendered statically from that
// JSON at build time — the badge endpoint NEVER calls GitHub (the
// search API's 30 req/min cap would DoS it instantly).
//
// Confidence: 0.75 - parser is unit-tested; the GitHub-API plumbing
// is straightforward but code-search visibility under the Actions
// GITHUB_TOKEN is the untested edge (a classic PAT in REGISTRY_TOKEN
// is the fallback).
// Open: Does GitHub code search index .murphysig files in forks or
// only source repos? Forks are currently whatever search returns.
//
// Review: Kev + claude-opus-5.5, 2026-10-06 — security + resilience.
// Declarations are attacker-controlled and the nightly commit deploys
// unattended, so parsed fields are now validated (version, date) or
// sanitised (author: control chars stripped, capped at 100). gh() retries
// rate limits with the advertised wait — two consecutive nightly runs had
// died on a single code-search 429. Confidence 0.85.
// Review: Kev + claude-opus-5.5, 2026-10-06 — security-auditor fold.
// buildEntry() is the gate for what reaches main: full_name must be a plain
// owner/repo (no "." or ".."), html_url must be https://github.com/, and
// declarations over 20 KB are skipped (a stranger could otherwise commit
// ~100 MB). Author + description lose bidi/zero-width chars (spoofing);
// description capped at 300. gh() has a 30s fetch timeout and refuses a
// Retry-After over 2 minutes. Confidence 0.9.
// Review: Kev + claude-opus-5.5, 2026-11-21 — the nightly run still went red
// every other night (11-08..11-21): code search answered 429 with Retry-After
// 130-736 s, past the 2-minute cap, under the default GITHUB_TOKEN
// (REGISTRY_TOKEN unset). gh() now raises RateLimitError for that, and
// sweepFailure() turns it into a skipped night (exit 0, registry untouched)
// while registry.json is under 72 h old; past that it fails loudly. A rate
// limit on a per-repo fetch aborts the sweep instead of silently dropping that
// repo from the committed registry. Confidence 0.85 — unit-tested with stubs;
// the 72 h threshold is a judgement call.
//
// Usage: GITHUB_TOKEN=$(gh auth token) node scripts/update-registry.mjs

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const API = "https://api.github.com";
const OUT = join(
  dirname(fileURLToPath(import.meta.url)),
  "..",
  "site",
  "src",
  "data",
  "registry.json",
);

// Fields come from strangers' repos and deploy unattended: validate the
// structured ones, sanitise the free-text one. Rendering escapes too
// (site/src/lib/escape.mjs) — this is the second wall, not the only one.
const VERSION_RE = /^v\d+(\.\d+){0,3}$/;
const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
// Control chars, line separators, zero-width and bidi-override characters:
// none belong in a name, and bidi/zero-width ones can make a displayed
// author or description read as something it is not.
const CONTROL_RE =
  /[\u0000-\u001f\u007f-\u009f\u200b-\u200f\u2028-\u202e\u2060-\u2069\ufeff]/g;
const AUTHOR_MAX = 100;
const DESCRIPTION_MAX = 300;
const DECLARATION_MAX = 20_000; // real declarations are ~1-2 KB
// GitHub owners are [A-Za-z0-9-]; repos add . and _ (but never "." or "..").
const FULL_NAME_RE = /^[A-Za-z0-9-]+\/(?!\.\.?$)[A-Za-z0-9._-]+$/;

const cleanText = (value, max) =>
  typeof value === "string" ? value.replace(CONTROL_RE, "").trim().slice(0, max) || null : null;

/** Parse the Project Details fields out of a .murphysig declaration. */
export function parseMurphysig(content) {
  const grab = (label) => {
    const m = content.match(new RegExp(`\\*\\*${label}\\*\\*:[ \\t]*([^\\r\\n]+)`));
    return m ? m[1].trim() : null;
  };
  let version = grab("Convention version");
  if (version) {
    version = version.replace(/^MurphySig\s+/i, "");
    if (!version.startsWith("v")) version = `v${version}`;
    if (!VERSION_RE.test(version)) version = null;
  }
  let initialized = grab("Initialized");
  if (initialized && !DATE_RE.test(initialized)) initialized = null;
  const author = cleanText(grab("Primary author"), AUTHOR_MAX);
  return { author, version, initialized };
}

/**
 * One registry entry from a search hit, or null if it should be skipped.
 * Everything here ends up committed to main and deployed unattended, so
 * identifiers are validated and stranger-supplied text is bounded.
 */
export function buildEntry(fullName, content, repo) {
  if (repo.private) return null; // registry is public-only, belt and braces
  if (!FULL_NAME_RE.test(fullName)) return null;
  if (typeof repo.html_url !== "string" || !repo.html_url.startsWith("https://github.com/")) return null;
  if (content.length > DECLARATION_MAX) return null;
  const [owner, name] = fullName.split("/");
  const parsed = parseMurphysig(content);
  return {
    owner,
    repo: name,
    full_name: fullName,
    html_url: repo.html_url,
    description: cleanText(repo.description, DESCRIPTION_MAX),
    author: parsed.author,
    version: parsed.version,
    initialized: parsed.initialized,
    last_push: repo.pushed_at ?? null,
    declaration: content,
  };
}

/** GitHub said "not now" (429 / secondary 403) and we could not wait it out. */
export class RateLimitError extends Error {
  constructor(message, { status } = {}) {
    super(message);
    this.name = "RateLimitError";
    this.status = status;
  }
}

// A rate-limited night is skipped while the committed registry is younger
// than this; after it, the job goes red so a lasting outage gets noticed.
const MAX_STALE_MS = 72 * 3_600_000;

/**
 * What a failed sweep should do: "skip" (exit 0, keep the committed
 * registry) for a rate limit while the registry is fresh, else "fail".
 */
export function sweepFailure(err, lastGeneratedAt, now = Date.now()) {
  if (!(err instanceof RateLimitError)) return "fail";
  const generated = Date.parse(lastGeneratedAt ?? "");
  if (!Number.isFinite(generated)) return "fail";
  return now - generated < MAX_STALE_MS ? "skip" : "fail";
}

const sleepMs = (ms) => new Promise((r) => setTimeout(r, ms));
const FETCH_TIMEOUT_MS = 30_000;
const MAX_RETRY_WAIT_MS = 120_000;

/** How long GitHub asked us to wait, in ms (Retry-After or "try again in Xs"). */
function retryDelayMs(res, body, attempt) {
  const header = Number(res.headers.get("retry-after"));
  if (Number.isFinite(header) && header > 0) return header * 1000;
  const m = /try again in ([\d.]+)s/i.exec(body);
  if (m) return Math.ceil(Number(m[1]) * 1000);
  return 2 ** attempt * 1000; // no hint: exponential backoff
}

/**
 * GitHub REST GET. Code search allows ~10 req/min, and a single 429 used to
 * kill the whole nightly sweep, so rate limits (429, or 403 with a rate-limit
 * body / Retry-After) are retried with the advertised wait. Anything else
 * fails fast.
 */
export async function gh(path, token, { fetch: fetchImpl = fetch, sleep = sleepMs, maxAttempts = 5 } = {}) {
  for (let attempt = 1; ; attempt++) {
    const res = await fetchImpl(`${API}${path}`, {
      signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
      },
    });
    if (res.ok) return res.json();
    const body = await res.text();
    const rateLimited =
      res.status === 429 ||
      (res.status === 403 && (res.headers.get("retry-after") || /rate limit/i.test(body)));
    if (!rateLimited) {
      throw new Error(`GitHub ${path} -> ${res.status}: ${body.slice(0, 200)}`);
    }
    if (attempt >= maxAttempts) {
      throw new RateLimitError(`GitHub ${path} -> ${res.status}: ${body.slice(0, 200)}`, { status: res.status });
    }
    const wait = retryDelayMs(res, body, attempt);
    if (wait > MAX_RETRY_WAIT_MS) {
      throw new RateLimitError(
        `GitHub ${path} -> ${res.status}: Retry-After ${wait}ms exceeds ${MAX_RETRY_WAIT_MS}ms`,
        { status: res.status },
      );
    }
    console.warn(`  ~ ${path} rate-limited (${res.status}); retry ${attempt}/${maxAttempts - 1} in ${wait}ms`);
    await sleep(wait);
  }
}

/**
 * Registry entries for the search hits. A repo that 404s or is malformed is
 * skipped; a rate limit aborts the whole sweep, because committing a registry
 * with that repo missing would delist it until the next good night.
 */
export async function fetchEntries(rootHits, ghFn) {
  const entries = [];
  for (const hit of rootHits) {
    const fullName = hit.repository.full_name;
    try {
      const [file, repo] = await Promise.all([
        ghFn(`/repos/${fullName}/contents/.murphysig`),
        ghFn(`/repos/${fullName}`),
      ]);
      const content = Buffer.from(file.content, "base64").toString("utf-8");
      const entry = buildEntry(fullName, content, repo);
      if (!entry) {
        console.warn(`  - ${fullName}: skipped (private, malformed or oversized)`);
        continue;
      }
      entries.push(entry);
      console.log(`  + ${fullName} (${entry.version ?? "version unknown"})`);
    } catch (err) {
      if (err instanceof RateLimitError) throw err;
      console.warn(`  ! ${fullName}: ${err.message}`);
    }
  }
  return entries;
}

async function sweep(token) {
  const ghFn = (path) => gh(path, token);
  // Code search caps at 1000 results — far beyond current scale.
  const search = await ghFn("/search/code?q=filename:.murphysig&per_page=100");
  const rootHits = search.items.filter(
    (item) => item.path === ".murphysig" && !item.repository.private,
  );
  console.log(
    `Search: ${search.total_count} hits, ${rootHits.length} root-level public`,
  );
  return fetchEntries(rootHits, ghFn);
}

function lastGeneratedAt() {
  try {
    return JSON.parse(readFileSync(OUT, "utf-8")).generated_at ?? null;
  } catch {
    return null;
  }
}

async function main() {
  const token = process.env.REGISTRY_TOKEN || process.env.GITHUB_TOKEN;
  if (!token) {
    console.error("Set GITHUB_TOKEN (or REGISTRY_TOKEN) first.");
    process.exit(2);
  }

  let entries;
  try {
    entries = await sweep(token);
  } catch (err) {
    const last = lastGeneratedAt();
    if (sweepFailure(err, last) === "skip") {
      // ::warning:: surfaces on the run summary without turning it red.
      console.log(`::warning::Registry sweep skipped (${err.message}); keeping registry from ${last}.`);
      return;
    }
    throw err;
  }

  entries.sort((a, b) => (b.last_push ?? "").localeCompare(a.last_push ?? ""));
  const registry = {
    generated_at: new Date().toISOString(),
    count: entries.length,
    repos: entries,
  };
  mkdirSync(dirname(OUT), { recursive: true });
  writeFileSync(OUT, `${JSON.stringify(registry, null, 2)}\n`);
  console.log(`Wrote ${OUT} (${entries.length} repos)`);
}

const isDirectRun =
  process.argv[1] && import.meta.url === `file://${process.argv[1]}`;
if (isDirectRun) {
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}
