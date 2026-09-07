// A real page avoids browser-dependent HTML pagination in the iPad print sheet.
export async function printPdf(svg, orientation) {
 const landscape=orientation==='landscape';
 const width=(landscape?297:210)*72/25.4;
 const height=(landscape?210:297)*72/25.4;
 const margin=12*72/25.4;
 const box=svg.viewBox.baseVal;
 const scale=Math.min((width-2*margin)/box.width,(height-2*margin)/box.height);
 const imageWidth=box.width*scale, imageHeight=box.height*scale;
 const canvas=document.createElement('canvas');
 // 300 dpi at the fitted physical size, independent of screen resolution.
 canvas.width=Math.round(imageWidth*300/72);
 canvas.height=Math.round(imageHeight*300/72);
 const source=svg.cloneNode(true);
 source.setAttribute('width',canvas.width);source.setAttribute('height',canvas.height);
 const url=URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(source)],{type:'image/svg+xml'}));
 try {
  const image=new Image();
  await new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=()=>reject(new Error('Das Druckbild konnte nicht vorbereitet werden.'));image.src=url;});
  const context=canvas.getContext('2d');
  context.fillStyle='white';context.fillRect(0,0,canvas.width,canvas.height);
  context.drawImage(image,0,0,canvas.width,canvas.height);
  const jpeg=await new Promise(resolve=>canvas.toBlob(resolve,'image/jpeg',0.98));
  if(!jpeg)throw new Error('Die PDF konnte nicht erstellt werden.');
  const bytes=new Uint8Array(await jpeg.arrayBuffer());
  const encoder=new TextEncoder(), chunks=[], offsets=[0];let length=0;
  const append=value=>{const chunk=typeof value==='string'?encoder.encode(value):value;chunks.push(chunk);length+=chunk.length;};
  const object=(id,value)=>{offsets[id]=length;append(`${id} 0 obj\n${value}\nendobj\n`);};
  append('%PDF-1.4\n');
  object(1,'<< /Type /Catalog /Pages 2 0 R >>');
  object(2,'<< /Type /Pages /Kids [3 0 R] /Count 1 >>');
  object(3,`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${width} ${height}] /Resources << /XObject << /Picture 4 0 R >> >> /Contents 5 0 R >>`);
  offsets[4]=length;
  append(`4 0 obj\n<< /Type /XObject /Subtype /Image /Width ${canvas.width} /Height ${canvas.height} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${bytes.length} >>\nstream\n`);
  append(bytes);append('\nendstream\nendobj\n');
  const drawing=`q\n${imageWidth} 0 0 ${imageHeight} ${(width-imageWidth)/2} ${(height-imageHeight)/2} cm\n/Picture Do\nQ\n`;
  object(5,`<< /Length ${encoder.encode(drawing).length} >>\nstream\n${drawing}endstream`);
  const xref=length;
  append('xref\n0 6\n0000000000 65535 f \n');
  for(const offset of offsets.slice(1))append(`${String(offset).padStart(10,'0')} 00000 n \n`);
  append(`trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF\n`);
  return new Blob(chunks,{type:'application/pdf'});
 } finally {URL.revokeObjectURL(url);canvas.width=canvas.height=0;}
}
