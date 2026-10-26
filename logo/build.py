#!/usr/bin/env python3
"""Build logo concepts: SVG sources + PNG previews via rsvg-convert. Run: python3 build.py"""
import os, subprocess
NAME = "Lumen"  # placeholder app name
FONT = "Inter, 'SF Pro Display', system-ui, sans-serif"
GRAD = '''<linearGradient id="g{n}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0A84FF"/><stop offset=".5" stop-color="#BF5AF2"/><stop offset="1" stop-color="#FF9F0A"/></linearGradient>'''
# marks drawn in a 100x100 box; {fg} = foreground color, {n} = unique id suffix
C = {
 "01-orb": dict(title="Orb", note="로컬에서 조용히 빛나는 하나의 구. 앱 빈 화면의 컬러 원과 같은 아이덴티티이고, 작은 하이라이트 점이 '항상 켜져 있는' 존재감을 줍니다.",
   mark='''<defs>{grad}<radialGradient id="h{n}" cx=".35" cy=".3" r=".7"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>
<circle cx="50" cy="50" r="38" fill="url(#g{n})"/><circle cx="50" cy="50" r="38" fill="url(#h{n})"/><circle cx="64" cy="36" r="6.5" fill="#fff"/>'''),
 "02-bubble-cursor": dict(title="Bubble · Cursor", note="말풍선 안에서 깜빡이는 커서. 답이 스트리밍되는 순간, 곧 대화가 이어지는 순간을 한 획으로 보여줍니다.",
   mark='''<path d="M28 20h44a14 14 0 0 1 14 14v26a14 14 0 0 1-14 14H46l-16 12v-12h-2a14 14 0 0 1-14-14V34a14 14 0 0 1 14-14z" fill="none" stroke="{fg}" stroke-width="8" stroke-linejoin="round"/>
<rect x="28" y="43" width="26" height="8" rx="4" fill="{fg}" opacity=".55"/><rect x="60" y="34" width="9" height="26" rx="4.5" fill="#0A84FF"/>'''),
 "03-monogram": dict(title="Monogram L·", note="소문자 l과 점: 'local'과 이름 첫 글자. 워드마크와 함께 쓰는 타이포 중심 방향으로, 작은 크기에서도 형태가 단단합니다.",
   mark='''<rect x="30" y="14" width="16" height="72" rx="8" fill="{fg}"/><circle cx="66" cy="74" r="10" fill="#0A84FF"/>''', wordmark=True),
 "04-wave": dict(title="Thought Wave", note="한 번의 부드러운 파동이 점으로 끝납니다. 생각이 흘러 답으로 맺히는 스트리밍의 리듬을 추상화했습니다.",
   mark='''<defs>{grad}</defs><path d="M14 58c10 0 12-24 22-24s12 32 22 32 10-20 18-20" fill="none" stroke="url(#g{n})" stroke-width="9" stroke-linecap="round"/><circle cx="84" cy="46" r="7" fill="{fg}"/>'''),
 "05-dialogue": dict(title="Dialogue", note="채워진 반원(답)과 열린 반원(질문)이 마주 보며 하나의 원을 이룹니다. 묻고 답하는 대화의 리듬을 가장 단순한 기하로 표현했습니다.",
   mark='''<defs>{grad}</defs><path d="M50 14a36 36 0 0 1 0 72z" fill="url(#g{n})"/><path d="M50 86a36 36 0 0 1 0-72" fill="none" stroke="{fg}" stroke-width="8"/><circle cx="50" cy="50" r="7" fill="{bgc}"/>'''),
}
def mark(key, fg, bgc, n):
    return C[key]["mark"].replace("{grad}", GRAD.replace("{n}", n)).replace("{fg}", fg).replace("{bgc}", bgc).replace("{n}", n)
def svg(w, h, body, bg=None):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{b}{body}</svg>'
def put(path, s, png=True, scale=1):
    open(path, "w").write(s)
    if png: subprocess.run(["rsvg-convert", "-z", str(scale), "-o", path[:-4] + ".png", path], check=True)
DARK, LIGHT = "#000000", "#FFFFFF"
def icon(key, n, size=180, dark=True):
    bg, fg = ("#1C1C1E", "#F5F5F7") if dark else ("#FFFFFF", "#1D1D1F")
    r = size * 0.2237  # iOS squircle approx
    k = size / 100 * 0.78; off = size * 0.11
    return f'<rect width="{size}" height="{size}" rx="{r}" fill="{bg}"/><g transform="translate({off} {off}) scale({k})">{mark(key, fg, bg, n)}</g>'
sheet_rows = []
for i, key in enumerate(C):
    d = C[key]; os.makedirs(key, exist_ok=True); p = lambda f: os.path.join(key, f)
    put(p("mark.svg"), svg(100, 100, mark(key, "#F5F5F7", DARK, "a")), png=False)
    put(p("mark-light.svg"), svg(100, 100, mark(key, "#1D1D1F", LIGHT, "a")), png=False)
    # previews 512 on dark/light
    put(p("preview-dark.svg"), svg(512, 512, f'<g transform="translate(106 106) scale(3)">{mark(key,"#F5F5F7",DARK,"a")}</g>', DARK))
    put(p("preview-light.svg"), svg(512, 512, f'<g transform="translate(106 106) scale(3)">{mark(key,"#1D1D1F",LIGHT,"a")}</g>', LIGHT))
    if d.get("wordmark"):
        for nm, fg, bg in (("dark", "#F5F5F7", DARK), ("light", "#1D1D1F", LIGHT)):
            put(p(f"wordmark-{nm}.svg"), svg(560, 160, f'<g transform="translate(36 30) scale(1)">{mark(key, fg, bg, "w")}</g><text x="150" y="104" font-family="{FONT}" font-weight="600" font-size="72" letter-spacing="-2" fill="{fg}">{NAME.lower()}</text>', bg))
    # app icon source + mockup: 180 + small sizes on dark and light wallpaper
    put(p("app-icon-1024.svg"), svg(1024, 1024, f'<rect width="1024" height="1024" fill="#1C1C1E"/><g transform="translate(112 112) scale(8)">{mark(key,"#F5F5F7","#1C1C1E","i")}</g>'))
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
<rect x="220" width="200" height="200" rx="20" fill="#fff"/><g transform="translate(250 30) scale(1.4)">{mark(key,"#1D1D1F","#fff",f"t{i}")}</g>
<g transform="translate(450 10)">{icon(key, f"u{i}", 180)}</g>
<g transform="translate(660 158)">{icon(key, f"v{i}", 32)}</g><g transform="translate(706 174)">{icon(key, f"x{i}", 16)}</g>
<text x="760" y="70" font-family="{FONT}" font-size="30" font-weight="700" fill="#F5F5F7">{i+1:02d} {d["title"]}</text>
<foreignObject/></g>''')
    # wrap note into 2 lines (~38 chars)
    note = d["note"]; lines = [note[j:j+40] for j in range(0, len(note), 40)][:4]
    rows.append("".join(f'<text x="800" y="{y+110+k*26}" font-family="Noto Sans CJK KR, Noto Sans KR, {FONT}" font-size="17" fill="#AEAEB2">{l}</text>' for k, l in enumerate(lines)))
W, Ht = 1600, 90 + H * len(sheet_rows) + 20
head = f'<text x="40" y="58" font-family="{FONT}" font-size="34" font-weight="700" fill="#F5F5F7">Logo concepts — “{NAME}” (placeholder)</text>'
put("overview.svg", svg(W, Ht, head + "".join(rows), "#0B0B0C"))
