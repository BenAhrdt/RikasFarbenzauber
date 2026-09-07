"""Browser regression: one fitted A4 page, valid byte offsets and uncropped artwork."""
import io
import re
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parent.parent
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(args=['--no-sandbox'])
    page = browser.new_page()
    page.route('http://rika.test/**', lambda route: route.fulfill(
        body=(root/'static/studio/print-pdf.js').read_text() if route.request.url.endswith('.js') else '<!doctype html>',
        content_type='text/javascript' if route.request.url.endswith('.js') else 'text/html'))
    page.goto('http://rika.test/')
    for width, height in [(600,650),(1000,650)]:
        for orientation in ['portrait','landscape']:
            data = bytes(page.evaluate('''async ({width,height,orientation}) => {
                const {printPdf}=await import('/print-pdf.js');
                const svg=new DOMParser().parseFromString(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}"><rect width="${width}" height="${height}" fill="red"/><rect x="20" y="20" width="${width-40}" height="${height-40}" fill="white"/></svg>`,'image/svg+xml').documentElement;
                return [...new Uint8Array(await (await printPdf(svg,orientation)).arrayBuffer())];
            }''', dict(width=width,height=height,orientation=orientation)))
            assert len(re.findall(rb'/Type /Page\b',data)) == 1
            w,h=map(float,re.search(rb'/MediaBox \[0 0 ([\d.]+) ([\d.]+)\]',data).groups())
            assert (w>h)==(orientation=='landscape')
            assert abs(min(w,h)-210*72/25.4)<0.01
            assert abs(max(w,h)-297*72/25.4)<0.01
            xref=int(re.search(rb'startxref\n(\d+)',data)[1])
            assert data[xref:].startswith(b'xref\n')
            offsets=re.findall(rb'(\d{10}) 00000 n',data[xref:])
            for number,offset in enumerate(offsets,1):
                assert data[int(offset):].startswith(f'{number} 0 obj'.encode())
            jpeg_start=data.index(b'stream\n',data.index(b'4 0 obj'))+7
            jpeg_length=int(re.search(rb'/Length (\d+)',data[data.index(b'4 0 obj'):])[1])
            image=Image.open(io.BytesIO(data[jpeg_start:jpeg_start+jpeg_length]))
            for x,y in [(2,2),(image.width-3,2),(2,image.height-3),(image.width-3,image.height-3)]:
                r,g,b=image.getpixel((x,y));assert r>200 and g<40 and b<40
            drawing=data[data.index(b'5 0 obj'):].split(b'stream\n',1)[1].split(b'endstream')[0]
            iw,_,_,ih,x,y=map(float,drawing.splitlines()[1].split()[:6])
            assert abs(iw/ih-width/height)<0.0001
            assert x>=12*72/25.4-0.01 and y>=12*72/25.4-0.01
            assert abs(2*x+iw-w)<0.01 and abs(2*y+ih-h)<0.01
    browser.close()
print('PASS: portrait/landscape artwork fitted on one A4 page in both orientations; PDF offsets and all four image corners verified')
