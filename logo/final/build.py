#!/usr/bin/env python3
"""Final logo assets (v5 emerald · Open Frame). Requires rsvg-convert + ImageMagick. Run: python3 build.py"""
import subprocess
ACC_D, ACC_L, SILVER, INK, BLACK, ICON_BG, EDGE = "#00D2BE", "#007A72", "#C4C9CF", "#121417", "#0B0B0C", "#141517", "#2A2D31"
def mark(fg, acc):
    return (f'<path d="M14 54V36a16 16 0 0 1 16-16h40a16 16 0 0 1 16 16v28a16 16 0 0 1-16 16H34" fill="none" stroke="{fg}" stroke-width="9" stroke-linecap="butt"/>'
            f'<rect x="32" y="37" width="10" height="26" rx="5" fill="{acc}"/>')
def svg(body, w=100, h=100): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>\n'
def w(name, s): open(name, "w").write(s)
def png(src, out, size): subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), "-b", ICON_BG, "-o", out, src], check=True)
w("mark-dark.svg", svg(mark(SILVER, ACC_D)))
w("mark-light.svg", svg(mark(INK, ACC_L)))
w("mark-mono-dark.svg", svg(mark(SILVER, SILVER)))
w("mark-mono-light.svg", svg(mark(INK, INK)))
# app icon: opaque square (OS applies mask), lighter-than-black bg + faint inner edge so it doesn't vanish on black
icon = f'<rect width="100" height="100" fill="{ICON_BG}"/><rect x=".5" y=".5" width="99" height="99" rx="22" fill="none" stroke="{EDGE}" stroke-width="1"/><g transform="translate(11 11) scale(.78)">{mark(SILVER, ACC_D)}</g>'
w("app-icon.svg", svg(icon))
# favicon: rounded tile, mark slightly larger for legibility at 16px
fav = f'<rect width="100" height="100" rx="22" fill="{ICON_BG}"/><g transform="translate(4 4) scale(.92)">{mark(SILVER, ACC_D)}</g>'
w("favicon.svg", svg(fav))
# maskable: full-bleed bg, mark inside the central 80% safe circle (mark spans 72u -> scaled .6 = 43% of tile)
mask = f'<rect width="100" height="100" fill="{ICON_BG}"/><g transform="translate(20 20) scale(.6)">{mark(SILVER, ACC_D)}</g>'
w("icon-maskable.svg", svg(mask))
for s in (16, 32, 48):
    subprocess.run(["rsvg-convert", "-w", str(s), "-h", str(s), "-o", f"favicon-{s}.png", "favicon.svg"], check=True)
subprocess.run(["convert", "favicon-16.png", "favicon-32.png", "favicon-48.png", "favicon.ico"], check=True)
png("app-icon.svg", "apple-touch-icon.png", 180)
for s in (192, 512): png("app-icon.svg", f"icon-{s}.png", s)
for s in (192, 512): png("icon-maskable.svg", f"icon-maskable-{s}.png", s)
for f in ("apple-touch-icon.png", "icon-192.png", "icon-512.png", "icon-maskable-192.png", "icon-maskable-512.png"):
    subprocess.run(["convert", f, "-background", ICON_BG, "-flatten", "-alpha", "off", f], check=True)
# preview sheet
FONT = "Inter, system-ui, sans-serif"
def img(f, x, y, s): return f'<image href="{f}" x="{x}" y="{y}" width="{s}" height="{s}"/>'
P = [f'<rect width="1200" height="640" fill="#1C1C1E"/><text x="40" y="52" font-family="{FONT}" font-size="28" font-weight="700" fill="#F5F5F7">Final · Open Frame (emerald)</text>',
     f'<rect x="40" y="80" width="560" height="260" rx="16" fill="#000"/><rect x="600" y="80" width="560" height="260" rx="16" fill="#F2F2F7"/>']
for x0, bg in ((40, "#000"), (600, "#F2F2F7")):
    r = 40; x = x0 + 30
    for s in (180, 48, 32, 16):
        P.append(f'<g transform="translate({x} {310 - s})"><clipPath id="c{x}"><rect width="{s}" height="{s}" rx="{s*.2237}"/></clipPath><g clip-path="url(#c{x})">{img("apple-touch-icon.png", 0, 0, s)}</g></g>'); x += s + 30
P.append(f'<rect x="40" y="370" width="270" height="230" rx="16" fill="#000"/><g transform="translate(95 400) scale(1.6)">{mark(SILVER, ACC_D)}</g>')
P.append(f'<rect x="330" y="370" width="270" height="230" rx="16" fill="#fff"/><g transform="translate(385 400) scale(1.6)">{mark(INK, ACC_L)}</g>')
P.append(f'<rect x="620" y="370" width="250" height="230" rx="16" fill="#fff"/><g transform="translate(665 400) scale(1.6)">{mark(INK, INK)}</g>')
P.append(f'<rect x="890" y="370" width="270" height="230" rx="16" fill="#F2F2F7"/><g transform="translate(935 395)"><clipPath id="mk"><circle cx="90" cy="90" r="90"/></clipPath><g clip-path="url(#mk)">{img("icon-maskable-192.png", 0, 0, 180)}</g></g>')
for x, t in ((50, "mark · dark"), (340, "mark · light"), (630, "mono · light"), (900, "maskable (circle mask)")):
    P.append(f'<text x="{x}" y="592" font-family="{FONT}" font-size="14" fill="#8E8E93">{t}</text>')
w("preview.svg", svg("".join(P), 1200, 640))
subprocess.run(["rsvg-convert", "-o", "preview.png", "preview.svg"], check=True)
