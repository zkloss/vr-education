"""Build a web terrain asset in Blender from the atlas elevation grid."""
from pathlib import Path
import base64,json,math
import numpy as np
import bpy

a=Path(__file__).resolve().parent
d=json.loads((a/'asia_terrain_data.json').read_text(encoding='utf8'))
W,H=d['w'],d['h']; L,B,R,T=d['bounds']
h=np.frombuffer(base64.b64decode(d['height']),dtype='<u2').astype(np.float32)
land=np.frombuffer(base64.b64decode(d['land']),dtype=np.uint8)
china=np.frombuffer(base64.b64decode(d['china']),dtype=np.uint8)
soft=np.frombuffer(base64.b64decode(d['chinaSoft']),dtype=np.uint8)
z=np.maximum(0,(h/256-19)/236)*.70+(land>127)*.009+soft/255*.045
xx=np.linspace(L,R,W);lat=np.linspace(T,B,H)
x,y=np.meshgrid((xx-100)*.156,(lat-35)*.18)
coords=np.column_stack((x.ravel(),y.ravel(),z))
i=np.arange(W*H).reshape(H,W)[:-1,:-1].ravel()
f1=np.column_stack((i,i+W,i+1));f2=np.column_stack((i+1,i+W,i+W+1))
f1=f1[np.any(land[f1]>127,axis=1)];f2=f2[np.any(land[f2]>127,axis=1)]
faces=np.concatenate((f1,f2))
bpy.ops.wm.read_factory_settings(use_empty=True)
mesh=bpy.data.meshes.new('Asia numerical relief')
mesh.from_pydata(coords.tolist(),[],faces.tolist());mesh.update()
mesh.polygons.foreach_set('use_smooth',np.ones(len(mesh.polygons),dtype=bool))
ob=bpy.data.objects.new('Asia relief',mesh);bpy.context.collection.objects.link(ob)
normals=np.empty(W*H*3,dtype=np.float32);mesh.vertices.foreach_get('normal',normals)
normals=normals.reshape(-1,3)[:,[0,2,1]];normals[:,2]*=-1
baked={'source':'Blender '+bpy.app.version_string,'vertices':W*H,'inputDigest':d.get('inputDigest'),'normalFormat':'int16',
       'triangles':len(faces),'normals':base64.b64encode(np.clip(normals*32767,-32767,32767).astype('<i2').tobytes()).decode()}
bpy.ops.wm.save_as_mainfile(filepath=str(a/'asia_relief.blend'))
bpy.ops.export_scene.gltf(filepath=str(a/'asia_relief.glb'),export_format='GLB',export_yup=True,export_cameras=False,export_lights=False)
(a/'blender_terrain_normals.json').write_text(json.dumps(baked,separators=(',',':')),encoding='utf8')
print(json.dumps({k:v for k,v in baked.items() if k!='normals'}),flush=True)
