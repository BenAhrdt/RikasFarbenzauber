import {api} from './api.js';
import {ask} from './dialog.js';
const $=s=>document.querySelector(s);
const MAX_BYTES=12*1024*1024;

async function cropPhoto(file){
 if(file.size>MAX_BYTES)throw new Error('Bitte ein Foto mit höchstens 12 MB wählen.');
 const url=URL.createObjectURL(file),image=new Image();
 try{await new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=()=>reject(new Error('Dieses Bild kann nicht geöffnet werden. Bitte JPG, PNG oder WebP verwenden; HEIC zuerst als JPG exportieren.'));image.src=url;});}catch(e){URL.revokeObjectURL(url);throw e;}
 if(image.naturalWidth*image.naturalHeight>24000000){URL.revokeObjectURL(url);throw new Error('Bitte ein Foto mit höchstens 24 Megapixeln verwenden.');}
 const previous=document.activeElement,dialog=document.createElement('dialog');dialog.className='magic-dialog photo-dialog';dialog.setAttribute('aria-labelledby','crop-title');
 // Static markup only; filenames and upload responses are never interpreted as HTML.
 dialog.innerHTML='<h2 id="crop-title">Dein Foto-Gegenstand</h2><p>Schneide störende Ränder weg. Du siehst hier deinen fertigen Ausschnitt.</p><canvas id="crop-preview" width="480" height="320" aria-label="Vorschau des Bildausschnitts"></canvas><label for="photo-name">Name</label><input id="photo-name" maxlength="80" autocomplete="off"><div class="crop-sliders"></div><label for="photo-style">So einfügen</label><select id="photo-style"><option value="plain">Als Foto-Gegenstand</option><option value="frame">Mit Bilderrahmen</option></select><p class="note">Der Hintergrund bleibt Teil des Fotos. Automatisches Freistellen oder Nachzeichnen ist noch nicht enthalten.</p><div class="dialog-actions"><button type="button" class="quiet" id="cancel-photo">Abbrechen</button><button type="button" class="primary" id="upload-photo">Foto speichern & einfügen</button></div>';
 document.body.append(dialog);
 const name=dialog.querySelector('#photo-name');name.value=file.name.replace(/\.[^.]+$/,'').slice(0,80)||'Mein Foto';
 const crop={left:0,top:0,right:0,bottom:0};
 const canvas=dialog.querySelector('canvas'),ctx=canvas.getContext('2d');
 const redraw=()=>{const sx=image.naturalWidth*crop.left/100,sy=image.naturalHeight*crop.top/100,sw=image.naturalWidth*(100-crop.left-crop.right)/100,sh=image.naturalHeight*(100-crop.top-crop.bottom)/100;const scale=Math.min(480/sw,320/sh);ctx.clearRect(0,0,480,320);ctx.drawImage(image,sx,sy,sw,sh,(480-sw*scale)/2,(320-sh*scale)/2,sw*scale,sh*scale);};
 for(const [key,label]of [['left','Links'],['right','Rechts'],['top','Oben'],['bottom','Unten']]){const row=document.createElement('label');row.textContent=label+' wegschneiden';const input=document.createElement('input');input.type='range';input.min=0;input.max=90;input.value=0;input.dataset.crop=key;input.setAttribute('aria-label',label+' wegschneiden');input.addEventListener('input',()=>{const other={left:'right',right:'left',top:'bottom',bottom:'top'}[key];crop[key]=Math.min(Number(input.value),90-crop[other]);input.value=crop[key];redraw();});row.append(input);dialog.querySelector('.crop-sliders').append(row);}
 redraw();dialog.showModal();name.focus();
 return new Promise(resolve=>{let done=false;const finish=value=>{if(done)return;done=true;dialog.close();dialog.remove();URL.revokeObjectURL(url);if(previous?.isConnected)previous.focus();resolve(value);};dialog.querySelector('#cancel-photo').onclick=()=>finish(null);dialog.addEventListener('cancel',e=>{e.preventDefault();finish(null);});dialog.querySelector('#upload-photo').onclick=()=>{if(!name.value.trim()){name.focus();return;}finish({name:name.value.trim(),crop:[crop.left/100,crop.top/100,1-crop.right/100,1-crop.bottom/100],framed:dialog.querySelector('#photo-style').value==='frame'});};});
}

