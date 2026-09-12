"""Isolated browser integration test; uses a temporary database, never user data."""
import os
import json
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright, expect
root = Path(__file__).resolve().parent.parent
python = str(root / '.venv/bin/python')
with tempfile.TemporaryDirectory(prefix='rika-browser-') as tmp:
    env = {**os.environ, 'DJANGO_DEBUG':'true', 'DATABASE_PATH':f'{tmp}/db.sqlite3', 'DJANGO_SETTINGS_MODULE':'config.settings','UPDATE_MANIFEST_URL':'https://updates.example.org/latest.json','UPDATE_INSTALL_ENABLED':'true','UPDATE_STATE_DIR':f'{tmp}/updates'}
    subprocess.run([python,'manage.py','migrate','--noinput'],env=env,cwd=root,check=True,stdout=subprocess.DEVNULL)
    log=open(f'{tmp}/server.log','w')
    server=subprocess.Popen([python,'manage.py','runserver','127.0.0.1:8765','--noreload'],env=env,cwd=root,stdout=log,stderr=log)
    try:
        for _ in range(80):
            try:
                urllib.request.urlopen('http://127.0.0.1:8765/login/');break
            except OSError: time.sleep(.1)
        with sync_playwright() as p:
            browser=p.chromium.launch(args=['--no-sandbox'])
            context=browser.new_context(viewport={'width':1024,'height':900},has_touch=True,device_scale_factor=1)
            page=context.new_page();errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('console',lambda msg:errors.append(msg.text) if msg.type=='error' else None)
            page.goto('http://127.0.0.1:8765/')
            assert page.url.endswith('/setup/')
            page.locator('#id_username').fill('Browserkind')
            page.locator('#id_password1').fill('browser-test-83-secure')
            page.locator('#id_password2').fill('browser-test-83-secure')
            page.get_by_role('button',name='Admin anlegen & starten').click()
            page.wait_for_url('**/verwaltung/')
            assert page.request.get('http://127.0.0.1:8765/setup/').status == 403
            # Management uses the application design and saves granular rights.
            page.goto('http://127.0.0.1:8765/verwaltung/benutzer/neu/')
            page.locator('#id_username').fill('Rechtetest')
            page.locator('#id_password1').fill('rights-test-83-secure')
            page.locator('#id_password2').fill('rights-test-83-secure')
            page.locator('#id_rooms').uncheck()
            page.locator('#id_photos').uncheck()
            page.get_by_role('button',name='✓ Benutzer speichern').click()
            page.wait_for_url('**/verwaltung/benutzer/')
            expect(page.locator('main')).to_contain_text('Rechtetest')
            page.goto('http://127.0.0.1:8765/verwaltung/zugang/')
            page.locator('#id_addresses').fill('https://farben.example.org\nhttps://rika.example.org')
            page.get_by_role('button',name='Adressen speichern',exact=True).click()
            expect(page.locator('#id_addresses')).to_have_value('https://farben.example.org\nhttps://rika.example.org')
            page.screenshot(path='/tmp/rika-access.png',full_page=True)
            page.goto('http://127.0.0.1:8765/verwaltung/benutzer/')
            page.screenshot(path='/tmp/rika-management.png',full_page=True)
            page.get_by_role('button',name='Als Rechtetest anmelden',exact=True).click()
            page.wait_for_url('http://127.0.0.1:8765/')
            expect(page.locator('.impersonation-banner')).to_contain_text('Rechtetest')
            page.get_by_role('button',name='↩ Zurück zum Admin',exact=True).click()
            page.wait_for_url('**/verwaltung/benutzer/')
            expect(page.locator('.impersonation-banner')).to_have_count(0)
            assert next(c for c in context.cookies() if c['name']=='sessionid')['expires'] > time.time()+300*86400
            page.goto('http://127.0.0.1:8765/')
            page.get_by_role('link',name='+ Neu: Figur',exact=True).click()
            expect(page.locator('body')).to_have_attribute('data-state','ready')
            expect(page.locator('[data-starter]')).to_have_count(3)
            expect(page.locator('[data-variant]')).to_have_count(10)
            expect(page.locator('#canvas [data-object]')).to_have_count(1)
            # A failed module must show a recoverable error, never a blank editor.
            page.route('**/studio/editor.js',lambda route:route.abort())
            page.reload()
            expect(page.locator('body')).to_have_attribute('data-state','error')
            expect(page.locator('#app-reload')).to_be_visible()
            assert page.locator('#app-main').evaluate('(el)=>el.inert')
            page.unroute('**/studio/editor.js')
            errors.clear() # Expected deliberately failed request above.
            page.locator('#app-reload').click()
            expect(page.locator('body')).to_have_attribute('data-state','ready')
            expect(page.locator('[data-variant]')).to_have_count(10)
            # Simulate the outdated cached HTML that previously broke setup.
            def stale_html(route):
                response=route.fetch()
                html=response.text().replace('id="starter-presets"','id="old-starter-presets"')
                route.fulfill(response=response,body=html)
            page.route('**/editor/?kind=character',stale_html)
            page.reload()
            expect(page.locator('body')).to_have_attribute('data-state','error')
            expect(page.locator('#app-loading')).to_contain_text('nicht vollständig geladen')
            page.unroute('**/editor/?kind=character')
            errors.clear()
            page.locator('#app-reload').click()
            expect(page.locator('body')).to_have_attribute('data-state','ready')
            expect(page.locator('[data-starter]')).to_have_count(3)
            expect(page.locator('[data-variant]')).to_have_count(10)
            expect(page.locator('body')).to_have_attribute('data-state','ready')
            page.locator('#project-name').fill('Rikas Sternfreund')
            page.get_by_text('Ideen zum Starten',exact=True).click()
            page.locator('[data-variant="1"]').tap()
            page.locator('[data-body="width"]').fill('1.2')
            page.locator('[data-body="width"]').dispatch_event('input')
            page.locator('[data-body="width"]').dispatch_event('change')
            page.locator('#avatar-category').select_option('Haare')
            page.locator('[data-choice="hair"]').select_option('braids')
            page.locator('#avatar-category').select_option('Accessoires')
            page.locator('[data-choice="glasses"]').select_option('round')
            page.locator('[data-choice="bag"]').select_option('crossbody')
            page.locator('#undo').click()
            expect(page.locator('[data-choice="bag"]')).to_have_value('none')
            page.locator('#redo').click()
            expect(page.locator('[data-choice="bag"]')).to_have_value('crossbody')
            page.locator('#part').select_option('shirt');page.get_by_role('button',name='Koralle',exact=True).tap()
            assert page.locator('#canvas [data-part="shirt"]').first.get_attribute('fill')=='#de8277'
            # Real touch drag through Chromium's input protocol.
            page.locator('#canvas').scroll_into_view_if_needed()
            box=page.locator('#canvas [data-part="shirt"]').first.bounding_box()
            x,y=box['x']+box['width']/2,box['y']+box['height']/2
            session=context.new_cdp_session(page)
            session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
            session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+30,'y':y+20}]})
            session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
            page.get_by_role('button',name='✓ Speichern',exact=True).click()
            expect(page.locator("#status")).to_contain_text("Gespeichert!")
            url=page.url
            page.reload()
            expect(page.locator('#project-name')).to_have_value('Rikas Sternfreund')
            assert page.locator('#canvas [data-part="shirt"]').first.get_attribute('fill')=='#de8277'
            data=page.request.get('http://127.0.0.1:8765/api/projects/').json()['projects'][0]
            assert data['document']['objects'][0]['x']>300
            appearance=data['document']['objects'][0]['appearance']
            assert appearance['body']['width']==1.2
            assert appearance['choices']['hair']=='braids'
            assert appearance['choices']['glasses']=='round'
            # Every catalog choice renders finite geometry, including max body dimensions.
            checked=page.evaluate('''async () => {
                const {catalog,defaultAppearance,avatarColors}=await import('/static/studio/avatar.js');
                const {svgElement}=await import('/static/studio/figure.js');
                const object={id:'check',asset:'avatar-v2',x:300,y:340,scale:1,rotation:0,flipped:false,variant:0,colors:avatarColors(),appearance:defaultAppearance()};
                let count=0;
                for(const [key,spec] of Object.entries(catalog.choices))for(const [value] of spec.options){
                    object.appearance=defaultAppearance();object.appearance.choices[key]=value;
                    const svg=svgElement({version:1,canvas:{width:600,height:650,background:'#ffffff'},objects:[object]},'outline');
                    if(svg.outerHTML.includes('NaN')||svg.outerHTML.includes('undefined'))throw new Error(key+' invalid geometry');
                    for(const n of svg.querySelectorAll('[stroke]'))if(n.getAttribute('stroke')!=='#000000')throw new Error('Non-black outline: '+key);
                    count++;
                }
                return count;
            }''')
            assert checked>100
            page.locator('#mode').select_option('outline')
            assert page.locator('#canvas [data-part="shirt"]').first.get_attribute('fill')=='#ffffff'
            with page.expect_download() as download:
                page.get_by_role('button',name='↓ PNG speichern',exact=True).click()
            downloaded=Path(download.value.path()).read_bytes()
            assert downloaded[:8]==b'\x89PNG\r\n\x1a\n'
            with page.expect_download() as download:
                page.get_by_role('button',name='↓ SVG speichern',exact=True).click()
            assert b'<svg' in Path(download.value.path()).read_bytes()
            page.emulate_media(media='print')
            assert page.locator('.topbar').is_hidden()
            expect(page.locator('#print-orientation')).to_have_value('portrait')
            import re
            for orientation in ['portrait','landscape']:
                page.locator('#print-orientation').select_option(orientation,force=True)
                pdf=page.pdf(prefer_css_page_size=True)
                boxes=re.findall(rb'/MediaBox\s*\[([\d. ]+)\]',pdf)
                assert boxes, 'PDF page dimensions missing'
                x,y,w,h=map(float,boxes[0].split())
                assert (w>h)==(orientation=='landscape'), (orientation,w,h)
                assert len(re.findall(rb'/Type\s*/Page\b',pdf))==1, 'Unexpected extra printed page'
            page.locator('#print-orientation').select_option('portrait',force=True)
            page.emulate_media(media='screen')
            # The button exports an actual one-page PDF even if popups are blocked.
            page.evaluate('window.originalOpen=window.open;window.open=()=>null')
            for orientation in ['portrait','landscape']:
                page.locator('#print-orientation').select_option(orientation)
                with page.expect_download() as printed:
                    page.locator('#print').click()
                pdf=Path(printed.value.path()).read_bytes()
                assert pdf.startswith(b'%PDF-1.4')
                assert len(re.findall(rb'/Type /Page\b',pdf))==1
                w,h=map(float,re.search(rb'/MediaBox \[0 0 ([\d.]+) ([\d.]+)\]',pdf).groups())
                assert (w>h)==(orientation=='landscape')
            page.evaluate("() => { window.open=()=>{throw new Error('Popup unavailable')}; }")
            with page.expect_download() as restricted:
                page.locator('#print').click()
            assert Path(restricted.value.path()).read_bytes().startswith(b'%PDF-1.4')
            expect(page.locator('#print')).to_be_enabled()
            page.evaluate('() => { window.open=window.originalOpen; }')
            page.locator('#print-orientation').select_option('portrait')
            page.locator('#mode').select_option('color')
            # The preview must stay above the export panel after scrolling on mobile/tablet.
            for width,height in [(390,844),(844,390),(768,1024),(1024,768),(1100,900)]:
                page.set_viewport_size({'width':width,'height':height})
                page.locator('.export-panel').scroll_into_view_if_needed()
                workspace=page.locator('.workspace').bounding_box()
                panel=page.locator('.export-panel').bounding_box()
                assert workspace['y']+workspace['height'] <= panel['y'], (width,workspace,panel)
            page.set_viewport_size({'width':1024,'height':900})
            page.screenshot(path='/tmp/rika-editor-tablet.png',full_page=True)
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path='/tmp/rika-editor-mobile.png',full_page=True)
            page.goto('http://127.0.0.1:8765/')
            page.locator('.preview svg').wait_for()
            page.set_viewport_size({'width':1280,'height':900})
            page.screenshot(path='/tmp/rika-dashboard.png',full_page=True)
            # A separate device session can open the saved figure.
            second=browser.new_page();second.goto(url)
            second.locator('#id_username').fill('Browserkind');second.locator('#id_password').fill('browser-test-83-secure');second.get_by_role('button',name='In meine Farbenwelt').click()
            second.goto(url);expect(second.locator('#project-name')).to_have_value('Rikas Sternfreund')
            # Existing figures keep their original asset until explicitly upgraded.
            legacy_doc=data['document'].copy()
            legacy_obj=json.loads(json.dumps(legacy_doc['objects'][0]))
            legacy_obj['asset']='sprout-v1';legacy_obj.pop('appearance')
            legacy_obj['colors']={k:legacy_obj['colors'][k] for k in ['skin','hair','shirt','trousers','shoes','eyes','horns']}
            legacy_doc['objects']=[legacy_obj]
            token=next(c['value'] for c in context.cookies() if c['name']=='csrftoken')
            legacy=page.request.post('http://127.0.0.1:8765/api/projects/',headers={'X-CSRFToken':token},data={'name':'Altbestand','document':legacy_doc}).json()
            second.goto('http://127.0.0.1:8765/editor/'+legacy['id']+'/')
            expect(second.locator('#legacy-notice')).to_be_visible()
            second.locator('#upgrade-avatar').click()
            second.get_by_role('dialog').get_by_role('button',name='Ausprobieren',exact=True).click()
            expect(second.locator('#avatar-controls')).to_be_visible()
            second.locator('#undo').click()
            expect(second.locator('#legacy-notice')).to_be_visible()
            second.locator('#redo').click()
            expect(second.locator('#avatar-controls')).to_be_visible()
            second.locator('#save').click()
            expect(second.locator('#status')).to_contain_text('Gespeichert!')
            second.reload()
            expect(second.locator('#avatar-controls')).to_be_visible()
            page.request.delete('http://127.0.0.1:8765/api/projects/'+legacy['id']+'/',headers={'X-CSRFToken':token})
            page.on('dialog',lambda dialog:errors.append('Unexpected system dialog: '+dialog.type))
            page.goto('http://127.0.0.1:8765/?kind=room')
            page.get_by_role('link',name='+ Neu: Raum oder Haus',exact=True).click()
            expect(page.locator('body')).to_have_attribute('data-state','ready')
            page.locator('#project-name').fill('Zauberzimmer')
            page.locator('#canvas [data-object]').first.wait_for()
            expect(page.locator('#canvas [data-object]')).to_have_count(5)
            page.get_by_role('button',name='Sofa hinzufügen',exact=True).scroll_into_view_if_needed()
            source=page.get_by_role('button',name='Sofa hinzufügen',exact=True).bounding_box()
            target=page.locator('#canvas').bounding_box()
            page.mouse.move(source['x']+source['width']/2,source['y']+source['height']/2)
            page.mouse.down()
            page.mouse.move(target['x']+target['width']*.75,target['y']+target['height']*.75,steps=10)
            page.mouse.up()
            expect(page.locator('#canvas [data-object]')).to_have_count(6)
            page.locator('#undo').click()
            expect(page.locator('#canvas [data-object]')).to_have_count(5)
            page.get_by_role('button',name='Bett hinzufügen',exact=True).click()
            expect(page.locator('#canvas [data-object]')).to_have_count(6)
            page.get_by_role('button',name='Koralle',exact=True).click()
            page.get_by_role('button',name='▣ Kopieren',exact=True).click()
            expect(page.locator('#canvas [data-object]')).to_have_count(7)
            page.get_by_role('button',name='↓ Nach hinten',exact=True).click()
            page.get_by_role('button',name='⇆ Spiegeln',exact=True).click()
            page.get_by_role('button',name='↻ Drehen',exact=True).click()
            page.get_by_role('button',name='× Löschen',exact=True).click()
            expect(page.get_by_role('dialog')).to_be_visible()
            page.get_by_role('button',name='Behalten',exact=True).click()
            expect(page.locator('#canvas [data-object]')).to_have_count(7)
            page.get_by_role('button',name='× Löschen',exact=True).click()
            page.keyboard.press('Escape')
            expect(page.locator('#canvas [data-object]')).to_have_count(7)
            page.get_by_role('button',name='× Löschen',exact=True).click()
            page.get_by_role('dialog').get_by_role('button',name='Ja, löschen',exact=True).click()
            expect(page.locator('#canvas [data-object]')).to_have_count(6)
            page.locator('#undo').click()
            expect(page.locator('#canvas [data-object]')).to_have_count(7)
            page.locator('#redo').click()
            expect(page.locator('#canvas [data-object]')).to_have_count(6)
            # Drag the selected object using real touch events, then save it.
            page.locator('#selection').select_option(index=6)
            bounds=page.locator('#canvas').bounding_box()
            group=page.locator('#canvas [data-object]').last
            box=group.bounding_box()
            x,y=box['x']+box['width']/2,box['y']+box['height']/2
            session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
            session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+25,'y':y+15}]})
            session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
            photo=Image.new('RGB',(200,100),'red')
            photo.paste('blue',(100,0,200,100))
            photo_path=f'{tmp}/my-table.png';photo.save(photo_path)
            page.get_by_text('Eigene Fotos',exact=True).click()
            assert page.locator('#photo-camera').get_attribute('capture')=='environment'
            page.locator('#photo-file').set_input_files(photo_path)
            expect(page.get_by_role('dialog')).to_be_visible()
            page.locator('#cancel-photo').click()
            expect(page.locator('#canvas [data-object]')).to_have_count(6)
            page.locator('#photo-file').set_input_files(photo_path)
            page.locator('#photo-name').fill('Mein echter Tisch')
            page.locator('[data-crop="right"]').fill('50')
            page.locator('[data-crop="right"]').dispatch_event('input')
            page.locator('#photo-style').select_option('frame')
            page.locator('#upload-photo').click()
            expect(page.locator('#status')).to_contain_text('Foto gespeichert')
            expect(page.locator('#canvas [data-object]')).to_have_count(7)
            expect(page.locator('#canvas image')).to_have_count(1)
            page.locator('#toggle-frame').click()
            page.locator('#toggle-frame').click()
            photos=page.request.get('http://127.0.0.1:8765/api/photos/').json()['photos']
            assert len(photos)==1 and photos[0]['width']==100 and photos[0]['height']==100
            page.locator('#save').click()
            expect(page.locator("#status")).to_contain_text("Gespeichert!")
            room_url=page.url
            expect(page.locator('body')).to_have_attribute('data-state','ready')
            page.locator('#project-name').fill('Ungespeicherter Name')
            page.get_by_role('link',name='← Meine Projekte',exact=True).click()
            expect(page.get_by_role('dialog')).to_be_visible()
            page.get_by_role('button',name='Weiter gestalten',exact=True).click()
            assert page.url==room_url
            page.get_by_role('link',name='← Meine Projekte',exact=True).click()
            page.get_by_role('button',name='Seite verlassen',exact=True).click()
            page.wait_for_url('**/?kind=room')
            page.goto(room_url)
            expect(page.locator('#project-name')).to_have_value('Zauberzimmer')
            page.reload()
            expect(page.locator('#canvas [data-object]')).to_have_count(7)
            page.locator('#mode').select_option('outline')
            assert page.locator('#canvas [data-part]').first.get_attribute('fill')=='#ffffff'
            with page.expect_download() as output:
                page.locator('#png').click()
            png=Path(output.value.path()).read_bytes()
            assert int.from_bytes(png[16:20],'big')==1800
            page.locator('#mode').select_option('color')
            with page.expect_download() as output:
                page.locator('#svg').click()
            svg=Path(output.value.path()).read_text()
            assert 'data:image/jpeg;base64,' in svg
            assert '/api/photos/' not in svg
            with page.expect_download() as photo_png:
                page.locator('#png').click()
            with Image.open(photo_png.value.path()) as rendered:
                assert any(r>245 and g<15 and b<15 for r,g,b,a in rendered.convert('RGBA').get_flattened_data()), 'Photo missing from PNG'
            expect(page.locator('#print-orientation')).to_have_value('landscape')
            for orientation in ['landscape','portrait']:
                page.locator('#print-orientation').select_option(orientation)
                pdf=page.pdf(prefer_css_page_size=True)
                boxes=re.findall(rb'/MediaBox\s*\[([\d. ]+)\]',pdf)
                x,y,w,h=map(float,boxes[0].split())
                assert (w>h)==(orientation=='landscape')
                assert len(re.findall(rb'/Type\s*/Page\b',pdf))==1
            page.locator('#print-orientation').select_option('landscape')
            page.screenshot(path='/tmp/rika-room-tablet.png',full_page=True)
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path='/tmp/rika-room-mobile.png',full_page=True)
            page.set_viewport_size({'width':1280,'height':900})
            page.goto('http://127.0.0.1:8765/?kind=world')
            page.get_by_role('link',name='+ Neu: Ort',exact=True).click()
            expect(page.locator('body')).to_have_attribute('data-state','ready')
            page.locator('#project-name').fill('Schlossgarten')
            page.locator('summary').filter(has_text='Mit einer Idee starten').click()
            page.locator('[data-template="castle"]').click()
            page.get_by_role('dialog').get_by_role('button',name='Vorlage übernehmen',exact=True).click()
            page.locator('#save').click()
            expect(page.locator("#status")).to_contain_text("Gespeichert!")
            page.goto('http://127.0.0.1:8765/?kind=scene')
            page.get_by_role('link',name='+ Neu: Szene',exact=True).click()
            expect(page.locator('#canvas [data-object]')).to_have_count(0)
            page.get_by_text('Meine Figuren & Projekte',exact=True).click()
            page.locator('#load-projects').click()
            page.get_by_role('button',name='Schlossgarten als Grundlage',exact=True).click()
            page.get_by_role('button',name='Rikas Sternfreund',exact=True).click()
            expect(page.locator('#canvas [data-object]')).to_have_count(5)
            page.locator('#save').click()
            expect(page.locator("#status")).to_contain_text("Gespeichert!")
            page.reload()
            expect(page.locator('#canvas [data-object]')).to_have_count(5)
            page.screenshot(path='/tmp/rika-scene.png',full_page=True)
            # Free drawing uses the large canvas, supports geometric tools,
            # filling closed contours and three distinct export views.
            page.goto('http://127.0.0.1:8765/?kind=drawing')
            page.get_by_role('link',name='+ Neu: Zeichnung',exact=True).click()
            expect(page.locator('#drawing-color')).to_have_value('#000000')
            expect(page.locator('#drawing-size')).to_have_value('4')
            workspace=page.locator('.workspace').bounding_box()
            options=page.locator('.space-options').bounding_box()
            assert workspace['width']>options['width']*2,(workspace,options)
            page.get_by_role('button',name='□ Rechteck',exact=True).click()
            bounds=page.locator('#canvas').bounding_box()
            x1,y1=bounds['x']+bounds['width']*.25,bounds['y']+bounds['height']*.25
            x2,y2=bounds['x']+bounds['width']*.55,bounds['y']+bounds['height']*.55
            session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x1,'y':y1}]})
            session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x2,'y':y2}]})
            session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
            expect(page.locator('#canvas [data-stroke]')).to_have_count(1)
            page.locator('#drawing-color').fill('#edc56b')
            page.get_by_role('button',name='🪣 Füllen',exact=True).click()
            page.locator('#canvas').tap(position={'x':bounds['width']*.4,'y':bounds['height']*.4})
            expect(page.locator('#canvas [data-stroke]')).to_have_attribute('fill','#edc56b')
            page.locator('#mode').select_option('outline')
            expect(page.locator('#canvas [data-stroke]')).to_have_attribute('fill','#ffffff')
            expect(page.locator('#canvas [data-stroke]')).to_have_attribute('stroke','#000000')
            page.locator('#mode').select_option('outline-colored')
            expect(page.locator('#canvas [data-stroke]')).to_have_attribute('fill','#edc56b')
            page.locator('#save').click()
            expect(page.locator('#status')).to_contain_text('Gespeichert!')
            page.reload()
            expect(page.locator('#canvas [data-stroke]')).to_have_count(1)
            page.screenshot(path='/tmp/rika-drawing.png',full_page=True)
            page.goto('http://127.0.0.1:8765/editor/?kind=room')
            token=next(c['value'] for c in context.cookies() if c['name']=='csrftoken')
            uploaded=page.request.post('http://127.0.0.1:8765/api/photos/',headers={'X-CSRFToken':token},multipart={'name':'Löschtest','photo':{'name':'delete.png','mimeType':'image/png','buffer':Path(photo_path).read_bytes()}})
            assert uploaded.status==201
            page.get_by_text('Eigene Fotos',exact=True).click()
            page.locator('#load-photos').click()
            remove=page.get_by_role('button',name='Löschtest löschen',exact=True)
            remove.click()
            page.get_by_role('dialog').get_by_role('button',name='Behalten',exact=True).click()
            expect(remove).to_be_visible()
            remove.click()
            page.get_by_role('dialog').get_by_role('button',name='Ja, löschen',exact=True).click()
            expect(remove).to_have_count(0)
            expect(page.locator('#status')).to_contain_text('Foto aus deiner Bibliothek gelöscht')
            page.goto('http://127.0.0.1:8765/?kind=character')
            page.locator('[data-delete]').click()
            page.get_by_role('dialog').get_by_role('button',name='Behalten',exact=True).click()
            expect(page.locator('.project-card')).to_have_count(1)
            page.locator('[data-delete]').click()
            page.get_by_role('dialog').get_by_role('button',name='Ja, löschen',exact=True).click()
            page.locator('.project-card').wait_for(state='detached')
            expect(page.locator('.project-card')).to_have_count(0)
            # Simulate the external worker without installing anything on this host.
            update_state={'state':'idle','progress':0,'message':'Bereit.'}
            page.route('**/verwaltung/updates/status/',lambda route:route.fulfill(json=update_state))
            page.route('**/verwaltung/updates/check/',lambda route:route.fulfill(json={'available':True,'install_enabled':True,'release':{'version':'9.0.0','notes':'Browser-Test'}}))
            pending_update=[]
            page.route('**/verwaltung/updates/install/',lambda route:pending_update.append(route))
            page.goto('http://127.0.0.1:8765/verwaltung/updates/')
            page.locator('#check-update').click()
            expect(page.locator('#release-version')).to_have_text('Version 9.0.0')
            page.locator('#install-update').click()
            update_state.update(state='running',job='browser-job',progress=60,message='Datenbank wird gesichert …')
            page.get_by_role('dialog').get_by_role('button',name='Update starten',exact=True).click()
            expect(page.locator('#update-status')).to_have_text('Update wird angefordert. Die Release-Quelle wird geprüft …')
            expect(page.locator('#update-progress')).to_be_visible()
            page.wait_for_timeout(200)
            assert pending_update, 'Update request missing after confirmation'
            pending_update[0].fulfill(status=202,json={'job':'browser-job','version':'9.0.0'})
            expect(page.locator('#update-bar')).to_have_attribute('value','60')
            page.screenshot(path='/tmp/rika-update-progress.png',full_page=True)
            update_state.update(state='success',progress=100,message='Update erfolgreich installiert.')
            with page.expect_navigation(wait_until='load',timeout=15000):
                expect(page.locator('#update-status')).to_have_text('Update erfolgreich installiert.',timeout=10000)
            expect(page.locator('#update-status')).to_have_text('Update erfolgreich installiert.')
            assert not errors,errors
            browser.close()
            print('PASS: setup, login, figures, touch, exports, responsive layout, rooms/worlds/scenes, free drawing shapes/fill/modes, photos, history, deletion; no browser errors')
    finally:
        server.terminate();server.wait(timeout=10);log.close()
