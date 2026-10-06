#!/usr/bin/env node
// Signed: Kev + claude-opus-5.5, 2026-10-06
// Format: MurphySig v0.4 (https://murphysig.dev/spec)
// Prior: Unknown (new file)
//
// Context: CI gate, run after `npm run build`: every page in dist/ must be
// allowed by the site CSP in ../netlify.toml. Fails on a changed inline
// script (stale sha256 pin) or a new external origin — the drift that would
// break the site once the policy enforces. Logic lives in src/lib/csp.mjs.
//
// Confidence: 0.85 - thin wrapper over the unit-tested module.

import { readFileSync, readdirSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import {
  parsePolicy,
  violations,
  policyFromNetlifyToml,
} from "../src/lib/csp.mjs";

const SITE = fileURLToPath(new URL("..", import.meta.url));
const DIST = join(SITE, "dist");
const HEADER = "Content-Security-Policy-Report-Only";
const SELF = "https://murphysig.dev";

const toml = readFileSync(join(SITE, "..", "netlify.toml"), "utf8");
const raw = policyFromNetlifyToml(toml, "/*", HEADER);
if (!raw) {
  console.error(`check-csp: no ${HEADER} on the "/*" block in netlify.toml`);
  process.exit(1);
}
const policy = parsePolicy(raw);

const pages = readdirSync(DIST, { recursive: true }).filter((f) =>
  f.endsWith(".html"),
);
if (pages.length === 0) {
  console.error("check-csp: no HTML in dist/ — run `npm run build` first");
  process.exit(1);
}

let failures = 0;
for (const page of pages) {
  for (const v of violations(
    policy,
    readFileSync(join(DIST, page), "utf8"),
    SELF,
  )) {
    console.error(`${relative(SITE, join(DIST, page))}: ${v}`);
    failures++;
  }
}
if (failures) {
  console.error(
    `check-csp: ${failures} violation(s). Update the policy in netlify.toml (a changed inline script needs its new sha256).`,
  );
  process.exit(1);
}
console.log(`check-csp: ${pages.length} pages allowed by the site CSP.`);
