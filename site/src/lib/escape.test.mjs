// Signed: Kev + claude-opus-5.5, 2026-10-06
// Format: MurphySig v0.4 (https://murphysig.dev/spec)
// Prior: Unknown (new file)
//
// Context: The registry renders third-party .murphysig content (author,
// version, repo description) into JSON-LD <script> blocks and SVG badges.
// These tests pin the two escapes that keep that content inert.
// Run with: node --test src/lib/
//
// Confidence: 0.9 - pure functions; payloads are the standard breakouts.

import { test } from "node:test";
import assert from "node:assert/strict";
import { jsonForScript, escapeXml } from "./escape.mjs";

const BREAKOUT = "</script><script>alert(document.domain)</script>";

test("jsonForScript cannot close the surrounding <script>", () => {
  const out = jsonForScript({ author: BREAKOUT });
  assert.ok(!out.includes("</script"), out);
  assert.ok(!out.includes("<"), out);
});

test("jsonForScript escapes HTML comment and CDATA openers", () => {
  const out = jsonForScript({ a: "<!-- x", b: "]]>", c: "a & b" });
  assert.ok(!/[<>&]/.test(out), out);
});

test("jsonForScript escapes U+2028/U+2029 line separators", () => {
  const out = jsonForScript({ a: "x\u2028y\u2029z" });
  assert.ok(!out.includes("\u2028") && !out.includes("\u2029"), out);
});

test("jsonForScript round-trips to the same data", () => {
  const data = {
    name: "a/b",
    author: BREAKOUT,
    n: 1,
    nested: { s: "x\u2028 & <y>" },
  };
  assert.deepEqual(JSON.parse(jsonForScript(data)), data);
});

test("escapeXml neutralises tags, attributes and entities", () => {
  assert.equal(
    escapeXml(`v1"/><script>alert(1)</script>&'`),
    "v1&quot;/&gt;&lt;script&gt;alert(1)&lt;/script&gt;&amp;&apos;",
  );
});

test("escapeXml leaves ordinary badge text alone", () => {
  assert.equal(escapeXml("signed v0.4"), "signed v0.4");
});
