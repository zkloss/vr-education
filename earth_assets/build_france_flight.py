from pathlib import Path
import re,shutil
root=Path(__file__).resolve().parents[1]
source=(root/'地球漫游_自由拖动版.html').read_text(encoding='utf-8')
source=source.replace('<title>自由拖动地球</title>','<title>法国巴黎 → 中国南京</title>')
source=source.replace('time:24,playing:false,manual:true,lon:104,lat:35,distance:3.0,arrived:true','time:0,playing:true,manual:false,lon:2.3522,lat:48.8566,distance:2.4,arrived:false')
start=source.index('function upgradeSurface(specularMap,cloudMap){')
end=source.index(' cloudUniforms=',start)
surface=r'''function upgradeSurface(specularMap,cloudMap){
 waterUniforms.uOcean.value=specularMap;earth.material.specular.set(0x000000);earth.material.shininess=1;
 earth.material.onBeforeCompile=shader=>{Object.assign(shader.uniforms,waterUniforms);
 shader.fragmentShader=`uniform float uTime;uniform float uWater;uniform sampler2D uOcean;
 float waterHash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
 float waterNoise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);return mix(mix(waterHash(i),waterHash(i+vec2(1,0)),f.x),mix(waterHash(i+vec2(0,1)),waterHash(i+vec2(1,1)),f.x),f.y);}
 `+shader.fragmentShader;
 shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',`#include <map_fragment>
 float seaMask=smoothstep(.35,.75,texture2D(uOcean,vMapUv).r);
 vec2 drift=vMapUv*vec2(45.,23.)+vec2(uTime*.018,-uTime*.009);
 float flow=.65*waterNoise(drift)+.35*waterNoise(drift*2.1+uTime*.011);
 vec3 sea=mix(vec3(.009,.035,.095),vec3(.012,.062,.13),flow);
 diffuseColor.rgb=mix(diffuseColor.rgb,sea,seaMask*uWater*.7);`);
 };earth.material.needsUpdate=true;
 window.earthSurface={specular:'disabled',waveNormal:'removed',water:'smooth diffuse drift'};
'''
source=source[:start]+surface+source[end:]
source=source.replace('density)*.56','density)*.4')
flight=Path('france_flight.js').read_text(encoding='utf-8')
source=source.replace('const loader=new THREE.TextureLoader();',flight+'\nconst loader=new THREE.TextureLoader();')
start=source.index('function journey(t){');end=source.index('\nfunction ui()',start)
source=source[:start]+'''function journey(t){const u=flyEase(THREE.MathUtils.clamp((t-.8)/6.4,0,1)),a=pos(48.8566,2.3522),b=pos(32.0603,118.7969),angle=a.angleTo(b);const p=a.multiplyScalar(Math.sin((1-u)*angle)).add(b.multiplyScalar(Math.sin(u*angle))).divideScalar(Math.sin(angle)).normalize();state.lat=THREE.MathUtils.radToDeg(Math.asin(p.y));state.lon=THREE.MathUtils.radToDeg(Math.atan2(-p.z,p.x));state.distance=2.4+.65*Math.sin(Math.PI*u)}'''+source[end:]
source=source.replace('Math.min(state.time+dt,24)','Math.min(state.time+dt,8)').replace('if(state.time>=24)','if(state.time>=8)').replace('THREE.MathUtils.clamp(t,0,24)','THREE.MathUtils.clamp(t,0,8)').replace('state.time>20','state.time>=7.2')
source=source.replace('updateWorld(dt);renderer.render(scene,camera);','updateWorld(dt);updateFlight();renderer.render(scene,camera);')
style='''.flightOverlay{position:absolute;inset:0;pointer-events:none;z-index:5;font-family:"Microsoft YaHei",sans-serif}.cityTag{position:absolute;transform:translate(15px,-50%);padding:9px 12px;border-left:2px solid #f3c98b;background:linear-gradient(90deg,#06101dc9,#06101d40);border-radius:0 4px 4px 0;white-space:nowrap;max-width:220px}.cityTag strong{display:block;font-size:17px;font-weight:500;letter-spacing:.08em;color:#ffedcf;text-shadow:0 1px 4px #000}.cityTag span{display:block;font-size:9px;letter-spacing:.06em;color:#a1bacb;margin-top:6px}.flightNote{position:absolute;left:4vw;bottom:6vh;color:#e6edf4;text-shadow:0 1px 5px #000}.flightKicker{font-size:10px;letter-spacing:.22em;color:#a2b9cd;margin-bottom:12px}.flightTitle{font-size:24px;letter-spacing:.14em;font-weight:400}.flightTitle span{font-size:20px;color:#e7bb7d;margin:0 10px}.flightSub{font-size:11px;color:#9baebd;margin-top:12px;letter-spacing:.08em}.flightTrack{height:1px;width:220px;background:#d7e4ec20;margin-top:17px}.flightTrack i{display:block;height:1px;background:#efc88f;transition:width .05s}.flightActions{position:absolute;bottom:6vh;right:4vw;pointer-events:auto}.flightActions button{font-size:10px;color:#bbcbd7;background:#07111b80;border-color:#acbcc82f}.flightOverlay.hidden{display:none}@media(max-width:700px){.cityTag strong{font-size:13px}.cityTag span{font-size:8px}.cityTag{transform:translate(-50%,15px);padding:8px}.flightTitle{font-size:20px}.flightTrack{width:170px}.flightSub{font-size:9px}}'''
source=source.replace('</style>',style+'</style>')
source=source.replace("if(e.key.toLowerCase()==='f'){", "if(e.key.toLowerCase()==='h')document.querySelector('.flightOverlay').classList.toggle('hidden');if(e.key.toLowerCase()==='f'){")
out=root/'地球漫游_巴黎飞南京版.html';out.write_text(source,encoding='utf-8');shutil.copy2(out,root/'抗战历史沉浸式课堂.html');shutil.copy2(out,root/'地球漫游_法国飞中国版.html');shutil.copy2(out,Path.cwd()/out.name)
for name in ['france_flight.js','build_france_flight.py']:shutil.copy2(name,root/'earth_assets'/name)
freepath=root/'地球漫游_自由拖动版.html'
free=freepath.read_text(encoding='utf-8')
fs=free.index('function upgradeSurface(specularMap,cloudMap){');fe=free.index(' cloudUniforms=',fs)
free=free[:fs]+surface+free[fe:]
free=free.replace('density)*.56','density)*.4')
freepath.write_text(free,encoding='utf-8');shutil.copy2(freepath,Path.cwd()/freepath.name)
print('Built France-China globe',out.stat().st_size)
