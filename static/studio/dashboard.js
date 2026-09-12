import {ask} from './dialog.js';
import {api} from './api.js';
import {svgElement} from './figure.js';
const status=document.querySelector('#status');
const lastCategory=document.querySelector('.categories a:last-of-type');
if(lastCategory){const drawing=document.createElement('a');drawing.href='/?kind=drawing';drawing.textContent='🎨 Freies Malen';if(new URLSearchParams(location.search).get('kind')==='drawing'){drawing.className='active';drawing.setAttribute('aria-current','page');}lastCategory.after(drawing);}
try{const {projects}=await api('/api/projects/');for(const p of projects){const preview=document.querySelector(`[data-preview="${p.id}"]`);if(preview)preview.replaceChildren(svgElement(p.document));}}catch(e){status.textContent=e.message;throw e;}
document.querySelectorAll('[data-delete]').forEach(button=>button.addEventListener('click',async()=>{if(!await ask('Das Projekt wird dauerhaft gelöscht.',{title:'Projekt löschen?',accept:'Ja, löschen',cancel:'Behalten'}))return;button.disabled=true;try{await api(`/api/projects/${button.dataset.delete}/`,'DELETE');location.reload();}catch(e){status.textContent=e.message;button.disabled=false;}}));
