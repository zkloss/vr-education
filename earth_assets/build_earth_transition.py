from pathlib import Path
import shutil
import re
root=Path(__file__).resolve().parents[1]; assets=root/'earth_assets'
source=root/'地球漫游_太空质感版.html'
s=source.read_text(encoding='utf8')
def replace(old,new):
    global s
    if old not in s: raise RuntimeError('Missing: '+old[:100])
    s=s.replace(old,new,1)
s=re.sub(r'<title>.*?</title>','<title>巴黎飞南京 · 推进转场测试</title>',s,count=1)
replace('for(const city of [paris,nanjing]){let m=', 'const cityMarkers=[];for(const city of [paris,nanjing]){let m=')
replace('m.position.copy(pos(city.lat,city.lon,1.012));scene.add(m)}','m.position.copy(pos(city.lat,city.lon,1.012));scene.add(m);cityMarkers.push(m)}')
replace('state.distance=3.3+.2*Math.sin(Math.PI*u)}','state.distance=t<=transitionTiming.zoomStart?3.3+.2*Math.sin(Math.PI*u):3.3+(1.42-3.3)*between(t,transitionTiming.zoomStart,transitionTiming.zoomEnd)}')
replace('state.time=Math.min(state.time+dt,8);if(state.time>=8)state.playing=false','state.time=Math.min(state.time+dt,transitionTiming.end);if(state.time>=transitionTiming.end)state.playing=false')
replace('state.time=THREE.MathUtils.clamp(t,0,8);','state.time=THREE.MathUtils.clamp(t,0,transitionTiming.end);')
replace('camera.position.copy(pos(state.lat,state.lon,state.distance/Math.min(camera.aspect,1)));', '''const aspectBoost=1/Math.min(camera.aspect,1)-1;
 const zoomBlend=!state.manual?between(state.time,transitionTiming.zoomStart,transitionTiming.zoomEnd):0;
 camera.position.copy(pos(state.lat,state.lon,state.distance*(1+aspectBoost*(1-zoomBlend))));''')
replace('updateFlight();updateReferenceGlow();renderer.render(scene,camera);','updateFlight();updateReferenceGlow();updateSceneTransition();if(!earthTransition.nextScene)renderer.render(scene,camera);')
replace("state.arrived=false;ui()}","state.arrived=false;document.querySelector('.flightOverlay').classList.remove('hidden');ui()}")
# Append setup before animation begins; deferred callbacks run after setup.
replace('let last=performance.now();function loop(now)',Path('earth_transition.js').read_text(encoding='utf8')+'\nlet last=performance.now();function loop(now)')
css='''
#sceneBlackout{position:fixed;inset:0;z-index:50;background:#000;opacity:0;pointer-events:none}
#nextScene{position:fixed;inset:0;z-index:20;display:none;align-items:center;justify-content:center;background:radial-gradient(ellipse at 50% 48%,#132c36 0%,#0b1720 48%,#050b11 100%);color:#b5c9d3}
#nextScene.visible{display:flex}
#nextScene::before{content:"";position:absolute;inset:0;background-image:linear-gradient(#9ac5d406 1px,transparent 1px),linear-gradient(90deg,#9ac5d406 1px,transparent 1px);background-size:64px 64px;mask-image:radial-gradient(ellipse,black,transparent 75%);pointer-events:none}
.nextSceneCenter{position:relative;text-align:center}.nextSceneRule{height:1px;width:36px;background:#6b9aab;margin:0 auto 26px}
.nextSceneCenter h1{font-size:24px;letter-spacing:.25em;font-weight:300;margin:0}.nextSceneCenter p{font-size:11px;letter-spacing:.16em;color:#5e7a89;margin-top:18px}
#transitionReplay,#backToGlobe{position:absolute;bottom:5.5vh;font-size:11px;background:transparent;border-color:#a9c4cd22;color:#819eac}
#transitionReplay{right:4.5vw}#backToGlobe{left:4.5vw}
'''
s=s.replace('</style>',css+'</style>',1)
out=root/'地球漫游_推进转场版.html';out.write_text(s,encoding='utf8')
for name in ['抗战历史沉浸式课堂.html','地球漫游_南京精修版.html','地球漫游_巴黎飞南京版.html','地球漫游_法国飞中国版.html']:
    shutil.copy2(out,root/name)
for name in ['earth_transition.js','build_earth_transition.py']:shutil.copy2(name,assets/name)
shutil.copy2(out,Path.cwd()/out.name)
print('Built',out.stat().st_size)
