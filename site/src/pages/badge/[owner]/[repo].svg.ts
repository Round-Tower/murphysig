/**
 * Signed: Kev + claude-fable-5, 2026-06-09
 * Format: MurphySig v0.4 (https://murphysig.dev/spec)
 * Prior: Unknown (new file)
 *
 * Context: Static badge endpoint — /badge/<owner>/<repo>.svg. One SVG
 * is pre-rendered per registry entry at build time. Repos not in the
 * registry fall through to the Netlify rewrite onto
 * /badge-not-found.svg (see netlify.toml). No runtime GitHub calls.
 *
 * Confidence: 0.85 - thin glue over lib/badge.ts and registry.json.
 */

import type { APIRoute } from "astro";
import registry from "../../../data/registry.json";
import { signedBadge } from "../../../lib/badge";

export function getStaticPaths() {
  return registry.repos.map((r) => ({
    params: { owner: r.owner, repo: r.repo },
    props: { version: r.version },
  }));
}

export const GET: APIRoute = ({ props }) => {
  return new Response(signedBadge(props.version), {
    headers: { "Content-Type": "image/svg+xml; charset=utf-8" },
  });
};
