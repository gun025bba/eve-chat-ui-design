#!/usr/bin/env python3
"""Build logo concepts: SVG sources + PNG previews via rsvg-convert. Run: python3 build.py"""
import os, subprocess
NAME = "Lumen"  # placeholder app name
FONT = "Inter, 'SF Pro Display', system-ui, sans-serif"
PAL = os.environ.get("PAL", "emerald")
PALS = {  # accent dark/light, fg dark/light, icon bg
 "emerald": dict(acc={"d": "#00D2BE", "l": "#007A72"}, fgd="#C4C9CF", fgl="#121417", ibg="#0B0B0C"),
 "blue": dict(acc={"d": "#3D8BFF", "l": "#0B4FE0"}, fgd="#F5F5F7", fgl="#0A1A3A", ibg="#0A1428"),
}
P = PALS[PAL]; BLUE = P["acc"]
def grad(n, mode): return ""
# stroke 9, butt ends = the one crisp detail; no tail
C = {
 "01-open-frame": dict(title="Open Frame", note="꼬리를 없애고, 외곽선의 왼쪽 아래 모서리를 열어 두었습니다. 닫히지 않은 틀은 '아직 생성 중인 답'을 뜻하고, 잘린 획 끝 두 곳이 날카로운 디테일입니다.",
   mark='''<path d="M14 54V36a16 16 0 0 1 16-16h40a16 16 0 0 1 16 16v28a16 16 0 0 1-16 16H34" fill="none" stroke="{fg}" stroke-width="9" stroke-linecap="butt"/><rect x="32" y="37" width="10" height="26" rx="5" fill="{acc}"/>'''),
 "02-corners": dict(title="Corners", note="말풍선을 대각선의 두 모서리 괄호로만 남겼습니다. 가운데 커서에 초점이 모이는 구도로, 대화 앱보다는 생각하는 도구라는 인상을 줍니다.",
   mark='''<path d="M16 46V34a14 14 0 0 1 14-14h14M84 54v12a14 14 0 0 1-14 14H56" fill="none" stroke="{fg}" stroke-width="9" stroke-linecap="butt"/><rect x="45" y="36" width="10" height="28" rx="5" fill="{acc}"/>'''),
 "03-cursor-tile": dict(title="Cursor Tile", note="외곽선을 없애고 커서만 중심에 둔, 가장 단순한 버전입니다. 커서 윗부분의 사선 컷 하나가 유일한 샤프 디테일입니다.",
   mark='''<path d="M38 26 62 14v64a12 12 0 0 1-24 0z" fill="{acc}"/><rect x="38" y="84" width="0" height="0" fill="{fg}"/>'''),
}
MONO = False
def mark(key, fg, bgc, n):
    mode = "l" if fg == P["fgl"] else "d"
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
    bg, fg = (P["ibg"], P["fgd"]) if dark else ("#FFFFFF", P["fgl"])
    r = size * 0.2237  # iOS squircle approx
    k = size / 100 * 0.78; off = size * 0.11
    return f'<rect width="{size}" height="{size}" rx="{r}" fill="{bg}"/><g transform="translate({off} {off}) scale({k})">{mark(key, fg, bg, n)}</g>'
os.makedirs(PAL, exist_ok=True); os.chdir(PAL)
sheet_rows = []
for i, key in enumerate(C):
    d = C[key]; os.makedirs(key, exist_ok=True); p = lambda f: os.path.join(key, f)
    put(p("mark.svg"), svg(100, 100, mark(key, P["fgd"], DARK, "a")), png=False)
    MONO = True
    put(p("mark-mono-dark.svg"), svg(100, 100, mark(key, P["fgd"], DARK, "m")), png=False)
    put(p("mark-mono-light.svg"), svg(100, 100, mark(key, P["fgl"], LIGHT, "m")), png=False)
    put(p("mono-preview.svg"), svg(512, 256, f'<rect width="256" height="256" fill="#000"/><rect x="256" width="256" height="256" fill="#fff"/><g transform="translate(38 38) scale(1.8)">{mark(key,P["fgd"],DARK,"m1")}</g><g transform="translate(294 38) scale(1.8)">{mark(key,P["fgl"],LIGHT,"m2")}</g>'))
    MONO = False
    put(p("mark-light.svg"), svg(100, 100, mark(key, P["fgl"], LIGHT, "a")), png=False)
    # previews 512 on dark/light
    put(p("preview-dark.svg"), svg(512, 512, f'<g transform="translate(106 106) scale(3)">{mark(key,P["fgd"],DARK,"a")}</g>', DARK))
    put(p("preview-light.svg"), svg(512, 512, f'<g transform="translate(106 106) scale(3)">{mark(key,P["fgl"],LIGHT,"a")}</g>', LIGHT))
    if d.get("wordmark"):
        for nm, fg, bg in (("dark", P["fgd"], DARK), ("light", P["fgl"], LIGHT)):
            put(p(f"wordmark-{nm}.svg"), svg(560, 160, f'<g transform="translate(36 30) scale(1)">{mark(key, fg, bg, "w")}</g><text x="150" y="104" font-family="{FONT}" font-weight="600" font-size="72" letter-spacing="-2" fill="{fg}">{NAME.lower()}</text>', bg))
    # app icon source + mockup: 180 + small sizes on dark and light wallpaper
    put(p("app-icon-1024.svg"), svg(1024, 1024, f'<rect width="1024" height="1024" fill="{P["ibg"]}"/><g transform="translate(112 112) scale(8)">{mark(key,P["fgd"],P["ibg"],"i")}</g>'))
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
<rect width="200" height="200" rx="20" fill="#000" stroke="#2C2C2E"/><g transform="translate(30 30) scale(1.4)">{mark(key,P["fgd"],"#000",f"s{i}")}</g>
<rect x="220" width="200" height="200" rx="20" fill="#fff"/><g transform="translate(250 30) scale(1.4)">{mark(key,P["fgl"],"#fff",f"t{i}")}</g>
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
head = f'<text x="40" y="58" font-family="{FONT}" font-size="34" font-weight="700" fill="#F5F5F7">Logo concepts v5 ({PAL}) — “{NAME}” (placeholder)</text>'
put("overview.svg", svg(W, Ht, head + "".join(rows), "#1C1C1E"))
