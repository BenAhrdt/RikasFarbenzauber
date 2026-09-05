export async function api(url,method='GET',body){
 const csrf=document.querySelector('[name=csrfmiddlewaretoken]')?.value;
 const response=await fetch(url,{method,headers:{'Content-Type':'application/json','X-CSRFToken':csrf||''},body:body?JSON.stringify(body):undefined});
 if(response.redirected)throw new Error('Bitte melde dich erneut an. Sichere deine Figur vorher als PNG.');
 const data=await response.json().catch(()=>({error:'Der Server ist gerade nicht erreichbar.'}));
 if(!response.ok)throw new Error(data.error||'Das hat nicht geklappt. Bitte versuche es noch einmal.');
 return data;
}
export function download(blob,name){const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),10000);}
