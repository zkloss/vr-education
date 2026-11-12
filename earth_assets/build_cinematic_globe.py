from pathlib import Path
import base64
import shutil
import re

root = Path(__file__).resolve().parents[1]
assets = root / 'earth_assets'
backup = assets / '柔光版_太空改版前.html'
if not backup.exists():
    shutil.copy2(root / '地球漫游_柔光参考版.html', backup)
s = backup.read_text(encoding='utf-8')

def replace(old, new, count=1):
    global s
    if old not in s:
        raise RuntimeError('Missing source: ' + old[:100])
    s = s.replace(old, new, count)

s = re.sub(r'<title>.*?</title>', '<title>巴黎飞南京 · 太空质感版</title>', s, count=1)
replace('renderer.toneMappingExposure=1.12', 'renderer.toneMappingExposure=1.05')
replace('renderer.setClearColor(0x080c10)', 'renderer.setClearColor(0x030609)')
replace('new THREE.AmbientLight(0x9eb9d2,.6)', 'new THREE.AmbientLight(0x8da9c6,.24)')
replace('new THREE.DirectionalLight(0xf5f8ff,2.15)', 'new THREE.DirectionalLight(0xfff6e9,2.7)')
replace('distance:3.08,arrived:false', 'distance:3.3,arrived:false')
replace('state.distance=3.08+.25*Math.sin(Math.PI*u)', 'state.distance=3.3+.2*Math.sin(Math.PI*u)')
replace('sun.position.copy(pos(state.lat+18,state.lon-35,10));', 'sun.position.copy(pos(22,state.lon-78,10));waterUniforms.uNightSun.value.copy(sun.position).normalize();')

# Night lighting is derived from the same sun direction as the surface light.
replace('uCloud:{value:null}},cloudSphere', 'uCloud:{value:null},uNight:{value:null},uNightSun:{value:new THREE.Vector3()}},cloudSphere')
replace('function upgradeSurface(specularMap,cloudMap){', 'function upgradeSurface(specularMap,cloudMap,nightMap){')
replace('waterUniforms.uCloud.value=cloudMap;', 'waterUniforms.uCloud.value=cloudMap;waterUniforms.uNight.value=nightMap;')
replace('earth.material.onBeforeCompile=shader=>{Object.assign(shader.uniforms,waterUniforms);', '''earth.material.onBeforeCompile=shader=>{Object.assign(shader.uniforms,waterUniforms);
 shader.vertexShader='varying vec3 vNightNormal;\\n'+shader.vertexShader;
 shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\\n vNightNormal=normalize(mat3(modelMatrix)*normal);');''')
replace('uniform sampler2D uCloud;\n float waterHash', 'uniform sampler2D uCloud;uniform sampler2D uNight;uniform vec3 uNightSun;varying vec3 vNightNormal;\n float waterHash')
replace('vec3(.014,.066,.16),vec3(.025,.1,.21)', 'vec3(.006,.026,.063),vec3(.011,.041,.083)')
replace('diffuseColor.rgb,sea,seaMask*uWater*.62', 'diffuseColor.rgb,sea,seaMask*uWater*.72')
replace('diffuseColor.rgb,.96', 'diffuseColor.rgb,.82')
replace('vec3(.97,1.01,1.015),vec3(.94,1.035,1.03)', 'vec3(.94,.98,1.02),vec3(.96,.99,.98)')
replace('float horizon=pow(1.0-max(dot(normal,normalize(vViewPosition)),0.0),3.2);\n gl_FragColor.rgb=mix(gl_FragColor.rgb,vec3(.13,.3,.4),horizon*.32);', '''float solar=dot(normalize(vNightNormal),normalize(uNightSun));
 float night=1.0-smoothstep(-.1,.28,solar);
 vec3 cities=texture2D(uNight,vMapUv).rgb;
 gl_FragColor.rgb+=cities*night*1.35;
 float horizon=pow(1.0-max(dot(normal,normalize(vViewPosition)),0.0),4.0);
 float rimDay=smoothstep(-.22,.6,solar);
 gl_FragColor.rgb+=vec3(.018,.065,.12)*horizon*rimDay;''')
replace("style:'natural atmosphere'", "style:'directional sunlight with night cities'")
replace('float light=.22+.78*max(dot(normalize(vN),normalize(uSun)),0.0)', 'float light=.07+.93*max(dot(normalize(vN),normalize(uSun)),0.0)')
replace('shape*.4', 'shape*.46')

start = s.index(' atmosphere=new THREE.Mesh(')
end = s.index('scene.add(atmosphere);', start) + len('scene.add(atmosphere);')
s = s[:start] + ''' atmosphere=new THREE.Mesh(new THREE.SphereGeometry(1.075,128,96),new THREE.ShaderMaterial({transparent:true,side:THREE.BackSide,depthWrite:false,blending:THREE.AdditiveBlending,uniforms:{uSun:{value:new THREE.Vector3()}},vertexShader:'varying vec3 vP;void main(){vP=(modelMatrix*vec4(position,1.0)).xyz;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',fragmentShader:'varying vec3 vP;uniform vec3 uSun;void main(){vec3 ray=normalize(vP-cameraPosition);float b=length(cross(cameraPosition,ray));float density=exp(-max(b-1.0,0.0)*76.0)*(1.0-smoothstep(1.035,1.075,b));float light=.13+.87*pow(max(dot(normalize(vP),normalize(uSun)),0.0),.65);gl_FragColor=vec4(vec3(.1,.38,.65),density*light*.5);}'}));atmosphere.renderOrder=3;scene.add(atmosphere);''' + s[end:]

