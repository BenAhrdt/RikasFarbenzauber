import {bindPhotos} from './photos.js';
import {ask,guardNavigation} from './dialog.js';
import {draw,svgElement} from './figure.js';
import {library,object,template,spaceDocument,uid} from './objects.js';
import {api} from './api.js';
import {bindExports} from './export.js';
import {bindDrawing} from './drawing.js';
const $=s=>document.querySelector(s),canvas=$('#canvas'),status=$('#status'),name=$('#project-name');
const kind=$('.space-editor').dataset.kind;
let project=JSON.parse($('#project-data').textContent),doc=project?.document||template(kind==='room'?'room':kind==='world'?'garden':'empty');
if(!project&&kind==='drawing'){doc=spaceDocument('drawing');name.value='Meine Zeichnung';}
let selectedId=null,drag=null,dirty=false,undo=[],redo=[];
if(project)name.value=project.name;
const selected=()=>doc.objects.find(o=>o.id===selectedId),mode=()=>$('#mode').value;
const labels={hairAccent:'Haarsträhnen',accessory:'Accessoires',metal:'Schmuck',wings:'Flügel',main:'Hauptfarbe',detail:'Zweite Farbe',accent:'Akzente',skin:'Haut',hair:'Haare',shirt:'Oberteil',trousers:'Hose',shoes:'Schuhe',eyes:'Augen',horns:'Kopfschmuck'};
const snapshot=()=>JSON.stringify(doc);
function record(before=snapshot()){undo.push(before);if(undo.length>60)undo.shift();redo=[];}
function changed(){dirty=true;status.textContent='Noch nicht gespeichert.';render();}
function mutate(fn){record();fn();changed();}
function render(){
 draw(canvas,doc,mode());const o=selected();
 $('#photo-options').hidden=o?.asset!=='photo-v1';
 const group=[...canvas.querySelectorAll('[data-object]')].find(g=>g.dataset.object===selectedId);
 if(group){const box=group.getBBox();const border=document.createElementNS(canvas.namespaceURI,'rect');for(const [k,v]of Object.entries({x:box.x-7,y:box.y-7,width:box.width+14,height:box.height+14,fill:'none',stroke:'#7561be','stroke-width':2,'stroke-dasharray':'7 5','pointer-events':'none',class:'selection-border'}))border.setAttribute(k,v);group.append(border);}
 $('#selection-label').textContent=kind==='drawing'?'Dein freies Zeichenblatt':o?`${library[o.asset]?.[0]||(o.asset==='photo-v1'?'Foto':'Figur')} ausgewählt · ${doc.objects.length}/100`:`${doc.objects.length}/100 Gegenstände · Antippen zum Auswählen`;
 $('#mode-label').textContent=mode()==='outline'?'Ausmalbild':mode()==='outline-colored'?'Ausmalbild farbig':'Farbig';
 const previous=$('#part').value;$('#part').replaceChildren();for(const part of Object.keys(o?.colors||{}))$('#part').add(new Option(labels[part]||part,part));if(o?.colors[previous])$('#part').value=previous;
 for(const el of document.querySelectorAll('.transform-tools button,#custom-color,#part,.swatch'))el.disabled=!o;
 if(o)$('#custom-color').value=o.colors[$('#part').value];
 $('#background').value=doc.canvas.background;$('#ground').value=doc.canvas.ground;
 $('#selection').replaceChildren(new Option('Keine Auswahl',''));doc.objects.forEach((item,i)=>$('#selection').add(new Option(`${i+1}. ${library[item.asset]?.[0]||(item.asset==='photo-v1'?'Foto':'Figur')}`,item.id)));$('#selection').value=selectedId||'';
 $('#undo').disabled=!undo.length;$('#redo').disabled=!redo.length;
 document.querySelectorAll('[data-color]').forEach(b=>b.setAttribute('aria-pressed',o?.colors[$('#part').value]===b.dataset.color));
}
function add(asset,x=450,y=350){if(doc.objects.length>=100){status.textContent='Deine Fläche ist voll (100 Gegenstände).';return;}mutate(()=>{const o=object(asset,x,y);doc.objects.push(o);selectedId=o.id;});}
function buildLibrary(){const category=$('#category').value;$('#library').replaceChildren();for(const [asset,info]of Object.entries(library)){if(category!=='Alle'&&info[1]!==category)continue;const b=document.createElement('button');b.dataset.asset=asset;b.setAttribute('aria-label',info[0]+' hinzufügen');const preview=svgElement({version:1,canvas:{width:600,height:650,background:'#ffffff'},objects:[{...object(asset,300,325),scale:1.8}]});preview.setAttribute('aria-hidden','true');b.append(preview,document.createTextNode(info[0]));b.addEventListener('click',()=>add(asset));b.addEventListener('pointerdown',e=>{if(e.pointerType==='mouse'&&e.button!==0)return;libraryDrag={asset,id:e.pointerId,x:e.clientX,y:e.clientY};});$('#library').append(b);}}
let libraryDrag=null;
window.addEventListener('pointerup',e=>{if(!libraryDrag||libraryDrag.id!==e.pointerId)return;const d=libraryDrag;libraryDrag=null;const box=canvas.getBoundingClientRect();if(Math.hypot(e.clientX-d.x,e.clientY-d.y)>12&&e.clientX>=box.left&&e.clientX<=box.right&&e.clientY>=box.top&&e.clientY<=box.bottom){const p=point(e);add(d.asset,clamp(p.x,900),clamp(p.y,650));}});
window.addEventListener('pointercancel',()=>libraryDrag=null);
$('#category').addEventListener('change',buildLibrary);
function clamp(n,max){return Math.max(0,Math.min(max,n));}
function point(e){return new DOMPoint(e.clientX,e.clientY).matrixTransform(canvas.getScreenCTM().inverse());}
canvas.addEventListener('pointerdown',e=>{if(drag)return;const target=e.target.closest('[data-object]');selectedId=target?.dataset.object||null;const o=selected();if(o){const p=point(e);drag={id:e.pointerId,x:p.x,y:p.y,ox:o.x,oy:o.y,before:snapshot(),moved:false};canvas.setPointerCapture(e.pointerId);}render();if(e.target.dataset.part&&o){$('#part').value=e.target.dataset.part;$('#custom-color').value=o.colors[$('#part').value];}});
canvas.addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;const p=point(e);if(!drag.moved&&Math.hypot(p.x-drag.x,p.y-drag.y)<3)return;drag.moved=true;const o=selected();o.x=clamp(drag.ox+p.x-drag.x,900);o.y=clamp(drag.oy+p.y-drag.y,650);changed();});
function endDrag(e){if(drag?.id!==e.pointerId)return;if(drag.moved)record(drag.before);drag=null;render();}
for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,endDrag);
canvas.addEventListener('keydown',e=>{const delta={ArrowLeft:[-5,0],ArrowRight:[5,0],ArrowUp:[0,-5],ArrowDown:[0,5]}[e.key];const o=selected();if(!delta||!o)return;e.preventDefault();mutate(()=>{o.x=clamp(o.x+delta[0],900);o.y=clamp(o.y+delta[1],650);});});
$('#selection').addEventListener('change',e=>{selectedId=e.target.value||null;render();});
$('.transform-tools').addEventListener('click',async e=>{const action=e.target.closest('[data-action]')?.dataset.action,o=selected();if(!action||!o)return;if(action==='delete'&&!await ask('Du kannst ihn danach mit „Zurück“ wiederherstellen.',{title:'Gegenstand löschen?',accept:'Ja, löschen',cancel:'Behalten'}))return;if(action==='copy'&&doc.objects.length>=100){status.textContent='Deine Fläche ist voll (100 Gegenstände).';return;}mutate(()=>{const i=doc.objects.indexOf(o);switch(action){case 'smaller':o.scale=Math.max(.3,o.scale-.1);break;case 'larger':o.scale=Math.min(1.8,o.scale+.1);break;case 'rotate':o.rotation=o.rotation>=180?-165:o.rotation+15;break;case 'flip':o.flipped=!o.flipped;break;case 'copy':{const copy=JSON.parse(JSON.stringify(o));copy.id=uid();copy.x=clamp(copy.x+25,900);copy.y=clamp(copy.y+25,650);doc.objects.push(copy);selectedId=copy.id;break;}case 'delete':doc.objects.splice(i,1);selectedId=null;break;case 'back':if(i>0)[doc.objects[i-1],doc.objects[i]]=[doc.objects[i],doc.objects[i-1]];break;case 'front':if(i<doc.objects.length-1)[doc.objects[i+1],doc.objects[i]]=[doc.objects[i],doc.objects[i+1]];break;}});});
$('#undo').addEventListener('click',()=>{if(!undo.length)return;redo.push(snapshot());doc=JSON.parse(undo.pop());selectedId=null;changed();});
$('#redo').addEventListener('click',()=>{if(!redo.length)return;undo.push(snapshot());doc=JSON.parse(redo.pop());selectedId=null;changed();});
const palette=[['Flieder','#b3a1d3'],['Rosa','#e9b6cc'],['Koralle','#de8277'],['Sonne','#edc56b'],['Grün','#a9be91'],['Blau','#729ba8'],['Himmel','#b1d9e7'],['Creme','#f3dfbb'],['Weiß','#ffffff'],['Braun','#947059'],['Grau','#b5b4be'],['Dunkel','#383348']];
for(const [label,color]of palette){const b=document.createElement('button');b.className='swatch';b.dataset.color=color;b.setAttribute('aria-label',label);const svg=document.createElementNS(canvas.namespaceURI,'svg'),c=document.createElementNS(canvas.namespaceURI,'circle');svg.setAttribute('viewBox','0 0 40 40');for(const [k,v]of Object.entries({cx:20,cy:20,r:17,fill:color,stroke:'#aaa'}))c.setAttribute(k,v);svg.append(c);b.append(svg);b.addEventListener('click',()=>{if(selected())mutate(()=>selected().colors[$('#part').value]=color);});$('#palette').append(b);}
$('#part').addEventListener('change',()=>{$('#custom-color').value=selected().colors[$('#part').value];});
$('#custom-color').addEventListener('change',e=>{if(selected())mutate(()=>selected().colors[$('#part').value]=e.target.value);});
for(const key of ['background','ground'])$('#'+key).addEventListener('change',e=>mutate(()=>doc.canvas[key]=e.target.value));
$('#mode').addEventListener('change',render);
name.addEventListener('input',()=>{dirty=true;status.textContent='Noch nicht gespeichert.';});
document.querySelectorAll('[data-template]').forEach(b=>b.addEventListener('click',async()=>{if(doc.objects.length&&!await ask('Die neue Vorlage ersetzt deine Arbeitsfläche. Mit „Zurück“ kannst du sie wiederherstellen.',{title:'Vorlage übernehmen?',accept:'Vorlage übernehmen',cancel:'Weiter gestalten'}))return;mutate(()=>{doc=b.dataset.template==='empty'?spaceDocument(kind):template(b.dataset.template);selectedId=null;});}));
$('#save').addEventListener('click',async()=>{if(!name.value.trim()){status.textContent='Gib deinem Projekt bitte einen Namen.';name.focus();return;}const button=$('#save'),saved=snapshot(),savedName=name.value;button.disabled=true;status.textContent='Wird gespeichert …';try{project=await api(project?`/api/projects/${project.id}/`:'/api/projects/',project?'PUT':'POST',{name:savedName,kind,document:JSON.parse(saved),revision:project?.revision});history.replaceState(null,'',`/editor/${project.id}/`);dirty=snapshot()!==saved||name.value!==savedName;status.textContent=dirty?'Gespeichert. Neueste Änderungen bitte noch speichern.':'✓ Gespeichert! Dein Projekt wartet auf dich.';}catch(e){status.textContent=e.message;}finally{button.disabled=false;}});
$('#load-projects').addEventListener('click',async()=>{const button=$('#load-projects');button.disabled=true;try{const data=await api('/api/projects/');$('#saved-library').replaceChildren();for(const saved of data.projects){if(saved.id===project?.id)continue;const b=document.createElement('button');b.className='quiet wide';b.textContent=saved.name;b.addEventListener('click',()=>{if(doc.objects.length+saved.document.objects.length>100){status.textContent='Dafür ist die Fläche zu voll (maximal 100 Gegenstände).';return;}mutate(()=>{for(const source of saved.document.objects){const copy=JSON.parse(JSON.stringify(source));copy.id=uid();if(saved.kind==='character'){copy.x=450;copy.y=400;copy.scale=.65;}doc.objects.push(copy);selectedId=copy.id;}});});$('#saved-library').append(b);if(saved.document.version===2){const base=document.createElement('button');base.className='quiet wide';base.textContent=saved.name+' als Grundlage';base.addEventListener('click',async()=>{if(doc.objects.length&&!await ask('Diese Grundlage ersetzt deine Arbeitsfläche. Mit „Zurück“ kannst du sie wiederherstellen.',{title:'Grundlage übernehmen?',accept:'Übernehmen',cancel:'Weiter gestalten'}))return;mutate(()=>{doc=JSON.parse(JSON.stringify(saved.document));doc.objects.forEach(o=>o.id=uid());selectedId=null;});});$('#saved-library').append(base);}}if(!$('#saved-library').children.length)$('#saved-library').textContent='Noch keine anderen Projekte gespeichert.';}catch(e){status.textContent=e.message;}finally{button.disabled=false;}});
bindDrawing({canvas,getDocument:()=>doc,snapshot,commit:before=>{record(before);changed();},status});
if(kind==='drawing'){
 $('.library-panel').hidden=true;$('.transform-tools').hidden=true;$('.history-tools label').hidden=true;
 for(const el of [document.querySelector('label[for="part"]'),$('#part'),$('#palette'),$('#custom-color').parentElement,$('#ground').parentElement,$('.space-options details')])el.hidden=true;
 const paper=$('#background').parentElement;paper.firstChild.textContent='Papierfarbe';
 $('.space-options h2').textContent='Dein Zeichenblatt';$('#drawing-toggle').click();
}
bindExports(()=>doc,()=>name.value,mode,status);
guardNavigation(()=>dirty);
bindPhotos({status,selected,mutate,
 isPhotoUsed:id=>doc.objects.some(o=>o.photo?.id===id),
 onPhotoDeleted:id=>{const references=state=>JSON.parse(state).objects.some(o=>o.photo?.id===id);if(undo.some(references)||redo.some(references)){undo=[];redo=[];}render();},
 insert:(photo,framed,replaceId)=>{
 const existing=doc.objects.find(o=>o.id===replaceId&&o.asset==='photo-v1');
 if(!existing&&doc.objects.length>=100){status.textContent='Deine Fläche ist voll. Dein Foto findest du in „Meine Fotos“. ';return;}
 mutate(()=>{const ref={id:photo.id,width:photo.width,height:photo.height};if(existing){existing.photo=ref;selectedId=existing.id;}else{const o={id:uid(),asset:'photo-v1',x:450,y:350,scale:1,rotation:0,flipped:false,variant:framed?1:0,colors:{main:'#947059',detail:'#f3dfbb',accent:'#ffffff'},photo:ref};doc.objects.push(o);selectedId=o.id;}});
}});
buildLibrary();render();
