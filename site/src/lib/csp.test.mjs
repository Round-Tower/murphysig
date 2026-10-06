// Signed: Kev + claude-opus-5.5, 2026-10-06
// Format: MurphySig v0.4 (https://murphysig.dev/spec)
// Prior: Unknown (new file)
//
// Context: The site CSP pins its two inline scripts by sha256, so any change
// to them (or a new external origin) silently breaks the policy — invisible
// while it's Report-Only, a broken page once it enforces. csp.mjs checks the
// built HTML against the policy in netlify.toml; these tests pin that check.
// Run with: node --test src/lib/
//
// Confidence: 0.85 - covers the resource kinds this site actually emits
// (inline/module scripts, stylesheets, images, handlers); not a full CSP engine.

import { test } from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import {
  parsePolicy,
  inlineScriptHashes,
  violations,
  policyFromNetlifyToml,
} from "./csp.mjs";

const SELF = "https://murphysig.dev";
const sha = (s) =>
  `'sha256-${createHash("sha256").update(s).digest("base64")}'`;
const INLINE = "document.documentElement.classList.add('js');";

const policy = (extra = "") =>
  parsePolicy(
    `default-src 'self'; script-src 'self' ${sha(INLINE)}; ` +
      `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; ` +
      `img-src 'self' data:; object-src 'none'${extra}`,
  );

test("parsePolicy maps directives to their sources", () => {
  const p = parsePolicy("default-src 'self'; img-src 'self' data: ;");
  assert.deepEqual(p.get("default-src"), ["'self'"]);
  assert.deepEqual(p.get("img-src"), ["'self'", "data:"]);
});

test("inlineScriptHashes hashes executable inline scripts only", () => {
  const html =
    `<script>${INLINE}</script>` +
    `<script type="module">let a=1</script>` +
    `<script type="application/ld+json">{"a":1}</script>` +
    `<script src="/x.js"></script>`;
  assert.deepEqual(inlineScriptHashes(html), [sha(INLINE), sha("let a=1")]);
});

test("a page whose resources are all allowed has no violations", () => {
  const html =
    `<script>${INLINE}</script>` +
    `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=X">` +
    `<link rel="stylesheet" href="/_astro/a.css">` +
    `<img src="/badge/a/b.svg"><img src="data:image/png;base64,AA">` +
    `<p style="color:red">x</p>`;
  assert.deepEqual(violations(policy(), html, SELF), []);
});

test("an inline script whose hash is not listed is a violation", () => {
  const out = violations(policy(), "<script>alert(1)</script>", SELF);
  assert.equal(out.length, 1);
  assert.match(out[0], /script-src.*inline script/);
});

test("an external origin not in the directive is a violation", () => {
  const html =
    `<link rel="stylesheet" href="https://evil.example/x.css">` +
    `<script src="https://cdn.example/x.js"></script>` +
    `<img src="https://img.example/a.png">`;
  const out = violations(policy(), html, SELF);
  assert.equal(out.length, 3, out.join("\n"));
});

test("inline event handlers and javascript: URLs are violations", () => {
  const html = `<a href="javascript:void(0)" onclick="x()">x</a>`;
  const out = violations(policy(), html, SELF);
  assert.equal(out.length, 2, out.join("\n"));
});

test("a directive that is absent falls back to default-src", () => {
  const p = parsePolicy("default-src 'self'");
  assert.deepEqual(violations(p, `<iframe src="/a"></iframe>`, SELF), []);
  assert.equal(
    violations(p, `<iframe src="https://x.example/"></iframe>`, SELF).length,
    1,
  );
});

test("policyFromNetlifyToml reads the header from the named block", () => {
  const toml = `
[[headers]]
  for = "/badge/*"
  [headers.values]
    Content-Security-Policy-Report-Only = "default-src 'none'"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    Content-Security-Policy-Report-Only = "default-src 'self'; img-src data:"
`;
  assert.equal(
    policyFromNetlifyToml(toml, "/*", "Content-Security-Policy-Report-Only"),
    "default-src 'self'; img-src data:",
  );
  assert.equal(policyFromNetlifyToml(toml, "/nope", "X"), null);
});

test("an end tag with whitespace (</script >) still closes the script", () => {
  const html = `<script>a()</script ><script>b()</script\t>`;
  const hashes = inlineScriptHashes(html);
  assert.equal(hashes.length, 2);
  assert.notEqual(hashes[0], hashes[1]);
});

test("policyFromNetlifyToml treats the header name literally (no regex)", () => {
  const toml = `[[headers]]\n  for = "/*"\n  [headers.values]\n    XaY = "wrong"\n    X.Y = "right"\n`;
  assert.equal(policyFromNetlifyToml(toml, "/*", "X.Y"), "right");
  assert.equal(policyFromNetlifyToml(toml, "/*", "X\\Y"), null);
});

test("an end tag with attributes or newlines (</script\\t\\n bar>) closes the script", () => {
  const hashes = inlineScriptHashes(`<script>a()</script\t\n bar><script>b()</script>`);
  assert.equal(hashes.length, 2);
});
