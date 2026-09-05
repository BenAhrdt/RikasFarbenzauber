import {api} from './api.js';
import {ask} from './dialog.js';
const $=s=>document.querySelector(s);let release=null,polling=false,job=null,waitingSince=Date.now();
function forgetJob(){try{sessionStorage.removeItem('rika-update-job');}catch{}}
async function poll(){
 if(!polling)return;
 try{const state=await api('/verwaltung/updates/status/');
  if(job&&state.job!==job){$('#update-status').textContent=Date.now()-waitingSince>60000?'Der Update-Dienst hat noch nicht übernommen. Bitte den Dienststatus im LXC prüfen. Die Seite wartet weiter …':'Update ist vorgemerkt. Der Dienst startet …';}
  else if(['running','pending','success','error'].includes(state.state)){
   $('#update-progress').hidden=false;$('#update-bar').value=state.progress||0;$('#update-status').textContent=state.state==='pending'&&Date.now()-waitingSince>60000?'Der Update-Dienst hat noch nicht übernommen. Bitte den Dienststatus im LXC prüfen. Die Seite wartet weiter …':state.message;
   if(state.state==='success'){polling=false;setTimeout(()=>location.reload(),1800);return;}
   if(state.state==='error'){forgetJob();polling=false;$('#check-update').disabled=false;return;}
  }
 }catch{$('#update-status').textContent='Server startet neu. Verbindung wird wiederhergestellt …';}
 setTimeout(poll,2000);
}
$('#check-update').onclick=async()=>{const button=$('#check-update');button.disabled=true;$('#update-status').textContent='Suche nach Updates …';$('#release-info').hidden=true;try{const result=await api('/verwaltung/updates/check/','POST',{});release=result.release;$('#update-status').textContent=result.available?'Eine neue Version ist verfügbar.':'Du verwendest die aktuelle Version.';if(result.available){$('#release-info').hidden=false;$('#release-version').textContent='Version '+release.version;$('#release-notes').textContent=release.notes;$('#install-update').disabled=!result.install_enabled;}}catch(e){$('#update-status').textContent=e.message;}finally{button.disabled=false;}};
$('#install-update').onclick=async()=>{if(!release)return;if(!await ask('Das Update erstellt eine Sicherung und startet die Anwendung neu. Bitte stelle sicher, dass alle ihre Projekte gespeichert haben.',{title:'Version '+release.version+' installieren?',accept:'Update starten',cancel:'Später'}))return;$('#install-update').disabled=true;$('#check-update').disabled=true;$('#update-progress').hidden=false;$('#update-bar').removeAttribute('value');$('#update-status').textContent='Update wird angefordert. Die Release-Quelle wird geprüft …';$('#update-status').scrollIntoView({block:'center',behavior:'smooth'});waitingSince=Date.now();const slow=setTimeout(()=>{$('#update-status').textContent='Die Update-Anforderung dauert länger. Bitte diese Seite geöffnet lassen …';},10000);try{const result=await api('/verwaltung/updates/install/','POST',{version:release.version});clearTimeout(slow);job=result.job;try{sessionStorage.setItem('rika-update-job',job);}catch{/* Progress works even when browser storage is disabled. */}$('#update-progress').hidden=false;polling=true;poll();}catch(e){$('#update-status').textContent=e.message;$('#update-progress').hidden=true;$('#check-update').disabled=false;$('#install-update').disabled=false;}finally{clearTimeout(slow);}};
try{const state=await api('/verwaltung/updates/status/');if(['running','pending'].includes(state.state)){job=state.job;polling=true;$('#check-update').disabled=true;poll();}else if(state.state==='success'){forgetJob();$('#update-status').textContent=state.message;}else if(state.state==='error'){$('#update-status').textContent=state.message;}else{job=sessionStorage.getItem('rika-update-job');if(job){polling=true;poll();}}}catch{/* The check button remains available for a retry. */}
