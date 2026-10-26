#!/usr/bin/env python3
"""v4/overview.png: blue (v3) vs emerald (v4) per concept, at 180/32/16 on dark and light. Run after both builds."""
import os, runpy, subprocess
here = os.path.dirname(os.path.abspath(__file__))
def load(d):
    cwd = os.getcwd(); os.chdir(d); g = runpy.run_path("build.py"); os.chdir(cwd); return g
v3, v4 = load(os.path.join(here, "../v3")), load(here)
FONT = v4["FONT"]
pairs = [("Monogram l", "02-monogram", "01-monogram"), ("Bubble", "03-bubble", "02-bubble")]
out = []; y = 80
for t, k3, k4 in pairs:
    out.append(f'<text x="40" y="{y}" font-family="{FONT}" font-size="26" font-weight="700" fill="#F5F5F7">{t}</text>'); y += 20
    for lab, g, k in (("Blue (v3)", v3, k3), ("Emerald (v4)", v4, k4)):
        for dark in (True, False):
            x0 = 40 if dark else 560
            bg = "#000" if dark else "#F2F2F7"
            out.append(f'<rect x="{x0}" y="{y}" width="500" height="220" rx="16" fill="{bg}"/>')
            x = x0 + 20
            for s in (180, 32, 16):
                out.append(f'<g transform="translate({x} {y + 200 - s})">{g["icon"](k, f"c{len(out)}", s, dark)}</g>'); x += s + 30
            out.append(f'<text x="{x0+330}" y="{y+40}" font-family="{FONT}" font-size="18" fill="#8E8E93">{lab} · {"dark" if dark else "light"}</text>')
        y += 240
    y += 30
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{y}"><rect width="1100" height="{y}" fill="#0B0B0C"/><text x="40" y="48" font-family="{FONT}" font-size="30" font-weight="700" fill="#F5F5F7">v3 blue vs v4 emerald — 180 / 32 / 16 px</text>{"".join(out)}</svg>'
open(os.path.join(here, "overview.svg"), "w").write(svg)
subprocess.run(["rsvg-convert", "-z", "2", "-o", os.path.join(here, "overview.png"), os.path.join(here, "overview.svg")], check=True)
