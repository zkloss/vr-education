const asiaData=__ASIA_DATA__;
let asiaView=null,atlasSurfacePromise=null;
function warmAtlasSurface(){return atlasSurfacePromise||(atlasSurfacePromise=new THREE.TextureLoader().loadAsync('__DAY_TERRAIN__'));}
async function initAsiaTerrain(){
 const buildStarted=performance.now();
 let lastBuildYield=performance.now();const yieldBuild=async()=>{if(performance.now()-lastBuildYield>10){await new Promise(r=>setTimeout(r,0));lastBuildYield=performance.now();}};
 const d=asiaData,unpack=s=>{const raw=atob(s),bytes=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);return bytes},h=new Uint16Array(unpack(d.height).buffer),land=unpack(d.land),ch=unpack(d.china),soft=unpack(d.chinaSoft),W=d.w,H=d.h,[L,B,R,T]=d.bounds;
 const sceneA=new THREE.Scene();sceneA.background=new THREE.Color('#101b25');sceneA.fog=new THREE.FogExp2('#101b25',.012);
 const rr=new THREE.WebGLRenderer({antialias:true});rr.setPixelRatio(Math.min(devicePixelRatio,1.65));rr.setSize(innerWidth,innerHeight);rr.outputColorSpace=THREE.SRGBColorSpace;rr.toneMapping=THREE.ACESFilmicToneMapping;rr.toneMappingExposure=1.06;rr.shadowMap.enabled=true;rr.shadowMap.type=THREE.PCFSoftShadowMap;document.getElementById('asiaMapMount').append(rr.domElement);
 const ca=new THREE.PerspectiveCamera(36,innerWidth/innerHeight,.1,160);
 sceneA.add(new THREE.HemisphereLight(0xdce8ec,0x151f27,.76));
 const key=new THREE.DirectionalLight(0xeaf1f5,2.35);key.position.set(-8,6,-5);key.castShadow=true;key.shadow.mapSize.set(1024,1024);Object.assign(key.shadow.camera,{left:-13,right:13,top:12,bottom:-12,near:1,far:40});key.shadow.normalBias=.025;key.shadow.bias=-.0001;key.shadow.radius=4;sceneA.add(key);
 const fill=new THREE.DirectionalLight(0x9cc9ed,.35);fill.position.set(6,7,5);sceneA.add(fill);
 const xy=(lon,lat)=>[(lon-100)*.156,(35-lat)*.18];
 const elevation=i=>Math.pow(Math.max(0,(h[i]/256-19)/236),1.0)*.70+(land[i]>127?.009:0)+soft[i]/255*.045;
 const at=(lon,lat,lift=.008)=>{const x=THREE.MathUtils.clamp((lon-L)/(R-L)*(W-1),0,W-1.001),y=THREE.MathUtils.clamp((T-lat)/(T-B)*(H-1),0,H-1.001),ix=Math.floor(x),iy=Math.floor(y),fx=x-ix,fy=y-iy,i=iy*W+ix,p=xy(lon,lat);return new THREE.Vector3(p[0],(THREE.MathUtils.lerp(THREE.MathUtils.lerp(elevation(i),elevation(i+1),fx),THREE.MathUtils.lerp(elevation(i+W),elevation(i+W+1),fx),fy))+lift,p[1])};
 const verts=new Float32Array(W*H*3),colors=new Float32Array(W*H*3),uvs=new Float32Array(W*H*2),indices=new Uint32Array((W-1)*(H-1)*6);let indexCount=0;
 // The same equirectangular day surface used for the globe, registered by longitude and latitude.
 const surfaceTexture=await warmAtlasSurface();surfaceTexture.colorSpace=THREE.SRGBColorSpace;surfaceTexture.anisotropy=Math.min(rr.capabilities.getMaxAnisotropy(),8);
 surfaceTexture.repeat.set((R-L)/360,(T-B)/180);surfaceTexture.offset.set((L+180)/360,(B+90)/180);
 for(let y=0;y<H;y++){if(y%12===0)await yieldBuild();for(let x=0;x<W;x++){
  const i=y*W+x,isChina=ch[i]>127,j=i*3,k=i*2;
  verts[j]=(L+x/(W-1)*(R-L)-100)*.156;verts[j+1]=elevation(i);verts[j+2]=(35-T+y/(H-1)*(T-B))*.18;uvs[k]=x/(W-1);uvs[k+1]=1-y/(H-1);
  let c=isChina?.98:.43;
  if(x>5&&x<W-6&&y>5&&y<H-6){const local=(h[i-5]+h[i+5]+h[i-W*5]+h[i+W*5])*.25;c*=THREE.MathUtils.clamp(1+(h[i]-local)/65535*3,.92,1.03);}colors[j]=colors[j+1]=colors[j+2]=c;
 }
 }
 for(let y=0;y<H-1;y++){if(y%32===0)await yieldBuild();for(let x=0;x<W-1;x++){const i=y*W+x;if(land[i]>127||land[i+W]>127||land[i+1]>127){indices[indexCount++]=i;indices[indexCount++]=i+W;indices[indexCount++]=i+1;}if(land[i+1]>127||land[i+W]>127||land[i+W+1]>127){indices[indexCount++]=i+1;indices[indexCount++]=i+W;indices[indexCount++]=i+W+1;}}
 }
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(verts,3));g.setAttribute('color',new THREE.BufferAttribute(colors,3));g.setAttribute('uv',new THREE.BufferAttribute(uvs,2));g.setIndex(new THREE.BufferAttribute(indices.subarray(0,indexCount),1));
 if(d.bakedNormals){const n=new Int16Array(unpack(d.bakedNormals).buffer),nf=new Float32Array(n.length);for(let i=0;i<n.length;i++)nf[i]=n[i]/32767;g.setAttribute('normal',new THREE.BufferAttribute(nf,3));}else g.computeVertexNormals();
 const mat=new THREE.MeshStandardMaterial({map:surfaceTexture,vertexColors:true,roughness:.90,metalness:0,transparent:true});
 mat.onBeforeCompile=sh=>{sh.vertexShader='varying vec2 atlasUV;\n'+sh.vertexShader;sh.vertexShader=sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n atlasUV=uv;');sh.fragmentShader='varying vec2 atlasUV;\n'+sh.fragmentShader;sh.fragmentShader=sh.fragmentShader.replace('#include <color_fragment>','#include <color_fragment>\n vec2 edge=min(atlasUV,1.0-atlasUV);diffuseColor.a*=smoothstep(0.0,.06,min(edge.x,edge.y));');};
 const bumpImg=new Image();bumpImg.src=d.bump;
 const bumpTex=new THREE.Texture(bumpImg);bumpImg.onload=()=>{bumpTex.needsUpdate=true};
 mat.bumpMap=bumpTex;mat.bumpScale=.002;
 const terrain=new THREE.Mesh(g,mat);terrain.castShadow=false;terrain.receiveShadow=true;sceneA.add(terrain);
 const ocean=new THREE.Mesh(new THREE.PlaneGeometry(220,220),new THREE.MeshStandardMaterial({color:0x17375d,emissive:0x031221,emissiveIntensity:.12,roughness:.55,metalness:.04}));ocean.rotation.x=-Math.PI/2;ocean.position.y=-.012;ocean.receiveShadow=false;sceneA.add(ocean);
 ocean.material.onBeforeCompile=sh=>{sh.vertexShader='varying vec3 seaPos;\n'+sh.vertexShader;sh.vertexShader=sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n seaPos=(modelMatrix*vec4(position,1.)).xyz;');sh.fragmentShader='varying vec3 seaPos;\n'+sh.fragmentShader;sh.fragmentShader=sh.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
 float ripple=sin(seaPos.x*58.+sin(seaPos.z*3.))*sin(seaPos.z*83.+seaPos.x*5.);float broad=sin(seaPos.x*.32+seaPos.z*.3);diffuseColor.rgb*=.96+broad*.035+ripple*.006;
 float reflection=exp(-pow((seaPos.x+seaPos.z*.55+5.)/5.,2.))*(1.-smoothstep(-9.,5.,seaPos.z));
 diffuseColor.rgb+=vec3(.055,.075,.085)*reflection;
 `);};
 function lines(arr,color,alpha){const pts=[];for(const ring of arr)for(let j=1;j<ring.length;j++){const a=ring[j-1],b=ring[j];if(a[0]<L||a[0]>R||b[0]<L||b[0]>R||a[1]<B||a[1]>T||b[1]<B||b[1]>T)continue;const n=Math.max(1,Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/.07));for(let k=0;k<n;k++)for(const t of [k/n,(k+1)/n]){const p=at(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t);pts.push(p.x,p.y,p.z);}}const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(pts,3));const line=new THREE.LineSegments(geo,new THREE.LineBasicMaterial({color,transparent:true,opacity:alpha,depthWrite:false}));sceneA.add(line);return line;}
 lines(d.outline,0xdce8db,.48);
 lines(d.rivers.filter(r=>r.line.some(p=>p[0]>75&&p[0]<135&&p[1]>20&&p[1]<50)).map(r=>r.line),0x3a80bb,.55);
 const rivers=lines(d.rivers.filter(r=>r.name==='Yangtze'||r.name==='Huang').map(r=>r.line),0x5098c8,.80);rivers.renderOrder=8;rivers.material.depthTest=true;
 const riverMeshes=[],waterVerts=[],waterIndices=[];
 for(const river of d.rivers){if(!river.line.some(p=>p[0]>74&&p[0]<135&&p[1]>18&&p[1]<54))continue;
  const pts=[];for(let j=1;j<river.line.length;j++){const a=river.line[j-1],b=river.line[j],steps=Math.max(1,Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/.045));for(let k=0;k<steps;k++){const t=k/steps,lon=a[0]+(b[0]-a[0])*t,lat=a[1]+(b[1]-a[1])*t;if(lon>=74&&lon<=135&&lat>=18&&lat<=54)pts.push(at(lon,lat,.007));}}
  if(pts.length<2)continue;const v=[],ids=[],width=['Yangtze','Huang'].includes(river.name)?.012:.006;
  for(let j=0;j<pts.length;j++){const dir=pts[Math.min(j+1,pts.length-1)].clone().sub(pts[Math.max(j-1,0)]),side=new THREE.Vector3(-dir.z,0,dir.x).normalize().multiplyScalar(width/2);for(const sign of [-1,1]){const p=pts[j].clone().addScaledVector(side,sign);v.push(p.x,p.y,p.z)}if(j){const i=j*2;ids.push(i-2,i-1,i,i-1,i+1,i)}}
  const base=waterVerts.length/3;for(const x of v)waterVerts.push(x);for(const x of ids)waterIndices.push(x+base);riverMeshes.push(river.name);
 }
 const rg=new THREE.BufferGeometry();rg.setAttribute('position',new THREE.Float32BufferAttribute(waterVerts,3));rg.setIndex(waterIndices);rg.computeVertexNormals();sceneA.add(new THREE.Mesh(rg,new THREE.MeshStandardMaterial({color:0x286d99,emissive:0x08263e,emissiveIntensity:.12,roughness:.32,metalness:.05,side:THREE.DoubleSide,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2})));
 const leaderLayer=document.createElementNS('http://www.w3.org/2000/svg','svg');leaderLayer.classList.add('atlasLeaders');leaderLayer.setAttribute('aria-hidden','true');nextScene.append(leaderLayer);
 const labels=[];function label(text,lon,lat,type='mountain'){const el=document.createElement('div');el.className='mapLabel '+type;if(type==='city')el.innerHTML='<span class=cityIcon>▥</span><span><strong>'+text+'</strong><small>城市地标 · 阅江楼</small></span>';else el.textContent=text;nextScene.append(el);labels.push({el,p:at(lon,lat,type==='city'?.46:.075)});}
 label('昆仑山',85,36);label('祁连山',98,38);label('秦岭',108,34);label('横断山',99,29);label('大兴安岭',122,48);label('南岭',112,25);label('喜马拉雅山脉',85,28);label('天山',83,43);label('青藏高原',92,33);label('长江',111,30,'river');label('黄河',109,37,'river');
 // Five-star flag: 3:2 ratio and the four small stars face the large star.
 const fc=document.createElement('canvas');fc.width=600;fc.height=400;const ctx=fc.getContext('2d');ctx.fillStyle='#de2910';ctx.fillRect(0,0,600,400);ctx.fillStyle='#ffde00';function star(cx,cy,r,ang){ctx.beginPath();for(let i=0;i<10;i++){const a=ang+i*Math.PI/5,rad=i%2?r*.381966:r;const x=cx+Math.cos(a)*rad,y=cy+Math.sin(a)*rad;i?ctx.lineTo(x,y):ctx.moveTo(x,y)}ctx.closePath();ctx.fill()}star(100,100,60,-Math.PI/2);for(const [x,y] of [[200,40],[240,80],[240,140],[200,180]])star(x,y,20,Math.atan2(100-y,100-x));
 const flagTexture=new THREE.CanvasTexture(fc);flagTexture.colorSpace=THREE.SRGBColorSpace;const flagBase=at(116.4,39.9,.02),pole=new THREE.Mesh(new THREE.CylinderGeometry(.014,.021,1.75,16),new THREE.MeshStandardMaterial({color:0x8f9eaa,metalness:.7,roughness:.35}));const flagRig=new THREE.Group();flagRig.position.copy(flagBase);pole.position.set(0,.875,0);pole.castShadow=false;pole.material.transparent=true;pole.material.depthTest=false;pole.material.depthWrite=false;pole.frustumCulled=false;pole.renderOrder=30;sceneA.add(pole);
 const fg=new THREE.PlaneGeometry(1.05,.7,28,14),flag=new THREE.Mesh(fg,new THREE.MeshBasicMaterial({map:flagTexture,side:THREE.DoubleSide,vertexColors:true}));fg.setAttribute('color',new THREE.Float32BufferAttribute(new Float32Array(fg.attributes.position.count*3).fill(1),3));flag.position.set(.54,1.40,0);flag.castShadow=false;flag.material.transparent=true;flag.material.depthTest=false;flag.material.depthWrite=false;flag.frustumCulled=false;flag.renderOrder=31;sceneA.add(flag);

 const defaults={yaw:-.20,pitch:.69,distance:14.6},control={...defaults},target=new THREE.Vector3(.3,.15,-.2);
 const nodeData=__CITY_MODELS__,nodeObjects=[];let selectedNode='nanjing';
 function nodeLabel(node){
  const el=document.createElement('button');el.className='mapLabel city atlasNode';el.type='button';el.title=(node.location||node.name)+' · '+(node.site||node.building);el.innerHTML='<span class="cityIcon">'+String(node.eventIndex+1).padStart(2,'0')+'</span><span class="eventLabel"><strong>'+node.name+'</strong><small>'+node.event+'</small></span>';el.onclick=e=>{e.stopPropagation();focusNode(node.id)};nextScene.append(el);const line=document.createElementNS(leaderLayer.namespaceURI,'line'),dot=document.createElementNS(leaderLayer.namespaceURI,'circle');dot.setAttribute('r','3');leaderLayer.append(line,dot);labels.push({el,p:at(node.lon,node.lat,.035),node,line,dot});return el;
 }
 // A marker belongs to exactly one event, even within the same city.
 for(const node of nodeData)nodeObjects.push({node,el:nodeLabel(node)});
 const chapters=nodeData.map(node=>({name:node.event,years:node.chapter.split(' · ').at(-1),nodes:[node.id],place:node.name}));
 let selectedChapter=0;
 const sidebar=document.createElement('aside');sidebar.className='historySidebar';sidebar.innerHTML='<header class="sidebarHeading"><small>事件总览</small><h1>山河之间 · 抗战</h1><p>1931—1945</p></header><nav class="chapterList" aria-label="事件目录"></nav>';
 const card=document.querySelector('.exploreCard');nextScene.append(sidebar);const chapterMedia=document.createElement('section');chapterMedia.className='chapterMedia';chapterMedia.setAttribute('aria-label','章节图片展示区域');sidebar.append(chapterMedia,card);
 const chapterArt=__CHAPTER_ART__;
 chapterMedia.innerHTML='<button class="chapterPicture" aria-label="放大章节插画"><img alt=""><span>放大查看 ↗</span></button><div class="chapterCaption" aria-live="polite"><strong></strong><p></p><small>AI 历史情境插画 · 非史料照片</small><button class="chapterEnter" title="查看对应事件图文">查看事件 →</button></div>';
 chapterMedia.querySelector('.chapterEnter').onclick=()=>{if(chapters[selectedChapter].nodes[0]==='nanjing_surrender')window.openNanjingImmersive();else window.openAtlasBookChapter?.(selectedChapter);};
 const artImage=chapterMedia.querySelector('img'),artButton=chapterMedia.querySelector('button');
 artImage.decoding='async';
 const preparedArt=chapterArt.map(art=>{const img=new Image();img.decoding='async';img.src=art.previewSrc||art.src;return img;});
 const artWarm={decoded:0,total:chapterArt.length};

 const artDialog=document.createElement('dialog');artDialog.className='chapterArtDialog';artDialog.setAttribute('aria-label','章节历史情境插画');
 artDialog.innerHTML='<header><div><b></b><p></p></div><button aria-label="关闭章节插画">关闭 ×</button></header><img alt=""><footer>AI 历史情境插画 · 用于概括章节事件，非史料照片或精确现场复原</footer>';
 document.body.append(artDialog);artDialog.querySelector('button').onclick=()=>artDialog.close();artDialog.onclick=e=>{if(e.target===artDialog)artDialog.close();};
 let mediaOpen=false,mediaTurn=0,mediaAnimation=null;
 chapterMedia.setAttribute('aria-hidden','true');chapterMedia.inert=true;
 function dismissEventCard(){
  ++mediaTurn;mediaAnimation?.cancel();mediaAnimation=null;mediaOpen=false;
  chapterMedia.classList.remove('eventOpen');chapterMedia.setAttribute('aria-hidden','true');chapterMedia.inert=true;
 }
 function showChapterArt(reveal=true){
  const index=selectedChapter,art=chapterArt[index],chapter=chapters[index];if(!art)return;
  const ticket=++mediaTurn,wasOpen=mediaOpen,changed=chapterMedia.dataset.chapter!==String(index+1);
  mediaAnimation?.cancel();mediaAnimation=null;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  function commit(){
   if(ticket!==mediaTurn)return;
   chapterMedia.dataset.chapter=String(index+1);artImage.src=art.previewSrc||art.src;artImage.alt=art.alt;
   artButton.setAttribute('aria-label','放大第'+(index+1)+'个事件插画：'+chapter.name);
   chapterMedia.querySelector('.chapterCaption strong').textContent=chapter.name+' · '+chapter.years;
   chapterMedia.querySelector('.chapterCaption p').textContent=art.summary;
   if(!reveal)return;
   mediaOpen=true;chapterMedia.inert=false;chapterMedia.setAttribute('aria-hidden','false');chapterMedia.classList.add('eventOpen');
   if(!reduced)mediaAnimation=chapterMedia.animate([
    {opacity:0,transform:'translateX(-16px) translateY(5px) scale(.985)'},
    {opacity:1,transform:'translateX(0) translateY(0) scale(1)'}
   ],{duration:340,easing:'cubic-bezier(.2,.7,.25,1)'});
  }
  if(wasOpen&&changed&&!reduced){
   mediaAnimation=chapterMedia.animate([{opacity:1,transform:'translateX(0)'},{opacity:0,transform:'translateX(8px)'}],{duration:100,easing:'ease-out',fill:'forwards'});
   const outgoing=mediaAnimation;outgoing.finished.then(()=>{if(ticket===mediaTurn){outgoing.cancel();commit();}}).catch(()=>{});
  }else commit();
 }
 artButton.onclick=()=>{const art=chapterArt[selectedChapter];artDialog.querySelector('img').src=art.src;artDialog.querySelector('img').alt=art.alt;artDialog.querySelector('b').textContent=chapters[selectedChapter].name+' · '+chapters[selectedChapter].years;artDialog.querySelector('header p').textContent=art.summary;artDialog.showModal();};
 window.setAtlasChapterImage=(src,alt='')=>{if(src){artImage.src=src;artImage.alt=alt;}};
 const chapterList=sidebar.querySelector('.chapterList');chapters.forEach((chapter,index)=>{const b=document.createElement('button');b.className='chapterRow';b.innerHTML='<span class="chapterNum">'+String(index+1).padStart(2,'0')+'</span><strong>'+chapter.name+'</strong><time>'+chapter.years+'</time>';const thumb=new Image();thumb.className='chapterThumb';thumb.src=chapterArt[index].previewSrc||chapterArt[index].src;thumb.alt='';thumb.width=42;thumb.height=24;thumb.decoding='async';b.querySelector('.chapterNum').after(thumb);b.title=chapter.name+'：'+chapterArt[index].summary;b.onclick=()=>{selectedChapter=index;focusNode(chapter.nodes[0]);};chapterList.append(b);});
 card.innerHTML='<div class="modelPicker"><span>城市地标</span><select aria-label="切换地标"></select></div><div class="cardArt modelStage" aria-label="地标三维自动旋转展示"><button class="modelZoom" aria-expanded="false">放大查看</button><button class="modelSpin" aria-pressed="true">暂停旋转</button></div><div class="cardText"><span class="modelSiteBadge" hidden></span><h2></h2><p class="nodeChapter"></p><p class="nodeNote"></p></div>';
 const stage=card.querySelector('.modelStage'),previewScene=new THREE.Scene();
 const previewRenderer=new THREE.WebGLRenderer({antialias:true,alpha:true});previewRenderer.setPixelRatio(Math.min(Math.max(devicePixelRatio,2.5),3));previewRenderer.outputColorSpace=THREE.SRGBColorSpace;previewRenderer.toneMapping=THREE.ACESFilmicToneMapping;previewRenderer.toneMappingExposure=1.05;stage.prepend(previewRenderer.domElement);
 const previewCamera=new THREE.PerspectiveCamera(32,1,.01,100);
 previewScene.add(new THREE.HemisphereLight(0xe5f4ff,0x293540,1.15));
 const previewKey=new THREE.DirectionalLight(0xffedcf,2.5);previewKey.position.set(3,5,4);previewScene.add(previewKey);
 const previewFill=new THREE.DirectionalLight(0xb0dfff,.8);previewFill.position.set(-4,2,-3);previewScene.add(previewFill);
 const modelCache=new Map(),preview={renderer:previewRenderer,scene:previewScene,camera:previewCamera,stage,group:null,spinning:true,elapsed:0};
 function sizePreview(){const w=stage.clientWidth,h=stage.clientHeight;if(w<1||h<1||(preview.width===w&&preview.height===h))return;preview.width=w;preview.height=h;previewRenderer.setSize(w,h,false);previewCamera.aspect=w/h;const distance=Math.max(3.9,4.65/previewCamera.aspect);previewCamera.position.set(0,distance/3.9,distance);previewCamera.lookAt(0,0,0);previewCamera.updateProjectionMatrix();}
 new ResizeObserver(sizePreview).observe(stage);sizePreview();

 // Shared material maps: deterministic seamless color, height and roughness maps.
 const surfaceMaps=new Map();
 function surfaceFor(name){
  const kind=/roof|glazed|eaves/.test(name)?'tile':/timber|wood|lattice/.test(name)?'wood':/gold/.test(name)?'gold':/brick|plaster/.test(name)?'brick':/stone|terrace|balustrade/.test(name)?'stone':'plain';
  if(kind==='plain')return {roughness:.7};
  if(surfaceMaps.has(kind))return surfaceMaps.get(kind);
  const N=1024,color=document.createElement('canvas'),height=document.createElement('canvas');color.width=color.height=height.width=height.height=N;
  const c=color.getContext('2d'),h=height.getContext('2d');c.fillStyle='#dddddd';c.fillRect(0,0,N,N);h.fillStyle='#aaa';h.fillRect(0,0,N,N);
  let seed=741;const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  if(kind==='brick'||kind==='stone'||kind==='tile'){
   const rows=kind==='brick'?16:kind==='stone'?8:8,cols=kind==='brick'?4:kind==='stone'?3:16,w=N/cols,v=N/rows;
   c.fillStyle=kind==='tile'?'#737373':'#818181';c.fillRect(0,0,N,N);h.fillStyle='#303030';h.fillRect(0,0,N,N);
   for(let row=0;row<rows;row++)for(let col=-1;col<=cols;col++){
    const x=col*w+(row%2&&kind!=='tile'?w/2:0),y=row*v,g=185+Math.floor(rnd()*50),gap=kind==='tile'?3:4;
    c.fillStyle=`rgb(${g},${g},${g})`;c.fillRect(x+gap,y+gap,w-gap*2,v-gap*2);h.fillStyle='#bcbcbc';h.fillRect(x+gap,y+gap,w-gap*2,v-gap*2);
    if(kind==='tile'){const grad=h.createLinearGradient(x,0,x+w,0);grad.addColorStop(0,'#555');grad.addColorStop(.45,'#eee');grad.addColorStop(1,'#555');h.fillStyle=grad;h.fillRect(x+gap,y+gap,w-gap*2,v-gap*2);c.strokeStyle='#fafafa55';c.strokeRect(x+gap+2,y+gap+2,w-gap*2-4,v-gap*2-4);}
   }
  }else if(kind==='wood'){
   for(let i=0;i<460;i++){let x=rnd()*N;c.strokeStyle=`rgba(45,30,20,${.05+rnd()*.16})`;h.strokeStyle=`rgba(25,25,25,${rnd()*.3})`;c.lineWidth=h.lineWidth=.5+rnd()*2;for(const ctx of [c,h]){ctx.beginPath();for(let y=0;y<=N;y+=8){let xx=x+Math.sin(y*Math.PI*4/N+x)*3+Math.sin(y*Math.PI*12/N+x)*1.2;y?ctx.lineTo(xx,y):ctx.moveTo(xx,y);}ctx.stroke();}}
  }else{
   for(let j=0;j<32;j++){h.fillStyle=j%4===0?'#777':'#aaa';h.fillRect(0,j*32,N,3);c.fillStyle='#ffffff35';c.fillRect(0,j*32,N,2);}
  }
  // Fine pores vary both color and height without introducing large stains.
  for(let i=0;i<26000;i++){const x=rnd()*N,y=rnd()*N;c.fillStyle=rnd()>.5?'#00000014':'#ffffff20';c.fillRect(x,y,1+rnd()*2,1+rnd()*2);h.fillStyle=rnd()>.5?'#ffffff28':'#00000020';h.fillRect(x,y,1,1);}
  const tex=(canvas,srgb)=>{const t=new THREE.CanvasTexture(canvas);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=Math.min(8,previewRenderer.capabilities.getMaxAnisotropy());if(srgb)t.colorSpace=THREE.SRGBColorSpace;return t;};
  const result={map:tex(color,true),bumpMap:tex(height,false),bumpScale:kind==='tile'?.018:kind==='brick'?.013:kind==='stone'?.009:.004,roughness:kind==='tile'?.4:kind==='gold'?.3:.82,metalness:kind==='gold'?.72:.03};surfaceMaps.set(kind,result);return result;
 }
 function surfaceUV(geo,name){
  const p=geo.attributes.position,n=geo.attributes.normal,uv=new Float32Array(p.count*2),period=/brick|plaster/.test(name)?1.8:/roof|glazed|eaves/.test(name)?1.6:2.4;
  for(let i=0;i<p.count;i+=3){let nx=0,ny=0,nz=0;for(let j=0;j<3;j++){nx+=n.getX(i+j);ny+=n.getY(i+j);nz+=n.getZ(i+j);}nx=Math.abs(nx);ny=Math.abs(ny);nz=Math.abs(nz);for(let j=0;j<3;j++){const k=i+j,x=p.getX(k),y=p.getY(k),z=p.getZ(k);uv[k*2]=(nx>ny&&nx>nz?z:x)/period;uv[k*2+1]=(ny>nx&&ny>nz?z:y)/period;}}
  geo.setAttribute('uv',new THREE.BufferAttribute(uv,2));
 }
 function prepareModel(node){
  let pivot=modelCache.get(node.id);if(pivot)return pivot;
  const model=new THREE.Group();
  for(const part of node.model.meshes){const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(new Float32Array(unpack(part.positions).buffer),3));geo.setAttribute('normal',new THREE.BufferAttribute(new Float32Array(unpack(part.normals).buffer),3));surfaceUV(geo,part.name);model.add(new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:new THREE.Color(...part.color),...surfaceFor(part.name)})));}
  const box=new THREE.Box3().setFromObject(model),center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3());model.position.sub(center);const scale=2/Math.max(size.x,size.y,size.z,.001);model.scale.setScalar(scale);model.position.multiplyScalar(scale);pivot=new THREE.Group();pivot.add(model);modelCache.set(node.id,pivot);return pivot;
 }
 function showModel(node){
  if(preview.group)previewScene.remove(preview.group);
  const pivot=prepareModel(node);pivot.rotation.set(0,.5,0);preview.group=pivot;previewScene.add(pivot);
  // The normal render loop draws it; no forced draw/resize inside the click.
 }
 const modelWarm={ready:0,total:nodeData.length,done:false,maxTaskMs:0};
 function warmEventAssets(){
  const queue=[...nodeData],target=new THREE.WebGLRenderTarget(96,96);
  const later=fn=>{if('requestIdleCallback' in window)requestIdleCallback(fn,{timeout:1000});else setTimeout(fn,16);};
  function step(){
   const node=queue.shift();if(!node){target.dispose();modelWarm.done=true;return;}
   const began=performance.now(),active=preview.group,pivot=prepareModel(node),oldTarget=previewRenderer.getRenderTarget();
   if(active)previewScene.remove(active);previewScene.add(pivot);
   try{previewRenderer.setRenderTarget(target);previewRenderer.render(previewScene,previewCamera);}finally{
    previewRenderer.setRenderTarget(oldTarget);previewScene.remove(pivot);if(active)previewScene.add(active);
   }
   modelWarm.ready++;modelWarm.maxTaskMs=Math.max(modelWarm.maxTaskMs,performance.now()-began);later(step);
  }
  // Decode the display-sized images before their first animated appearance.
  (async()=>{for(const img of preparedArt){try{await img.decode();artWarm.decoded++;}catch{}await new Promise(r=>setTimeout(r,0));}})();
  later(step);
 }
 const zoomModel=card.querySelector('.modelZoom');function toggleModelZoom(value){stage.classList.toggle('expanded',value);zoomModel.textContent=value?'收起展示':'放大查看';zoomModel.setAttribute('aria-expanded',String(value));sizePreview();}zoomModel.onclick=e=>{e.stopPropagation();toggleModelZoom(!stage.classList.contains('expanded'));};addEventListener('keydown',e=>{if(e.key==='Escape')toggleModelZoom(false);});
 const spin=card.querySelector('.modelSpin');spin.onclick=e=>{e.stopPropagation();preview.spinning=!preview.spinning;spin.textContent=preview.spinning?'暂停旋转':'继续旋转';spin.setAttribute('aria-pressed',String(preview.spinning));};
 const list=card.querySelector('select');for(const node of nodeData){const option=document.createElement('option');option.value=node.id;option.textContent=String(node.eventIndex+1).padStart(2,'0')+' '+node.event+' · '+node.name;list.append(option);}list.onchange=()=>focusNode(list.value);
 function focusNode(id,{reveal=true}={}){
  const node=nodeData.find(n=>n.id===id);if(!node)return;selectedNode=id;showModel(node);const badge=card.querySelector('.modelSiteBadge');badge.hidden=!node.siteKind;badge.textContent=node.siteKind?'专属地标 · '+node.siteKind:'';
  card.querySelector('h2').textContent=node.name+' · '+node.building;card.querySelector('.nodeChapter').textContent=node.event+' · '+chapters[node.eventIndex].years;card.querySelector('.nodeNote').textContent=node.note;
  for(const o of nodeObjects)o.el.classList.toggle('selected',o.node.id===(node.mapId||id));
  list.value=id;if(!chapters[selectedChapter].nodes.includes(id))selectedChapter=chapters.findIndex(c=>c.nodes.includes(id));for(const [index,b] of [...chapterList.children].entries())b.setAttribute('aria-pressed',String(index===selectedChapter));showChapterArt(reveal);chapterList.children[selectedChapter]?.scrollIntoView({block:'nearest'});
 }
 document.querySelector('.refTimeline').innerHTML='<span>1931—1945 · 事件地图</span><span>点击事件或地点 · 同步查看图文</span><span>'+chapters.length+'个事件 · '+nodeObjects.length+'个对应地点</span>';
 window.focusAtlasNode=focusNode;focusNode('shenyang',{reveal:false});warmEventAssets();
 window.beginAtlasHistory=()=>{
  dismissEventCard();focusNode('shenyang',{reveal:false});
  const node=nodeObjects.find(o=>o.node.id==='shenyang');
  if(node&&!matchMedia('(prefers-reduced-motion:reduce)').matches)node.el.animate([
   {boxShadow:'0 0 0 0 #edcf8866'},
   {boxShadow:'0 0 0 10px #edcf8800'}
  ],{duration:1100,iterations:2,easing:'ease-out'});
 };
 if(window.earthTransition?.nextScene)window.beginAtlasHistory();

__HISTORY_BOOK__
__NANJING_IMMERSIVE__


 const canvas=rr.domElement,pointers=new Map();let dragA=null,mode='rotate',blankTap=null;
 const bounds=()=>{target.x=THREE.MathUtils.clamp(target.x,-9,9);target.z=THREE.MathUtils.clamp(target.z,-7,8)};
 function setMode(value){mode=value;for(const b of document.querySelectorAll('#mapTools [data-mode]'))b.setAttribute('aria-pressed',b.dataset.mode===mode);canvas.style.cursor=mode==='pan'?'grab':'crosshair';}
 function resetMap(){target.set(.3,.15,-.2);Object.assign(control,defaults);pointers.clear();dragA=null;setMode('rotate')}
 function beginGesture(){const ps=[...pointers.values()];if(!ps.length){dragA=null;canvas.style.cursor=mode==='pan'?'grab':'crosshair';return;}
  const p=ps[0],q=ps[1];dragA={x:q?(p.x+q.x)/2:p.x,y:q?(p.y+q.y)/2:p.y,yaw:control.yaw,pitch:control.pitch,distance:control.distance,target:target.clone(),pinch:q?Math.hypot(q.x-p.x,q.y-p.y):0,kind:q?'touchPan':p.rotate?'rotate':'pan'};canvas.style.cursor='grabbing';
 }
 function panFrom(anchor,dx,dy){const scale=2*control.distance*Math.tan(THREE.MathUtils.degToRad(ca.fov/2))/canvas.clientHeight;
  const right=new THREE.Vector3(Math.cos(control.yaw),0,-Math.sin(control.yaw)),forward=new THREE.Vector3(-Math.sin(control.yaw),0,-Math.cos(control.yaw));
  target.copy(anchor).addScaledVector(right,-dx*scale).addScaledVector(forward,dy*scale/Math.max(.3,Math.sin(control.pitch)));bounds();
 }
 canvas.addEventListener('contextmenu',e=>e.preventDefault());
 canvas.addEventListener('pointerdown',e=>{if(![0,1,2].includes(e.button))return;e.preventDefault();if(asiaView)asiaView.time=Math.max(asiaView.time,2);
  if(e.button===0&&pointers.size===0)blankTap={id:e.pointerId,x:e.clientX,y:e.clientY,moved:false};else blankTap=null;
  pointers.set(e.pointerId,{x:e.clientX,y:e.clientY,rotate:e.button===0&&!e.shiftKey&&mode==='rotate'});try{canvas.setPointerCapture(e.pointerId)}catch(_){}beginGesture();
 });
 canvas.addEventListener('pointermove',e=>{const p=pointers.get(e.pointerId);if(!p||!dragA)return;e.preventDefault();if(blankTap&&Math.hypot(e.clientX-blankTap.x,e.clientY-blankTap.y)>6)blankTap.moved=true;p.x=e.clientX;p.y=e.clientY;
  const ps=[...pointers.values()],q=ps[1],x=q?(ps[0].x+q.x)/2:p.x,y=q?(ps[0].y+q.y)/2:p.y,dx=x-dragA.x,dy=y-dragA.y;
  if(dragA.kind==='pan'||dragA.kind==='touchPan'){panFrom(dragA.target,dx,dy);if(q&&dragA.pinch>5)control.distance=THREE.MathUtils.clamp(dragA.distance*dragA.pinch/Math.max(5,Math.hypot(q.x-ps[0].x,q.y-ps[0].y)),5.5,34);}else{control.yaw=dragA.yaw-dx*.005;control.pitch=THREE.MathUtils.clamp(dragA.pitch+dy*.004,.28,1.40);
   if(q&&dragA.pinch>5)control.distance=THREE.MathUtils.clamp(dragA.distance*dragA.pinch/Math.max(5,Math.hypot(q.x-ps[0].x,q.y-ps[0].y)),5.5,34);
  }
 });
 for(const ev of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(ev,e=>{
  if(ev==='pointerup'&&e.button===0&&blankTap?.id===e.pointerId&&!blankTap.moved&&pointers.size===1&&Math.hypot(e.clientX-blankTap.x,e.clientY-blankTap.y)<=6)dismissEventCard();
  blankTap=null;if(pointers.delete(e.pointerId))beginGesture();
 });
 addEventListener('blur',()=>{blankTap=null;pointers.clear();beginGesture()});
 canvas.addEventListener('wheel',e=>{e.preventDefault();if(asiaView)asiaView.time=Math.max(asiaView.time,2);if(e.shiftKey||Math.abs(e.deltaX)>Math.abs(e.deltaY))panFrom(target.clone(),-e.deltaX||-e.deltaY,0);else control.distance=THREE.MathUtils.clamp(control.distance*Math.exp(e.deltaY*.001),5.5,34)},{passive:false});
 document.getElementById('mapReset').onclick=resetMap;
 for(const b of document.querySelectorAll('#mapTools [data-mode]'))b.onclick=()=>setMode(b.dataset.mode);setMode('rotate');
 addEventListener('keydown',e=>{if(!nextScene.classList.contains('visible')||/INPUT|TEXTAREA|SELECT/.test(e.target.tagName))return;
  const steps={ArrowLeft:[45,0],ArrowRight:[-45,0],ArrowUp:[0,45],ArrowDown:[0,-45]};if(steps[e.key]){e.preventDefault();panFrom(target.clone(),...steps[e.key]);}
 });
 addEventListener('resize',()=>{ca.aspect=innerWidth/innerHeight;ca.updateProjectionMatrix();rr.setSize(innerWidth,innerHeight)});
 asiaView={rr,sceneA,ca,control,target,flag,fg,flagRig,flagBase,pole,labels,preview,time:0};window.asiaTerrainInfo={ready:true,buildMs:performance.now()-buildStarted,style:'globe day-surface texture, geographically registered vegetation, desert, rock and snow',modelSource:d.modelSource||'Three.js height grid',reliefScale:.70,chinaRaised:.045,mountains:true,riverSurfaces:riverMeshes.length,rivers:d.rivers.length,flag:'five-star',flagState:()=>({wave:{time:asiaView.time,tip:[fg.attributes.position.getX(28),fg.attributes.position.getY(28),fg.attributes.position.getZ(28)],hoist:[fg.attributes.position.getX(0),fg.attributes.position.getY(0),fg.attributes.position.getZ(0)]},scale:flagRig.scale.toArray(),position:flagRig.position.toArray(),camera:ca.position.toArray(),facing:flagRig.quaternion.angleTo(ca.quaternion),visible:flag.visible,pixels:(()=>{const points=Array.from({length:fg.attributes.position.count},(_,i)=>{const v=new THREE.Vector3().fromBufferAttribute(fg.attributes.position,i);flag.localToWorld(v);v.project(ca);return [(v.x*.5+.5)*innerWidth,(-v.y*.5+.5)*innerHeight]});return [Math.max(...points.map(p=>p[0]))-Math.min(...points.map(p=>p[0])),Math.max(...points.map(p=>p[1]))-Math.min(...points.map(p=>p[1]))]})()}),landmark:'Blender Yuejiang Tower miniature',landmarkTriangles:nodeData.reduce((n,x)=>n+x.model.triangles,0),landmarkScale:0,landmarkDisplay:'sidebar',assetWarmState:()=>({models:{...modelWarm,cached:modelCache.size},images:{...artWarm}}),previewState:()=>({selected:selectedNode,angle:preview.group?.rotation.y,spinning:preview.spinning,cached:modelCache.size,surfaceKinds:[...surfaceMaps.keys()],meshes:preview.group?.children[0].children.length,width:stage.clientWidth,height:stage.clientHeight,pixelRatio:previewRenderer.getPixelRatio(),buffer:[previewRenderer.domElement.width,previewRenderer.domElement.height]}),mapBuildingCount:0,nodes:nodeData.map(({id,name,event,eventIndex,building,lon,lat,kind})=>({id,name,event,eventIndex,building,lon,lat,kind})),selected:()=>selectedNode,focus:focusNode,control,getView:()=>({target:target.toArray(),mode,pointers:pointers.size,...control}),vertices:W*H,renderInfo:()=>({calls:rr.info.render.calls,triangles:rr.info.render.triangles,programs:rr.info.programs.map(p=>p.diagnostics?{runnable:p.diagnostics.runnable,log:p.diagnostics.programLog}:null)})};
}
let asiaBuild=null;function ensureAtlas(){if(!asiaBuild)asiaBuild=initAsiaTerrain().catch(e=>{window.asiaBuildError=String(e);console.error(e)});return asiaBuild;}
function renderAsiaTerrain(dt){if(window.atlasImmersiveActive)return;if(!asiaView){ensureAtlas();return;}const a=asiaView;if(!a.orbit)a.orbit={...a.control};const f=1-Math.exp(-dt*18);for(const k of ['yaw','pitch','distance']){a.orbit[k]+=(a.control[k]-a.orbit[k])*f;if(Math.abs(a.control[k]-a.orbit[k])<.00001)a.orbit[k]=a.control[k];}const c=a.orbit;a.time+=dt;const intro=Math.pow(1-THREE.MathUtils.clamp(a.time/1.8,0,1),3),pitch=c.pitch+intro*.14,yaw=c.yaw-intro*.07;const dist=c.distance*(1+intro*.07)/Math.min(1,a.ca.aspect/.95);a.ca.position.set(Math.sin(yaw)*Math.cos(pitch)*dist,Math.sin(pitch)*dist,Math.cos(yaw)*Math.cos(pitch)*dist).add(a.target);a.ca.lookAt(a.target);
 // Waves travel from the fixed hoist to the free edge. UV-based rest positions
 // avoid cumulative drift; cloth shading makes depth readable head-on too.
 const p=a.fg.attributes.position,uv=a.fg.attributes.uv,cloth=a.fg.attributes.color;
 for(let i=0;i<p.count;i++){
  const u=uv.getX(i),v=uv.getY(i),phase=u*9-a.time*3.8;
  const ripple=Math.sin(phase),fine=Math.sin(u*17-a.time*6.1+v*2.2);
  p.setXYZ(i,-.525+1.05*u*(.965+.025*Math.cos(phase)),
   (v-.5)*.7+u*(.058*ripple+.018*u*fine-.018),
   u*(.14*ripple+.025*u*fine));
  const shade=THREE.MathUtils.clamp(.82+.15*Math.cos(phase+.5)+.03*fine,.63,1);
  cloth.setXYZ(i,shade,shade,shade);
 }
 p.needsUpdate=true;cloth.needsUpdate=true;
 a.ca.updateMatrixWorld();
 // The whole waving mesh and pole face the camera together, anchored at Beijing.
 // Keep a readable screen size through zoom; neither edge-on views nor terrain hide it.
 a.flagRig.quaternion.copy(a.ca.quaternion);
 const flagDistance=a.ca.position.distanceTo(a.flagBase);
 const flagScale=2*flagDistance*Math.tan(THREE.MathUtils.degToRad(a.ca.fov/2))/innerHeight*90/1.31;
 a.flagRig.scale.setScalar(flagScale);
 a.flag.quaternion.copy(a.ca.quaternion);a.pole.quaternion.copy(a.ca.quaternion);
 a.flag.scale.setScalar(flagScale);a.pole.scale.setScalar(flagScale);
 a.flag.position.set(.54,1.40,0).multiplyScalar(flagScale).applyQuaternion(a.ca.quaternion).add(a.flagBase);
 a.pole.position.set(0,.875,0).multiplyScalar(flagScale).applyQuaternion(a.ca.quaternion).add(a.flagBase);
 a.flag.updateMatrixWorld(true);a.pole.updateMatrixWorld(true);
 updateAtlasLabels(a,c);
 if(a.preview?.group){const p=a.preview;if(p.spinning)p.group.rotation.y+=Math.min(dt,.05)*.48;p.elapsed+=dt;p.renderer.render(p.scene,p.camera);}

 a.rr.render(a.sceneA,a.ca);
}

// Offsets stay unchanged during a gesture. Solve once after the camera settles;
// the dot always projects the original geographic point, never the text position.
function updateAtlasLabels(a,c){
 const width=innerWidth,height=innerHeight;
 const side=document.querySelector('.historySidebar').getBoundingClientRect();
 const left=side.right+14,right=width-16,top=80,bottom=height-112;
 const overlap=(r,q,g=8)=>r.x<q.x+q.w+g&&r.x+r.w+g>q.x&&r.y<q.y+q.h+g&&r.y+r.h+g>q.y;
 const avoid=[...document.querySelectorAll('#mapTools,#mapReset,.refHeader')].map(el=>{const r=el.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};});
 // Reserve the readable flag face so geographic labels cannot cover the stars.
 const flagCorners=[[-.525,-.35],[.525,-.35],[.525,.35],[-.525,.35]].map(([x,y])=>a.flag.localToWorld(new THREE.Vector3(x,y,0)).project(a.ca)).map(v=>({x:(v.x*.5+.5)*width,y:(-v.y*.5+.5)*height}));
 const fx=Math.min(...flagCorners.map(p=>p.x)),fy=Math.min(...flagCorners.map(p=>p.y));
 avoid.push({x:fx-8,y:fy-8,w:Math.max(...flagCorners.map(p=>p.x))-fx+16,h:Math.max(...flagCorners.map(p=>p.y))-fy+16});
 const nodes=a.labels.filter(l=>l.node);
 for(const l of a.labels){
  const v=l.p.clone().project(a.ca);l.anchor={x:(v.x*.5+.5)*width,y:(-v.y*.5+.5)*height};
  l.inView=v.z>-1&&v.z<1&&Math.abs(v.x)<.98&&Math.abs(v.y)<.94;
 }
 const key=[width,height,...a.target.toArray(),c.yaw,c.pitch,c.distance].join(',');
 const settled=!window.asiaTerrainInfo.getView().pointers&&a.time>=1.8&&['yaw','pitch','distance'].every(k=>c[k]===a.control[k]);
 if(!a.labelLayoutKey||(settled&&key!==a.labelLayoutKey)){
  const used=[];
  for(const l of nodes){
   l.el.style.display='flex';const w=l.el.offsetWidth,h=l.el.offsetHeight,p=l.anchor;
   if(!l.inView){l.placed=false;continue;}
   const candidates=[];
   if(l.offset)candidates.push(l.offset);
   for(let y=-180;y<=180;y+=36)for(let x=-220;x<=220;x+=44)candidates.push({x:x-w/2,y:y-h-16});
   let best=null,score=Infinity;
   for(const off of candidates){
    const r={x:p.x+off.x,y:p.y+off.y,w,h};
    if(r.x<left||r.x+w>right||r.y<top||r.y+h>bottom||used.some(q=>overlap(r,q))||avoid.some(q=>overlap(r,q)))continue;
    const distance=Math.hypot(off.x+w/2,off.y+h/2);
    const cost=distance+(l.offset?Math.hypot(off.x-l.offset.x,off.y-l.offset.y)*.55:0);
    if(cost<score){score=cost;best={off,r};}
   }
   l.placed=!!best;
   if(best){l.offset=best.off;used.push(best.r);}
  }
  a.labelLayoutKey=key;a.labelLayoutCount=(a.labelLayoutCount||0)+1;
 }
 const cityRects=[];
 for(const l of nodes){
  const p=l.anchor,off=l.offset||{x:12,y:-40},x=p.x+off.x,y=p.y+off.y;
  const w=l.el.offsetWidth||l.width||90,h=l.el.offsetHeight||l.height||34;l.width=w;l.height=h;
  const show=l.inView&&l.placed&&x>=left&&x+w<=right&&y>=top&&y+h<=bottom;
  l.el.style.display=show?'flex':'none';l.line.style.display=l.dot.style.display=show?'':'none';
  if(!show)continue;
  l.el.style.left=x.toFixed(2)+'px';l.el.style.top=y.toFixed(2)+'px';
  l.el.dataset.anchorX=p.x.toFixed(2);l.el.dataset.anchorY=p.y.toFixed(2);
  l.dot.setAttribute('cx',p.x);l.dot.setAttribute('cy',p.y);
  const ex=Math.max(x,Math.min(x+w,p.x)),ey=Math.max(y,Math.min(y+h,p.y));
  for(const [k,v] of Object.entries({x1:p.x,y1:p.y,x2:ex,y2:ey}))l.line.setAttribute(k,v);
  cityRects.push({x,y,w,h});
 }
 const used=[...cityRects];
 for(const l of a.labels.filter(l=>!l.node)){
  const p=l.anchor; l.el.style.display='block';
  const w=l.el.offsetWidth,h=l.el.offsetHeight,r={x:p.x-w/2,y:p.y-h/2,w,h};
  const show=l.inView&&c.distance<13.5&&r.x>left&&r.x+w<right&&r.y>top&&r.y+h<bottom&&!used.some(q=>overlap(r,q,5))&&!avoid.some(q=>overlap(r,q,5));
  l.el.style.left=p.x.toFixed(2)+'px';l.el.style.top=p.y.toFixed(2)+'px';l.el.style.display=show?'block':'none';if(show)used.push(r);
 }
}
