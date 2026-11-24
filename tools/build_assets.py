"""Build the profile README images (assets/*.svg).

Design: a labelled hardware panel, the same system as the portfolio site
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
from fontTools.pens.transformPen import TransformPen
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


def arrow(x: float, y: float, size: float, color: str, width: float) -> str:
    """A north-east arrow drawn as strokes (Plex Mono has no ↗ glyph)."""
    return (
        f'<path d="M{num(x)} {num(y + size)} L{num(x + size)} {num(y)} M{num(x + size * 0.3)} {num(y)} L{num(x + size)} {num(y)} L{num(x + size)} {num(y + size * 0.7)}" '
        f'fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="square"/>'
    )


# ── header: the faceplate ────────────────────────────────────────────────
def header(t: dict, mono: Face, mono_md: Face, grot: Face, circles) -> str:
    W, H, M = 1200, 460, 48
    b: list[str] = []
    b.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="{t["panel"]}" stroke="{t["hair"]}" stroke-width="2"/>')

    # top strip: instrument labels
    b.append(mono.path("adriansalvadorekomo / dataops", M, 46, 14, t["ink2"], 0.4))
    b.append(mono.path("leipzig, de · rev 2026.11", W - M, 46, 14, t["ink2"], 0.4, "end"))
    b.append(f'<rect x="{M}" y="66" width="{W - 2 * M}" height="1" fill="{t["hair"]}"/>')

    # the display window holding the dot-matrix mark
    wx, wy, ws = M, 98, 268
    k = ws / 64
    b.append(f'<rect x="{wx}" y="{wy}" width="{ws}" height="{ws}" rx="{num(14 * k)}" fill="{t["window"]}" stroke="{t["window_line"]}" stroke-width="2"/>')
    for cx, cy, r, fill in circles:
        b.append(f'<circle cx="{num(wx + cx * k)}" cy="{num(wy + cy * k)}" r="{num(r * k)}" fill="{fill}"/>')

    # name and role
    x0 = 356
    b.append(grot.path("adrián salvador ekomo", x0 - 3, 172, 64, t["ink"], -0.6))
    # focus: data engineering & devops; mlops is a secondary line (same wording as the portfolio)
    px = x0
    b.append(mono.path("data engineering ", px, 222, 26, t["ink2"]))
    px += mono.width("data engineering ", 26)
    b.append(mono_md.path("&", px, 222, 26, ORANGE))
    px += mono.width("&", 26)
    b.append(mono.path(" devops", px, 222, 26, t["ink2"]))
    px += mono.width(" devops", 26) + 28
    b.append(mono_md.path("+", px, 222, 18, ORANGE))
    px += mono.width("+", 18)
    b.append(mono.path(" mlops foundations", px, 222, 18, t["ink2"]))
    assert px + mono.width(" mlops foundations", 18) < W - M, "role line too long"

    # readouts: what this profile holds — evidence, not availability
    top = 266
    third = (W - M - x0) / 3
    cells = [("01  projects", "7 documented", False, third), ("02  credentials", "7 verifiable", False, third), ("03  notes", "7 write-ups", False, third)]
    cx = x0
    for label, value, led, colw in cells:
        assert mono_md.width(value, 18) + (22 if led else 0) <= colw - 24, value
        b.append(f'<rect x="{num(cx)}" y="{top}" width="{num(colw - 20)}" height="1" fill="{t["hair"]}"/>')
        b.append(mono.path(label, cx, top + 30, 13, t["ink2"], 0.4))
        vx = cx
        if led:
            b.append(f'<circle cx="{num(cx + 6)}" cy="{top + 59}" r="6" fill="{ORANGE}"/>')
            vx += 22
        b.append(mono_md.path(value, vx, top + 66, 18, t["ink"]))
        cx += colw

    # bottom strip: the one-line promise
    b.append(f'<rect x="{M}" y="398" width="{W - 2 * M}" height="1" fill="{t["hair"]}"/>')
    b.append(mono.path("I build data pipelines that check the data before anyone reports on it, and the infrastructure that ships them.", M, 432, 15, t["ink2"], 0.1))
    return svg(W, H, "Adrián Salvador Ekomo — data engineering and devops, with mlops foundations. 7 documented projects, 7 verifiable credentials, 7 write-ups.", b)


# ── link keys (one image per key; theme-agnostic) ────────────────────────
def key(n: str, label: str, primary: bool, mono: Face, mono_md: Face) -> str:
    W, H = 300, 120
    fill = ORANGE if primary else "#ebe9e4"
    ink, ink2 = "#121212", ("#121212" if primary else "#5c5952")
    b = [
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="18" fill="{fill}" stroke="#121212" stroke-width="3"/>',
        mono.path(n, 24, 42, 20, ink2, 0.5),
        arrow(W - 46, 24, 20, ink, 3),
        mono_md.path(label, 24, 94, 30, ink, 0.2),
    ]
    return svg(W, H, f"{label} (opens the link)", b)


# ── stack: a panel of labelled keys ──────────────────────────────────────
STACK = [
    ("01  data", ["python*", "sql*", "spark sql", "pyspark", "pandas", "postgresql"]),
    ("02  platform", ["databricks*", "delta lake", "unity catalog", "databricks workflows", "medallion"]),
    ("03  pipelines", ["airflow", "prefect", "talend", "data-quality gates", "great expectations", "star schema"]),
    ("04  infra", ["terraform*", "ansible", "openstack", "docker", "compose", "nginx", "linux"]),
    ("05  delivery", ["github actions", "jenkins", "sonarqube", "pytest", "git", "kubernetes (course)"]),
    ("06  ml & ops", ["mlflow", "scikit-learn", "tensorflow", "fastapi", "prometheus", "grafana"]),
]


def stack(t: dict, mono: Face, mono_md: Face) -> str:
    W, M, row, kh, size = 1200, 48, 58, 36, 15
    H = 92 + row * len(STACK) + 24
    b = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="{t["panel"]}" stroke="{t["hair"]}" stroke-width="2"/>']
    b.append(mono.path("stack / tools behind the projects", M, 46, 14, t["ink2"], 0.4))
    lx = W - M - mono.width("core", 14, 0.4)
    b.append(f'<circle cx="{num(lx - 14)}" cy="41" r="5" fill="{ORANGE}"/>')
    b.append(mono.path("core", W - M, 46, 14, t["ink2"], 0.4, "end"))
    b.append(f'<rect x="{M}" y="66" width="{W - 2 * M}" height="1" fill="{t["hair"]}"/>')
    y = 92
    for label, tools in STACK:
        b.append(mono.path(label, M, y + 24, 14, t["ink2"], 0.4))
        x = M + 190
        for tool in tools:
            core = tool.endswith("*")
            name = tool.rstrip("*")
            pad = 16
            w = mono_md.width(name, size) + 2 * pad + (18 if core else 0)
            b.append(f'<rect x="{num(x)}" y="{y}" width="{num(w)}" height="{kh}" rx="7" fill="{t["key"]}" stroke="{t["hair"]}" stroke-width="1.5"/>')
            tx = x + pad
            if core:
                b.append(f'<circle cx="{num(x + pad + 4)}" cy="{y + kh / 2}" r="4.5" fill="{ORANGE}"/>')
                tx += 18
            b.append(mono_md.path(name, tx, y + 23.5, size, t["ink"]))
            x += w + 10
        assert x <= W - M + 10, f"row {label} overflows: {x}"
        y += row
    return svg(W, H, "Stack: " + "; ".join(f"{l.split()[-1]}: " + ", ".join(s.rstrip('*') for s in tools) for l, tools in STACK), b)


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
        (OUT / f"stack-{name}.svg").write_text(stack(t, mono, mono_md))
    keys = [("01", "portfolio", True), ("02", "linkedin", False), ("03", "credly", False), ("04", "email", False)]
    for n, label, primary in keys:
        (OUT / f"key-{label}.svg").write_text(key(n, label, primary, mono, mono_md))
    for p in sorted(OUT.glob("*.svg")):
        print(f"{p.name:22s} {p.stat().st_size / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
