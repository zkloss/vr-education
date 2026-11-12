from pathlib import Path
import bpy,math
from mathutils import Vector
a=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
stone=mat('grey masonry',(.38,.40,.34));trim=mat('pale stone',(.58,.58,.48));shadow=mat('door darkness',(.055,.075,.055));ground=mat('ground',(.21,.29,.23))
def box(name,loc,scale,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 bevel=o.modifiers.new('soft stone edges','BEVEL');bevel.width=.018;bevel.segments=2;return o
box('wall',(0,0,.9),(5,1.3,1.8),stone);box('cornice',(0,0,1.85),(5.2,1.5,.15),trim)
for x in [-2.1,2.1]:
 box('watchtower',(x,0,1.25),(.8,1.5,2.5),stone);box('tower rim',(x,0,2.55),(1,1.7,.15),trim)
 for dx in [-.34,0,.34]:box('merlon',(x+dx,-.65,2.75),(.17,.25,.3),trim)
for x in [-1.15,0,1.15]:
 # Dark arched recesses are shallow geometry on this illustrative miniature.
 box('gate opening',(x,-.66,.55),(.66,.035,1.10),shadow)
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.33,depth=.04,location=(x,-.67,1.1),rotation=(math.pi/2,0,0));bpy.context.object.data.materials.append(shadow)
for x in [-1.6,-1.2,-.8,-.4,0,.4,.8,1.2,1.6]:box('parapet',(x,-.63,2.05),(.2,.25,.28),trim)
for z in [.3,.6,.9,1.2,1.5]:box('mortar line',(0,-.657,z),(5.01,.012,.012),trim)
box('street',(0,0,-.05),(200,200,.1),ground)
for x in [-6,-4.8,4.8,6]:
 box('distant wall',(x,2,.65),(1.1,2,1.3),stone)
 bpy.ops.mesh.primitive_cone_add(vertices=4,radius1=1.05,depth=.65,location=(x,2,1.63),rotation=(0,0,math.pi/4));bpy.context.object.data.materials.append(trim)
world=bpy.data.worlds.new('green sky');bpy.context.scene.world=world;world.color=(.28,.36,.31)
for loc,power,size in [((-4,-6,8),1500,5),((4,1,5),600,4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(6,-10,5));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.05))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=8
sc=bpy.context.scene;sc.camera=cam;sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.render.resolution_x=640;sc.render.resolution_y=320;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(a/'nanjing_gate_card.png');bpy.ops.render.render(write_still=True)
