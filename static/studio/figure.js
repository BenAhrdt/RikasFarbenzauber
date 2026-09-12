import {paintAvatar,upgrade} from './avatar.js';
import {paintAsset} from './objects.js';
// Original vector artwork. Asset IDs and named color regions are stable document contracts.
const NS = 'http://www.w3.org/2000/svg';
export const colors = {skin:'#eac0a0',hair:'#786056',shirt:'#a999df',trousers:'#729ba8',shoes:'#e4ad65',eyes:'#383348',horns:'#a9be91'};
export function newDocument(){return {version:1,canvas:{width:600,height:650,background:'#ffffff'},objects:[upgrade({id:Array.from(crypto.getRandomValues(new Uint8Array(16)),byte=>byte.toString(16).padStart(2,'0')).join(''),asset:'sprout-v1',x:300,y:340,scale:1,rotation:0,flipped:false,colors:{...colors},variant:0})]};}
function node(tag,attrs){const n=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n;}
function drawingPath(stroke){const p=stroke.points;if(stroke.kind==='line')return `M${p[0][0]} ${p[0][1]} L${p.at(-1)[0]} ${p.at(-1)[1]}`;if(stroke.kind==='rectangle'){const [a,b]=[p[0],p.at(-1)];return `M${a[0]} ${a[1]} H${b[0]} V${b[1]} H${a[0]} Z`;}if(stroke.kind==='triangle'){const [a,b]=[p[0],p.at(-1)],mid=(a[0]+b[0])/2;return `M${mid} ${a[1]} L${b[0]} ${b[1]} L${a[0]} ${b[1]} Z`;}if(stroke.kind==='circle'){const [a,b]=[p[0],p.at(-1)],r=Math.hypot(b[0]-a[0],b[1]-a[1]);return `M${a[0]-r} ${a[1]} A${r} ${r} 0 1 0 ${a[0]+r} ${a[1]} A${r} ${r} 0 1 0 ${a[0]-r} ${a[1]} Z`;}const points=p.length===1?[p[0],[p[0][0]+.01,p[0][1]]]:p;return points.map((q,i)=>`${i?'L':'M'}${q[0]} ${q[1]}`).join(' ')+(stroke.closed?' Z':'');}
export function draw(svg,doc,mode='color'){
 const outlined=mode!=='color';
 svg.replaceChildren();svg.setAttribute('viewBox',`0 0 ${doc.canvas.width} ${doc.canvas.height}`);
 svg.append(node('rect',{width:doc.canvas.width,height:doc.canvas.height,fill:outlined?'#ffffff':doc.canvas.background}));
 if(doc.version===2&&!doc.canvas.plain)svg.append(node('rect',{x:0,y:420,width:doc.canvas.width,height:230,fill:outlined?'#ffffff':doc.canvas.ground,stroke:outlined?'#000000':'#a99c8c','stroke-width':2}));
 for(const o of doc.objects){
  const g=node('g',{'data-object':o.id,transform:`translate(${o.x} ${o.y}) rotate(${o.rotation}) scale(${o.flipped?-o.scale:o.scale} ${o.scale})`,'stroke':outlined?'#000000':'#494052','stroke-width':3.5,'stroke-linejoin':'round','stroke-linecap':'round'});svg.append(g);
  const shape=(tag,attrs,part)=>{const n=node(tag,{...attrs,fill:outlined?'#ffffff':o.colors[part],'data-part':part});g.append(n);return n;};
  if(o.asset==='avatar-v2'){paintAvatar(g,o,outlined?'outline':'color');continue;}
  if(o.asset==='photo-v1'){
   const factor=200/Math.max(o.photo.width,o.photo.height),w=o.photo.width*factor,h=o.photo.height*factor;
   if(o.variant===1){shape('rect',{x:-w/2-15,y:-h/2-15,width:w+30,height:h+30,rx:4},'main');shape('rect',{x:-w/2-5,y:-h/2-5,width:w+10,height:h+10},'detail');}
   if(outlined)shape('rect',{x:-w/2,y:-h/2,width:w,height:h},'accent');
   else g.append(node('image',{x:-w/2,y:-h/2,width:w,height:h,href:`/api/photos/${o.photo.id}/image/`,preserveAspectRatio:'xMidYMid meet'}));
   continue;
  }
  if(o.asset!=='sprout-v1'){paintAsset(shape,o.asset);continue;}
  shape('path',{d:'M-55 55 L-53 161 Q-35 180 -10 165 L0 100 L10 165 Q35 180 53 161 L55 55Z'},'trousers');
  shape('path',{d:'M-54 153 Q-80 156 -78 179 Q-54 189 -12 179 L-11 156Z'},'shoes');
  shape('path',{d:'M54 153 Q80 156 78 179 Q54 189 12 179 L11 156Z'},'shoes');
  shape('path',{d:'M-63-19 Q-100 6 -103 60 Q-98 82 -82 70 L-58 27 M63-19 Q100 6 103 60 Q98 82 82 70 L58 27'},'skin');
  shape('path',{d:o.variant===1?'M-39-39 L-73-15 L-57 20 L-43 13 L-73 93 Q0 113 73 93 L43 13 L57 20 L73-15 L39-39Z':'M-39-39 L-78-14 L-58 22 L-47 15 L-57 79 Q0 96 57 79 L47 15 L58 22 L78-14 L39-39Z'},'shirt');
  shape('path',{d:'M0-2 L8 15 L27 17 L13 30 L16 49 L0 40 L-16 49 L-13 30 L-27 17 L-8 15Z'},'horns');
  shape('ellipse',{cx:0,cy:-105,rx:83,ry:86},'hair');
  shape('ellipse',{cx:-78,cy:-88,rx:18,ry:25},'skin');shape('ellipse',{cx:78,cy:-88,rx:18,ry:25},'skin');
  shape('path',{d:'M-70-130 Q-65-182 0-175 Q65-182 70-130 L70-79 Q62-28 0-27 Q-62-28-70-79Z'},'skin');
  const hair=['M-76-120 Q-92-188-22-191 Q47-219 78-154 L73-116 Q33-125 10-157 Q-9-111-38-134 Q-55-112-76-120Z','M-76-116 Q-95-171-53-183 Q-44-221-9-191 Q39-220 55-181 Q93-175 76-116 L46-146 L22-128 L0-151 L-24-126 L-49-145Z','M-77-104 Q-109-119-88-145 Q-102-177-67-186 Q-66-216-34-202 Q-6-229 15-204 Q52-222 61-190 Q99-193 87-158 Q111-133 77-108 L54-150 Q4-121-24-157 L-54-137Z'];
  shape('path',{d:hair[o.variant]},'hair');
  if(o.variant===0){shape('path',{d:'M0-191 Q-51-194-43-232 Q-7-240 0-191Z M0-191 Q3-236 41-233 Q50-196 0-191Z'},'horns');}
  if(o.variant===1){shape('path',{d:'M0-194 L-37-213 L-32-245 L-11-226 L0-251 L12-226 L32-245 L37-213Z'},'horns');}
  if(o.variant===2){shape('path',{d:'M-70-175 L-76-217 Q-43-215-38-190 M70-175 L76-217 Q43-215 38-190'},'horns');}
  shape('ellipse',{cx:-27,cy:-95,rx:8,ry:12},'eyes');shape('ellipse',{cx:27,cy:-95,rx:8,ry:12},'eyes');
  g.append(node('path',{d:'M-14-64 Q0-50 14-64 M-3-82 L-6-74 L2-74',fill:'none'}));
 }
 for(const stroke of doc.strokes||[]){
  if(!stroke.points?.length)continue;
  const monochrome=mode==='outline';
  svg.append(node('path',{d:drawingPath(stroke),fill:monochrome?(stroke.closed?'#ffffff':'none'):(stroke.fill||'none'),stroke:monochrome?'#000000':stroke.color,'stroke-width':stroke.width,'stroke-linecap':'round','stroke-linejoin':'round','data-stroke':stroke.id,'pointer-events':'none'}));
 }
}
export function svgElement(doc,mode='color'){const svg=node('svg',{xmlns:NS,width:doc.canvas.width*2,height:doc.canvas.height*2});draw(svg,doc,mode);return svg;}
