// Original modular vector characters. Body parts and clothes share attachment points.
import {catalog} from './avatar-catalog.js';
export {catalog};
export function defaultAppearance(){return {choices:Object.fromEntries(Object.entries(catalog.choices).map(([k,v])=>[k,v.default])),body:Object.fromEntries(Object.entries(catalog.body).map(([k,v])=>[k,v.default]))};}
export function avatarColors(){return Object.fromEntries(Object.entries(catalog.colors).map(([k,v])=>[k,v[1]]));}
export function upgrade(o){return {...o,asset:'avatar-v2',colors:{...avatarColors(),...o.colors},appearance:defaultAppearance()};}
export function paintAvatar(root,o,mode){
 const ns=root.namespaceURI,c=o.appearance.choices,b=o.appearance.body;
 const node=(tag,attrs,parent=root)=>{const n=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);parent.append(n);return n;};
 const group=(transform,parent=root)=>node('g',{transform},parent);
 const whole=group(`scale(${b.height})`);
 const shape=(tag,attrs,part,parent=whole)=>node(tag,{...attrs,fill:mode==='outline'?'#ffffff':o.colors[part],'data-part':part},parent);
 const path=(d,part,parent=whole)=>shape('path',{d},part,parent);
 const ellipse=(cx,cy,rx,ry,part,parent=whole)=>shape('ellipse',{cx,cy,rx,ry},part,parent);
 const rect=(x,y,width,height,part,parent=whole,rx=5)=>shape('rect',{x,y,width,height,rx},part,parent);
 const line=(d,parent=whole)=>node('path',{d,fill:'none'},parent);
 const star=(x,y,r,part,parent=whole)=>{const pts=[];for(let i=0;i<10;i++){const a=-Math.PI/2+i*Math.PI/5,rr=i%2?r*.45:r;pts.push(`${x+Math.cos(a)*rr},${y+Math.sin(a)*rr}`);}return shape('polygon',{points:pts.join(' ')},part,parent);};
 const torso=group(`scale(${b.width} 1)`,whole),shoulder=55*b.shoulders;
 const legBottom=76+102*b.legs;
 // Rear accessories are deliberately behind body and clothing.
 if(c.tail==='cat')path('M35 79 Q130 151 113 35 Q106 10 96 30 Q119 141 35 99Z','accessory');
 if(c.tail==='fox')path('M35 82 Q148 155 142 10 Q90 15 67 56Z','hair');
 if(c.tail==='dragon')path('M30 85 Q114 124 151 42 L129 42 L132 18 L105 40 L87 28 Q72 72 30 65Z','wings');
 if(c.wings!=='none')for(const sign of [-1,1]){const g=group(`scale(${sign} 1)`,whole);if(c.wings==='fairy'){ellipse(91,-7,47,85,'wings',g);ellipse(95,73,37,40,'hairAccent',g);}if(c.wings==='butterfly'){path('M40 30 Q65-110 135-60 Q164 4 86 43 Q158 70 117 115 Q60 127 40 30Z','wings',g);ellipse(105,-15,18,32,'horns',g);}if(c.wings==='dragon'){path('M40 12 L129-81 L152 55 Q112 9 100 69 Q70 33 43 80Z','wings',g);line('M40 12 L129-81 L100 69',g);}}
 if(c.bag==='backpack')rect(-77,-27,154,133,'accessory',torso,24);
 // Legs stay attached when length and width change.
 for(const sign of [-1,1]){const g=group(`scale(${sign} 1)`,torso);rect(7,57,35,legBottom-57,'skin',g,12);
  const end=c.bottom==='shorts'?116:legBottom-7;
  if(c.bottom!=='skirt')path(`M5 58 L49 58 L${c.bottom==='wide'?57:43} ${end} L${c.bottom==='wide'?1:8} ${end}Z`,'trousers',g);
  if(c.bottom==='cargo')rect(26,100,20,27,'detail',g);
  const boot=c.shoes==='boots'?43:c.shoes==='high'?26:12;
  path(`M7 ${legBottom-boot} L44 ${legBottom-boot} L49 ${legBottom-2} Q69 ${legBottom} 66 ${legBottom+15} L7 ${legBottom+15}Z`,'shoes',g);
  if(c.shoes==='sneakers'||c.shoes==='high'){rect(9,legBottom+10,57,7,'detail',g,2);line(`M23 ${legBottom-7} L40 ${legBottom-7} M23 ${legBottom} L42 ${legBottom}`,g);}
  if(c.shoes==='flats'||c.shoes==='sandals')ellipse(25,legBottom-5,13,7,'skin',g);
 }
 if(c.bottom==='skirt')path('M-49 58 L49 58 L67 130 Q0 147-67 130Z','trousers',torso);
 // Arms with connected sleeves, always behind torso.
 for(const sign of [-1,1]){const g=group(`scale(${sign} 1)`,torso);const wave=c.pose==='wave'&&sign===1,hips=c.pose==='hips';
 const d=wave?`M${shoulder-4}-18 Q100-29 96-93 L118-95 Q131-6 ${shoulder+5} 30Z`:hips?`M${shoulder}-17 Q125 15 80 63 L55 42 L78 18 L${shoulder-10} 13Z`:`M${shoulder}-17 Q90 10 94 86 Q85 104 72 87 L${shoulder-9} 17Z`;
 path(d,['hoodie','sweater','jacket','stage','hunter','haori'].includes(c.top)?'shirt':'skin',g);ellipse(wave?107:hips?61:83,wave?-99:hips?49:89,12,15,'skin',g);
 path(`M${shoulder-17}-31 L${shoulder+20}-6 L${shoulder+7} 30 L${shoulder-23} 11Z`,'shirt',g);
 }
 rect(-17,-57,34,38,'skin',torso,8);
 const dress=c.top==='dress'||c.top==='tunic';
 path(`M-${shoulder-15}-39 Q0-21 ${shoulder-15}-39 L${shoulder+5}-15 L47 23 L${dress?78:55} ${dress?135:83} Q0 ${dress?154:97}-${dress?78:55} ${dress?135:83} L-47 23 L-${shoulder+5}-15Z`,'shirt',torso);
 if(c.top==='haori')for(const sign of [-1,1]){const g=group(`scale(${sign} 1)`,torso);path('M12-33 L49-40 L78-10 L69 127 L25 114Z','accessory',g);path('M27 0 L52 22 L27 44 L52 66 L27 88','detail',g);}
 if(c.top==='hoodie'){path('M-39-36 Q0-65 39-36 Q29 4 0-12 Q-29 4-39-36Z','detail',torso);rect(-26,46,52,25,'hairAccent',torso);line('M-12-10 L-12 20 M12-10 L12 20',torso);}
 if(['jacket','stage','vest'].includes(c.top)){path('M-34-38 L0-11 L34-38 L26 31 L0 71 L-26 31Z','detail',torso);line('M0-11 L0 86',torso);for(const x of [-35,35])rect(x-10,40,20,17,'accessory',torso);if(c.top==='stage'){star(-shoulder,-9,17,'metal',torso);star(shoulder,-9,17,'metal',torso);}}
 if(c.top==='hunter'){path('M-35-37 L-8-16 L-21 65 L-56 79 L-48 8Z','accessory',torso);path('M35-37 L8-16 L21 65 L56 79 L48 8Z','accessory',torso);rect(-53,65,106,12,'metal',torso);star(34,-8,12,'metal',torso);line('M-38 5 L-24 15 M-42 17 L-28 27',torso);}
 if(c.top==='sailor'){path('M-40-35 L0-15 L40-35 L31 4 L0 20 L-31 4Z','detail',torso);path('M0 15 L-27 3 L-25 33 L0 22 L25 33 L27 3Z','accessory',torso);ellipse(0,19,7,7,'metal',torso);}
 if(c.pattern==='lightning')path('M4-2 L-23 29 L-3 29 L-12 56 L25 18 L6 18 L17-2Z','metal',torso);
 if(c.pattern==='rune'){path('M0-2 L23 23 L0 48 L-23 23Z','horns',torso);line('M0 7 L0 39 M-13 23 L13 23',torso);}
 if(c.top==='sweater')for(const y of [62,71,80])line(`M-49 ${y} L49 ${y}`,torso);
 if(c.pattern==='star')star(0,23,21,'horns',torso);
 if(c.pattern==='heart')path('M0 43 Q-37 15-18 5 Q-4-1 0 12 Q8-5 23 7 Q38 23 0 43Z','horns',torso);
 if(c.pattern==='stripes')for(const y of [9,28,47])rect(-37,y,74,8,'horns',torso,1);
 if(c.pattern==='moon')path('M12 0 Q-28 4-15 34 Q1 53 22 31 Q-10 39 12 0Z','horns',torso);
 if(c.pattern==='flower'){for(let i=0;i<5;i++)ellipse(Math.cos(i*1.257)*15,23+Math.sin(i*1.257)*15,10,10,'horns',torso);ellipse(0,23,8,8,'metal',torso);}
 if(c.necklace==='pendant'){line('M-24-24 Q0 33 24-24',torso);star(0,9,9,'metal',torso);}
 if(c.necklace==='beads')for(let i=0;i<7;i++)ellipse(-24+i*8,-19+Math.sin(i*Math.PI/6)*20,5,5,'metal',torso);
 if(c.necklace==='scarf'){path('M-28-40 Q0-20 28-40 L30-20 Q0 2-30-20Z','accessory',torso);path('M12-19 L34-13 L43 42 L22 45Z','accessory',torso);}
 if(c.bag==='crossbody'){path('M-38-29 L-29-36 L58 57 L49 65Z','detail',torso);rect(28,49,56,49,'accessory',torso,12);ellipse(55,69,5,5,'metal',torso);}
 if(c.bag==='belt'){rect(-53,63,106,11,'detail',torso);rect(-26,59,52,34,'accessory',torso,12);}
 // Head, hair and all face accessories share one scalable coordinate system.
 const head=group(`translate(0 -113) scale(${b.head})`,whole);
 if(['long','braids','ponytail','curls'].includes(c.hair))path('M-68-37 Q-94 5-84 124 L-42 137 L-29 68 L29 68 L45 137 L89 118 Q95 0 68-37Z','hair',head);
 if(c.hair==='longbraid'){path('M44-63 Q89-119 103-54 L79-17Z','hair',head);for(let i=0;i<8;i++)ellipse(88+Math.sin(i*.8)*9,-20+i*24,17,19,i%2?'hairAccent':'hair',head);path('M82 165 L110 165 L103 199 L91 189 L80 197Z','accessory',head);}
 if(c.hair==='twintails')for(const sign of [-1,1]){const g=group(`scale(${sign} 1)`,head);path('M54-57 Q115-95 107-8 L121 119 L79 103 L75-23Z','hair',g);rect(66,-57,30,13,'accessory',g);path('M91-23 L101 91 L91 81Z','hairAccent',g);}
 if(c.hair==='ponytail')path('M51-60 Q139-110 109 72 L75 90 Q107-12 49-19Z','hairAccent',head);
 for(const sign of [-1,1]){const g=group(`scale(${sign} 1)`,head);if(c.ears==='elf')path('M62-10 L94-36 L82 26 L62 23Z','skin',g);else ellipse(69,7,c.ears==='small'?10:16,c.ears==='small'?17:23,'skin',g);}
 if(c.headShape==='square')rect(-65,-65,130,140,'skin',head,28);else ellipse(0,4,c.headShape==='oval'?60:69,c.headShape==='oval'?79:72,'skin',head);
 if(c.hair!=='bald'){
 const cap={short:'M-69-11 Q-91-73-31-79 Q36-110 71-41 L67-5 Q38-23 18-46 Q-9-6-28-32 Q-52-8-69-11Z',bob:'M-73 29 L-76-32 Q-72-90 0-82 Q79-91 76-29 L73 43 L56 30 L57-34 Q0-4-57-34 L-56 36Z',long:'M-73 24 L-76-34 Q-72-91 0-83 Q79-91 76-29 L69 45 L55 25 L55-37 Q0-18-55-37 L-55 27Z',sidecut:'M-68-7 Q-80-77-17-81 Q43-102 69-40 L48-21 Q-2-24-22-51 L-45 10Z',spikes:'M-70-8 L-86-51 L-58-43 L-53-86 L-23-65 L-5-103 L15-69 L48-93 L51-58 L81-67 L67-8 L35-39 L0-26 L-30-39Z'};
 path(cap[c.hair]||cap.short,'hair',head);
 if(c.hair==='curls')for(let i=0;i<9;i++){const a=Math.PI+i*Math.PI/8;ellipse(Math.cos(a)*66,-21+Math.sin(a)*53,21,23,i%3===0?'hairAccent':'hair',head);}
 if(c.hair==='buns')for(const x of [-68,68]){ellipse(x,-66,29,28,'hair',head);ellipse(x,-66,12,12,'hairAccent',head);}
 if(c.hair==='braids')for(const x of [-65,65]){for(let y=41;y<124;y+=20)ellipse(x,y,15,17,'hair',head);rect(x-15,123,30,8,'accessory',head);}
 if(c.fringe==='straight')path('M-58-49 L58-49 L55-18 L27-21 L0-17 L-27-21 L-55-18Z','hair',head);
 if(c.fringe==='side')path('M-57-54 Q5-94 57-46 Q15-36-17-5 L-30-26 L-54-9Z','hair',head);
 if(c.fringe==='curtain')path('M0-63 Q-46-79-61-35 L-57-7 Q-9-20 0-49 Q9-20 57-7 L61-35 Q46-79 0-63Z','hair',head);
 path('M35-61 Q53-49 51-30 L43-32 Q45-49 29-59Z','hairAccent',head);
 }
 for(const sign of [-1,1]){const g=group(`scale(${sign} 1)`,head);
 if(c.eyes==='happy')line('M17 6 Q28-10 39 6',g);
 else if(c.eyes==='sleepy'){line('M17 5 Q28 16 39 5',g);line('M36 10 L42 14',g);}
 else {if(c.eyes==='almond')path('M15 6 Q28-14 42 6 Q28 18 15 6Z','detail',g);else ellipse(28,5,c.eyes==='bold'?16:13,c.eyes==='bold'?20:16,'detail',g);ellipse(28,6,c.eyes==='bold'?9:7,11,'eyes',g);ellipse(31,1,3,4,'detail',g);if(c.eyes==='sparkle')star(28,5,6,'metal',g);}
 const brow=c.brows==='straight'?'M16-17 L39-17':c.brows==='bold'?'M15-17 L16-23 L40-20 L39-14Z':'M16-16 Q28-24 40-16';if(c.brows==='bold')path(brow,'hair',g);else line(brow,g);
 }
 if(c.nose==='round')ellipse(0,25,7,5,'skin',head);else line(c.nose==='triangle'?'M0 16 L-7 29 L6 29':'M-2 19 L-4 27 L2 27',head);
 if(c.mouth==='smile')line('M-16 42 Q0 58 16 42',head);
 if(c.mouth==='calm')line('M-11 45 L11 45',head);
 if(c.mouth==='small')ellipse(0,45,5,3,'accessory',head);
 if(c.mouth==='open')ellipse(0,46,9,12,'accessory',head);
 if(c.mouth==='grin')path('M-21 39 Q0 47 21 39 Q14 65 0 60 Q-14 65-21 39Z','detail',head);
 if(c.mouth==='laugh')path('M-20 39 L20 39 Q16 70 0 64 Q-16 70-20 39Z','accessory',head);
 if(c.faceDetail==='blush')for(const x of [-43,43])ellipse(x,30,12,6,'accessory',head);
 if(c.faceDetail==='freckles')for(const sign of [-1,1])for(const [x,y]of [[30,29],[41,26],[48,32]])ellipse(x*sign,y,1.6,1.6,'hair',head);
 if(c.faceDetail==='runes')for(const sign of [-1,1]){const g=group(`scale(${sign} 1)`,head);path('M39 21 L49 30 L39 39 L29 30Z','wings',g);path('M51 37 L59 45 L51 53 L43 45Z','hairAccent',g);}
 if(c.faceDetail==='stars')for(const x of [-44,44])star(x,28,8,'metal',head);
 if(c.glasses!=='none'){
  for(const sign of [-1,1]){const g=group(`scale(${sign} 1)`,head);if(c.glasses==='heart')path('M28 23 Q-3 0 13-10 Q25-17 28-6 Q34-19 47-9 Q61 5 28 23Z','accessory',g);else if(c.glasses==='round')node('circle',{cx:29,cy:7,r:22,fill:'none',stroke:mode==='outline'?'#000000':o.colors.accessory,'stroke-width':5},g);else {if(c.glasses==='sun')rect(9,-12,43,32,'eyes',g,8);else node('rect',{x:8,y:-12,width:44,height:35,rx:6,fill:'none',stroke:mode==='outline'?'#000000':o.colors.accessory,'stroke-width':5},g);} }
  line('M-7 3 Q0-3 7 3',head);
 }
 if(c.earrings!=='none')for(const x of [-75,75]){if(c.earrings==='stars')star(x,39,11,'metal',head);else if(c.earrings==='hoops')node('ellipse',{cx:x,cy:37,rx:10,ry:14,fill:'none',stroke:mode==='outline'?'#000000':o.colors.metal,'stroke-width':4},head);else ellipse(x,28,6,6,'metal',head);}
 if(c.hat==='headband'){rect(-69,-48,138,23,'accessory',head);rect(-29,-48,58,23,'metal',head);line('M-13-36 L0-43 L13-36 L0-29Z',head);path('M65-36 L103-24 L85-11 L65-25Z','accessory',head);}
 if(c.hat==='horns')for(const sign of [-1,1]){const g=group(`scale(${sign} 1)`,head);path('M36-66 Q30-98 56-123 Q47-94 66-72Z','horns',g);}
 if(c.hat==='foxmask'){const g=group('translate(58 -67) rotate(25) scale(.65)',head);path('M-43 13 L-51-61 L-19-37 Q0-46 19-37 L51-61 L43 13 L0 48Z','detail',g);path('M-34-4 L-9 7 L-28 13Z','accessory',g);path('M34-4 L9 7 L28 13Z','accessory',g);path('M-8 26 L8 26 L0 35Z','eyes',g);}
 if(c.headphones==='headset'){rect(65,-4,17,29,'accessory',head);line('M77 16 Q85 45 27 44',head);ellipse(25,44,9,5,'metal',head);}
 if(c.hat==='cap'){path('M-70-55 Q-65-116 0-105 Q66-110 70-55Z','accessory',head);path('M-67-54 Q-23-77 69-55 L93-42 Q20-34-67-54Z','detail',head);}
 if(c.hat==='beanie'){path('M-71-55 Q-76-127 0-117 Q76-127 71-55Z','accessory',head);rect(-73,-65,146,24,'detail',head,8);ellipse(0,-122,17,17,'accessory',head);}
 if(c.hat==='crown')path('M-51-72 L-58-113 L-25-95 L0-126 L25-95 L58-113 L51-72Z','metal',head);
 if(c.hat==='bow'){path('M10-69 Q-49-121-40-63 Q-28-39 10-69 Q59-120 61-67 Q46-39 10-69Z','accessory',head);ellipse(10,-69,10,10,'metal',head);}
 if(c.hat==='cat'){path('M-64-55 L-77-108 L-30-78 M64-55 L77-108 L30-78Z','accessory',head);}
 if(c.hat==='flower')for(let i=0;i<5;i++){const x=-48+i*24,y=-72-Math.sin(i*Math.PI/4)*11;ellipse(x,y,13,13,'accessory',head);ellipse(x,y,5,5,'metal',head);}
 if(c.hat==='beret')path('M-73-60 Q-101-114-19-119 Q78-137 76-72 L61-58Z','accessory',head);
 if(c.headphones==='overear'){node('path',{d:'M-78 9 Q-104-101 0-103 Q104-101 78 9',fill:'none',stroke:mode==='outline'?'#000000':o.colors.accessory,'stroke-width':10},head);rect(-89,-11,22,45,'accessory',head,10);rect(67,-11,22,45,'accessory',head,10);}
 // Hand-held items use the same wrist anchor as each pose.
 if(c.handheld!=='none'){const x=(c.pose==='wave'?107:c.pose==='hips'?61:83)*b.width,y=c.pose==='wave'?-99:c.pose==='hips'?49:89,g=group(`translate(${x} ${y})`,whole);
 if(c.handheld==='sword'){path('M-8-19 L-13-104 L0-132 L13-104 L8-19Z','wings',g);line('M0-119 L0-23',g);rect(-24,-20,48,9,'metal',g);rect(-6,-10,12,34,'accessory',g);star(0,-16,10,'metal',g);}
 if(c.handheld==='fan'){path('M0 9 L-55-45 Q0-94 55-45Z','accessory',g);for(const dx of [-40,-20,0,20,40])line(`M0 9 L${dx} ${-61+Math.abs(dx)*.25}`,g);ellipse(0,9,6,6,'metal',g);}
 if(c.handheld==='lightstick'){rect(-7,-30,14,51,'accessory',g);ellipse(0,-49,24,24,'wings',g);star(0,-49,16,'metal',g);}
 if(c.handheld==='orb'){ellipse(0,-27,28,28,'wings',g);path('M8-48 Q-22-36-9-13 Q-29-23-16-44Z','detail',g);star(9,-24,12,'metal',g);}
 if(c.handheld==='mic'){rect(-6,-31,12,47,'metal',g);ellipse(0,-37,14,17,'eyes',g);}
 if(c.handheld==='wand'){rect(-3,-42,6,65,'detail',g);star(0,-53,22,'metal',g);}
 if(c.handheld==='flower'){rect(-3,-35,6,59,'horns',g);for(let i=0;i<5;i++)ellipse(Math.cos(i*1.257)*13,-43+Math.sin(i*1.257)*13,10,10,'accessory',g);ellipse(0,-43,7,7,'metal',g);}
 if(c.handheld==='book'){rect(-23,-30,46,60,'accessory',g);line('M-14-28 L-14 29',g);star(6,0,11,'metal',g);}
 if(c.handheld==='ball'){ellipse(0,-9,27,27,'horns',g);line('M-26-9 L26-9 M0-35 Q17-9 0 17',g);}
 }
}
