from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
backup=root/'earth_assets'/'巴黎飞南京_美化前备份.html'
if not backup.exists():shutil.copy2(root/'地球漫游_巴黎飞南京版.html',backup)
source=backup.read_text(encoding='utf-8')
source=source.replace('renderer.toneMappingExposure=1.15','renderer.toneMappingExposure=1.02')
source=source.replace('new THREE.Vector2(.45,.45)','new THREE.Vector2(.3,.3)')
source=source.replace('new THREE.AmbientLight(0x779ac0,.38)','new THREE.AmbientLight(0x8ba8ca,.4)')
source=source.replace('new THREE.DirectionalLight(0xfff5e6,2.45)','new THREE.DirectionalLight(0xfff7ed,2.05)')
source=source.replace('state.lon-35,10','state.lon-44,10')
source=source.replace('0xa4d4eb,.48','0x9db7c6,.24').replace('0xc7e3e8,.28','0x9fbbc7,.12').replace('0xffd49a,.95','0xf3cd9c,.62')
source=source.replace('rgba(255,193,90,0.15)','rgba(244,198,125,0.045)')
source=source.replace('chinaBorder.material.opacity=.82+.15*Math.sin(fxTime*.8)','chinaBorder.material.opacity=.54+.04*Math.sin(fxTime*.8)')
source=source.replace('uOcean:{value:null}','uOcean:{value:null},uCloud:{value:null}')
source=source.replace('waterUniforms.uOcean.value=specularMap;earth.material','waterUniforms.uOcean.value=specularMap;waterUniforms.uCloud.value=cloudMap;earth.material')
source=source.replace('uniform sampler2D uOcean;\n float waterHash','uniform sampler2D uOcean;uniform sampler2D uCloud;\n float waterHash')
source=source.replace('diffuseColor.rgb=mix(diffuseColor.rgb,sea,seaMask*uWater*.7);', '''diffuseColor.rgb=mix(diffuseColor.rgb,sea,seaMask*uWater*.62);
 float landMask=1.0-seaMask;
 float cloudShadow=smoothstep(.18,.8,texture2D(uCloud,vec2(fract(vMapUv.x+uTime*.00075+.004),vMapUv.y+.002)).r);
 diffuseColor.rgb*=1.0-cloudShadow*.16;
 float luminance=dot(diffuseColor.rgb,vec3(.2126,.7152,.0722));
 diffuseColor.rgb=mix(vec3(luminance),diffuseColor.rgb,1.05);
 diffuseColor.rgb*=mix(vec3(.97,1.01,1.015),vec3(.97,1.0,.97),landMask);''')
source=source.replace('};earth.material.needsUpdate=true;', '''shader.fragmentShader=shader.fragmentShader.replace('#include <opaque_fragment>',`#include <opaque_fragment>
 float horizon=pow(1.0-max(dot(normal,normalize(vViewPosition)),0.0),3.2);
 gl_FragColor.rgb=mix(gl_FragColor.rgb,vec3(.055,.19,.34),horizon*.24);`);
 };earth.material.needsUpdate=true;''')
source=source.replace("window.earthSurface={specular:'disabled',waveNormal:'removed',water:'smooth diffuse drift'}", "window.earthSurface={specular:'disabled',waveNormal:'removed',water:'smooth diffuse drift',cloudShadows:true,style:'natural atmosphere'}")
# A thin lit atmosphere: stronger on the sunward limb, subdued on the dark side.
start=source.index(' atmosphere=new THREE.Mesh(')
end=source.index('scene.add(atmosphere);',start)+len('scene.add(atmosphere);')
source=source[:start]+''' atmosphere=new THREE.Mesh(new THREE.SphereGeometry(1.023,96,64),new THREE.ShaderMaterial({transparent:true,side:THREE.BackSide,depthWrite:false,blending:THREE.AdditiveBlending,uniforms:{uSun:{value:new THREE.Vector3(1,1,1)}},vertexShader:'varying vec3 vN;varying vec3 vV;varying vec3 vW;void main(){vec4 p=modelViewMatrix*vec4(position,1.0);vN=normalize(normalMatrix*normal);vV=normalize(-p.xyz);vW=normalize(mat3(modelMatrix)*normal);gl_Position=projectionMatrix*p;}',fragmentShader:'varying vec3 vN;varying vec3 vV;varying vec3 vW;uniform vec3 uSun;void main(){float rim=pow(1.0-abs(dot(normalize(vN),normalize(vV))),3.4);float lit=.2+.8*smoothstep(-.3,.65,dot(normalize(vW),normalize(uSun)));vec3 c=mix(vec3(.06,.2,.5),vec3(.25,.58,.9),lit);gl_FragColor=vec4(c,rim*lit*.42);}'}));scene.add(atmosphere);'''+source[end:]
source=source.replace('updateWorld(dt);updateFlight();', 'updateWorld(dt);if(atmosphere)atmosphere.material.uniforms.uSun.value.copy(sun.position).normalize();updateFlight();')
# More depth in the translucent clouds; keep their established movement speed.
source=source.replace('float light=.25+.75*max(dot(normalize(vN),normalize(uSun)),0.0);gl_FragColor=vec4(vec3(.83,.91,1.0)*light,smoothstep(.14,.85,density)*.4);', 'float light=.22+.78*max(dot(normalize(vN),normalize(uSun)),0.0);float shape=smoothstep(.18,.88,density);vec3 color=mix(vec3(.58,.69,.83),vec3(.96,.98,1.0),density)*light;gl_FragColor=vec4(color,shape*.46);')
source=source.replace('<title>法国巴黎 → 中国南京</title>','<title>巴黎飞南京 · 地球精修版</title>')
out=root/'地球漫游_南京精修版.html';out.write_text(source,encoding='utf-8')
for name in ['抗战历史沉浸式课堂.html','地球漫游_巴黎飞南京版.html','地球漫游_法国飞中国版.html']:shutil.copy2(out,root/name)
shutil.copy2(out,Path.cwd()/out.name);shutil.copy2(Path(__file__),root/'earth_assets'/Path(__file__).name)
print('Built polished globe',out.stat().st_size)
