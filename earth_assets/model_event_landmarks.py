from pathlib import Path
import bpy,math,json,base64
import numpy as np
from mathutils import Vector
a=Path(__file__).resolve().parent;out=a/'event_models';out.mkdir(exist_ok=True)
exec((a/'model_yuejiang.py').read_text(encoding='utf8').split("box('foundation'")[0])
grey=mat('grey brick facade',(.38,.40,.39));pale=mat('limestone carved stone',(.65,.66,.62));glass=mat('window dark glass',(.07,.13,.15));slate=mat('slate roof tiles',(.18,.23,.23))

def panel(x,y,z,w,h):
 box('recessed wooden window lattice',x,y,z,w,.05,h,dark)
 for dx in [-w/2,0,w/2]:box('timber mullion',x+dx,y-.04,z,.035,.045,h+.08,red)
 for dz in [-h/2,0,h/2]:box('timber window crossbar',x,y-.045,z+dz,w+.07,.045,.035,red)

def brickwork(w,y,h,start=.3):
 for j in range(int(h/.16)):
  z=start+j*.16
  box('brick mortar horizontal',0,y,z,w,.012,.012,pale)
  for i in range(int(w/.45)):
   x=-w/2+.225+i*.45+(j%2)*.225
   if x<w/2:box('brick mortar vertical',x,y,z+.08,.01,.012,.15,pale)

def tile_roof(z,w,d,h):
 roof('slate tiled roof',0,0,z,w,d,h)
 ob=bpy.context.object
 for item in list(bpy.context.scene.objects):
  if item.type=='MESH' and item.name.startswith('slate tiled roof'):
   item.data.materials.clear();item.data.materials.append(slate)
   wire=item.copy();wire.data=item.data.copy();bpy.context.collection.objects.link(wire);wire.name='slate roof tile seams'
   wire.data.materials.clear();wire.data.materials.append(pale)
   mod=wire.modifiers.new('Roof tile joints','WIREFRAME');mod.thickness=.009;mod.offset=1

def build(eid):
 box('limestone foundation',0,0,.12,8.4,5.4,.24,pale)
 if eid=='beiping':
  box('red plaster gate wall',0,0,1.05,7.3,2.8,1.8,red)
  # Open central passage has visible jambs rather than a printed door.
  box('dark gate recess',0,-1.42,.9,1.5,.04,1.55,dark)
  for x in [-.83,.83]:box('stone gate jamb',x,-1.49,.94,.17,.20,1.72,pale)
  box('stone gate lintel',0,-1.49,1.82,1.85,.2,.17,pale)
  box('gallery balcony stone',0,0,2.04,7.7,3.05,.18,pale)
  box('upper timber hall',0,0,2.70,6.8,2.2,1.2,red)
  for x in [-2.8,-1.85,-.92,0,.92,1.85,2.8]:panel(x,-1.12,2.73,.68,.78)
  for x in [-3.25,-2.32,-1.39,-.46,.46,1.39,2.32,3.25]:box('red timber column',x,-1.24,2.67,.10,.12,1.22,red)
  roof('traditional gate roof',0,0,3.27,8.1,3.8,.75);roof('lower green eaves',0,0,2.04,7.9,3.3,.30)
  rail(0,0,2.12,7.5,3.0)
  for k in range(4):box('stone approach steps',0,-1.8-k*.22,.26-k*.045,2.8,.3,.09,pale)
 elif eid=='xian':
  box('grey brick five bay hall',0,0,.98,7.4,2.4,1.45,grey)
  brickwork(7.4,-1.215,1.45)
  for i in range(5):
   x=(i-2)*1.44;panel(x,-1.29,1.04,1.00,1.10)
   box('timber porch pillar',x-.64,-1.63,1.03,.09,.10,1.48,dark)
  box('porch stone paving',0,-1.5,.30,7.7,.85,.14,pale)
  tile_roof(1.74,8.1,3.5,.78)
  for k in range(4):box('hall front stair',0,-2.0-k*.19,.27-k*.045,2.3,.25,.09,pale)
  for x in [-3.65,3.65]:box('grey side wall',x,0,.99,.13,2.4,1.46,grey)
 elif eid=='nanjing':
  # Contemporary memorial architecture: low granite volumes, solemn open plaza.
  box('granite memorial plaza',0,0,.29,8.0,5.0,.12,pale)
  box('sunken memorial forecourt',0,-.3,.39,5.7,3.4,.10,grey)
  box('granite exhibition hall',.7,1.0,.95,5.3,2.0,1.3,grey)
  ob=box('sloping granite roof',.7,1.0,1.66,5.7,2.3,.18,pale);ob.rotation_euler[1]=-.13
  box('tall remembrance wall',-3.0,.1,1.42,.22,4.2,2.25,grey)
  for x in [-1.2,-.4,.4,1.2,2.0]:box('dark hall glazing',x,-.035,.94,.55,.04,.73,glass)
  for j in range(9):box('granite horizontal joints',.7,-.022,.38+j*.14,5.3,.013,.012,pale)
  for i in range(13):box('memorial paving joints',-3.6+i*.60,-.7,.46,.012,3.8,.012,grey)
  box('quiet reflecting water',1.2,-1.55,.47,3.2,.65,.025,glass)
  box('memorial stone slab',-1.9,-1.45,.88,.20,1.0,.85,pale)
 elif eid=='nanjing_surrender':
  box('brick auditorium body',0,.35,1.38,6.9,3.2,2.3,grey)
  # Pitched western hall roof with a columned entry and tall windows.
  verts=[(-3.65,-1.4,2.56),(3.65,-1.4,2.56),(3.65,2.1,2.56),(-3.65,2.1,2.56),(-3.65,.35,3.55),(3.65,.35,3.55)]
  mesh=bpy.data.meshes.new('pitched slate roof');mesh.from_pydata(verts,[],[(0,1,5,4),(4,5,2,3),(0,4,3),(1,2,5)]);mesh.materials.append(slate);ob=bpy.data.objects.new('pitched slate roof',mesh);bpy.context.collection.objects.link(ob)
  for i in range(40):
   x=-3.6+i*.18
   for yy in [-.53,1.22]:
    ob=box('slate roof tile ribs',x,yy,3.06,.035,2.0,.025,pale);ob.rotation_euler[0]=.515 if yy<.35 else -.515
  box('stone entry portico floor',0,-1.65,.39,3.7,1.15,.20,pale)
  for x in [-1.5,-.5,.5,1.5]:
   bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.12,depth=2.13,location=(x,-1.95,1.55));bpy.context.object.name='stone entrance column';bpy.context.object.data.materials.append(pale)
   for z in [.51,2.57]:box('carved column capital',x,-1.95,z,.32,.32,.14,pale)
  box('stone portico cornice',0,-1.82,2.7,3.9,1.3,.20,pale)
  for x in [-2.8,-2.05,2.05,2.8]:panel(x,-1.27,1.48,.44,1.3)
  for side in [-1,1]:
   for y in [-.65,.15,.95,1.7]:
    box('tall side window glass',side*3.46,y,1.45,.04,.48,1.35,glass)
    box('stone window sill',side*3.5,y,.74,.10,.64,.10,pale)
  box('timber double doors',0,-1.29,1.2,1.25,.06,1.7,dark)
  for k in range(5):box('auditorium front steps',0,-2.3-k*.16,.38-k*.055,3.8,.22,.11,pale)

