// Signed: Kev + claude-opus-5.5, 2026-10-06
// Format: MurphySig v0.4 (https://murphysig.dev/spec)
// Prior: Unknown (new file)
//
// Context: murphysig.dev renders third-party registry content, so its CSP
// matters — and it pins the two Astro inline scripts by sha256 instead of
// allowing 'unsafe-inline'. That pin drifts the moment either script changes.
// This module checks built HTML against the policy in netlify.toml so CI
// fails on drift before the policy goes from Report-Only to enforcing.
// Deliberately small: it understands the resource kinds this static site
// emits (inline/module scripts, script src, stylesheets, img, iframe, form
// action, inline handlers, javascript: URLs), not the whole CSP grammar.
// Fonts load from inside Google's stylesheet, which no HTML scan can see —
// font-src is reviewed by hand.
//
// Confidence: 0.8 - regex HTML scanning is fine for Astro's own output;
// it would not be for arbitrary HTML.

import { createHash } from "node:crypto";

const JS_TYPES = new Set([
  "",
  "module",
  "text/javascript",
  "application/javascript",
]);

/** "a b; c d" → Map { a → [b], c → [d] } */
export function parsePolicy(policy) {
  const map = new Map();
  for (const part of policy.split(";")) {
    const [name, ...sources] = part.trim().split(/\s+/).filter(Boolean);
    if (name) map.set(name.toLowerCase(), sources);
  }
  return map;
}

function attr(tagAttrs, name) {
  const m = tagAttrs.match(
    new RegExp(`\\s${name}\\s*=\\s*(?:"([^"]*)"|'([^']*)'|([^\\s>]+))`, "i"),
  );
  return m ? (m[1] ?? m[2] ?? m[3]) : null;
}

/** CSP hash sources for every inline script a browser would execute. */
export function inlineScriptHashes(html) {
  const out = [];
  for (const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)) {
    const [, attrs, body] = m;
    if (attr(attrs, "src") !== null) continue;
    if (!JS_TYPES.has((attr(attrs, "type") ?? "").toLowerCase())) continue; // data blocks (ld+json)
    out.push(`'sha256-${createHash("sha256").update(body).digest("base64")}'`);
  }
  return out;
}

function sourcesFor(policy, directive) {
  return policy.get(directive) ?? policy.get("default-src") ?? [];
}

function urlAllowed(sources, raw, self) {
  const url = new URL(raw, self);
  if (url.protocol === "data:" || url.protocol === "blob:")
    return sources.includes(url.protocol);
  if (url.origin === self && sources.includes("'self'")) return true;
  return sources.some((s) => {
    if (s.startsWith("'") || s.endsWith(":")) return false;
    const src = new URL(s.includes("://") ? s : `https://${s}`);
    if (src.protocol !== url.protocol) return false;
    if (src.hostname.startsWith("*."))
      return url.hostname.endsWith(src.hostname.slice(1));
    return src.host === url.host;
  });
}

/** Every resource in `html` the policy would block, as readable strings. */
export function violations(policy, html, self) {
  const out = [];
  const scriptSrc = sourcesFor(policy, "script-src");
  for (const hash of inlineScriptHashes(html)) {
    if (!scriptSrc.includes(hash) && !scriptSrc.includes("'unsafe-inline'")) {
      out.push(`script-src: inline script ${hash} not allowed`);
    }
  }
  const check = (directive, url) => {
    if (url && !urlAllowed(sourcesFor(policy, directive), url, self)) {
      out.push(`${directive}: ${url} not allowed`);
    }
  };
  for (const [, tag, attrs] of html.matchAll(
    /<(script|link|img|iframe|form)\b([^>]*)>/gi,
  )) {
    switch (tag.toLowerCase()) {
      case "script":
        check("script-src", attr(attrs, "src"));
        break;
      case "link":
        if (/(^|\s)stylesheet(\s|$)/i.test(attr(attrs, "rel") ?? ""))
          check("style-src", attr(attrs, "href"));
        break;
      case "img":
        check("img-src", attr(attrs, "src"));
        break;
      case "iframe":
        check("frame-src", attr(attrs, "src"));
        break;
      case "form":
        check("form-action", attr(attrs, "action"));
        break;
    }
  }
  if (!scriptSrc.includes("'unsafe-inline'")) {
    for (const [, handler] of html.matchAll(/<[a-z][^>]*?\s(on[a-z]+)\s*=/gi)) {
      out.push(`script-src: inline handler ${handler} not allowed`);
    }
    for (const m of html.matchAll(
      /\s(?:href|src|action)\s*=\s*["']?\s*javascript:/gi,
    )) {
      out.push(`script-src: javascript: URL not allowed (${m[0].trim()})`);
    }
  }
  return out;
}

/** The value of `header` in the [[headers]] block whose `for` is `path`. */
export function policyFromNetlifyToml(toml, path, header) {
  for (const block of toml.split(/^\[\[headers\]\]\s*$/m).slice(1)) {
    const forMatch = block.match(/^\s*for\s*=\s*"([^"]*)"/m);
    if (forMatch?.[1] !== path) continue;
    const esc = header.replace(/[-]/g, "\\-");
    const m = block.match(new RegExp(`^\\s*${esc}\\s*=\\s*"([^"]*)"`, "m"));
    return m ? m[1] : null;
  }
  return null;
}
