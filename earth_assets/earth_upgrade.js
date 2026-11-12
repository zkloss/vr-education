const worldData=__WORLD__,provinceData=__PROVINCES__,chinaData=__CHINA__;
const effects={borders:true,provinces:true,clouds:true,water:true};window.earthEffects=effects;
const panel=document.createElement('div');panel.className='layers';panel.innerHTML='<div class="layerTitle">地球图层 <span>LIVE EARTH</span></div><div class="layerButtons">'+[['borders','国家边界'],['provinces','中国省界'],['clouds','流动云层'],['water','动态海面']].map(([k,n])=>'<button data-layer="'+k+'" aria-pressed="true">'+n+'</button>').join('')+'</div><div class="layerHint">点击陆地查看国家 · H 隐藏界面</div>';document.body.append(panel);
panel.querySelectorAll('button').forEach(b=>b.onclick=()=>{let k=b.dataset.layer;effects[k]=!effects[k];b.setAttribute('aria-pressed',effects[k])});
const polygons=f=>f.geometry.type==='MultiPolygon'?f.geometry.coordinates:f.geometry.type==='Polygon'?[f.geometry.coordinates]:[];
const countries=worldData.features.filter(f=>!['CHN','TWN','HKG','MAC'].includes(f.properties.ADM0_A3));
const china=chinaData.features[0];china.properties={NAME_ZH:'中国',NAME:'China',ADM0_A3:'CHN',LABEL_X:104,LABEL_Y:35,LABELRANK:1};countries.push(china);
function makeLines(features,color,opacity,r){let v=[];for(const f of features)for(const poly of polygons(f))for(const ring of poly)for(let i=1;i<ring.length;i++){const a=pos(ring[i-1][1],ring[i-1][0],r),b=pos(ring[i][1],ring[i][0],r);v.push(a.x,a.y,a.z,b.x,b.y,b.z)}let g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(v,3));let mesh=new THREE.LineSegments(g,new THREE.LineBasicMaterial({color,transparent:true,opacity,depthWrite:false}));scene.add(mesh);return mesh}
const borders=makeLines(countries.filter(f=>f!==china),0xa4d4eb,.48,1.0035),provinces=makeLines(provinceData.features,0xc7e3e8,.28,1.004),chinaBorder=makeLines([china],0xffd49a,.95,1.0055);
const highlight=makeLines([],0xffdc99,1,1.006);let selected=china;
const fillCanvas=document.createElement('canvas');fillCanvas.width=4096;fillCanvas.height=2048;const fc=fillCanvas.getContext('2d');const fillTex=new THREE.CanvasTexture(fillCanvas);fillTex.colorSpace=THREE.SRGBColorSpace;const fillMesh=new THREE.Mesh(new THREE.SphereGeometry(1.002,128,96),new THREE.MeshBasicMaterial({map:fillTex,transparent:true,depthWrite:false,opacity:.7}));scene.add(fillMesh);
function fillCountry(f){fc.clearRect(0,0,4096,2048);fc.fillStyle='rgba(255,193,90,0.15)';for(const poly of polygons(f)){fc.beginPath();for(const ring of poly){let first=true;for(const [lon,lat] of ring){let x=(lon+180)/360*4096,y=(90-lat)/180*2048;if(first){fc.moveTo(x,y);first=false}else fc.lineTo(x,y)}fc.closePath()}fc.fill('evenodd')}fillTex.needsUpdate=true}
fillCountry(china);
const shortNames={PRK:'朝鲜',KOR:'韩国',RUS:'俄罗斯',USA:'美国',GBR:'英国',ARE:'阿联酋',LAO:'老挝',VNM:'越南',IRN:'伊朗',SYR:'叙利亚',TZA:'坦桑尼亚',COD:'刚果（金）',COG:'刚果（布）'};
const nameOf=f=>shortNames[f.properties.ADM0_A3]||f.properties.NAME_ZH||f.properties.NAME;
const labelContainer=document.createElement('div');labelContainer.className='geoLabels';document.body.append(labelContainer);
const geoLabels=countries.filter(f=>f.properties.LABEL_X!==undefined&&f.properties.ADM0_A3!=='ATA'&&(f.properties.LABELRANK||6)<=4).map(f=>{let div=document.createElement('div');div.className='geoName'+(f===china?' chinaName':'');div.textContent=nameOf(f);labelContainer.append(div);return {div,p:pos(f.properties.LABEL_Y,f.properties.LABEL_X,1.008),rank:f.properties.LABELRANK||6,f}}).sort((a,b)=>(a.f===china?-1:b.f===china?1:a.rank-b.rank));
const provinceLabels=provinceData.features.filter(f=>f.properties.centroid&&f.properties.name).map(f=>{let div=document.createElement('div');div.className='provinceName';div.textContent=f.properties.name.replace(/省|壮族自治区|回族自治区|维吾尔自治区|自治区|特别行政区/g,'');labelContainer.append(div);return {div,p:pos(f.properties.centroid[1],f.properties.centroid[0],1.008)}});
let waterUniforms={uTime:{value:0},uWater:{value:1},uOcean:{value:null}},cloudSphere=null,cloudUniforms=null,fxTime=0;
function upgradeSurface(specularMap,cloudMap){waterUniforms.uOcean.value=specularMap;earth.material.shininess=48;earth.material.specular.set(0x83b6c8);earth.material.onBeforeCompile=shader=>{
 Object.assign(shader.uniforms,waterUniforms);
 shader.fragmentShader='uniform float uTime;uniform float uWater;uniform sampler2D uOcean;\n'+shader.fragmentShader;
 shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',`#include <map_fragment>
 float seaMask=smoothstep(.35,.75,texture2D(uOcean,vMapUv).r);
 vec2 q=vMapUv*vec2(210.0,95.0);
 float swell=sin(q.x+sin(q.y*.7+uTime*.13)*2.0-uTime*.7)*sin(q.y*1.8+q.x*.25+uTime*.45);
 float ripple=sin(q.x*3.4+q.y*2.2-uTime*1.5)*sin(q.y*3.1-q.x*.7+uTime*.9);
 float flow=pow(.5+.5*sin(q.y*.55+sin(q.x*.18-uTime*.1)*2.8-uTime*.23),18.0);
 vec3 oceanColor=mix(vec3(.008,.035,.085),vec3(.015,.12,.19),.45+.2*swell+.13*ripple);
 oceanColor+=vec3(.025,.12,.16)*flow*.55;
 diffuseColor.rgb=mix(diffuseColor.rgb,oceanColor,seaMask*uWater*.82);`);
 shader.fragmentShader=shader.fragmentShader.replace('#include <normal_fragment_maps>',`#include <normal_fragment_maps>
 vec3 waveNormal=normalize(normal+vec3(swell*.10,ripple*.07,0.0)*seaMask*uWater);
 normal=waveNormal;`);
 };earth.material.needsUpdate=true;
 cloudUniforms={uMap:{value:cloudMap},uTime:{value:0},uSun:{value:new THREE.Vector3(1,1,1)}};
 cloudSphere=new THREE.Mesh(new THREE.SphereGeometry(1.014,96,64),new THREE.ShaderMaterial({uniforms:cloudUniforms,transparent:true,depthWrite:false,vertexShader:'varying vec2 vUv;varying vec3 vN;void main(){vUv=uv;vN=normalize(mat3(modelMatrix)*normal);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',fragmentShader:'uniform sampler2D uMap;uniform float uTime;uniform vec3 uSun;varying vec2 vUv;varying vec3 vN;void main(){vec2 uv=vec2(fract(vUv.x+uTime*.00075),vUv.y);float density=texture2D(uMap,uv).r;float light=.25+.75*max(dot(normalize(vN),normalize(uSun)),0.0);gl_FragColor=vec4(vec3(.83,.91,1.0)*light,smoothstep(.14,.85,density)*.56);}'}));cloudSphere.renderOrder=2;scene.add(cloudSphere);
 window.earthDetails={countries:countries.length,provinces:provinceData.features.filter(f=>f.properties.name).length,borderVertices:borders.geometry.attributes.position.count,shaderReady:true};
}
function inRing(x,y,ring){let inside=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){let a=ring[i],b=ring[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])inside=!inside}return inside}
function hitCountry(f,lon,lat){return polygons(f).some(p=>inRing(lon,lat,p[0])&&!p.slice(1).some(r=>inRing(lon,lat,r)))}
const raycaster=new THREE.Raycaster();let clickStart=null;
renderer.domElement.addEventListener('pointerdown',e=>clickStart={x:e.clientX,y:e.clientY});
renderer.domElement.addEventListener('pointerup',e=>{if(!earth||!clickStart||Math.hypot(e.clientX-clickStart.x,e.clientY-clickStart.y)>5)return;let rect=renderer.domElement.getBoundingClientRect();raycaster.setFromCamera(new THREE.Vector2((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1),camera);const hit=raycaster.intersectObject(earth)[0];if(!hit)return;const p=hit.point.normalize(),lat=THREE.MathUtils.radToDeg(Math.asin(p.y)),lon=THREE.MathUtils.radToDeg(Math.atan2(-p.z,p.x));let f=countries.find(f=>hitCountry(f,lon,lat));if(f)selectCountry(f)});
function selectCountry(f){selected=f;fillCountry(f);if(f!==china){const temp=makeLines([f],0xffdc99,1,1.006);highlight.geometry.dispose();highlight.geometry=temp.geometry;scene.remove(temp);temp.material.dispose()}highlight.visible=f!==china;state.arrived=true;document.body.classList.add('arrived');document.querySelector('.dest h1').innerHTML=nameOf(f)+'<span class="english">'+f.properties.NAME.toUpperCase()+'</span>';document.querySelector('.dest p').textContent=f===china?'山河入眼，万里在场。':'拖动地球，继续探索。';window.earthSelected=nameOf(f)}
window.selectEarthCountry=code=>{let f=countries.find(f=>f.properties.ADM0_A3===code);if(f)selectCountry(f)};
function updateWorld(dt){fxTime+=dt;waterUniforms.uTime.value=fxTime;waterUniforms.uWater.value=effects.water?1:0;const show=effects.borders;borders.visible=show;chinaBorder.visible=show;provinces.visible=effects.provinces&&state.distance<3.6;highlight.visible=show&&selected!==china;fillMesh.visible=show;chinaBorder.material.opacity=.82+.15*Math.sin(fxTime*.8);if(cloudSphere){cloudSphere.visible=effects.clouds;cloudUniforms.uTime.value=fxTime;cloudUniforms.uSun.value.copy(sun.position).normalize()}
 const occupied=[],cam=camera.position.clone().normalize(),clean=document.body.classList.contains('clean'),pr=panel.getBoundingClientRect();function place(item,isProvince){const dot=item.p.clone().normalize().dot(cam);if(dot<1/state.distance+.025||clean||!show||(isProvince&&(!effects.provinces||state.distance>2.5))){item.div.style.display='none';return}const p=item.p.clone().project(camera),x=(p.x*.5+.5)*innerWidth,y=(-p.y*.5+.5)*innerHeight;const width=isProvince?48:Math.min(150,item.div.textContent.length*12+15),height=isProvince?20:29;if(x<innerWidth*.28||x>innerWidth-45||y<100||y>innerHeight-110||(x+width/2>pr.left-8&&x-width/2<pr.right+8&&y+height/2>pr.top-8&&y-height/2<pr.bottom+8)||occupied.some(a=>Math.abs(x-a.x)<(width+a.w)/2&&Math.abs(y-a.y)<(height+a.h)/2)){item.div.style.display='none';return}item.div.style.display='block';item.div.style.transform='translate(-50%,-50%) translate('+x+'px,'+y+'px)';occupied.push({x,y,w:width,h:height})}
 geoLabels.forEach(i=>place(i,false));provinceLabels.forEach(i=>place(i,true));window.earthFxTime=fxTime;
}
