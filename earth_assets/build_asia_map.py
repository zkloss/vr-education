from pathlib import Path
import json,base64,shutil
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
root=Path(__file__).resolve().parents[1]; a=root/'earth_assets'
W,H=1281,933; bounds=[35,-10,155,77]
def polys(f):
 g=f['geometry'];return g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
def xy(p):return ((p[0]-bounds[0])/(bounds[2]-bounds[0])*(W-1),(bounds[3]-p[1])/(bounds[3]-bounds[1])*(H-1))
countries=json.loads((a/'countries50.geojson').read_text(encoding='utf8'))['features']
provinces=json.loads((a/'china_provinces.json').read_text(encoding='utf8'))['features']
china=[f for f in provinces if f['properties'].get('adcode')!='100000_JD']
def mask(fs):
 im=Image.new('L',(W,H));d=ImageDraw.Draw(im)
 for f in fs:
  for p in polys(f):
   d.polygon([xy(v) for v in p[0]],fill=255)
   for r in p[1:]:d.polygon([xy(v) for v in r],fill=0)
 return np.array(im)
land=mask(countries);cmask=mask(china)
# GMT Earth Relief 5 arc-minute grid; elevations in meters, no photographic brightness.
import h5py
with h5py.File(a/'earth_relief_05m_g.grd','r') as dem:
 z=dem['z'][:].astype(np.float32)*float(np.asarray(dem['z'].attrs.get('scale_factor',1)).ravel()[0])+float(np.asarray(dem['z'].attrs.get('add_offset',0)).ravel()[0])
 lon=dem['lon'][:]; lat=dem['lat'][:]
 # NetCDF grid rows increase south to north. Image rows run north to south.
 ix0=int(np.searchsorted(lon,bounds[0]));ix1=int(np.searchsorted(lon,bounds[2]))+1
 iy0=int(np.searchsorted(lat,bounds[1]));iy1=int(np.searchsorted(lat,bounds[3]))+1
 crop=z[iy0:iy1,ix0:ix1][::-1]
 meters=np.array(Image.fromarray(crop).resize((W,H),Image.Resampling.BICUBIC))
 raw=19+np.maximum(0,meters)/8000*236
 # Only a light resampling filter; do not erase ridges.
 kernel=np.exp(-np.arange(-3,4,dtype=np.float32)**2/(2*.95**2));kernel/=kernel.sum()
 for axis in [0,1]:
  pad=[(0,0),(0,0)];pad[axis]=(3,3);v=np.pad(raw,pad,mode='edge');out=np.zeros_like(raw)
  for j,k in enumerate(kernel):
   sl=[slice(None),slice(None)];sl[axis]=slice(j,j+raw.shape[axis]);out+=v[tuple(sl)]*k
  raw=out
