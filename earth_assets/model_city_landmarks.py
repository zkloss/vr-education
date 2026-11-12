from pathlib import Path
import bpy,math,json,base64
import numpy as np
from mathutils import Vector
a=Path(__file__).resolve().parent
out=a/'city_models';out.mkdir(exist_ok=True)
# Reuse the established roof and railing builders, not the Nanjing building.
exec((a/'model_yuejiang.py').read_text(encoding='utf8').split("box('foundation'")[0])
blue=mat('slate roof',(.075,.14,.19));brick=mat('brick facade',(.34,.29,.24));gold=mat('gold stupa',(.68,.46,.12))
nodes=[
 dict(id='shenyang',name='沈阳',building='大政殿',lon=123.45,lat=41.80,kind='城市',chapter='01 东北的警报',note='八角重檐轮廓；城市导航微缩示意。'),
 dict(id='beiping',name='北平',building='正阳门风格城楼',lon=116.39,lat=39.90,kind='城市',chapter='02 救亡运动 · 03 全民族抗战',note='今北京；城楼作为城市导航，不复原具体战时街景。'),
 dict(id='xian',name='西安',building='钟楼',lon=108.94,lat=34.26,kind='城市',chapter='02 西安事变',note='三重屋檐与方形台基的艺术化微缩。'),
 dict(id='lugou',name='卢沟桥',building='十一孔联拱桥',lon=116.21,lat=39.85,kind='事件',chapter='03 七七事变',note='与北平同一区域，选中后显示局部桥梁地标。'),
 dict(id='shanghai',name='上海',building='四行仓库',lon=121.47,lat=31.24,kind='城市',chapter='04 淞沪抗战',note='仓库窗格、平屋顶与体量示意；非测绘复原。'),
 dict(id='pingxing',name='平型关',building='大捷纪念碑示意',lon=113.68,lat=39.34,kind='战役',chapter='05 两个战场',note='现代纪念性地标；定位为战役区域入口，不代表精确战斗点。'),
 dict(id='taierzhuang',name='台儿庄',building='古城门示意',lon=117.73,lat=34.56,kind='战役',chapter='05 台儿庄战役',note='城门、运河意象，艺术化区域导航地标。'),
 dict(id='wuhan',name='武汉',building='黄鹤楼',lon=114.30,lat=30.54,kind='城市',chapter='05 武汉会战',note='采用现代城市地标意象，不作为1938年原貌。'),
 dict(id='yanan',name='延安',building='宝塔',lon=109.50,lat=36.59,kind='城市',chapter='06 持久抗战 · 08 走向胜利',note='八角九层宝塔微缩示意。'),
 dict(id='myanmar',name='缅甸',building='仰光大金塔',lon=96.15,lat=16.80,kind='区域',chapter='07 国际联系 · 远征军',note='仰光地标作为区域入口，不表示远征军战斗发生于塔址。')]

def cyl(name,x,y,z,r,h,m,n=16,r2=None):
 bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r,radius2=r if r2 is None else r2,depth=h,location=(x,y,z));o=bpy.context.object;o.name=name;o.data.materials.append(m);return o
def arch(x,y,z,r,d,top,m):
 # Extruded spandrel above a genuine arched opening.
 v=[];n=18
 for yy in [y-d/2,y+d/2]:
  for i in range(n+1):
   t=math.pi-math.pi*i/n;xx=x+r*math.cos(t);zz=z+r*math.sin(t);v.extend([(xx,yy,zz),(xx,yy,top)])
 f=[];stride=2*(n+1)
 for i in range(n):
  k=2*i;f.extend([(k,k+2,k+3,k+1),(stride+k+1,stride+k+3,stride+k+2,stride+k),(k,stride+k,stride+k+2,k+2),(k+1,k+3,stride+k+3,stride+k+1)])
 f.extend([(0,1,stride+1,stride),(2*n,stride+2*n,stride+2*n+1,2*n+1)])
 me=bpy.data.meshes.new('arch');me.from_pydata(v,[],f);ob=bpy.data.objects.new('arched stone span',me);bpy.context.collection.objects.link(ob);me.materials.append(m)
