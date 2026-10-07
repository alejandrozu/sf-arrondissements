import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        html=open('arrondissements.html').read()
        doc='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'+html+'</body></html>'
        open('/tmp/claude-0/preview.html','w').write(doc)
        for name,w,h,scheme in [('desk',1400,1000,'light'),('phone',400,900,'dark')]:
            pg=await b.new_page(viewport={'width':w,'height':h},color_scheme=scheme)
            msgs=[]; pg.on('console',lambda m: msgs.append(m.text)); pg.on('pageerror',lambda e: msgs.append(str(e)))
            await pg.goto('file:///tmp/claude-0/preview.html'); await pg.wait_for_timeout(1500)
            await pg.screenshot(path=f'shot_{name}.png',full_page=True)
            if name=='desk':
                await pg.hover('#plot .col >> nth=5'); await pg.wait_for_timeout(200); await pg.screenshot(path='shot_chart.png',full_page=True)
            sw=await pg.evaluate('document.documentElement.scrollWidth')
            print(name,'scrollWidth',sw,msgs)
        pg=await b.new_page(viewport={'width':1400,'height':1000})
        msgs=[]; pg.on('pageerror',lambda e: msgs.append(str(e)))
        await pg.goto('file:///tmp/claude-0/preview.html'); await pg.wait_for_timeout(800)
        await pg.fill('#q','Potrero Terrace'); await pg.press('#q','Enter'); await pg.wait_for_timeout(600)
        await pg.screenshot(path='shot_nb.png')
        await pg.click('[data-mode=ring]'); await pg.wait_for_timeout(400)
        await pg.click('#zrst'); await pg.wait_for_timeout(300)
        await pg.mouse.click(300,700); await pg.wait_for_timeout(400)
        await pg.screenshot(path='shot_ring.png')
        pressed=await pg.evaluate("[...document.querySelectorAll('.modes .btn')].map(b=>b.getAttribute('aria-pressed'))")
        await pg.click('[data-mode=ring]'); await pg.wait_for_timeout(300)
        pressed2=await pg.evaluate("[...document.querySelectorAll('.modes .btn')].map(b=>b.getAttribute('aria-pressed'))")
        print('modes',pressed,pressed2,msgs)
        await b.close()
asyncio.run(main())
