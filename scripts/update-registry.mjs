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
// Usage: GITHUB_TOKEN=$(gh auth token) node scripts/update-registry.mjs

import { writeFileSync, mkdirSync } from "node:fs";
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

/** Parse the Project Details fields out of a .murphysig declaration. */
export function parseMurphysig(content) {
  const grab = (label) => {
    const m = content.match(new RegExp(`\\*\\*${label}\\*\\*:\\s*(.+)`));
    return m ? m[1].trim() : null;
  };
  let version = grab("Convention version");
  if (version) {
    version = version.replace(/^MurphySig\s+/i, "");
    if (!version.startsWith("v")) version = `v${version}`;
  }
  return {
    author: grab("Primary author"),
    version,
    initialized: grab("Initialized"),
  };
}

async function gh(path, token) {
  const res = await fetch(`${API}${path}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });
  if (!res.ok) {
    throw new Error(
      `GitHub ${path} -> ${res.status}: ${(await res.text()).slice(0, 200)}`,
    );
  }
  return res.json();
}

async function main() {
  const token = process.env.REGISTRY_TOKEN || process.env.GITHUB_TOKEN;
  if (!token) {
    console.error("Set GITHUB_TOKEN (or REGISTRY_TOKEN) first.");
    process.exit(2);
  }

  // Code search caps at 1000 results — far beyond current scale.
  const search = await gh(
    "/search/code?q=filename:.murphysig&per_page=100",
    token,
  );
  const rootHits = search.items.filter(
    (item) => item.path === ".murphysig" && !item.repository.private,
  );
  console.log(
    `Search: ${search.total_count} hits, ${rootHits.length} root-level public`,
  );

  const entries = [];
  for (const hit of rootHits) {
    const fullName = hit.repository.full_name;
    try {
      const [file, repo] = await Promise.all([
        gh(`/repos/${fullName}/contents/.murphysig`, token),
        gh(`/repos/${fullName}`, token),
      ]);
      if (repo.private) continue; // registry is public-only, belt and braces
      const content = Buffer.from(file.content, "base64").toString("utf-8");
      const parsed = parseMurphysig(content);
      entries.push({
        owner: fullName.split("/")[0],
        repo: fullName.split("/")[1],
        full_name: fullName,
        html_url: repo.html_url,
        description: repo.description ?? null,
        author: parsed.author,
        version: parsed.version,
        initialized: parsed.initialized,
        last_push: repo.pushed_at ?? null,
        declaration: content,
      });
      console.log(`  + ${fullName} (${parsed.version ?? "version unknown"})`);
    } catch (err) {
      console.warn(`  ! ${fullName}: ${err.message}`);
    }
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
