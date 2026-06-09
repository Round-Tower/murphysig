/**
 * Signed: Kev + claude-fable-5, 2026-06-09
 * Format: MurphySig v0.4 (https://murphysig.dev/spec)
 * Prior: Unknown (new file)
 *
 * Context: Shields-style flat SVG badge for the MurphySig registry.
 * Pre-rendered at build time from data/registry.json — this module
 * must never call the network (GitHub search's 30 req/min cap would
 * DoS a live badge endpoint instantly).
 *
 * Confidence: 0.8 - width estimation is approximate (no canvas at
 * build time); fine for the label/value strings we control.
 */

const FONT = "Verdana,Geneva,DejaVu Sans,sans-serif";

function textWidth(text: string): number {
  // ~6.2px per char at 11px Verdana, plus breathing room.
  return Math.round(text.length * 6.2) + 14;
}

export function badgeSvg(label: string, value: string, color: string): string {
  const lw = textWidth(label);
  const vw = textWidth(value);
  const w = lw + vw;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="20" role="img" aria-label="${label}: ${value}">
  <title>${label}: ${value}</title>
  <g shape-rendering="crispEdges">
    <rect width="${lw}" height="20" fill="#1a1a1a"/>
    <rect x="${lw}" width="${vw}" height="20" fill="${color}"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="${FONT}" font-size="11">
    <text x="${lw / 2}" y="14">${label}</text>
    <text x="${lw + vw / 2}" y="14">${value}</text>
  </g>
</svg>
`;
}

export function signedBadge(version: string | null): string {
  return badgeSvg(
    "MurphySig",
    version ? `signed ${version}` : "signed",
    "#15803d",
  );
}

export function notFoundBadge(): string {
  return badgeSvg("MurphySig", "not found", "#737373");
}
