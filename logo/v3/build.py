#!/usr/bin/env python3
"""Build logo concepts: SVG sources + PNG previews via rsvg-convert. Run: python3 build.py"""
import os, subprocess
NAME = "Lumen"  # placeholder app name
FONT = "Inter, 'SF Pro Display', system-ui, sans-serif"
BLUE = {"d": "#3D8BFF", "l": "#0B4FE0"}  # solid blue; dark bg ~6:1 vs black, light bg ~6:1 vs white
GRADS = {"d": ("#3D8BFF", "#5A9DFF"), "l": ("#0B4FE0", "#2563EB")}  # very subtle, optional
def grad(n, mode):
    a, b = GRADS[mode]
    return f'<linearGradient id="g{n}" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'
C = {
 "01-drop": dict(title="Drop", note="v1 Orb의 둥근 원에서 한 모서리만 뾰족하게 남겼습니다. 원이면서 동시에 말풍선으로 읽히는 하나의 형태로, 16px에서도 실루엣이 분명합니다.",
   mark='''<defs>{grad}</defs><path d="M50 14A36 36 0 1 1 50 86H14V50A36 36 0 0 1 50 14Z" fill="{acc}"/>'''),
 "02-monogram": dict(title="Monogram l", note="v1의 둥근 l 획에 윗부분 사선 컷 하나만 더했습니다. 점은 같은 블루의 원 하나로 두었습니다. 요소는 획과 점, 둘뿐입니다.",
   mark='''<path d="M30 30 46 16v62a8 8 0 0 1-16 0z" fill="{fg}"/><circle cx="66" cy="76" r="10" fill="{acc}"/>''', wordmark=True),
 "03-bubble": dict(title="Bubble", note="v1의 둥근 말풍선 외곽선에서 꼬리만 뾰족하게 다듬고, 안의 장식은 모두 덜어냈습니다. 커서 하나만 남겨 대화가 이어지는 순간을 표현합니다.",
   mark='''<path d="M30 20h40a16 16 0 0 1 16 16v22a16 16 0 0 1-16 16H44L24 88V73a16 16 0 0 1-10-15V36a16 16 0 0 1 16-16z" fill="none" stroke="{fg}" stroke-width="9" stroke-linejoin="miter" stroke-miterlimit="8"/><rect x="32" y="35" width="10" height="24" rx="5" fill="{acc}"/>'''),
}
MONO = False
def mark(key, fg, bgc, n):
    mode = "l" if fg.upper() in ("#0A1A3A", "#1D1D1F") else "d"
    acc = fg if MONO else BLUE[mode]
    return C[key]["mark"].replace("{grad}", grad(n, mode)).replace("{acc}", acc).replace("{fg}", fg).replace("{bgc}", bgc).replace("{n}", n)
def svg(w, h, body, bg=None):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{b}{body}</svg>'
def put(path, s, png=True, scale=1):
    open(path, "w").write(s)
    if png: subprocess.run(["rsvg-convert", "-z", str(scale), "-o", path[:-4] + ".png", path], check=True)
DARK, LIGHT = "#000000", "#FFFFFF"
def icon(key, n, size=180, dark=True):
    bg, fg = ("#0A1428", "#F5F5F7") if dark else ("#FFFFFF", "#0A1A3A")
    r = size * 0.2237  # iOS squircle approx
    k = size / 100 * 0.78; off = size * 0.11
    return f'<rect width="{size}" height="{size}" rx="{r}" fill="{bg}"/><g transform="translate({off} {off}) scale({k})">{mark(key, fg, bg, n)}</g>'
