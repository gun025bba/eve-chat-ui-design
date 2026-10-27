"""Eve icon set: 24px grid, 1.75 stroke, round caps/joins, 2px live-area padding. Run: python3 build.py"""
I = {
 "chevron-left":'<path d="M15 5l-7 7 7 7"/>',
 "chevron-right":'<path d="M9 5l7 7-7 7"/>',
 "chevron-down":'<path d="M5 9l7 7 7-7"/>',
 "compose":'<path d="M12 4H7a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3v-5"/><path d="M9.5 14.5l.5-3 8-8 2.5 2.5-8 8z"/>',
 "settings":'<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>',
 "search":'<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.4-4.4"/>',
 "globe":'<circle cx="12" cy="12" r="8"/><path d="M4 12h16M12 4c2.5 2.6 2.5 13.4 0 16M12 4c-2.5 2.6-2.5 13.4 0 16"/>',
 "send":'<path d="M12 19V5M6 11l6-6 6 6"/>',
 "stop":'<rect x="7" y="7" width="10" height="10" rx="2.5"/>',
 "arrow-down":'<path d="M12 5v14M6 13l6 6 6-6"/>',
 "copy":'<rect x="8" y="8" width="12" height="12" rx="3"/><path d="M16 8V7a3 3 0 0 0-3-3H7a3 3 0 0 0-3 3v6a3 3 0 0 0 3 3h1"/>',
 "check":'<path d="M5 12.5l4.5 4.5L19 7.5"/>',
 "regenerate":'<path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3"/><path d="M19.5 4.5v4h-4"/>',
 "thumb-up":'<path d="M8 11v9H5a1 1 0 0 1-1-1v-7a1 1 0 0 1 1-1z"/><path d="M8 11l4-7a2 2 0 0 1 2 2.3L13.5 10H18a2 2 0 0 1 2 2.4l-1.2 6A2 2 0 0 1 16.8 20H8"/>',
 "thumb-down":'<g transform="rotate(180 12 12)"><path d="M8 11v9H5a1 1 0 0 1-1-1v-7a1 1 0 0 1 1-1z"/><path d="M8 11l4-7a2 2 0 0 1 2 2.3L13.5 10H18a2 2 0 0 1 2 2.4l-1.2 6A2 2 0 0 1 16.8 20H8"/></g>',
 "edit":'<path d="M4 20l1-4L16 5l3 3L8 19z"/><path d="M14 7l3 3"/>',
 "trash":'<path d="M4 7h16M10 4h4M6 7l1 11a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-11"/>',
 "archive":'<rect x="3.5" y="4.5" width="17" height="4" rx="1.5"/><path d="M5 8.5V18a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8.5M10 12.5h4"/>',
 "restore":'<path d="M4.5 12a7.5 7.5 0 1 0 2.2-5.3"/><path d="M4.5 4.5v4h4"/><path d="M12 8.5V12l2.5 1.5"/>',
 "share":'<path d="M12 15V4M8 8l4-4 4 4"/><path d="M8 11H7a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5a2 2 0 0 0-2-2h-1"/>',
 "close":'<path d="M6 6l12 12M18 6L6 18"/>',
 "more":'<circle cx="6" cy="12" r=".9"/><circle cx="12" cy="12" r=".9"/><circle cx="18" cy="12" r=".9"/>',
 "plus":'<path d="M12 5v14M5 12h14"/>',
 "warning":'<path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17.2v.1"/>',
 "info":'<circle cx="12" cy="12" r="8"/><path d="M12 11v5M12 8v.1"/>',
 "link":'<path d="M10 14l4-4"/><path d="M9 7.5l1.5-1.5a3.5 3.5 0 0 1 5 5L14 12.5M10 11.5L8.5 13a3.5 3.5 0 0 0 5 5L15 16.5"/>',
 "source":'<path d="M6 4h9l3 3v13H6z"/><path d="M9 11h6M9 15h4"/>',
 "think":'<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.5.4.5 1 .5 1.6V16h6v-.5c0-.6 0-1.2.5-1.6A6 6 0 0 0 12 3z"/>',
 "sun-horizon":'<path d="M3 18h18M7 18a5 5 0 0 1 10 0M12 7v2M5.6 10.6l1.4 1.4M18.4 10.6L17 12"/>',
 "eye":'<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="2.5"/>',
 "followup":'<path d="M9 15l-5-5 5-5"/><path d="M4 10h10a6 6 0 0 1 0 12h-2"/>',
 "sparkle":'<path d="M12 3c.6 4.6 2.4 6.4 7 7-4.6.6-6.4 2.4-7 7-.6-4.6-2.4-6.4-7-7 4.6-.6 6.4-2.4 7-7z"/>',
 "memory":'<path d="M7 4h10a1 1 0 0 1 1 1v15l-6-4-6 4V5a1 1 0 0 1 1-1z"/>',
 "bell":'<path d="M6 16V11a6 6 0 0 1 12 0v5l1.5 2h-15z"/><path d="M10 21h4"/>',
 "moon":'<path d="M19 14.5A7.5 7.5 0 0 1 9.5 5a7.5 7.5 0 1 0 9.5 9.5z"/>',
 "lock":'<rect x="5" y="10.5" width="14" height="10" rx="2.5"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>',
 "offline":'<path d="M4 4l16 16"/><path d="M8.5 16.5a5 5 0 0 1 7 0M5 13a10 10 0 0 1 4-2.4M19 13a10 10 0 0 0-2.6-1.9M2 9.5a14 14 0 0 1 4.5-2.8M22 9.5A14 14 0 0 0 11 6M12 20v.1"/>',
 "download":'<path d="M12 4v11M8 11l4 4 4-4M5 20h14"/>',
}
H='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
for k,v in I.items(): open(f"svg/{k}.svg","w").write(H+v+"</svg>\n")
sp=['<svg xmlns="http://www.w3.org/2000/svg" style="display:none">']+[f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k,v in I.items()]+['</svg>']
open("sprite.svg","w").write("\n".join(sp)+"\n")
cells="".join(f'<figure><svg class="i"><use href="#i-{k}"/></svg><svg class="i s"><use href="#i-{k}"/></svg><figcaption>{k}</figcaption></figure>' for k in I)
open("preview.html","w").write(f'''<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width"><title>Eve icons</title>
<style>body{{margin:0;padding:24px;background:#000;color:#F5F5F7;font:13px -apple-system,system-ui,sans-serif}}h1{{font:600 22px/28px inherit;margin:0 0 4px}}p{{color:rgba(235,235,245,.62);margin:0 0 20px}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));gap:8px}}figure{{margin:0;background:#1C1C1E;border-radius:14px;padding:14px 8px 10px;text-align:center;box-shadow:inset 0 0 0 .5px rgba(84,84,88,.6)}}
.i{{width:24px;height:24px;fill:none;stroke:currentColor;stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round;margin:0 6px}}.s{{width:17px;height:17px;color:#00D2BE;stroke-width:2}}figcaption{{margin-top:8px;color:rgba(235,235,245,.62);font-size:11px}}</style>
{"".join(sp)}<h1>Eve 아이콘 · {len(I)}개</h1><p>24px 그리드 · 획 1.75 · 둥근 끝 · 오른쪽은 17px(획 2) 축소 확인</p><main>{cells}</main>''')
print(len(I))
