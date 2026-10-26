#!/usr/bin/env python3
"""Build logo concepts: SVG sources + PNG previews via rsvg-convert. Run: python3 build.py"""
import os, subprocess
NAME = "Lumen"  # placeholder app name
FONT = "Inter, 'SF Pro Display', system-ui, sans-serif"
GRADS = {  # blue range: deep navy -> electric -> ice; darker stops on light backgrounds for contrast
 "d": ("#1F5BFF", "#3D8BFF", "#9BDCFF"),
 "l": ("#071A47", "#0B3FB8", "#1F6BFF"),
}
ACC = {"d": "#4DA3FF", "l": "#0B4FE0"}
def grad(n, mode):
    a, b, c = GRADS[mode]
    return f'<linearGradient id="g{n}" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="{a}"/><stop offset=".55" stop-color="{b}"/><stop offset="1" stop-color="{c}"/></linearGradient>'
C = {
 "01-prism": dict(title="Prism (Orb v2)", note="v1 Orb를 각진 결정체로 다듬었습니다. 여섯 면으로 깎인 보석이 빛을 굴절시키듯, 질문을 받아 답으로 바꾸는 모델을 상징합니다.",
   mark='''<defs>{grad}</defs><path d="M50 10 86 30v40L50 90 14 70V30z" fill="url(#g{n})"/>
<path d="M50 10 86 30 50 50z" fill="#fff" opacity=".28"/><path d="M14 70 50 50 50 90z" fill="#000" opacity=".22"/><path d="M50 50 86 70 50 90z" fill="#000" opacity=".1"/>'''),
 "02-bubble-cursor": dict(title="Bubble · Cursor v2", note="말풍선을 직선과 사선 꼬리로 다시 그리고, 커서를 날카로운 블록으로 바꿨습니다. 답이 스트리밍되는 순간을 단단한 인상으로 보여줍니다.",
   mark='''<path d="M14 18h72v54H46L26 88V72H14z" fill="none" stroke="{fg}" stroke-width="9" stroke-linejoin="miter"/>
<rect x="56" y="31" width="12" height="28" fill="{acc}"/><path d="M28 41h20v8H28z" fill="{fg}" opacity=".5"/>'''),
 "03-monogram": dict(title="Monogram l· v2", note="l 획의 윗부분을 사선으로 잘라내고 점을 마름모로 바꿨습니다. 'local'과 이름 첫 글자라는 의미는 그대로 두고 칼날 같은 인상을 더했습니다.",
   mark='''<path d="M30 24 48 12v76H30z" fill="{fg}"/><path d="M68 62 80 74 68 86 56 74z" fill="{acc}"/>''', wordmark=True),
 "04-shard": dict(title="Shard (new)", note="두 개의 날카로운 삼각 조각이 어긋나며 맞물립니다. 질문과 답이 정확히 들어맞는 순간을 기하학적 절단면으로 표현했습니다.",
   mark='''<defs>{grad}</defs><path d="M14 14h58L14 72z" fill="url(#g{n})"/><path d="M86 28v58H28z" fill="{fg}"/>'''),
}
def mark(key, fg, bgc, n):
    mode = "l" if fg.upper() in ("#0A1A3A", "#0A1A3A") else "d"
    return C[key]["mark"].replace("{grad}", grad(n, mode)).replace("{acc}", ACC[mode]).replace("{fg}", fg).replace("{bgc}", bgc).replace("{n}", n)
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
head = f'<text x="40" y="58" font-family="{FONT}" font-size="34" font-weight="700" fill="#F5F5F7">Logo concepts v2 (sharp · blue) — “{NAME}” (placeholder)</text>'
put("overview.svg", svg(W, Ht, head + "".join(rows), "#0B0B0C"))