sheet_rows = []
for i, key in enumerate(C):
    d = C[key]; os.makedirs(key, exist_ok=True); p = lambda f: os.path.join(key, f)
    put(p("mark.svg"), svg(100, 100, mark(key, "#F5F5F7", DARK, "a")), png=False)
    MONO = True
    put(p("mark-mono-dark.svg"), svg(100, 100, mark(key, "#F5F5F7", DARK, "m")), png=False)
    put(p("mark-mono-light.svg"), svg(100, 100, mark(key, "#0A1A3A", LIGHT, "m")), png=False)
    put(p("mono-preview.svg"), svg(512, 256, f'<rect width="256" height="256" fill="#000"/><rect x="256" width="256" height="256" fill="#fff"/><g transform="translate(38 38) scale(1.8)">{mark(key,"#F5F5F7",DARK,"m1")}</g><g transform="translate(294 38) scale(1.8)">{mark(key,"#0A1A3A",LIGHT,"m2")}</g>'))
    MONO = False
    put(p("mark-light.svg"), svg(100, 100, mark(key, "#0A1A3A", LIGHT, "a")), png=False)
    # previews 512 on dark/light
    put(p("preview-dark.svg"), svg(512, 512, f'<g transform="translate(106 106) scale(3)">{mark(key,"#F5F5F7",DARK,"a")}</g>', DARK))
    put(p("preview-light.svg"), svg(512, 512, f'<g transform="translate(106 106) scale(3)">{mark(key,"#0A1A3A",LIGHT,"a")}</g>', LIGHT))
    if d.get("wordmark"):
        for nm, fg, bg in (("dark", "#F5F5F7", DARK), ("light", "#0A1A3A", LIGHT)):
            put(p(f"wordmark-{nm}.svg"), svg(560, 160, f'<g transform="translate(36 30) scale(1)">{mark(key, fg, bg, "w")}</g><text x="150" y="104" font-family="{FONT}" font-weight="600" font-size="72" letter-spacing="-2" fill="{fg}">{NAME.lower()}</text>', bg))
    # app icon source + mockup: 180 + small sizes on dark and light wallpaper
    put(p("app-icon-1024.svg"), svg(1024, 1024, f'<rect width="1024" height="1024" fill="#0A1428"/><g transform="translate(112 112) scale(8)">{mark(key,"#F5F5F7","#0A1428","i")}</g>'))
    parts = []; x = 40
    for s in (180, 120, 60, 32, 16):
        parts.append(f'<g transform="translate({x} {220 - s})">{icon(key, f"d{s}", s)}</g>'); x += s + 40
    x = 40
    for s in (180, 120, 60, 32, 16):
        parts.append(f'<g transform="translate({x} {480 - s})">{icon(key, f"l{s}", s, False)}</g>'); x += s + 40
    mock = f'<rect width="700" height="260" fill="#000"/><rect y="260" width="700" height="260" fill="#F2F2F7"/>' + "".join(parts) + \
           f'<text x="40" y="246" font-family="{FONT}" font-size="15" fill="#8E8E93">{d["title"]} · 180 / 120 / 60 / 32 / 16 px</text>'
    put(p("ios-mockup.svg"), svg(700, 520, mock))
    sheet_rows.append((key, d))
# contact sheet: one row per concept: dark tile, light tile, icon 180, 32, 16, label
rows = []; H = 230
for i, (key, d) in enumerate(sheet_rows):
    y = 90 + i * H
    rows.append(f'''<g transform="translate(40 {y})">
<rect width="200" height="200" rx="20" fill="#000" stroke="#2C2C2E"/><g transform="translate(30 30) scale(1.4)">{mark(key,"#F5F5F7","#000",f"s{i}")}</g>
<rect x="220" width="200" height="200" rx="20" fill="#fff"/><g transform="translate(250 30) scale(1.4)">{mark(key,"#0A1A3A","#fff",f"t{i}")}</g>
<g transform="translate(450 10)">{icon(key, f"u{i}", 180)}</g>
<g transform="translate(660 158)">{icon(key, f"v{i}", 32)}</g><g transform="translate(706 174)">{icon(key, f"x{i}", 16)}</g>
<text x="760" y="70" font-family="{FONT}" font-size="30" font-weight="700" fill="#F5F5F7">{i+1:02d} {d["title"]}</text>
<foreignObject/></g>''')
    # wrap note into 2 lines (~38 chars)
    note = d["note"]; lines=[""]
    for w in note.split(" "):
        if len(lines[-1])+len(w)>40: lines.append("")
        lines[-1]=(lines[-1]+" "+w).strip()
    rows.append("".join(f'<text x="800" y="{y+110+k*26}" font-family="Noto Sans CJK KR, Noto Sans KR, {FONT}" font-size="17" fill="#AEAEB2">{l}</text>' for k, l in enumerate(lines)))
W, Ht = 1600, 90 + H * len(sheet_rows) + 20
head = f'<text x="40" y="58" font-family="{FONT}" font-size="34" font-weight="700" fill="#F5F5F7">Logo concepts v3 (soft + one sharp detail) — “{NAME}” (placeholder)</text>'
put("overview.svg", svg(W, Ht, head + "".join(rows), "#0B0B0C"))