# Replace the bloom sprite with a restrained surface marker, facing outwards.
start = s.index('const glowMapCanvas=')
end = s.index('const loader=new THREE.TextureLoader();', start)
s = s[:start] + '''const markerNormal=pos(32.0603,118.7969),markerGroup=new THREE.Group();
markerGroup.position.copy(markerNormal.clone().multiplyScalar(1.018));
markerGroup.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),markerNormal);
const markerRing=new THREE.Mesh(new THREE.RingGeometry(.011,.0125,64),new THREE.MeshBasicMaterial({color:0xaedcec,transparent:true,opacity:.8,side:THREE.DoubleSide,depthWrite:false}));markerGroup.add(markerRing);
const markerPulse=new THREE.Mesh(new THREE.RingGeometry(.019,.0197,64),new THREE.MeshBasicMaterial({color:0x7cbacf,transparent:true,opacity:.28,side:THREE.DoubleSide,depthWrite:false}));markerGroup.add(markerPulse);
const markerDot=new THREE.Mesh(new THREE.CircleGeometry(.0035,24),new THREE.MeshBasicMaterial({color:0xe4f5fa,side:THREE.DoubleSide}));markerGroup.add(markerDot);scene.add(markerGroup);
function updateReferenceGlow(){const alpha=THREE.MathUtils.smoothstep(state.time,5.4,7.2);markerGroup.visible=alpha>0;markerRing.material.opacity=alpha*.8;const pulse=(fxTime*.35)%1;markerPulse.scale.setScalar(.85+pulse*.6);markerPulse.material.opacity=alpha*(1-pulse)*.26;window.earthStyle={look:'directional sunlight, night cities, thin atmosphere',borders:false,arrival:'南京',fullGlobe:true};}
''' + s[end:]

start = s.index('Promise.all([tex(')
end = s.index(']).then', start)
night_uri = 'data:image/jpeg;base64,' + base64.b64encode((assets / 'earth_night_8k.jpg').read_bytes()).decode()
s = s[:end] + ",tex('" + night_uri + "',true)" + s[end:]
replace('([map,normalMap,specularMap,cloudMap])=>', '([map,normalMap,specularMap,cloudMap,nightMap])=>')
replace('upgradeSurface(specularMap,cloudMap);', 'upgradeSurface(specularMap,cloudMap,nightMap);')

# Keep labels concise and make the departure annotation retire during flight.
replace("node.style.display=v&&Math.abs(p.x)<.8", "node.style.display=v&&(id==='parisTag'?state.time<3:state.time>4.7)&&Math.abs(p.x)<.8")
s = s.replace('法国 · 巴黎</strong><span>出发地 · 48.86°N / 2.35°E', '法国 · 巴黎</strong><span>出发地')
s = s.replace('中国 · 南京</strong><span>目的地 · 32.06°N / 118.80°E', '中国 · 南京</strong><span>32.06°N / 118.80°E')
replace('color:0xc8edf3,transparent:true,opacity:.8', 'color:0xaed6e4,transparent:true,opacity:.48')
replace('color:0xffe4b7', 'color:0xc7e9f4')
replace('color:0xffe1a9', 'color:0xb5dbe7')

css = '''
body{background:#030609;color:#dce7ed}
body::after{content:"";pointer-events:none;position:fixed;inset:0;z-index:3;background:radial-gradient(ellipse at 50% 43%,transparent 43%,rgba(0,0,0,.27) 100%)}
.flightOverlay{z-index:5}
.cityTag{padding:3px 0 3px 18px;border:0;background:none;transform:translate(14px,-50%);text-shadow:0 1px 8px #000}
.cityTag::before{content:"";position:absolute;left:0;top:50%;width:11px;height:1px;background:#a9c4cf80}
.cityTag strong{font-size:12px;font-weight:400;letter-spacing:1.4px;color:#dcebf0}
.cityTag span{font-size:9px;color:#7f9aa8;letter-spacing:.5px;margin-top:5px}
.flightNote{left:4.5vw;bottom:5.5vh;max-width:300px}
.flightKicker{font-size:9px;letter-spacing:3px;color:#6e8d9c;margin-bottom:12px}
.flightTitle{font-size:22px;font-weight:300;letter-spacing:4px;color:#e1eaee}
.flightTitle span{color:#6e9eaf;margin:0 12px;font-size:17px}
.flightSub{font-size:10px;color:#738794;margin-top:12px;letter-spacing:.6px}
.flightTrack{width:146px;height:1px;margin-top:19px;background:#57758520}
.flightTrack i{background:#89b4c6}
.flightActions{right:4.5vw;bottom:5.5vh}
.flightActions button{font-size:10px;color:#7f98a7;border:1px solid #a9c4cd20;background:transparent;padding:10px 16px;letter-spacing:1px}
.flightActions button:hover{color:#e5eff5;border-color:#a9c4cd60;background:#6cacc50d}
@media(max-width:700px){.flightNote{bottom:4vh}.flightTitle{font-size:18px}.flightSub{max-width:180px;line-height:1.8}.cityTag strong{font-size:11px}.cityTag span{font-size:8px}}
'''
s = s.replace('</style>', css + '</style>', 1)
out = root / '地球漫游_太空质感版.html'
out.write_text(s, encoding='utf-8')
for name in ['抗战历史沉浸式课堂.html', '地球漫游_南京精修版.html', '地球漫游_巴黎飞南京版.html', '地球漫游_法国飞中国版.html']:
    shutil.copy2(out, root / name)
shutil.copy2(out, Path.cwd() / out.name)
shutil.copy2(__file__, assets / Path(__file__).name)
print('Built:', out, out.stat().st_size)
