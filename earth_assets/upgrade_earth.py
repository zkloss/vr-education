from pathlib import Path
import base64,json,shutil
from PIL import Image
root=Path(__file__).resolve().parents[1]; assets=root/'earth_assets'
backup=root/'地球漫游_初版备份.html'
if not backup.exists():shutil.copy2(root/'抗战历史沉浸式课堂.html',backup)
im=Image.open(assets/'clouds.jpg');im.thumbnail((4096,2048));im.save(assets/'clouds_4k.jpg',quality=90)
source=Path('earth_template.template').read_text(encoding='utf-8')
extra=Path('earth_upgrade.js').read_text(encoding='utf-8')
for key,name in [('__WORLD__','countries50.geojson'),('__PROVINCES__','china_provinces.json'),('__CHINA__','china_outline.json')]:
 d=json.loads((assets/name).read_text(encoding='utf-8'))
 for f in d['features']:
  if key=='__WORLD__':f['properties']={k:v for k,v in f['properties'].items() if k in ['NAME_ZH','NAME','ADM0_A3','LABEL_X','LABEL_Y','LABELRANK']}
 extra=extra.replace(key,json.dumps(d,ensure_ascii=False,separators=(',',':')))
source=source.replace('const loader=new THREE.TextureLoader();',extra+'\nconst loader=new THREE.TextureLoader();')
source=source.replace("tex('__SPECULAR__')]).then(([map,normalMap,specularMap])", "tex('__SPECULAR__'),tex('__CLOUDS__')]).then(([map,normalMap,specularMap,cloudMap])")
source=source.replace("state.loaded=true;$('status')", "upgradeSurface(specularMap,cloudMap);state.loaded=true;$('status')")
source=source.replace('sun.position.copy(pos(state.lat+18,state.lon-35,10));renderer.render(scene,camera);','sun.position.copy(pos(state.lat+18,state.lon-35,10));updateWorld(dt);renderer.render(scene,camera);window.earthRenderInfo=()=>({calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,programs:renderer.info.programs.map(p=>p.diagnostics?{runnable:p.diagnostics.runnable,log:p.diagnostics.programLog}:{} )});')
source=source.replace('let earth,atmosphere;', 'let earth,atmosphere;')
source=source.replace('function home(){','function home(){selectCountry(china);')
source=source.replace('function replay(){','function replay(){selectCountry(china);')
source=source.replace('1.025,96,64','1.016,96,64').replace('rim*.65','rim*.4')
source=source.replace('specular:new THREE.Color(0x5b7587)','specular:new THREE.Color(0x75adce)')
source=source.replace('new THREE.AmbientLight(0x779ac0,.55)','new THREE.AmbientLight(0x779ac0,.38)')
css='''.caption{top:36%}.dest h1{font-size:clamp(38px,4.5vw,74px);max-width:28vw;letter-spacing:.12em}.dest .english{letter-spacing:.25em;font-size:10px;line-height:1.7}.layers{position:absolute;right:5vw;top:11vh;width:266px;border:1px solid #bddff124;background:#07121dc9;border-radius:7px;padding:16px;backdrop-filter:blur(16px)}.layerTitle{font-size:12px;letter-spacing:.15em;color:#cbdfe9;display:flex;justify-content:space-between}.layerTitle span{font-size:9px;color:#6cabbc}.layerButtons{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:13px}.layerButtons button{font-size:10px;padding:9px 7px}.layerButtons button[aria-pressed=true]{border-color:#73c3db77;color:#9fe3f2;background:#16334299}.layerButtons button[aria-pressed=false]{opacity:.5}.layerHint{font-size:9px;color:#698fa2;margin-top:12px}.geoLabels{position:absolute;inset:0;pointer-events:none;overflow:hidden}.geoName,.provinceName{position:absolute;top:0;left:0;white-space:nowrap;text-shadow:0 1px 3px #000,0 0 7px #000,0 0 12px #000;font-size:12px;color:#e6f1f4;letter-spacing:.1em}.chinaName{font-size:18px;color:#ffdda5;letter-spacing:.4em}.provinceName{font-size:9px;color:#b5d1de}.clean .layers{display:none}#label{display:none}.controls{gap:6px}.hint{display:none}@media(max-width:700px){.layers{width:200px;padding:12px;top:9vh;right:4vw}.dest h1{max-width:75vw;font-size:38px}.caption{top:30%}.geoName{font-size:10px}.bottom{left:3vw;right:3vw}.journey{width:90px}.controls button{font-size:9px;padding:10px 6px}.credit{display:none}}'''
source=source.replace('</style>',css+'.layers,.bottom{z-index:4}.brand,.caption,.credit{z-index:3}.geoLabels{z-index:2}.shade{z-index:1}'+ '</style>')
source=source.replace('__THREE__',(assets/'three.min.js').read_text(encoding='utf-8'))
for key,name in [('__EARTH__','earth_8k.jpg'),('__NORMAL__','earth_normal.jpg'),('__SPECULAR__','earth_specular.jpg'),('__CLOUDS__','clouds_4k.jpg')]:
 source=source.replace(key,'data:image/jpeg;base64,'+base64.b64encode((assets/name).read_bytes()).decode())
out=root/'地球漫游_增强版.html';out.write_text(source,encoding='utf-8');shutil.copy2(out,root/'抗战历史沉浸式课堂.html')
print('Built enhanced globe:',out.stat().st_size)
