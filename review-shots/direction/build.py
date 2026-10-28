import re,sys
from playwright.sync_api import sync_playwright
d='/workspace/llm-chat-ui-design/'
sp=open(d+'icons/sprite.svg').read()
t=open(d+'review-shots/direction/board.tpl.html').read()
t=t.replace('__SPRITE__',sp).replace('__MARK__','../../logo/final/mark-dark.svg')
open(d+'review-shots/direction/eve-direction-AB.html','w').write(t)
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':2760,'height':1500},device_scale_factor=2)
    pg.goto('file://'+d+'review-shots/direction/eve-direction-AB.html');pg.wait_for_timeout(500)
    pg.screenshot(path=d+'review-shots/direction/eve-direction-AB.png',full_page=True)
    # overflow check
    print(pg.evaluate("""()=>[...document.querySelectorAll('.page')].map(p=>[p.scrollHeight,p.clientHeight,[...p.children].slice(-1)[0].getBoundingClientRect().bottom-p.getBoundingClientRect().bottom])"""))
    print(pg.evaluate("document.documentElement.scrollHeight"))
    b.close()
