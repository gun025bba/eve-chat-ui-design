#!/usr/bin/env python3
"""v5/overview.png (emerald vs blue per variant, 180/32/16, dark+light) and _check/silhouette-check.png (uncommitted)."""
import os, runpy, subprocess
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
def load(p):
    os.environ["PAL"] = p; g = runpy.run_path(os.path.join(here, "build.py")); os.chdir(here); return g
E, B = load("emerald"), load("blue"); FONT = E["FONT"]
def png(name, w, h, body, bg="#1C1C1E"):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>'
    open(name + ".svg", "w").write(s); subprocess.run(["rsvg-convert", "-z", "2", "-o", name + ".png", name + ".svg"], check=True)
out = []; y = 70; c = 0
for key, d in E["C"].items():
    out.append(f'<text x="40" y="{y+20}" font-family="{FONT}" font-size="24" font-weight="700" fill="#F5F5F7">{d["title"]}</text>'); y += 36
    for lab, g in (("Emerald", E), ("Blue", B)):
        for dark in (True, False):
            x0 = 40 if dark else 560
            out.append(f'<rect x="{x0}" y="{y}" width="500" height="220" rx="16" fill="{"#000" if dark else "#F2F2F7"}"/>')
            x = x0 + 20
            for s in (180, 32, 16):
                c += 1; out.append(f'<g transform="translate({x} {y+200-s})">{g["icon"](key, f"k{c}", s, dark)}</g>'); x += s + 30
            out.append(f'<text x="{x0+330}" y="{y+40}" font-family="{FONT}" font-size="18" fill="#8E8E93">{lab} · {"dark" if dark else "light"}</text>')
        y += 240
    y += 20
OV = (1100, y, f'<text x="40" y="46" font-family="{FONT}" font-size="28" font-weight="700" fill="#F5F5F7">v5 — emerald vs blue · 180 / 32 / 16 px</text>' + "".join(out))
# silhouette check: own simplified, generic shapes (not real logos), solid black at 64px + 16px
REF = {
 "generic oval bubble + tail (Kakao-like)": '<ellipse cx="50" cy="46" rx="38" ry="30"/><path d="M28 66 22 84 44 72z"/>',
 "generic round bubble + side tail (iMessage-like)": '<ellipse cx="50" cy="48" rx="38" ry="32"/><path d="M20 66q0 16-8 20 18 0 24-12z"/>',
 "generic paper-plane (Telegram-like)": '<circle cx="50" cy="50" r="38"/><path d="M28 50 72 32 62 70 50 58 44 66 44 54z" fill="#fff"/>',
 "v4 Bubble (previous)": None,
}
os.makedirs("_check", exist_ok=True)
E["mark"].__globals__["MONO"] = True
items = [(k, v if v else '<path d="M30 20h40a16 16 0 0 1 16 16v22a16 16 0 0 1-16 16H44L24 88V73a16 16 0 0 1-10-15V36a16 16 0 0 1 16-16z" fill="none" stroke="#000" stroke-width="9" stroke-miterlimit="8"/><rect x="32" y="35" width="10" height="24" rx="5"/>') for k, v in REF.items()]
items += [(d["title"] + " (v5)", E["mark"](k, "#000", "#fff", f"q{i}").replace("#007A72", "#000")) for i, (k, d) in enumerate(E["C"].items())]
body = ""; 
for i, (lab, m) in enumerate(items):
    x = 30 + (i % 4) * 260; yy = 40 + (i // 4) * 260
    fill = 'fill="#000"' if "Kakao" in lab or "iMessage" in lab or "Telegram" in lab else ''
    body += f'<rect x="{x}" y="{yy}" width="240" height="240" rx="12" fill="#fff"/><g transform="translate({x+40} {yy+20}) scale(1.4)" {fill}>{m}</g>'
    body += f'<g transform="translate({x+200} {yy+180}) scale(.16)" {fill}>{m}</g><text x="{x+10}" y="{yy+232}" font-family="{FONT}" font-size="12" fill="#555">{lab}</text>'
png("_check/silhouette-check", 1080, 560, '<text x="30" y="26" font-family="' + FONT + '" font-size="18" fill="#F5F5F7">Silhouette check (own generic shapes, not real logos) — solid, 140px + 16px</text>' + body)

png("overview", *OV)
