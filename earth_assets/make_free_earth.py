from pathlib import Path
import re,shutil
root=Path(__file__).resolve().parents[1]
source=(root/'地球漫游_增强版.html').read_text(encoding='utf-8')
source=source.replace('<title>VR 赋能教育 · 抗战历史沉浸式课堂</title>','<title>自由拖动地球</title>')
source=source.replace('time:0,playing:true,manual:false,lon:-78,lat:15,distance:5.4,arrived:false','time:24,playing:false,manual:true,lon:104,lat:35,distance:3.0,arrived:true')
source=source.replace('const offset=innerWidth>900?.17:0;','const offset=0;')
source=source.replace('</style>','''
.brand,.caption,.credit,.label,.bottom,.layers,.geoLabels,.shade{display:none!important}
</style>''')
# Direct manipulation only. Keep fullscreen available without adding controls.
source=re.sub(r"document\.addEventListener\('keydown',e=>\{if\(e\.target\.tagName==='BUTTON'\).*?\}\);", "document.addEventListener('keydown',e=>{if(e.key.toLowerCase()==='f'){if(!document.fullscreenElement)document.documentElement.requestFullscreen?.().catch(()=>{});else document.exitFullscreen?.()}});renderer.domElement.addEventListener('dblclick',()=>{if(!document.fullscreenElement)document.documentElement.requestFullscreen?.().catch(()=>{});else document.exitFullscreen?.()});",source)
source=re.sub(r"^renderer\.domElement\.addEventListener\('pointerup',e=>\{if\(!earth\|\|!clickStart.*$",'',source,flags=re.M)
# Hidden labels are not projected each frame in the clean edition.
start=source.index(' const occupied=[],cam=camera.position.clone().normalize()')
end=source.index('\n}',start)
source=source[:start]+' window.earthFxTime=fxTime;'+source[end:]
out=root/'地球漫游_自由拖动版.html';out.write_text(source,encoding='utf-8')
shutil.copy2(out,root/'抗战历史沉浸式课堂.html')
shutil.copy2(out,Path.cwd()/out.name)
shutil.copy2(Path(__file__),root/'earth_assets'/'make_free_earth.py')
print('Built free globe',out.stat().st_size)