def gate():
 box('left pier',-1.8,0,1,2.1,2.7,2,brick);box('right pier',1.8,0,1,2.1,2.7,2,brick);arch(0,0,.55,.75,2.7,2,brick)
 for x in [-2.8,-2,-1.2,-.4,.4,1.2,2,2.8]:box('battlement',x,-1.22,2.2,.45,.25,.45,stone)
 box('red upper hall',0,0,2.65,4,2.3,1.25,red);roof('upper sweeping roof',0,0,3.3,5.5,3.5,.65)
 roof('lower eaves',0,0,2.6,5.8,3.8,.35)
 for x in [-1.5,-.75,0,.75,1.5]:box('windows',x,-1.17,2.8,.32,.05,.5,dark)
def build(id):
 box('stone plinth',0,0,.1,6.5,4.5,.2,stone)
 if id=='shenyang':
  cyl('octagonal terrace',0,0,.35,2.7,.5,ivory,8)
  cyl('octagonal hall',0,0,1.3,1.9,1.6,red,8)
  for z,r in [(2.1,2.6),(3.1,2.05)]:
   cyl('eight sided roof',0,0,z,r,.8,roofmat,8,.3);cyl('green eaves',0,0,z-.4,r+.07,.10,green,8)
  cyl('finial',0,0,3.8,.17,.7,gold,12,0)
  for i in range(8):
   t=2*math.pi*i/8;cyl('pillar',1.95*math.cos(t),1.95*math.sin(t),1.3,.09,1.6,red,8)
 elif id in ['beiping','taierzhuang']:
  gate()
  if id=='taierzhuang':
   box('water strip',0,-2.05,.16,6.4,.5,.06,blue)
 elif id=='xian':
  box('high square base',0,0,.75,4.8,4.8,1.4,brick)
  box('front tunnel shadow',0,-2.41,.62,1.0,.02,1.0,dark)
  for i in range(3):
   z=1.5+i*.85;w=4.8-i*.8;box('timber floor',0,0,z+.3,w*.68,w*.68,.65,red);roof('triple eaves',0,0,z+.6,w,w,.65)
 elif id=='lugou':
  box('river',0,0,.17,8,3.6,.05,blue)
  for i in range(11):
   x=-3.5+i*.7;arch(x,0,.25,.28,1.2,1.13,ivory)
   if i<10:box('pier',x+.35,0,.58,.15,1.35,.8,stone)
  box('bridge deck',0,0,1.16,7.9,1.4,.16,stone)
  for y in [-.68,.68]:
   box('parapet',0,y,1.46,7.9,.09,.16,ivory)
   for i in range(24):
    x=-3.8+i*7.6/23;box('stone post',x,y,1.43,.10,.11,.46,ivory);cyl('lion marker',x,y,1.74,.09,.15,stone,8,.04)
 elif id=='shanghai':
  box('warehouse',0,0,1.9,5.8,3.3,3.6,brick)
  for z in [.65,1.2,1.75,2.3,2.85,3.4]:
   box('floor sill',0,-1.68,z-.25,5.8,.09,.05,stone)
   for x in [-2.5,-1.8,-1.1,-.4,.4,1.1,1.8,2.5]:box('warehouse window',x,-1.67,z,.32,.05,.35,dark)
  box('roof cornice',0,0,3.76,6.05,3.55,.18,ivory);box('roof tower',1.9,.4,4,1.1,1.2,.5,brick)
 elif id=='pingxing':
  for k in range(4):box('memorial steps',0,0,.18+k*.18,5.8-k*.65,3.8-k*.4,.22,ivory)
  box('obelisk base',0,0,1.05,1.9,1.6,.55,brick)
  cyl('tapered memorial shaft',0,0,2.8,1.0,3.1,stone,4,.55)
  box('central inscription panel',0,-.61,2.8,.34,.03,1.7,dark)
 elif id=='wuhan':
  for i in range(5):
   z=.35+i*.85;w=4.8-i*.45;box('tower story',0,0,z+.35,w*.61,w*.61,.72,red);roof('crane tower roof',0,0,z+.7,w,w,.45)
   for x in [-w*.3,w*.3]:
    for y in [-w*.3,w*.3]:cyl('gallery pillar',x,y,z+.35,.06,.7,red,8)
 elif id=='yanan':
  for i in range(9):
   z=.3+i*.48;r=1.25-i*.073;cyl('octagonal brick storey',0,0,z+.22,r,.44,wall,8);cyl('brick eave',0,0,z+.45,r+.13,.12,stone,8,r+.03)
   box('arched window dark',0,-r*.93,z+.23,.20,.03,.25,dark)
  cyl('pointed crown',0,0,4.95,.7,.5,stone,8,0)
 elif id=='myanmar':
  for k in range(4):cyl('terrace',0,0,.25+k*.22,2.7-k*.3,.24,ivory,32)
  profile=[(1.0,1.5),(1.25,1.65),(1.65,1.5),(2.2,1.18),(2.6,.8),(2.9,.48),(3.6,.32),(4.2,.18),(5.4,0)]
  for (z,r),(z2,r2) in zip(profile,profile[1:]):cyl('bell stupa',0,0,(z+z2)/2,r,z2-z,gold,32,r2)
  for x in [-2,2]:
   for y in [-1.7,1.7]:cyl('small stupa',x,y,.75,.4,1.1,gold,16,0)

