// Signed: Kev + claude-opus-5.5, 2026-10-06
// Format: MurphySig v0.4 (https://murphysig.dev/spec)
// Prior: Unknown (new file)
//
// Context: The registry pulls .murphysig declarations from ANY public repo
// nightly and commits them straight to main, which Netlify deploys — no
// human in the loop. Author, version and repo description are therefore
// attacker-controlled by the time they reach a page. Two sinks bypass
// Astro's own escaping: the JSON-LD <script> (set:html) and the hand-built
// SVG badge. These helpers are the only things standing between a
// stranger's .murphysig and live script on murphysig.dev.
//
// Confidence: 0.9 - the standard escapes (OWASP: JSON in a script block,
// XML text + attribute context); unit-tested with the breakout payloads.

/**
 * JSON safe to place inside <script>…</script>. JSON.stringify leaves
 * "</script>" intact; escaping <, > and & as \u-sequences keeps the value
 * identical after JSON.parse while making the tag unclosable. U+2028/2029
 * are escaped for older JS parsers that treat them as line terminators.
 */
export function jsonForScript(value) {
  return JSON.stringify(value)
    .replace(/</g, "\\u003c")
    .replace(/>/g, "\\u003e")
    .replace(/&/g, "\\u0026")
    .replace(/\u2028/g, "\\u2028")
    .replace(/\u2029/g, "\\u2029");
}

/** Escape text for XML/SVG element content and quoted attributes. */
export function escapeXml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}
