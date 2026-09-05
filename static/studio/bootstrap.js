// Independent of editor imports: also handles missing or broken module files.
(async()=>{
 const page=document.body.dataset.page;
 if(!page)return;
 const main=document.querySelector('#app-main'),banner=document.querySelector('#app-loading'),text=document.querySelector('#app-loading-text'),reload=document.querySelector('#app-reload');
 main.inert=true;main.setAttribute('aria-busy','true');banner.hidden=false;
 reload.onclick=()=>location.reload();
 let failed=false;
 function failure(error){failed=true;document.body.dataset.state='error';banner.hidden=false;text.textContent='Die Seite konnte nicht vollständig geladen werden. Bitte lade sie erneut. Deine gespeicherten Projekte bleiben erhalten.';reload.hidden=false;main.inert=true;main.setAttribute('aria-busy','false');console.error('Farbenzauber konnte nicht starten:',error);}
 const slow=setTimeout(()=>{if(!failed){text.textContent='Das Laden dauert länger. Bitte warte noch einen Moment oder lade erneut.';reload.hidden=false;}},10000);
 try{
  if(page==='editor')await import('./editor.js');
  else if(page==='space')await import('./space.js');
  else if(page==='dashboard')await import('./dashboard.js');
  else throw new Error('Unknown page');
  document.body.dataset.state='ready';main.inert=false;main.setAttribute('aria-busy','false');banner.hidden=true;
 }catch(error){failure(error);}finally{clearTimeout(slow);}
})();
