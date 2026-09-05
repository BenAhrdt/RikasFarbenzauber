// App-owned modal: native <dialog> supplies focus trapping and inert background,
// while all content, actions and appearance belong to Farbenzauber.
let active = null;
export function ask(message, {title='Bist du sicher?', accept='Ja, fortfahren', cancel='Abbrechen'}={}) {
 if(active)return Promise.resolve(false);
 const previous=document.activeElement;
 const dialog=document.createElement('dialog');dialog.className='magic-dialog';
 dialog.setAttribute('aria-labelledby','magic-dialog-title');dialog.setAttribute('aria-describedby','magic-dialog-message');
 const icon=document.createElement('span');icon.className='dialog-flower';icon.textContent='✿';icon.setAttribute('aria-hidden','true');
 const heading=document.createElement('h2');heading.id='magic-dialog-title';heading.textContent=title;
 const text=document.createElement('p');text.id='magic-dialog-message';text.textContent=message;
 const actions=document.createElement('div');actions.className='dialog-actions';
 const no=document.createElement('button');no.className='quiet';no.textContent=cancel;no.autofocus=true;
 const yes=document.createElement('button');yes.className='primary';yes.textContent=accept;
 actions.append(no,yes);dialog.append(icon,heading,text,actions);document.body.append(dialog);active=dialog;
 return new Promise(resolve=>{
  let done=false;
  function finish(value){if(done)return;done=true;dialog.close();dialog.remove();active=null;if(previous?.isConnected)previous.focus({preventScroll:true});resolve(value);}
  no.addEventListener('click',()=>finish(false));yes.addEventListener('click',()=>finish(true));
  dialog.addEventListener('cancel',e=>{e.preventDefault();finish(false);});
  dialog.addEventListener('click',e=>{if(e.target!==dialog)return;const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)finish(false);});
  dialog.showModal();no.focus();
 });
}

export function guardNavigation(isDirty){
 const leave=()=>ask('Deine letzten Änderungen sind noch nicht gespeichert. Möchtest du die Seite trotzdem verlassen?',{title:'Noch nicht gespeichert',accept:'Seite verlassen',cancel:'Weiter gestalten'});
 document.addEventListener('click',async e=>{
  const link=e.target.closest('a[href]');
  if(!link||e.defaultPrevented||e.button!==0||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey||link.target==='_blank'||link.hasAttribute('download')||!isDirty())return;
  if(link.hash&&link.pathname===location.pathname)return;
  e.preventDefault();if(await leave())location.assign(link.href);
 });
 document.addEventListener('submit',async e=>{
  if(!isDirty()||e.defaultPrevented)return;
  e.preventDefault();const form=e.target;if(await leave())HTMLFormElement.prototype.submit.call(form);
 });
 // Browser reload, tab close and browser Back cannot be paused for a custom
 // async dialog. Deliberately no beforeunload: never show a system popup.
}