export function bindPhotos({status,selected,mutate,insert,isPhotoUsed,onPhotoDeleted}){
 let replaceId=null,busy=false;
 const picker=(camera,replace=false)=>{if(busy)return;replaceId=replace?selected()?.id:null;$(camera?'#photo-camera':'#photo-file').click();};
 $('#choose-photo').onclick=()=>picker(false);$('#camera-photo').onclick=()=>picker(true);
 $('#replace-photo').onclick=()=>picker(false,true);$('#replace-camera').onclick=()=>picker(true,true);
 $('#toggle-frame').onclick=()=>{if(selected()?.asset==='photo-v1')mutate(()=>{selected().variant=selected().variant===1?0:1;});};
 async function refresh(){const {photos}=await api('/api/photos/');const container=$('#photo-library');container.replaceChildren();for(const photo of photos){const card=document.createElement('div');card.className='photo-card';const img=new Image();img.src=`/api/photos/${photo.id}/image/`;img.alt=photo.name;img.loading='lazy';const title=document.createElement('strong');title.textContent=photo.name;card.append(img,title);for(const [label,framed]of [['Einfügen',false],['Im Rahmen',true]]){const button=document.createElement('button');button.className='quiet';button.textContent=label;button.onclick=()=>insert(photo,framed,null);card.append(button);}const remove=document.createElement('button');remove.className='quiet photo-delete';remove.textContent='Foto löschen';remove.setAttribute('aria-label',photo.name+' löschen');remove.onclick=async()=>{
 if(isPhotoUsed(photo.id)){status.textContent='Dieses Foto ist noch auf deiner Arbeitsfläche. Entferne es dort und speichere das Projekt zuerst.';return;}
 if(!await ask('„'+photo.name+'“ wird dauerhaft aus deiner Fotobibliothek gelöscht. Das lässt sich nicht rückgängig machen.',{title:'Foto löschen?',accept:'Ja, löschen',cancel:'Behalten'}))return;
 remove.disabled=true;
 try{await api(`/api/photos/${photo.id}/`,'DELETE');onPhotoDeleted(photo.id);await refresh();status.textContent='✓ Foto aus deiner Bibliothek gelöscht.';}catch(e){status.textContent=e.message;remove.disabled=false;}
 };card.append(remove);container.append(card);}if(!photos.length)container.textContent='Hier warten bald deine eigenen Fotos.';}
 $('#load-photos').onclick=async()=>{try{await refresh();}catch(e){status.textContent=e.message;}};
 for(const input of [$('#photo-file'),$('#photo-camera')])input.addEventListener('change',async()=>{const file=input.files[0],target=replaceId;input.value='';if(!file||busy)return;busy=true;try{const choice=await cropPhoto(file);if(!choice)return;status.textContent='Dein Foto wird gespeichert …';const body=new FormData();body.append('photo',file);body.append('name',choice.name);body.append('crop',JSON.stringify(choice.crop));const response=await fetch('/api/photos/',{method:'POST',headers:{'X-CSRFToken':$('[name=csrfmiddlewaretoken]').value},body});if(response.redirected)throw new Error('Bitte melde dich erneut an.');const photo=await response.json().catch(()=>({error:'Das Foto konnte nicht hochgeladen werden.'}));if(!response.ok)throw new Error(photo.error||'Das Foto konnte nicht hochgeladen werden.');insert(photo,choice.framed,target);status.textContent='✓ Foto gespeichert. Bitte auch dein Projekt speichern.';await refresh();}catch(e){status.textContent=e.message;}finally{busy=false;}});
}
