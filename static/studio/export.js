import {svgElement} from './figure.js';
import {download} from './api.js';
import {printPdf} from './print-pdf.js';

async function embedPhotos(svg){
 const pending=new Map();
 for(const image of svg.querySelectorAll('image')){
  const url=image.getAttribute('href');
  if(!url||url.startsWith('data:'))continue;
  if(!pending.has(url))pending.set(url,(async()=>{
   const response=await fetch(url);
   if(!response.ok||response.redirected||!response.headers.get('Content-Type')?.startsWith('image/'))throw new Error('Foto nicht verfügbar. Bitte erneut anmelden.');
   const blob=await response.blob();
   return new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=reject;reader.readAsDataURL(blob);});
  })());
  image.setAttribute('href',await pending.get(url));
 }
 return svg;
}

export function bindExports(getDocument,getName,getMode,status){
 const orientation=document.querySelector('#print-orientation');
 orientation.value=getDocument().canvas.width>getDocument().canvas.height?'landscape':'portrait';
 const setOrientation=()=>{document.body.dataset.printOrientation=orientation.value;};
 orientation.addEventListener('change',setOrientation);setOrientation();
 const filename=()=>getName().trim().replace(/[^\p{L}\p{N}_ -]/gu,'').slice(0,80)||'Farbenzauber';
 const prepare=async()=>{const doc=JSON.parse(JSON.stringify(getDocument()));const svg=await embedPhotos(svgElement(doc,getMode()));return {doc,svg,blob:new Blob([new XMLSerializer().serializeToString(svg)],{type:'image/svg+xml;charset=utf-8'})};};
 document.querySelector('#svg').addEventListener('click',async e=>{const button=e.currentTarget;button.disabled=true;try{const result=await prepare();download(result.blob,`${filename()}.svg`);status.textContent='✓ Dein Bild ist bereit.';}catch(error){status.textContent=error.message||'Export fehlgeschlagen.';}finally{button.disabled=false;}});
 document.querySelector('#png').addEventListener('click',async e=>{const button=e.currentTarget;button.disabled=true;let url;try{const {doc,blob}=await prepare();url=URL.createObjectURL(blob);const img=new Image();await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=reject;img.src=url;});const canvas=document.createElement('canvas');canvas.width=doc.canvas.width*2;canvas.height=doc.canvas.height*2;canvas.getContext('2d').drawImage(img,0,0);const png=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));if(!png)throw new Error();download(png,`${filename()}.png`);status.textContent='✓ Dein Bild ist bereit.';}catch(error){status.textContent=error.message||'Der Export hat nicht geklappt. Versuche den SVG-Download.';}finally{if(url)URL.revokeObjectURL(url);button.disabled=false;}});
 let pdfUrl;
 document.querySelector('#print').addEventListener('click',async e=>{
  const button=e.currentTarget;button.disabled=true;
  let preview;
  status.textContent='Druck-PDF wird vorbereitet …';
  try{
   // Open during the tap; restrictive browsers can throw instead of returning null.
   try{preview=window.open('about:blank','_blank');}catch{preview=null;}
   if(preview){preview.opener=null;preview.document.title='Druck-PDF';preview.document.body.textContent='Dein Bild wird auf eine A4-Seite eingepasst …';}
   const selectedOrientation=orientation.value;
   const {svg}=await prepare();const pdf=await printPdf(svg,selectedOrientation);
   if(preview&&!preview.closed){if(pdfUrl)URL.revokeObjectURL(pdfUrl);pdfUrl=URL.createObjectURL(pdf);preview.location.replace(pdfUrl);}
   else download(pdf,`${filename()}.pdf`);
   status.textContent='✓ A4-PDF mit einer Seite ist bereit. Auf dem iPad: Teilen → Drucken.';
  }catch(error){if(preview&&!preview.closed)preview.close();status.textContent=error.message||'Druckvorbereitung fehlgeschlagen.';}
  finally{button.disabled=false;}
 });
}