def export_model(node):
 dep=bpy.context.evaluated_depsgraph_get();groups={}
 for ob in list(bpy.context.scene.objects):
  if ob.type not in ['MESH','CURVE']:continue
  ev=ob.evaluated_get(dep);me=ev.to_mesh();me.calc_loop_triangles();m=ob.data.materials[0];g=groups.setdefault(m.name,{'color':list(m.diffuse_color[:3]),'v':[],'n':[]});nm=ob.matrix_world.to_3x3().inverted().transposed()
  for tri in me.loop_triangles:
   for idx in tri.vertices:
    v=ob.matrix_world@me.vertices[idx].co;n=nm@me.vertices[idx].normal;g['v'].extend((v.x,v.z,-v.y));g['n'].extend((n.x,n.z,-n.y))
  ev.to_mesh_clear()
 meshes=[dict(name=k,color=g['color'],positions=base64.b64encode(np.array(g['v'],dtype='<f4').tobytes()).decode(),normals=base64.b64encode(np.array(g['n'],dtype='<f4').tobytes()).decode()) for k,g in groups.items()]
 node['model']=dict(meshes=meshes,triangles=sum(len(g['v'])//9 for g in groups.values()))
 id=node['id'];bpy.ops.wm.save_as_mainfile(filepath=str(out/(id+'.blend')));bpy.ops.export_scene.gltf(filepath=str(out/(id+'.glb')),export_format='GLB')
 world=bpy.data.worlds.new('studio');bpy.context.scene.world=world;world.color=(.2,.25,.3)
 for loc,power in [((-7,-9,10),1800),((4,3,8),1000)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=6;o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=(9,-12,9));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,2))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=10
 sc=bpy.context.scene;sc.camera=cam;sc.render.engine='CYCLES';sc.cycles.samples=8;sc.cycles.use_denoising=True;sc.render.resolution_x=420;sc.render.resolution_y=320;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(out/(id+'.png'));bpy.ops.render.render(write_still=True)
 node['preview']='data:image/png;base64,'+base64.b64encode((out/(id+'.png')).read_bytes()).decode()
 print('MODEL_OK',id,node['model']['triangles'],flush=True)

for node in nodes:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);build(node['id']);export_model(node)
nanjing=json.loads((a/'nanjing_yuejiang.json').read_text(encoding='utf8'))
nodes.insert(5,dict(id='nanjing',name='南京',building='阅江楼',lon=118.78,lat=32.09,kind='城市',chapter='04 南京历史 · 08 中国战区受降',note='现有阅江楼模型，作为现代导航地标；非1937年原貌。',model=nanjing,preview='data:image/png;base64,'+base64.b64encode((a/'nanjing_yuejiang.png').read_bytes()).decode()))
(a/'city_landmarks.json').write_text(json.dumps(nodes,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('ALL_MODELS_OK',len(nodes),flush=True)
