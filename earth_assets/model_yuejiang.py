from pathlib import Path
import bpy,math,json,base64
import numpy as np
from mathutils import Vector
a=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(name,rgb):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.roughness=.82;m.use_nodes=True;bsdf=m.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(*rgb,1);bsdf.inputs['Roughness'].default_value=.82;return m
stone=mat('limestone terrace',(.58,.57,.50));ivory=mat('stone balustrade',(.76,.73,.63));red=mat('vermilion timber',(.40,.065,.035));roofmat=mat('ochre glazed roof',(.49,.36,.13));green=mat('green glazed eaves',(.10,.23,.17));dark=mat('wooden window lattice',(.075,.055,.033));wall=mat('warm plaster',(.62,.48,.30))
def box(name,x,y,z,w,d,h,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,z));o=bpy.context.object;o.name=name;o.dimensions=(w,d,h);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);return o
def roof(name,x,y,z,w,d,h):
 v=[];faces=[];N=12;K=8
 for k in range(K+1):
  t=k/K;hw=w*(.16+.34*t);hd=d*(.035+.465*t)
  for side in range(4):
   for j in range(N):
    u=j/N
    px,py=[(-hw+2*hw*u,-hd),(hw,-hd+2*hd*u),(hw-2*hw*u,hd),(-hw,hd-2*hd*u)][side]
    corner=(abs(px)/hw*abs(py)/hd)**5
    v.append((x+px,y+py,z+h*(1-t)**1.65+.20*t**6*corner))
 for k in range(K):
  for j in range(4*N):
   n=(j+1)%(4*N);faces.append((k*4*N+j,(k+1)*4*N+j,(k+1)*4*N+n,k*4*N+n))
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],faces);me.materials.append(roofmat);o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
 for p in me.polygons:p.use_smooth=True
 box('roof ridge',x,y,z+h+.035,w*.35,.10,.10,green)
 # Thin glazed eaves and the sweeping corners define the roof silhouette.
 for side in range(4):
  pts=[Vector(v[K*4*N+side*N+j]) for j in range(N)]+[Vector(v[K*4*N+((side+1)*N)%(4*N)])]
  cu=bpy.data.curves.new('green eave','CURVE');cu.dimensions='3D';cu.bevel_depth=.035;cu.bevel_resolution=1;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
  for p,q in zip(sp.points,pts):p.co=(*q,1)
  ob=bpy.data.objects.new('green glazed edge',cu);bpy.context.collection.objects.link(ob);ob.data.materials.append(green)
def rail(x,y,z,w,d):
 for yy in [y-d/2,y+d/2]:
  box('railing',x,yy,z+.24,w,.055,.055,ivory)
  for i in range(13):box('baluster',x-w/2+w*i/12,yy,z+.14,.045,.045,.28,ivory)
 for xx in [x-w/2,x+w/2]:
  box('railing',xx,y,z+.24,.055,d,.055,ivory)
  for i in range(9):box('baluster',xx,y-d/2+d*i/8,z+.14,.045,.045,.28,ivory)
box('foundation',0,0,.15,7.2,5.8,.30,stone);box('terrace',0,0,.40,6.7,5.3,.20,ivory)
for i in range(12):box('front stair',0,-3.5+i*.075,.025+i*.035,1.45,.85,.05+i*.07,stone)
for floor in range(4):
 z=.58+floor*1.15;w=4.4-floor*.44;d=3.3-floor*.30
 box('story body',0,0,z+.44,w*.85,d*.82,.88,wall);box('gallery floor',0,0,z,w+.25,d+.25,.12,ivory)
 rail(0,0,z+.02,w+.20,d+.20)
 for xx in [-w/2,-w/4,0,w/4,w/2]:
  for yy in [-d/2,d/2]:
   box('red pillar',xx,yy,z+.43,.11,.11,.86,red)
   if abs(xx)<w/2:box('window',xx,yy*.825,z+.48,w*.18,.035,.47,dark)
 for yy in [-d/4,0,d/4]:
  for xx in [-w/2,w/2]:box('red pillar',xx,yy,z+.43,.11,.11,.86,red)
 box('red lintel',0,-d/2,z+.82,w,.12,.12,red);box('red lintel',0,d/2,z+.82,w,.12,.12,red)
 roof('upturned tier '+str(floor),0,0,z+.90,w+1.0,d+.9,.55 if floor<3 else .88)
for x,y,w,d,z in [(-3.0,.6,2.8,2.6,.65),(-1.8,2.5,3.4,2.6,.65)]:
 box('wing body',x,y,z+.4,w*.8,d*.75,.8,wall);roof('lower side wing',x,y,z+.85,w+.35,d+.35,.65)
 for xx in [-w*.35,0,w*.35]:box('wing red column',x+xx,y-d*.4,z+.4,.12,.12,.8,red)
# Save actual geometry and export a compact material-grouped web mesh from the same scene.
dep=bpy.context.evaluated_depsgraph_get();groups={}
for ob in list(bpy.context.scene.objects):
 if ob.type not in ['MESH','CURVE']:continue
 ev=ob.evaluated_get(dep);me=ev.to_mesh();me.calc_loop_triangles();m=ob.data.materials[0];g=groups.setdefault(m.name,{'color':list(m.diffuse_color[:3]),'v':[],'n':[]});normal_matrix=ob.matrix_world.to_3x3().inverted().transposed()
 for tri in me.loop_triangles:
  for idx in tri.vertices:
   v=ob.matrix_world@me.vertices[idx].co;n=normal_matrix@me.vertices[idx].normal
   g['v'].extend((v.x,v.z,-v.y));g['n'].extend((n.x,n.z,-n.y))
 ev.to_mesh_clear()
out=[]
for name,g in groups.items():out.append({'name':name,'color':g['color'],'positions':base64.b64encode(np.array(g['v'],dtype='<f4').tobytes()).decode(),'normals':base64.b64encode(np.array(g['n'],dtype='<f4').tobytes()).decode()})
(a/'nanjing_yuejiang.json').write_text(json.dumps({'name':'阅江楼风格微缩地标','source':'Blender '+bpy.app.version_string,'meshes':out,'triangles':sum(len(g['v'])//9 for g in groups.values())},separators=(',',':')),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(a/'nanjing_yuejiang.blend'));bpy.ops.export_scene.gltf(filepath=str(a/'nanjing_yuejiang.glb'),export_format='GLB',export_cameras=False,export_lights=False)
world=bpy.data.worlds.new('studio');bpy.context.scene.world=world;world.color=(.18,.23,.28)
for loc,power in [((-8,-10,12),2400),((5,4,8),1600)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=7;o.rotation_euler=(Vector((0,0,2.7))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(10,-14,10));cam=bpy.context.object;cam.rotation_euler=(Vector((-1,0,2.3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=11
sc=bpy.context.scene;sc.camera=cam;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.resolution_x=720;sc.render.resolution_y=560;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(a/'nanjing_yuejiang.png');bpy.ops.render.render(write_still=True)
print('LANDMARK_OK',sum(len(g['v'])//9 for g in groups.values()),flush=True)
