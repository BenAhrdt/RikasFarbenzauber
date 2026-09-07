// Own vector library. Every asset has three separately colorable regions.
export const library={
 'poster-v1':['Anime-Poster','Deko','#b8a1dc','#f3dfbb','#e8a4c5'],
 'lightstick-v1':['Lightstick','Musik','#b8a1dc','#f3dfbb','#e8a4c5'],
 'stage-v1':['Bühnenpodest','Musik','#b8a1dc','#f3dfbb','#e8a4c5'],
 'spotlight-v1':['Bühnenscheinwerfer','Musik','#b8a1dc','#f3dfbb','#e8a4c5'],
 'keyboard-v1':['Keyboard','Musik','#b8a1dc','#f3dfbb','#e8a4c5'],
 'headphones-v1':['Kopfhörer','Musik','#b8a1dc','#f3dfbb','#e8a4c5'],
 'lantern-v1':['Papierlaterne','Deko','#b8a1dc','#f3dfbb','#e8a4c5'],
 'ramen-v1':['Ramen-Schale','Deko','#b8a1dc','#f3dfbb','#e8a4c5'],
 'catplush-v1':['Katzen-Plüschtier','Spielzeug','#b8a1dc','#f3dfbb','#e8a4c5'],
 'gamepad-v1':['Gamecontroller','Spielzeug','#b8a1dc','#f3dfbb','#e8a4c5'],
 'mirror-v1':['Schminkspiegel','Möbel','#b8a1dc','#f3dfbb','#e8a4c5'],
 'stringlights-v1':['Sternen-Lichterkette','Deko','#b8a1dc','#f3dfbb','#e8a4c5'],

 'sofa-v1':['Sofa','Möbel','#b3a1d3','#e9dff4','#786056'],
 'bed-v1':['Bett','Möbel','#a8c8d7','#f4dfb5','#947059'],
 'table-v1':['Tisch','Möbel','#ddb98f','#9c745b','#f0d3a0'],
 'shelf-v1':['Regal','Möbel','#cfac88','#a79ccd','#8caa93'],
 'rug-v1':['Teppich','Deko','#ecc2bd','#fff0cf','#b99ccc'],
 'lamp-v1':['Lampe','Deko','#edcc83','#89705b','#faf0c4'],
 'window-v1':['Fenster','Bauen','#b1d9e7','#eee2c6','#a99ac9'],
 'door-v1':['Tür','Bauen','#bba0d3','#f2d18a','#806447'],
 'house-v1':['Haus','Bauen','#f0d9b6','#ca8d96','#a0c7d9'],
 'castle-v1':['Schloss','Bauen','#d5c6e5','#a58ec8','#edd28d'],
 'tree-v1':['Baum','Natur','#a6bf8b','#947056','#d4dba3'],
 'flower-v1':['Blume','Natur','#dc9fc0','#8cac78','#f0ce80'],
 'cloud-v1':['Wolke','Natur','#ffffff','#c6dbea','#f3f7fb'],
 'rock-v1':['Stein','Natur','#b5b4be','#d5d2da','#9291a2'],
 'plant-v1':['Topfpflanze','Deko','#9cb68b','#d89e89','#c4d8a7'],
 'sun-v1':['Sonne','Natur','#f0cf78','#edb77d','#fff0b8'],
 'chair-v1':['Stuhl','Möbel','#bba5d5','#957153','#eddbb3'],
 'desk-v1':['Schreibtisch','Möbel','#dfbc96','#b2a1ce','#897158'],
 'pillow-v1':['Kissen','Deko','#dba8bc','#f6d5e1','#b59aca'],
 'clock-v1':['Uhr','Deko','#b2a1ce','#fff0cf','#66557c'],
 'books-v1':['Bücher','Deko','#a2c2ad','#dba0b0','#ebcd89'],
 'teddy-v1':['Teddybär','Spielzeug','#c19a78','#f3dbbb','#685347'],
 'guitar-v1':['Gitarre','Musik','#deaa79','#785c49','#e9d7b6'],
 'microphone-v1':['Mikrofon','Musik','#a396bd','#605970','#d6d0e0'],
 'speaker-v1':['Lautsprecher','Musik','#a7a2b6','#565062','#d8b0d3'],
 'skateboard-v1':['Skateboard','Spielzeug','#b6a1d4','#757183','#edcb86'],
 'balloon-v1':['Luftballon','Deko','#e7acc3','#b4a0d1','#fae3ed'],
 'ball-v1':['Ball','Spielzeug','#a3c5dc','#f3d58f','#ad97c8'],
 'mushroom-v1':['Pilz','Natur','#dba0ab','#efdec6','#fff3df'],
 'pond-v1':['Teich','Natur','#a0c9d8','#bfd5a4','#e9b0ca'],
 'tent-v1':['Zelt','Bauen','#b8b0d9','#f3d59b','#8b7ba6'],
 'bench-v1':['Bank','Möbel','#d3b58f','#917057','#bdd09c']
};
export function paintAsset(shape,asset){
 const rect=(x,y,width,height,part='main',rx=5)=>shape('rect',{x,y,width,height,rx},part);
 const path=(d,part='main')=>shape('path',{d},part);
 const ellipse=(cx,cy,rx,ry,part='main')=>shape('ellipse',{cx,cy,rx,ry},part);
 switch(asset){
 case 'poster-v1': rect(-62,-88,124,176,'detail');rect(-51,-77,102,154);ellipse(0,-23,27,33,'accent');path('M-38 56 L-28 13 L28 13 L38 56Z','accent');path('M-29-38 L-37-65 L-11-52 L4-74 L18-49 L35-60 L29-30Z','detail');break;
 case 'lightstick-v1': rect(-12,1,24,91,'detail');ellipse(0,-33,45,45);path('M0-67 L9-43 L34-43 L14-27 L21-2 L0-17 L-21-2 L-14-27 L-34-43 L-9-43Z','accent');break;
 case 'stage-v1': rect(-130,-15,260,64);ellipse(0,-15,130,32,'detail');for(const x of [-95,-48,0,48,95])ellipse(x,27,8,8,'accent');break;
 case 'spotlight-v1': path('M-8 18 L-55 99 L-41 103 L0 43 L41 103 L55 99 L8 18Z','detail');rect(-52,-67,104,89);ellipse(0,-26,39,34,'detail');ellipse(0,-26,28,24,'accent');break;
 case 'keyboard-v1': path('M-68 15 L54 100 L66 94 L-53 7Z','detail');path('M68 15 L-54 100 L-66 94 L53 7Z','detail');rect(-115,-48,230,66);rect(-104,-26,208,34,'accent');for(let x=-85;x<100;x+=21)rect(x,-26,9,20,'detail',0);break;
 case 'headphones-v1': path('M-63 27 L-63-28 Q-63-100 0-100 Q63-100 63-28 L63 27 L48 27 L48-28 Q48-83 0-83 Q-48-83-48-28 L-48 27Z','detail');rect(-73,-12,32,70);rect(41,-12,32,70);rect(-63,0,12,45,'accent');rect(51,0,12,45,'accent');break;
 case 'lantern-v1': rect(-3,-112,6,30,'detail');ellipse(0,-2,57,79);rect(-26,-85,52,13,'detail');rect(-26,73,52,13,'detail');path('M-17-62 Q-41 0-17 60 M17-62 Q41 0 17 60','accent');rect(-3,86,6,25,'accent');break;
 case 'ramen-v1': path('M-77-12 Q-62 73 0 74 Q62 73 77-12Z');ellipse(0,-12,77,24,'detail');ellipse(-22,-11,21,13,'accent');ellipse(-22,-11,9,7);path('M5-16 Q17-34 25-10 Q35 9 44-13','accent');path('M22-23 L61-91 L67-87 L30-20Z','detail');path('M39-18 L84-80 L90-76 L46-15Z','detail');break;
 case 'catplush-v1': ellipse(0,35,48,56);ellipse(-34,74,22,14,'detail');ellipse(34,74,22,14,'detail');path('M-49-19 L-56-83 L-22-58 Q0-69 22-58 L56-83 L49-19Z');ellipse(0,-18,52,43);ellipse(-20,-22,5,8,'accent');ellipse(20,-22,5,8,'accent');path('M-6-5 L6-5 L0 2Z','accent');ellipse(0,37,25,31,'detail');break;
 case 'gamepad-v1': path('M-58-35 Q-30-47-19-27 L19-27 Q30-47 58-35 Q82-11 79 35 Q70 59 43 26 L-43 26 Q-70 59-79 35 Q-82-11-58-35Z');rect(-50,-19,10,34,'detail');rect(-62,-7,34,10,'detail');ellipse(42,-12,7,7,'accent');ellipse(57,3,7,7,'accent');ellipse(18,13,10,10,'detail');break;
 case 'mirror-v1': rect(-6,42,12,49,'detail');ellipse(0,92,51,10,'detail');ellipse(0,-18,66,83);ellipse(0,-18,49,66,'accent');for(const [x,y]of [[0,-91],[-53,-52],[53,-52],[-54,16],[54,16],[0,54]])ellipse(x,y,6,6,'detail');path('M-25-38 L10-67 L17-59 L-18-30Z','detail');break;
 case 'stringlights-v1': path('M-125-35 Q0 43 125-35 L125-30 Q0 48-125-30Z','detail');for(const [x,y]of [[-100,-12],[-50,7],[0,14],[50,7],[100,-12]])path(`M${x} ${y} l6 13 15 1 -11 10 3 15 -13-8 -13 8 3-15 -11-10 15-1Z`,'accent');break;

 case 'chair-v1': rect(-42,-92,84,94);rect(-51,-3,102,22,'detail');rect(-43,17,14,75,'detail');rect(29,17,14,75,'detail');rect(-28,-72,56,49,'accent');break;
 case 'desk-v1': rect(-105,-28,210,20);rect(-92,-8,60,98,'detail');rect(76,-8,15,98,'accent');rect(-84,3,44,32);rect(-84,44,44,32);ellipse(-62,18,4,4,'accent');ellipse(-62,60,4,4,'accent');break;
 case 'pillow-v1': path('M-68-50 Q0-39 68-50 Q55 0 68 50 Q0 39-68 50 Q-55 0-68-50Z');ellipse(0,0,24,20,'detail');path('M-12 0 L0-13 L12 0 L0 13Z','accent');break;
 case 'clock-v1': ellipse(0,0,72,72);ellipse(0,0,58,58,'detail');path('M-4-39 L4-39 L4-2 L31 18 L26 24 L-4 4Z','accent');for(const [x,y]of [[0,-47],[47,0],[0,47],[-47,0]])ellipse(x,y,3,3,'accent');break;
 case 'books-v1': rect(-63,-30,126,25);rect(-55,-1,116,25,'detail');rect(-67,28,127,25,'accent');rect(-40,-25,88,15,'accent');break;
 case 'teddy-v1': ellipse(-36,-66,22,23);ellipse(36,-66,22,23);ellipse(0,19,49,65);ellipse(-43,64,25,22);ellipse(43,64,25,22);ellipse(-47,-1,18,30);ellipse(47,-1,18,30);ellipse(0,-41,48,44);ellipse(0,-25,24,17,'detail');ellipse(-16,-45,5,7,'accent');ellipse(16,-45,5,7,'accent');ellipse(0,-28,7,5,'accent');ellipse(0,20,27,33,'detail');break;
 case 'guitar-v1': path('M-20-20 Q-64-29-51 13 Q-85 54-43 79 Q0 108 43 79 Q85 54 51 13 Q64-29 20-20Z');rect(-12,-124,24,125,'detail');rect(-19,-142,38,35,'detail');ellipse(0,26,21,21,'detail');rect(-23,58,46,8,'accent');for(const x of [-5,0,5])rect(x,-112,1,170,'accent');break;
 case 'microphone-v1': rect(-6,-37,12,140,'detail');ellipse(0,105,53,10,'detail');rect(-20,-71,40,69);ellipse(0,-72,20,20,'detail');rect(-15,-49,30,6,'accent');break;
 case 'speaker-v1': rect(-55,-95,110,190);ellipse(0,-45,29,29,'detail');ellipse(0,40,43,43,'detail');ellipse(0,-45,12,12,'accent');ellipse(0,40,19,19,'accent');break;
 case 'skateboard-v1': ellipse(-62,30,15,15,'detail');ellipse(62,30,15,15,'detail');rect(-103,-8,206,28,'main',14);path('M-25 6 L0-5 L25 6 L0 16Z','accent');break;
 case 'balloon-v1': path('M0 20 Q-25 69 0 108 Q22 147 0 163Z','detail');ellipse(0,-35,49,64);ellipse(-17,-55,9,20,'accent');path('M0 27 L-9 39 L9 39Z');break;
 case 'ball-v1': ellipse(0,0,58,58);path('M-58 0 Q0-35 58 0 Q0 35-58 0Z','detail');path('M0-58 Q-29 0 0 58 Q29 0 0-58Z','accent');break;
 case 'mushroom-v1': path('M-23-5 L23-5 L34 77 Q0 94-34 77Z','detail');path('M-90 1 Q-70-110 0-95 Q70-110 90 1 Q0 30-90 1Z');ellipse(-39,-30,14,12,'accent');ellipse(9,-61,18,14,'accent');ellipse(47,-20,11,10,'accent');break;
 case 'pond-v1': ellipse(0,0,126,61);ellipse(-43,-10,32,18,'detail');ellipse(57,19,29,15,'detail');ellipse(-44,-14,12,9,'accent');break;
 case 'tent-v1': path('M-132 86 L-16-113 L132 86Z');path('M-16-113 L21-92 L132 86 L55 86Z','detail');path('M-78 86 L-16-34 L39 86Z','accent');break;
 case 'bench-v1': rect(-105,-65,210,22);rect(-105,-33,210,22);rect(-115,1,230,23);rect(-90,24,17,60,'detail');rect(73,24,17,60,'detail');rect(-90,-80,12,81,'detail');rect(78,-80,12,81,'detail');break;
 case 'sofa-v1': rect(-85,-55,170,78);rect(-92,12,184,43,'detail');rect(-108,-15,28,75);rect(80,-15,28,75);rect(-80,55,16,18,'accent');rect(64,55,16,18,'accent');rect(-68,-40,60,44,'detail');rect(8,-40,60,44,'detail');break;
 case 'bed-v1': rect(-105,-55,22,120,'accent');rect(83,-15,22,80,'accent');rect(-88,-20,176,65);rect(-80,-42,57,35,'detail');rect(-20,-20,102,60,'main');break;
 case 'table-v1': rect(-80,0,15,80,'detail');rect(65,0,15,80,'detail');rect(-100,-25,200,30);rect(-85,-20,170,8,'accent');break;
 case 'shelf-v1': rect(-70,-105,140,210);rect(-56,-90,112,70,'detail');rect(-56,-5,112,90,'detail');for(let i=0;i<4;i++)rect(-47+i*23,-73,17,53,i%2?'accent':'main');rect(-45,30,85,46,'accent');break;
 case 'rug-v1': ellipse(0,0,125,48);ellipse(0,0,98,32,'detail');path('M-40 0 L0-21 L40 0 L0 21Z','accent');break;
 case 'lamp-v1': rect(-6,-30,12,115,'detail');ellipse(0,85,42,10,'detail');path('M-35-100 L35-100 L60-25 L-60-25Z');ellipse(0,-25,59,10,'accent');break;
 case 'window-v1': rect(-70,-80,140,160,'detail');rect(-58,-68,116,136);rect(-5,-68,10,136,'detail',0);rect(-58,-5,116,10,'detail',0);path('M-85-90 L-45-90 L-62 60 L-85 75Z','accent');path('M85-90 L45-90 L62 60 L85 75Z','accent');break;
 case 'door-v1': rect(-60,-110,120,220,'accent');rect(-49,-98,98,208);rect(-33,-80,66,76,'detail');ellipse(28,27,7,7,'detail');break;
 case 'house-v1': rect(-105,-30,210,145);path('M-130-30 L0-140 L130-30Z','detail');rect(-23,38,46,77,'detail');rect(-83,0,43,44,'accent');rect(40,0,43,44,'accent');break;
 case 'castle-v1': rect(-80,-35,160,150);rect(-125,-85,55,200);rect(70,-85,55,200);path('M-138-85 L-97-160 L-57-85Z','detail');path('M57-85 L97-160 L138-85Z','detail');path('M-30 115 L-30 50 Q0 10 30 50 L30 115Z','accent');rect(-108,-55,20,35,'accent');rect(88,-55,20,35,'accent');break;
 case 'tree-v1': path('M-18 100 L-12-45 L12-45 L18 100Z','detail');ellipse(-38,-52,57,62);ellipse(37,-55,57,62);ellipse(0,-99,60,62,'accent');break;
 case 'flower-v1': rect(-5,-10,10,105,'detail');ellipse(-22,50,25,12,'detail');ellipse(23,30,25,12,'detail');for(let i=0;i<6;i++){const a=i*Math.PI/3;ellipse(Math.cos(a)*27,Math.sin(a)*27-30,20,20);}ellipse(0,-30,18,18,'accent');break;
 case 'cloud-v1': path('M-85 20 Q-120-20-65-35 Q-52-91-6-55 Q40-100 68-45 Q122-40 93 20Z');ellipse(-35,-12,17,6,'detail');ellipse(40,0,14,5,'accent');break;
 case 'rock-v1': path('M-70 40 L-82 10 L-35-55 L35-45 L76 12 L58 40Z');path('M-35-55 L-10 10 L-70 40Z','detail');path('M-10 10 L35-45 L76 12Z','accent');break;
 case 'plant-v1': path('M0 20 Q-72-1-51-66 Q-1-57 0 20Z');path('M0 20 Q-8-70 48-85 Q73-17 0 20Z','accent');path('M-40 12 L40 12 L28 85 L-28 85Z','detail');break;
 case 'sun-v1': for(let i=0;i<8;i++){const a=i*Math.PI/4;ellipse(Math.cos(a)*76,Math.sin(a)*76,10,10,'detail');}ellipse(0,0,52,52);ellipse(-17,-9,5,8,'accent');ellipse(17,-9,5,8,'accent');path('M-15 19 Q0 35 15 19Z','accent');break;
 }
}
export const uid=()=>Array.from(crypto.getRandomValues(new Uint8Array(16)),b=>b.toString(16).padStart(2,'0')).join('');
export function object(asset,x=450,y=360){const a=library[asset];return {id:uid(),asset,x,y,scale:1,rotation:0,flipped:false,variant:0,colors:{main:a[2],detail:a[3],accent:a[4]}};}
export function spaceDocument(kind){return {version:2,canvas:{width:900,height:650,background:kind==='room'?'#f3e8df':'#dceef6',ground:kind==='room'?'#dcc5b1':'#c3d5a6'},objects:[]};}
export function template(name){const doc=spaceDocument(name==='room'?'room':'world');const sets={room:[['rug-v1',440,515],['window-v1',260,200],['shelf-v1',730,350],['sofa-v1',430,400],['plant-v1',150,445]],house:[['cloud-v1',230,110],['house-v1',450,380],['tree-v1',180,400],['flower-v1',680,495]],garden:[['sun-v1',710,115],['tree-v1',200,340],['flower-v1',500,455],['flower-v1',620,490],['rock-v1',760,470]],castle:[['cloud-v1',220,90],['castle-v1',470,370],['tree-v1',180,420],['flower-v1',720,490]]};doc.objects=(sets[name]||[]).map(([a,x,y])=>object(a,x,y));return doc;}