# Enhance existing ridges relative to a broad relief field, without adding noise.
coarse=Image.fromarray(raw).resize((max(2,W//14),max(2,H//14)),Image.Resampling.BILINEAR).resize((W,H),Image.Resampling.BICUBIC)
raw=np.clip(raw+(raw-np.array(coarse))*.08,19,255)
height=np.clip(raw*256,0,65535).astype('<u2')
# China includes Taiwan, Hainan and islands from the same province dataset.
outline=json.loads((a/'china_outline.json').read_text(encoding='utf8'))['features'][0]
def area(r):return abs(sum(r[i-1][0]*r[i][1]-r[i][0]*r[i-1][1] for i in range(len(r)))/2)
border=[p[0] for p in polys(outline) if area(p[0])>.08]
rivers=json.loads((a/'rivers50.geojson').read_text(encoding='utf8'))['features']
river_lines=[]
for f in rivers:
 g=f['geometry']; lines=g['coordinates'] if g['type']=='MultiLineString' else [g['coordinates']]
 for line in lines:
  if any(40<p[0]<160 and -10<p[1]<75 for p in line):river_lines.append({'name':f['properties'].get('name_en') or f['properties'].get('name'),'line':line})
data={'w':W,'h':H,'bounds':bounds,'height':base64.b64encode(height.tobytes()).decode(),'land':base64.b64encode(land.tobytes()).decode(),'china':base64.b64encode(cmask.tobytes()).decode(),'chinaSoft':base64.b64encode(np.array(Image.fromarray(cmask).filter(ImageFilter.GaussianBlur(1.8))).tobytes()).decode(),'outline':border,'rivers':river_lines,'borders':[p[0] for f in countries for p in polys(f)]}
from io import BytesIO
bump=Image.fromarray(np.clip(raw,0,255).astype('uint8'))
buf=BytesIO();bump.save(buf,format='PNG')
data['bump']='data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()
import hashlib,subprocess,os
digest=hashlib.sha256((data['height']+data['land']+data['chinaSoft']).encode()+(a/'model_terrain_blender.py').read_bytes()).hexdigest()
data['inputDigest']=digest
bake_path=a/'blender_terrain_normals.json'
baked=json.loads(bake_path.read_text(encoding='utf8')) if bake_path.exists() else {}
if baked.get('inputDigest')!=digest or baked.get('normalFormat')!='int16':
 (a/'asia_terrain_data.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf8')
 subprocess.run([os.environ.get('BLENDER_PYTHON','python'),str(a/'model_terrain_blender.py')],check=True,timeout=180)
 baked=json.loads(bake_path.read_text(encoding='utf8'))
assert baked['vertices']==W*H and baked['inputDigest']==digest
data['bakedNormals']=baked['normals'];data['modelSource']=baked['source']
data_text=json.dumps(data,separators=(',',':'),ensure_ascii=False)
(a/'asia_terrain_data.json').write_text(data_text,encoding='utf8')
# The stable pre-map source is stored inside earth_assets.
backup=a/'推进转场_接地图前.html'
if not backup.exists():raise FileNotFoundError(backup)
# Always build from the pre-map version.
s=backup.read_text(encoding='utf8')
# Paris to a country-wide China view. Coordinates are a framing target, not a city.
s=s.replace('nanjingTag','chinaTag')
s=s.replace('nanjing={lat:32.0603,lon:118.7969}','chinaDestination={lat:35,lon:104}')
import re
s=re.sub(r'\bnanjing\b','chinaDestination',s)
s=s.replace('pos(32.0603,118.7969)','pos(35,104)')
s=s.replace('中国 · 南京','中国').replace('32.06°N / 118.80°E','国家全景')
s=s.replace('巴黎 <span>→</span> 南京','法国巴黎 <span>→</span> 中国')
s=s.replace('法国巴黎 → 中国南京','法国巴黎 → 中国')
s=s.replace("to:'中国·南京'","to:'中国',framingTarget:{lat:35,lon:104}")
s=s.replace("arrival:'南京'","arrival:'中国'").replace("destination:'南京'","destination:'中国'")
s=s.replace('[paris,chinaDestination]','[paris]')
s=s.replace('markerGroup.visible=alpha>0','markerGroup.visible=false')
s=s.replace('3.3+(1.42-3.3)','3.3+(2.35-3.3)')
s=s.replace("t<13?'02 / 越过太平洋'","t<13?'02 / 横越欧亚大陆'")

# East Asia camera narrative supersedes the old France-to-China flight.
intro=(a/'east_asia_intro.js').read_text(encoding='utf8')
journey_js=intro[:intro.index('function updateFlight')]
flight_js=intro[intro.index('function updateFlight'):]
js_start=s.index('function journey(t)');js_end=s.index('\nfunction ui()',js_start)
s=s[:js_start]+journey_js+s[js_end:]
js_start=s.index('function updateFlight()');js_end=s.index('const markerNormal=',js_start)
s=s[:js_start]+flight_js+'\n'+s[js_end:]
overlay_start=s.index("annotation.innerHTML=");overlay_end=s.index('document.body.append(annotation);',overlay_start)
s=s[:overlay_start]+"annotation.innerHTML="+json.dumps('<div id="chinaContextTag" class="cityTag"><strong>中国</strong><span>历史发生地</span></div><div id="japanContextTag" class="cityTag"><strong>日本</strong><span>东亚地理背景</span></div><div class="flightNote"><div class="flightKicker" id="flightStage">01 / 地球远景</div><div class="flightTitle">东亚 <span>→</span> 中国</div><div class="flightSub" id="flightSub">从世界看向东亚</div><div class="flightTrack"><i id="flightProgress"></i></div></div><div class="flightActions"><button id="flightReplay">重播开场</button></div>',ensure_ascii=False)+";"+s[overlay_end:]
s=s.replace('lon:2.3522,lat:48.8566,distance:3.3','lon:128,lat:22,distance:5.5')
s=s.replace("t<6?'01 / 太空出发':t<13?'02 / 横越欧亚大陆':t<20?'03 / 接近亚洲':'04 / 中国上空'", "t<2.2?'01 / 地球远景':t<5.6?'02 / 东亚视角':'03 / 中国全景'")
s=s.replace('m.visible=quiet>0','m.visible=false')
# Keep the geographic China label visible until the globe itself fades away.
s=s.replace("document.querySelector('.flightOverlay').style.opacity=swapped?'0':String(quiet);", "document.querySelector('.flightOverlay').style.opacity=swapped?'0':'1';document.querySelector('.flightNote').style.opacity=String(quiet);document.querySelector('.flightActions').style.opacity=String(quiet);")
s=s.replace("String(swapped||quiet===0)","String(swapped)")

s=s.replace("if(swapped&&!sceneEventSent){sceneEventSent=true;", "if(swapped&&!sceneEventSent){sceneEventSent=true;window.beginAtlasHistory?.();")


s=s.replace('preserveDrawingBuffer:true','preserveDrawingBuffer:false').replace('Math.min(devicePixelRatio,2)','Math.min(devicePixelRatio,1.4)')

# Keep the self-contained entry, but use screen-appropriate textures and a small first globe.
import re
texture_call=re.compile(r"tex\('data:image/jpeg;base64,([A-Za-z0-9+/=]+)',(true|false)\)")
texture_index=[0]
def compact_texture(match):
 i=texture_index[0];texture_index[0]+=1
 im=Image.open(BytesIO(base64.b64decode(match[1]))).convert('RGB')
 im.thumbnail(((2048 if i in [0,4] else 1024),2048),Image.Resampling.LANCZOS)
 b=BytesIO();im.save(b,format='JPEG',quality=86,optimize=True)
 return "tex('data:image/jpeg;base64,"+base64.b64encode(b.getvalue()).decode()+"',"+match[2]+(",true" if i==0 else "")+")"
s=texture_call.sub(compact_texture,s)
s=s.replace('const tex=(uri,color)=>','const tex=(uri,color,primary=false)=>')
# Show the day texture as soon as it is available; other surface maps finish in parallel.
s=s.replace("res(t)},undefined,rej)","if(primary&&!earth){earth=new THREE.Mesh(new THREE.SphereGeometry(1,96,64),new THREE.MeshPhongMaterial({map:t,shininess:12}));scene.add(earth);state.loaded=true;state.firstGlobeReadyMs=performance.now();$('status').textContent='';}res(t)},undefined,rej)")
s=s.replace("earth=new THREE.Mesh(new THREE.SphereGeometry(1,128,96)","if(earth){scene.remove(earth);earth.geometry.dispose();earth.material.dispose();}earth=new THREE.Mesh(new THREE.SphereGeometry(1,128,96)")
s=s.replace("if(atmosphere.material.uniforms", "if(atmosphere&&atmosphere.material.uniforms")

# During flight, gestures add a temporary offset instead of cancelling the timeline.
s=s.replace("let drag=null;const el=renderer.domElement;", "const flightLook={lon:0,lat:0,zoom:0},flightPose={lon:0,lat:0,zoom:0};let drag=null;const el=renderer.domElement;")
s=s.replace("homeMove=null;drag={x:e.clientX,y:e.clientY,lon:state.lon,lat:state.lat};", "if(!state.manual&&state.time<transitionTiming.sceneSwap){drag={flight:true,x:e.clientX,y:e.clientY,lon:flightLook.lon,lat:flightLook.lat};try{el.setPointerCapture(e.pointerId)}catch(_){};return;}homeMove=null;drag={x:e.clientX,y:e.clientY,lon:state.lon,lat:state.lat};")
s=s.replace("if(!drag)return;state.lon=", "if(!drag)return;if(drag.flight){flightLook.lon=THREE.MathUtils.clamp(drag.lon-(e.clientX-drag.x)*.12,-55,55);flightLook.lat=THREE.MathUtils.clamp(drag.lat+(e.clientY-drag.y)*.1,-28,28);return;}state.lon=")
s=s.replace("e.preventDefault();homeMove=null;state.manual=true;", "e.preventDefault();if(!state.manual&&state.time<transitionTiming.sceneSwap){flightLook.zoom=THREE.MathUtils.clamp(flightLook.zoom+e.deltaY*.001,-.5,1);return;}homeMove=null;state.manual=true;")
s=s.replace(" const aspectBoost=", " if(!state.manual){if(!drag||!drag.flight){const decay=Math.exp(-dt*2.8);flightLook.lon*=decay;flightLook.lat*=decay;flightLook.zoom*=decay;}const settle=1-between(state.time,7.5,10.1);for(const k of ['lon','lat','zoom'])flightPose[k]+=(flightLook[k]-flightPose[k])*(1-Math.exp(-dt*18));state.lon+=flightPose.lon*settle;state.lat=THREE.MathUtils.clamp(state.lat+flightPose.lat*settle,-78,78);state.distance+=flightPose.zoom*settle;}\n const aspectBoost=")
s=s.replace("let drag=null;const el=renderer.domElement;","let drag=null;const el=renderer.domElement;")
s=s.replace("function replay(){", "function replay(){flightLook.lon=flightLook.lat=flightLook.zoom=flightPose.lon=flightPose.lat=flightPose.zoom=0;drag=null;")
s=s.replace("window.seekEarthTour=t=>", "window.earthInteractionInfo=()=>({manual:state.manual,playing:state.playing,time:state.time,lat:state.lat,lon:state.lon,offset:{...flightLook},dragging:!!drag});window.seekEarthTour=t=>")
s=s.replace("nextScene.innerHTML=", "nextScene.innerHTML=",1)
start=s.index("nextScene.innerHTML=");end=s.index('document.body.append(nextScene);',start)
s=s[:start]+'''nextScene.innerHTML='<div id="asiaMapMount"></div><header class="refHeader"><b>山河之间</b><span>CHINA · TERRAIN ATLAS</span><button id="atlasBookOpen" type="button" aria-haspopup="dialog">探索图志</button></header><div class="asiaTitle"><span>探索 · 国家地形总览</span><h1>山河之间，中国</h1><p>山脉、江河与城市，在这里展开。</p></div><aside class="exploreCard"><div class="cardArt"><span>南京</span><i>微缩建筑示意</i></div><div class="cardText"><h2>南京 · 阅江楼</h2><p>重檐飞翘，循江而望。</p><button id="exploreNanjing">近看立体地标　　→</button></div><footer>探索节点 01 <span>地形图志 · 南京站</span></footer></aside><nav class="refTimeline"><span>全图</span><span>青藏高原</span><span>天山</span><span>长江流域</span><span class="active">南京</span></nav><div id="mapTools"><button data-mode="pan" aria-pressed="true">✥ 平移</button><button data-mode="rotate" aria-pressed="false">↻ 旋转</button></div><div class="asiaHint">左键环绕 · 右键平移 · 滚轮缩放｜单指环绕，双指平移 / 缩放</div><button id="transitionReplay">重新体验</button><button id="backToGlobe">返回地球</button><button id="mapReset">复位视角</button>';
'''+s[end:]
# Keep archived model assets intact; only current domestic locations enter the atlas.
atlas_nodes=json.loads((a/'city_landmarks_detail.json').read_text(encoding='utf8'))
atlas_nodes=[node for node in atlas_nodes if node['id']!='myanmar']
for node in atlas_nodes:
 for field in ('name','note'):
  node[field]=node[field].replace('北平','北京').replace('今北京；','')
 if node['id']=='yanan':node['chapter']='06 持久抗战 · 07 世界战场 · 08 走向胜利'
# Modern administrative names identify today's location; landmark names stay in cards.
modern_places={
 'lugou':{'name':'北京·丰台','building':'卢沟桥 · 十一孔联拱桥','location':'北京市丰台区','site':'卢沟桥','note':'现属北京市丰台区；卢沟桥保留为史迹名称，模型为十一孔联拱桥示意。','locationSource':'https://wwj.beijing.gov.cn/bjww/wwjzzcslm/1737418/1738088/1742737/523208/index.html'},
 'pingxing':{'name':'大同·灵丘','building':'平型关大捷纪念碑示意','location':'山西省大同市灵丘县','site':'平型关大捷区域','note':'平型关大捷主战场区域位于今山西省大同市灵丘县；此点为战役区域入口，非精确战斗点。','locationSource':'https://www.lingqiu.gov.cn/lqxrmzfz/lyggn/202307/090372e440934f5d91dc830fe983c05f.shtml'},
 'taierzhuang':{'name':'枣庄·台儿庄','building':'台儿庄古城门示意','location':'山东省枣庄市台儿庄区','site':'台儿庄','note':'现属山东省枣庄市台儿庄区；古城门与运河意象为艺术化史迹导航。','locationSource':'https://www.tez.gov.cn/zwgk/zwgkzt/zfgb/202306/P020230628652560953642.pdf'}
}
for node in atlas_nodes:
 if node['id'] in modern_places:node.update(modern_places[node['id']])
# One canonical event list drives markers, directory and book order.
events=json.loads((a/'atlas_events.json').read_text(encoding='utf8'))
templates={n['id']:n for n in atlas_nodes}
event_landmarks=json.loads((a/'event_landmarks.json').read_text(encoding='utf8'))
event_nodes=[]
for i,event in enumerate(events):
 node=dict(templates[event['model']])
 node.update(id=event['id'],mapId=event['id'],name=event['place'],event=event['name'],eventIndex=i,chapter=event['name']+' · '+event['years'])
 node['note']='对应事件：'+event['name']+'。三维模型为所在城市或地区的地标参考，不代表事件现场复原。'
 if event['id']=='nanjing_surrender':node.update(lon=118.809,lat=32.052,site='黄埔路中央军校大礼堂')
 if event['id'] in event_landmarks:node.update(event_landmarks[event['id']])
 event_nodes.append(node)
atlas_nodes=event_nodes
atlas_nodes_text=json.dumps(atlas_nodes,ensure_ascii=False,separators=(',',':'))
chapter_catalog=json.loads((a/'chapter_images'/'manifest.json').read_text(encoding='utf8'))
book_catalog=json.loads((a/'book_images'/'manifest.json').read_text(encoding='utf8'))
def event_art(catalog,folder,key):
 result=[]
 for event in events:
  art=dict(catalog[event[key]])
  override='chapterFile' if folder=='chapter_images' else 'bookFile'
  if event.get(override):art['file']=event[override]
  art.update(title=event['name'],summary=event['summary'],alt=event['name']+'：所属时期情境插画')
  art['src']='data:image/webp;base64,'+base64.b64encode((a/folder/art['file']).read_bytes()).decode()
  if folder=='chapter_images':
   from PIL import Image
   from io import BytesIO
   image=Image.open(a/folder/art['file']).convert('RGB')
   image.thumbnail((768,432),Image.Resampling.LANCZOS)
   small=BytesIO();image.save(small,format='WEBP',quality=86,method=6)
   art['previewSrc']='data:image/webp;base64,'+base64.b64encode(small.getvalue()).decode()

  result.append(art)
 return result
art_records=event_art(chapter_catalog,'chapter_images','art')
assert len({x['file'] for x in art_records})==len(events), 'Every event requires distinct directory art'
book_art=event_art(book_catalog,'book_images','bookArt')
assert len({x['file'] for x in book_art})==len(events), 'Every event requires distinct book art'
code=(a/'asia_terrain.js').read_text(encoding='utf8').replace('__HISTORY_BOOK__',(a/'history_book.js').read_text(encoding='utf8').replace('__BOOK_DATA__',(a/'history_book_data.json').read_text(encoding='utf8')).replace('__BOOK_ART__',json.dumps(book_art,ensure_ascii=False))).replace('__CHAPTER_ART__',json.dumps(art_records,ensure_ascii=False)).replace('__ASIA_DATA__',data_text).replace('__CITY_MODELS__',atlas_nodes_text).replace('__NANJING_MODEL__',(a/'nanjing_yuejiang.json').read_text(encoding='utf8')).replace('__DAY_TERRAIN__','data:image/jpeg;base64,'+base64.b64encode((a/'earth_8k.jpg').read_bytes()).decode()).replace('__BUMP_TERRAIN__','data:image/jpeg;base64,'+base64.b64encode((a/'elevation_4k.jpg').read_bytes()).decode())
scene_src='data:image/webp;base64,'+base64.b64encode((a/'nanjing_surrender_panorama_v3.webp').read_bytes()).decode()
code=code.replace('__NANJING_IMMERSIVE__',(a/'nanjing_immersive.js').read_text(encoding='utf8').replace('__NANJING_SCENE_IMAGE__',json.dumps(scene_src)))
s=s.replace('const smooth01=t=>',code+"\n\nconst smooth01=t=>",1)
s=s.replace('if(!earthTransition.nextScene)renderer.render(scene,camera);','if(!earthTransition.nextScene)renderer.render(scene,camera);else renderAsiaTerrain(dt);',1)
s=s.replace("placeholder:true","placeholder:false",1)
css="""
#nextScene{background:#182421;overflow:hidden}#nextScene::before{display:none}
#asiaMapMount{position:absolute;inset:0}#asiaMapMount canvas{position:absolute;inset:0;touch-action:none}
.asiaTitle{position:absolute;left:4.5vw;top:5.5vh;pointer-events:none}.asiaTitle span{font-size:9px;letter-spacing:3px;color:#8da4ad}.asiaTitle h1{font-size:30px;font-weight:400;letter-spacing:8px;color:#e6d6bd;margin:14px 0 9px}.asiaTitle p{font-size:11px;letter-spacing:3px;color:#96a9ad;margin:0}
.asiaHint{position:absolute;bottom:5vh;left:50%;transform:translateX(-50%);font-size:10px;letter-spacing:2px;color:#9aafb5;pointer-events:none}
.mapLabel{position:absolute;pointer-events:none;color:#b0c2be;font:10px "Microsoft YaHei",sans-serif;letter-spacing:1px;text-shadow:0 1px 4px #000000;white-space:nowrap;transform:translate(-50%,-50%)}.mapLabel.river{color:#a4d1d4;font-size:10px}.mapLabel.city{color:#e4ddd0;font-size:11px;background:#1c3038cc;padding:5px 9px;border-radius:3px;box-shadow:0 3px 14px #23485a12}
#asiaMapMount::after{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 52% 50%,transparent 45%,#040b1755 100%)}
#nextScene button{z-index:4;color:#c9d6d8;background:#182c38a8;border:1px solid #7899a433;border-radius:5px;padding:12px 19px;font-size:11px;backdrop-filter:blur(12px)}#nextScene button:hover{background:#2b424f;color:#fff}#mapReset{position:absolute;right:4.5vw;top:5.5vh}
@media(max-width:700px){.asiaTitle h1{font-size:23px}.asiaHint{bottom:13vh}.mapLabel{font-size:8px}}
"""
css+='\n/* Layout and tone matched to the video\'s opening exploration atlas. */\n.refHeader{position:absolute;left:5%;right:5%;top:24px;display:flex;gap:30px;align-items:center;border-bottom:1px solid #b8c5a422;padding-bottom:20px;color:#c4cbb8;pointer-events:none}.refHeader b{font-family:serif;font-size:20px;font-weight:400;letter-spacing:4px}.refHeader span{font-size:9px;letter-spacing:3px;opacity:.6}.refHeader i{margin-left:auto;font-style:normal;font-size:11px;border:1px solid #b5c6a733;padding:9px 16px}\n.asiaTitle{left:5%;top:15%}.asiaTitle span{color:#a5b493;letter-spacing:2px}.asiaTitle h1{font-family:"Songti SC","SimSun",serif;font-size:29px;letter-spacing:3px;color:#e1e6d5}.asiaTitle p{color:#a8b8a8;font-size:11px;letter-spacing:1px}\n.exploreCard{position:absolute;left:5%;top:33%;width:260px;background:#14241fdd;border:1px solid #a2b19340;color:#d0d9c6;box-shadow:0 15px 45px #0004}.cardArt{height:130px;position:relative;overflow:hidden;background:linear-gradient(155deg,#a7b2a0,#6d8675 45%,#253c32 46%,#12251f 80%)}.cardArt:before{content:"";position:absolute;width:140px;height:70px;left:60px;top:40px;background:linear-gradient(90deg,#8c9680 22%,#34493a 23%,#34493a 30%,#8c9680 31%,#8c9680 45%,#34493a 46%,#34493a 53%,#8c9680 54%,#8c9680 70%,#34493a 71%,#34493a 78%,#8c9680 79%);box-shadow:-9px -10px 0 -3px #a7ac94,9px -10px 0 -3px #a7ac94;transform:perspective(200px) rotateY(-15deg)}.cardArt span{position:absolute;left:16px;bottom:12px;font-family:serif;font-size:25px;color:#edf1df;text-shadow:0 2px 8px #13231d}.cardArt i{position:absolute;right:10px;bottom:15px;font-size:8px;font-style:normal;color:#d5decd}.cardText{padding:15px 17px}.cardText h2{font-family:serif;font-size:22px;font-weight:400;margin:0 0 9px}.cardText p{font-size:10px;color:#98aa98;margin:0 0 14px}#nextScene #exploreNanjing{position:static;padding:6px 0;border:0;border-radius:0;background:transparent;color:#cedabf;font-size:11px;box-shadow:none;cursor:pointer}.exploreCard footer{padding:12px 16px;border-top:1px solid #b6c8a323;font-size:9px;color:#a1b197}.exploreCard footer span{float:right;font-size:8px}\n.refTimeline{position:absolute;left:5%;right:5%;bottom:12%;display:flex;justify-content:space-between;border-top:1px solid #99ae8b40;padding-top:17px;color:#9caf9c;font-size:10px;letter-spacing:2px;pointer-events:none}.refTimeline .active{color:#d8e3c9;border-top:2px solid #c3d2ab;margin-top:-19px;padding-top:17px}.asiaHint{bottom:6%;color:#879d88}.mapLabel{color:#bbceb8}.mapLabel.river{color:#b4c9b8}.mapLabel.city{color:#d3dfc9;background:#182b23b8;border:1px solid #c2d7af26;box-shadow:none}.mapLabel.mountain{font-size:10px;color:#9eb59f}#asiaMapMount::after{background:radial-gradient(ellipse at 64% 48%,transparent 22%,#0c1718aa 100%)}#nextScene button{border-color:#90a58230;background:#17291f88;color:#b5c5aa}#mapReset{top:15%;right:5%}#transitionReplay,#backToGlobe{bottom:5%}\n@media(max-width:700px){.exploreCard{width:180px;top:37%}.cardArt{height:85px}.cardText{padding:10px}.refHeader span{display:none}.asiaTitle{top:16%}.asiaTitle h1{font-size:23px}.refTimeline{font-size:8px;letter-spacing:0;bottom:15%}.asiaHint{bottom:11%;font-size:8px}.exploreCard footer span{display:none}}\n'
css+='\n.cardArt{background-image:url(data:image/png;base64,'+base64.b64encode((a/'nanjing_gate_card.png').read_bytes()).decode()+');background-size:cover;background-position:center}.cardArt:before{display:none}'

css+='\n.exploreCard{display:none}.asiaTitle{left:5%;top:20%}.asiaTitle h1{color:#e0e9e9;font-size:32px}.asiaTitle span{color:#91adb5}.asiaTitle p{color:#9dacae;max-width:180px;line-height:1.9}.refHeader{color:#b9cbd1}.refTimeline{color:#a9aeaa;border-color:#8babb540}.refTimeline .active{color:#d5e8e8;border-color:#abcdd1}.mapLabel.city{background:#12232caa;color:#d1e2e5}.mapLabel.river{color:#9eb7ba}#asiaMapMount::after{background:radial-gradient(ellipse at 55% 50%,transparent 30%,#040b14cc 100%)}#nextScene button{color:#b9cdd3;background:#14212c99}\n'
css+='\n#mapTools{position:absolute;right:5%;top:23%;display:flex;gap:6px}#mapTools button{padding:9px 13px;font-size:11px;cursor:pointer}#mapTools button[aria-pressed=true]{background:#375462b8;border-color:#b0d5db88;color:#e8f7f8}.asiaHint{font-size:10px;letter-spacing:.4px;white-space:nowrap;color:#a5bbc3}@media(max-width:700px){#mapTools{top:27%}.asiaHint{font-size:8px;white-space:normal;text-align:center;width:74%}}\n'
s=s.replace('const black=active?', 'let black=active?')
s=s.replace(' const quiet=active?', ' if(swapped&&(!asiaView||asiaView.time<.65))black=Math.max(black,asiaView?1-THREE.MathUtils.smoothstep(asiaView.time,0,.65):1);\n const quiet=active?')

css+='\n/* Label hierarchy: city plaque, mountain lettering, blue river names. */\n.mapLabel.city{display:flex;align-items:center;gap:8px;padding:9px 12px;border:1px solid #e9ab9899;border-left:3px solid #e9ab98;border-radius:4px;background:#10242eed;color:#fff0e2;box-shadow:0 5px 24px #0008;text-shadow:none;transform:translate(-50%,-100%);z-index:3;letter-spacing:1px}.cityIcon{font-size:22px;color:#f0ba9f}.mapLabel.city strong{display:block;font:600 16px "Microsoft YaHei",sans-serif;letter-spacing:4px}.mapLabel.city small{display:block;font:9px "Microsoft YaHei",sans-serif;color:#bfd0d4;letter-spacing:.4px;margin-top:4px}.mapLabel.city:after{content:"";position:absolute;left:50%;top:100%;height:18px;width:1px;background:#edb097}.mapLabel.mountain{font:italic 12px "SimSun",serif;letter-spacing:2px;color:#d8ded0;opacity:.9;text-shadow:0 2px 4px #081015,0 0 6px #081015}.mapLabel.mountain:before{content:"△ ";font-style:normal;font-size:10px;color:#b9c6b5}.mapLabel.river{font:italic 11px "Microsoft YaHei",sans-serif;color:#83cff4;letter-spacing:2px;text-shadow:0 1px 4px #08233a,0 0 6px #08233a}.exploreCard{display:block;top:35%;width:225px;background:#0a1c27da;border-color:#98b1bc44}.cardArt{height:150px;background-color:#182b35;background-size:contain;background-repeat:no-repeat}.cardText h2{font-size:20px}.cardText p{font-size:10px}.exploreCard footer{display:none}@media(max-width:700px){.exploreCard{display:none}.mapLabel.city strong{font-size:13px}.mapLabel.city small{font-size:8px}.mapLabel.city{padding:6px 8px}.mapLabel.mountain{font-size:10px;letter-spacing:1px}}\n'
css+='\n.cardArt{background-image:url(data:image/png;base64,'+base64.b64encode((a/'nanjing_yuejiang.png').read_bytes()).decode()+')}'
css+='\n.mapLabel.city{transform:translate(24px,-112%)}.mapLabel.city:after{left:-24px;top:100%;width:24px;height:1px}.cardArt{background-size:96% auto}.mapLabel.mountain{background:transparent;border:0;padding:0}\n'
css+='\n.mapLabel.city{gap:5px;padding:6px 8px;transform:translate(12px,-112%)}.mapLabel.city strong{font-size:13px;letter-spacing:2px}.mapLabel.city small{font-size:8px;margin-top:2px}.mapLabel.city .cityIcon{font-size:17px}.mapLabel.city:after{left:-12px;width:12px}\n'
css+='\n.exploreCard{top:28%;width:240px;max-height:64vh;overflow:auto}.cardArt{height:115px}.cardArt span{font-size:11px;bottom:8px;left:10px}.cardArt i{display:none}.cardText{padding:11px 13px}.cardText h2{font-size:16px;line-height:1.5;margin-bottom:6px}.cardText .nodeChapter{font-size:10px;color:#b9d1d8;margin:5px 0}.cardText .nodeNote{font-size:10px;line-height:1.6;color:#a5b8bf;margin:6px 0 8px}.nodeList{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;padding:9px;border-top:1px solid #a9c7d52b}#nextScene .nodeList button{position:static;padding:6px 2px;border-radius:3px;font-size:10px;cursor:pointer}#nextScene .nodeList button[aria-pressed=true]{background:#365365;border-color:#deb29d;color:white}#nextScene .atlasNode{pointer-events:auto;cursor:pointer;position:absolute;z-index:3;background:#132a34c9;padding:3px 5px;gap:4px;transform:translate(8px,-100%);border:1px solid #bac9cd44;border-left:2px solid #d4a58e;border-radius:3px;box-shadow:0 2px 8px #0004;white-space:nowrap}#nextScene .atlasNode strong{font-size:11px;letter-spacing:1px}#nextScene .atlasNode .cityIcon{font-size:12px}#nextScene .atlasNode.selected{background:#254555f0;border-color:#ffd0b2;z-index:5}#nextScene .atlasNode.selected strong{font-size:13px;color:#fff0df}.atlasNode:after{left:-8px!important;width:8px!important}.refTimeline{font-size:9px;letter-spacing:1px;bottom:10%}@media(max-width:700px){.exploreCard{display:block;left:12px;top:auto;bottom:90px;width:205px;max-height:40vh}.cardArt{height:70px}.cardText .nodeNote{display:none}.cardText h2{font-size:13px}.nodeList{gap:3px;padding:5px}.refTimeline{display:none}.asiaTitle h1{font-size:20px}.atlasNode strong{font-size:10px!important}}\n'
css+='.nodeLeaders{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:2}.nodeLeaders line{stroke:#d9bd9d;stroke-width:1;opacity:.65}.asiaTitle{top:14%}.asiaTitle h1{font-size:25px;margin:8px 0}.exploreCard{top:30%}.atlasNode:after{display:none}@media(max-width:700px){.exploreCard{top:auto}}'
css+='\n/* Geographic names stay anchored; landmarks are displayed only in the sidebar. */\n#nextScene .atlasNode{transform:translate(-50%,-100%);padding:3px 6px;gap:3px;transition:none}\n#nextScene .atlasNode strong,#nextScene .atlasNode.selected strong{font-size:11px;letter-spacing:1px}\n#nextScene .atlasNode .cityIcon{font-size:13px}.nodeLeaders{display:none}\n.exploreCard{max-height:65vh}.cardArt.modelStage{height:clamp(140px,21vh,185px);background-image:none!important;background:radial-gradient(ellipse at 50% 45%,#354c58,#132632 75%)}\n.modelStage canvas{display:block;width:100%;height:100%;position:absolute;inset:0}.modelStage span{pointer-events:none;font:9px "Microsoft YaHei",sans-serif}\n#nextScene .modelStage .modelSpin{position:absolute;right:7px;bottom:6px;font-size:9px;padding:3px 5px;cursor:pointer;border-color:#829eac55;background:#152a36b0}\n@media(max-width:700px){.cardArt.modelStage{height:130px}.exploreCard{max-height:48vh}.cardText{padding:7px 10px}}\n'
css+='\n/* Chapter navigation and live landmark viewer, matching the reference hierarchy. */\n.asiaTitle{display:none}.refHeader{left:calc(clamp(280px,27vw,360px) + 28px);border-bottom:0}.refHeader b,.refHeader>span{display:none}\n.historySidebar{position:absolute;left:0;top:0;bottom:75px;width:clamp(280px,27vw,360px);box-sizing:border-box;padding:26px 20px 10px;background:linear-gradient(90deg,#060d15f2,#09131dd9 86%,#0b152000);display:flex;flex-direction:column;gap:12px;z-index:6;pointer-events:auto}\n.sidebarHeading small{font-size:9px;letter-spacing:3px;color:#9d9a85}.sidebarHeading h1{font:600 24px "SimSun",serif;letter-spacing:2px;color:#e7e5d8;margin:8px 0}.sidebarHeading p{font-size:10px;color:#99a4a8;letter-spacing:4px;margin:0}\n.chapterList{display:flex;flex-direction:column;flex-shrink:0;gap:2px}#nextScene .chapterRow{position:static;display:flex;align-items:center;gap:8px;min-height:33px;padding:6px 8px;border:0;border-left:1px solid #b4a88166;border-radius:0;background:transparent;backdrop-filter:none;cursor:pointer;text-align:left;color:#d0d4d3}.chapterRow strong{font:400 12px "Microsoft YaHei",sans-serif;white-space:nowrap}.chapterNum{font-size:11px;color:#b7ab82;min-width:14px}.chapterRow time{font-size:9px;white-space:nowrap;margin-left:auto;color:#9aabaf}#nextScene .chapterRow[aria-pressed=true]{background:linear-gradient(90deg,#b6a37136,transparent);border-left:2px solid #d0bb83;color:#fff3d0}\n.historySidebar .exploreCard{position:relative;inset:auto;width:100%;max-height:none;min-height:0;overflow:auto;flex:1;display:flex;flex-direction:column;background:#0b1723a6;border:1px solid #9aabb32e;box-shadow:none}\n.modelPicker{display:flex;align-items:center;gap:8px;padding:7px 9px;border-bottom:1px solid #b3bbbf22;font-size:9px;color:#acb7bc;flex-shrink:0}.modelPicker>span{white-space:nowrap}.modelPicker select{width:100%;min-width:0;color:#e1dfcf;background:#12212c;border:1px solid #7f98a13a;font-size:10px;padding:4px}\n.historySidebar .cardArt.modelStage{flex:1;min-height:150px;height:auto;max-height:280px;background:radial-gradient(ellipse at 50% 45%,#263847,#09131c 78%)}.historySidebar .cardText{padding:9px 12px;flex-shrink:0}.historySidebar .cardText h2{font-size:16px;color:#e0d8bd}.historySidebar .nodeNote{font-size:9px;line-height:1.45;margin-bottom:0}.historySidebar .nodeChapter{font-size:9px}\n@media(max-height:800px){.historySidebar{padding:18px 15px 8px;gap:8px}.sidebarHeading h1{font-size:20px}.sidebarHeading p{margin-bottom:3px}#nextScene .chapterRow{min-height:28px;padding:5px 7px}.chapterRow strong{font-size:11px}.historySidebar .cardArt.modelStage{min-height:130px}.historySidebar .nodeNote{display:none}.historySidebar .cardText{padding:7px 10px}}\n@media(max-width:700px){.historySidebar{width:228px;bottom:85px;padding:14px 10px;gap:6px}.sidebarHeading h1{font-size:17px}.chapterRow time{font-size:8px}.chapterRow strong{font-size:10px}.chapterList{gap:0}.historySidebar .cardArt.modelStage{min-height:120px}.historySidebar .cardText h2{font-size:13px}.refHeader{left:250px}.historySidebar .nodeNote{display:none}}\n'
css+='\n#nextScene .modelStage .modelZoom{position:absolute;left:8px;bottom:6px;font-size:9px;padding:3px 6px;cursor:pointer;background:#152a36b0;border-color:#829eac55}\n.historySidebar .cardArt.modelStage.expanded{position:fixed;inset:9vh 12vw;height:82vh;max-height:none;min-height:0;z-index:20;box-shadow:0 0 0 200vmax #000c;border:1px solid #aebcc54d}.modelStage.expanded .modelZoom,.modelStage.expanded .modelSpin{font-size:12px!important;padding:8px 14px!important;bottom:14px!important}\n'
css+='.historySidebar .cardArt.modelStage{background-color:#0a1520;background-image:radial-gradient(ellipse at 50% 40%,#2b3e4b,#09131c 80%)!important}'
css+='\n/* Bottom-aligned landmark card and a larger, calmer label hierarchy. */\n.historySidebar{bottom:0;padding-bottom:14px}\n.historySidebar .exploreCard{flex:0 0 auto;margin-top:auto;border:1px solid #9eafb34d;border-radius:9px;background:#0b1724ed;box-shadow:0 12px 30px #0005;overflow:hidden}\n.historySidebar .cardArt.modelStage:not(.expanded){flex:0 0 auto;height:clamp(150px,25vh,260px);min-height:0;max-height:none}\n.historySidebar .modelPicker{padding:9px 11px;color:#bcbba8;background:#14232e;border-color:#97aaad2c}\n.historySidebar .modelPicker select{border-radius:4px;font-size:11px;padding:5px 7px;background:#0d1c27;color:#e5dfcd}\n.historySidebar .cardText{padding:10px 13px}.historySidebar .cardText h2{font-size:18px;letter-spacing:1px;margin-bottom:5px}.historySidebar .nodeChapter{font-size:10px;color:#b7c6c9}\n#nextScene #backToGlobe{left:calc(clamp(280px,27vw,360px) + 24px);bottom:24px}\n.refTimeline{left:calc(clamp(280px,27vw,360px) + 24px);bottom:83px}\n#nextScene .atlasNode{padding:6px 10px;gap:6px;border:1px solid #a4b7b768;border-left:2px solid #b8ac82;border-radius:6px;background:linear-gradient(135deg,#213842ee,#10232bea);color:#f0ece1;box-shadow:0 3px 12px #0006;text-shadow:0 1px 2px #000b;backdrop-filter:blur(5px)}\n#nextScene .atlasNode strong,#nextScene .atlasNode.selected strong{font-family:"Microsoft YaHei","PingFang SC",sans-serif;font-size:16px;font-weight:600;line-height:1.2;letter-spacing:1px}\n#nextScene .atlasNode .cityIcon{font-size:16px;line-height:1;color:#d7c79b}\n#nextScene .atlasNode:hover{border-color:#d9c699;background:linear-gradient(135deg,#344f58f5,#1b333df5)}\n#nextScene .atlasNode.selected{border:1px solid #e2c788;border-left:2px solid #edcf88;background:linear-gradient(135deg,#53616aed,#253d46f2);box-shadow:0 0 0 2px #e1c88b1a,0 4px 16px #0007;color:#fff1d0}\n#nextScene .atlasNode:focus-visible{outline:2px solid #f2d79b;outline-offset:3px}\n.mapLabel.mountain{font-size:14px;letter-spacing:2px;color:#dfe7da}.mapLabel.river{font-size:14px;color:#9cdbef;text-shadow:0 1px 3px #041825,0 0 6px #051a2d}\n@media(max-height:800px){.historySidebar{padding-bottom:12px}.historySidebar .cardText{padding:9px 11px}}\n@media(max-width:700px){.historySidebar{bottom:0;padding-bottom:10px}.historySidebar .cardArt.modelStage:not(.expanded){height:clamp(110px,22vh,170px)}.historySidebar .cardText h2{font-size:15px}#nextScene .atlasNode strong,#nextScene .atlasNode.selected strong{font-size:14px!important}#nextScene .atlasNode{padding:5px 8px}#nextScene #backToGlobe{left:244px;bottom:22px}.mapLabel.mountain,.mapLabel.river{font-size:12px}}\n@media(max-height:620px){.historySidebar .chapterList{min-height:80px;overflow-y:auto;flex:1 1 auto}.historySidebar .cardArt.modelStage:not(.expanded){height:110px}.historySidebar .exploreCard{margin-top:4px}.historySidebar .nodeChapter{display:none}}\n'
css+='\n.historySidebar{gap:10px}.chapterMedia{flex:1 0 90px;min-height:90px;margin:4px 0 8px;overflow:auto;border-radius:5px}.chapterMedia img{display:block;width:100%;height:100%;max-height:280px;object-fit:contain}.historySidebar .exploreCard{margin-top:0;flex-shrink:0}.historySidebar .cardArt.modelStage:not(.expanded){height:clamp(120px,18vh,205px)}\n@media(max-height:800px){.historySidebar{gap:7px}.chapterMedia{flex-basis:80px;min-height:80px}.historySidebar .cardText{padding:7px 10px}.historySidebar .cardText h2{font-size:16px;margin:0 0 3px}.historySidebar .modelPicker{padding:6px 9px}}\n@media(max-height:650px){.historySidebar{overflow:auto}.historySidebar .chapterList{flex:0 0 auto;overflow:visible}.chapterMedia{min-height:60px;flex-basis:60px}.historySidebar .cardArt.modelStage:not(.expanded){height:110px}}\n'
css+='\n/* Compact landscape card keeps the chapter media area open. */\n.historySidebar .exploreCard{display:grid;grid-template-columns:43% minmax(0,1fr);grid-template-rows:auto 1fr;min-height:140px;border-radius:5px}\n.historySidebar .cardArt.modelStage:not(.expanded){grid-column:1;grid-row:1 / 3;width:100%;height:100%;min-height:140px;border-right:1px solid #9eafb326}\n.historySidebar .modelPicker{grid-column:2;grid-row:1;display:block;border:0;padding:10px 9px 0;font-size:9px}\n.historySidebar .modelPicker>span{display:none}.historySidebar .modelPicker select{font-size:10px;width:100%;padding:4px 2px;letter-spacing:0}\n.historySidebar .cardText{grid-column:2;grid-row:2;padding:8px 10px 10px;align-self:center}\n.historySidebar .cardText h2{font-size:15px;line-height:1.5;letter-spacing:0;margin:0 0 6px}\n.historySidebar .nodeChapter{font-size:9px;line-height:1.6;margin:0;color:#adbdbe}.historySidebar .nodeNote{display:none}\n#nextScene .modelStage:not(.expanded) .modelZoom,#nextScene .modelStage:not(.expanded) .modelSpin{font-size:8px;padding:3px 2px;bottom:5px;border-radius:3px}\n#nextScene .modelStage:not(.expanded) .modelZoom{left:4px}#nextScene .modelStage:not(.expanded) .modelSpin{right:4px}\n.chapterMedia{flex:1 0 140px;min-height:140px}\n@media(min-height:900px){.historySidebar .exploreCard{min-height:165px}.historySidebar .cardArt.modelStage:not(.expanded){min-height:165px}}\n@media(max-width:700px){.historySidebar .exploreCard{grid-template-columns:42% minmax(0,1fr);min-height:125px}.historySidebar .cardArt.modelStage:not(.expanded){min-height:125px}.historySidebar .cardText h2{font-size:12px}.historySidebar .cardText{padding:6px}.historySidebar .modelPicker{padding:7px 5px 0}.historySidebar .modelPicker select{font-size:9px}.historySidebar .nodeChapter{font-size:8px}#nextScene .modelStage:not(.expanded) .modelSpin{bottom:24px}.chapterMedia{min-height:100px;flex-basis:100px}}\n@media(max-height:650px){.chapterMedia{min-height:80px;flex-basis:80px}}\n'
css+='\n'+(a/'chapter_images.css').read_text(encoding='utf8')
css+='\n'+(a/'history_book.css').read_text(encoding='utf8')
css+='\n'+(a/'nanjing_immersive.css').read_text(encoding='utf8')
css+='\n/* Stable geographic callouts and their exact terrain anchors. */\n#nextScene .atlasNode{transform:none;transition:none}\n.atlasLeaders{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:2;overflow:hidden}.atlasLeaders line{stroke:#d9c89c;stroke-width:1;opacity:.65}.atlasLeaders circle{fill:#f1d38e;stroke:#152b37;stroke-width:1.5}\n'
css+='\n#label{display:none!important}\n'
s=s.replace('</style>',css+'</style>',1).replace('<title>巴黎飞南京 · 推进转场测试</title>','<title>VR 赋能教育 · 抗战历史沉浸式课堂</title>')
s=s.replace('arrival:8,zoomStart:8,zoomEnd:10,blackStart:9.4,blackFull:10.4,sceneSwap:10.5,end:11.3','arrival:5,zoomStart:5,zoomEnd:5.8,blackStart:5.4,blackFull:5.8,sceneSwap:5.85,end:6.3')
s=s.replace('if(!earthTransition.nextScene)renderer.render(scene,camera);else renderAsiaTerrain(dt);','if(!earthTransition.nextScene){renderer.render(scene,camera);if(state.time>2&&!atlasSurfacePromise)warmAtlasSurface().catch(()=>{atlasSurfacePromise=null});if(state.time>=transitionTiming.blackFull)ensureAtlas();}else renderAsiaTerrain(dt);')
s=s.replace('if(swapped&&(!asiaView||asiaView.time<.65))black=Math.max(black,asiaView?1-THREE.MathUtils.smoothstep(asiaView.time,0,.65):1);','if(swapped&&(!asiaView||asiaView.time<.3))black=Math.max(black,asiaView?1-THREE.MathUtils.smoothstep(asiaView.time,0,.3):1);')
# Reuse the integrated narration, matching and multiple-choice chapter.
nj_start=s.index('function installNanjingImmersive(){')
nj_end=s.index('installNanjingImmersive();',nj_start)+len('installNanjingImmersive();')
s=s[:nj_start]+(a/'nanjing_integrated_lesson.js').read_text(encoding='utf8')+s[nj_end:]
s=s.replace('</style>',(a/'nanjing_integrated_lesson.css').read_text(encoding='utf8')+'</style>',1)
s=s.rsplit('</body>',1)[0]+'<script>'+(a/'skip_intro.js').read_text(encoding='utf8')+'</script></body>'+s.rsplit('</body>',1)[1]
out=root/'抗战历史沉浸式课堂.html';out.write_text(s,encoding='utf8')
print('Built single entry:',out,'bytes',out.stat().st_size,'rivers',len(river_lines))
