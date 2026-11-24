"""Build the profile README images (assets/*.svg).

Design (minimal since 2026-11-25): one slim faceplate, the same system as the portfolio site
(adriansalvadorekomodev.vercel.app) — dot-matrix mark, one orange signal,
IBM Plex Mono for labels, Schibsted Grotesk for the name, hairlines, no shadows.

Text is converted to vector paths so the images look the same in every
browser and in the GitHub mobile app (an SVG shown as an image cannot load
web fonts). Both fonts are SIL Open Font License.

usage:
  uv run --no-project --with fonttools --with brotli python tools/build_assets.py \
      --mono  <IBM Plex Mono Regular .woff2/.ttf> \
      --mono-medium <IBM Plex Mono Medium> \
      --grotesk <Schibsted Grotesk variable> \
      --mark  <portfolio-webapp/public/brand/mark.svg>
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

DEFS: dict[str, str] = {}  # glyph id -> outline, collected per image
OUT = Path(__file__).resolve().parent.parent / "assets"

ORANGE = "#ff4f00"
THEMES = {
    # "black edition": the panel matches the mark's own display colour
    "dark": dict(panel="#121212", ink="#ebe9e4", ink2="#9b978f", hair="#2e2e2e", key="#1b1b1b", window="#121212", window_line="#2e2e2e"),
    # "aluminium edition": warm light panel, the mark keeps its black display
    "light": dict(panel="#ebe9e4", ink="#121212", ink2="#5c5952", hair="#cdc9c0", key="#f4f2ee", window="#121212", window_line="#121212"),
}


def num(v: float) -> str:
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


class Face:
    def __init__(self, path: str, tag: str, wght: float | None = None):
        self.tag = tag
        f = TTFont(path)
        if wght is not None and "fvar" in f:
            f = instancer.instantiateVariableFont(f, {"wght": wght})
        self.gs = f.getGlyphSet()
        self.cmap = f.getBestCmap()
        self.upm = f["head"].unitsPerEm
        self.hmtx = f["hmtx"]

    def _glyph(self, ch: str) -> str:
        g = self.cmap.get(ord(ch))
        if g is None:
            raise KeyError(f"glyph missing for {ch!r}")
        return g

    def width(self, text: str, size: float, track: float = 0) -> float:
        s = size / self.upm
        return sum(self.hmtx[self._glyph(c)][0] * s + track for c in text) - (track if text else 0)

    def path(self, text: str, x: float, y: float, size: float, fill: str, track: float = 0, anchor: str = "start") -> str:
        """Each glyph is defined once per image (<defs>) and placed with <use>."""
        if anchor == "end":
            x -= self.width(text, size, track)
        elif anchor == "middle":
            x -= self.width(text, size, track) / 2
        s = size / self.upm
        out, cx = [], x
        for ch in text:
            g = self._glyph(ch)
            gid = f"{self.tag}-{g}".replace(".", "_")
            if gid not in DEFS:
                pen = SVGPathPen(self.gs, ntos=lambda v: str(round(v)))
                self.gs[g].draw(pen)
                DEFS[gid] = pen.getCommands()
            if DEFS[gid]:
                out.append(f'<use href="#{gid}" transform="matrix({s:.5g} 0 0 {-s:.5g} {num(cx)} {num(y)})"/>')
            cx += self.hmtx[g][0] * s + track
        return f'<g fill="{fill}">' + "".join(out) + "</g>" if out else ""


def mark_circles(mark_svg: str) -> list[tuple[float, float, float, str]]:
    return [
        (float(cx), float(cy), float(r), fill)
        for cx, cy, r, fill in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)" fill="(#[0-9a-fA-F]+)"', mark_svg)
    ]


def svg(w: int, h: int, label: str, body: list[str]) -> str:
    defs = "".join(f'<path id="{k}" d="{d}"/>' for k, d in DEFS.items() if d)
    DEFS.clear()
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">'
        f"<title>{label}</title><defs>{defs}</defs>" + "".join(body) + "</svg>\n"
    )


# ── header: a slim faceplate, identity only ──────────────────────────────
def header(t: dict, mono: Face, mono_md: Face, grot: Face, circles) -> str:
    """Minimal on purpose (user, 2026-11-25): the mark, the name and the role. No counters, no claims;
    the pinned repositories carry the evidence."""
    W, H, M = 1200, 232, 40
    b: list[str] = []
    b.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="{t["panel"]}" stroke="{t["hair"]}" stroke-width="2"/>')

    # the display window holding the dot-matrix mark
    ws = H - 2 * M
    wx, wy = M, M
    k = ws / 64
    b.append(f'<rect x="{wx}" y="{wy}" width="{ws}" height="{ws}" rx="{num(14 * k)}" fill="{t["window"]}" stroke="{t["window_line"]}" stroke-width="2"/>')
    for cx, cy, r, fill in circles:
        b.append(f'<circle cx="{num(wx + cx * k)}" cy="{num(wy + cy * k)}" r="{num(r * k)}" fill="{fill}"/>')

    x0 = wx + ws + 40
    b.append(grot.path("adrián salvador ekomo", x0 - 3, 112, 60, t["ink"], -0.6))
    px = x0
    b.append(mono.path("data engineering ", px, 162, 24, t["ink2"]))
    px += mono.width("data engineering ", 24)
    b.append(mono_md.path("&", px, 162, 24, ORANGE))
    px += mono.width("&", 24)
    b.append(mono.path(" devops", px, 162, 24, t["ink2"]))
    px += mono.width(" devops", 24) + 24
    b.append(mono_md.path("+", px, 162, 17, ORANGE))
    px += mono.width("+", 17)
    b.append(mono.path(" mlops foundations", px, 162, 17, t["ink2"]))
    assert px + mono.width(" mlops foundations", 17) < W - M, "role line too long"
    return svg(W, H, "Adrián Salvador Ekomo — data engineering and devops, with mlops foundations.", b)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mono", required=True)
    ap.add_argument("--mono-medium", required=True)
    ap.add_argument("--grotesk", required=True)
    ap.add_argument("--mark", required=True)
    a = ap.parse_args()

    mono, mono_md = Face(a.mono, "m"), Face(a.mono_medium, "mm")
    grot = Face(a.grotesk, "g", wght=500)
    circles = mark_circles(Path(a.mark).read_text())
    assert len(circles) == 110, len(circles)

    OUT.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        (OUT / f"header-{name}.svg").write_text(header(t, mono, mono_md, grot, circles))
    for p in sorted(OUT.glob("*.svg")):
        print(f"{p.name:22s} {p.stat().st_size / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