meta={
 'beiping':('新华门建筑示意','事件关联建筑','https://cpc.people.com.cn/BIG5/33837/2534309.html'),
 'xian':('华清池五间厅示意','事件旧址','https://www.cppcc.gov.cn/zxww/2021/06/18/ARTI1623977956313123.shtml'),
 'nanjing':('南京大屠杀遇难同胞纪念馆示意','现代纪念建筑','https://cpc.people.com.cn/GB/64176/64180/2534073.html'),
 'nanjing_surrender':('中央军校大礼堂示意','受降仪式旧址','https://dfz.nanjing.gov.cn/gzdt/202508/t20250815_5628715.html')}
result={}
for eid,(name,kind,source) in meta.items():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);build(eid)
 for ob in list(bpy.context.scene.objects):
  if ob.type=='MESH' and len(ob.data.vertices)==8:
   mod=ob.modifiers.new('Detailed edge bevel','BEVEL');mod.width=min(.015,min(ob.dimensions)*.13);mod.segments=2
 # Each surface receives a procedural microtexture in the editable Blender file.
 for m in bpy.data.materials:
  if not m.use_nodes:continue
  ns=m.node_tree.nodes;links=m.node_tree.links;bs=ns.get('Principled BSDF')
  noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=85
  bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.018
  links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
 dep=bpy.context.evaluated_depsgraph_get();groups={}
 for ob in list(bpy.context.scene.objects):
  if ob.type not in ['MESH','CURVE'] or not ob.data.materials:continue
  ev=ob.evaluated_get(dep);me=ev.to_mesh();me.calc_loop_triangles();m=ob.data.materials[0];g=groups.setdefault(m.name,{'color':list(m.diffuse_color[:3]),'v':[],'n':[]});nm=ob.matrix_world.to_3x3().inverted().transposed()
  for tri in me.loop_triangles:
   for vi,li in zip(tri.vertices,tri.loops):
    v=ob.matrix_world@me.vertices[vi].co;n=nm@me.corner_normals[li].vector;n.normalize();g['v'].extend((v.x,v.z,-v.y));g['n'].extend((n.x,n.z,-n.y))
  ev.to_mesh_clear()
 meshes=[dict(name=k,color=g['color'],positions=base64.b64encode(np.array(g['v'],dtype='<f4').tobytes()).decode(),normals=base64.b64encode(np.array(g['n'],dtype='<f4').tobytes()).decode()) for k,g in groups.items()]
 result[eid]=dict(building=name,siteKind=kind,siteSource=source,model=dict(source='Blender '+bpy.app.version_string,meshes=meshes,triangles=sum(len(g['v'])//9 for g in groups.values()),detailVersion=3))
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(eid+'.blend')))
 bpy.ops.export_scene.gltf(filepath=str(out/(eid+'.glb')),export_format='GLB',export_cameras=False,export_lights=False)
 print('EVENT_MODEL_OK',eid,result[eid]['model']['triangles'],flush=True)
(a/'event_landmarks.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('ALL_EVENT_MODELS_OK',len(result),flush=True)
