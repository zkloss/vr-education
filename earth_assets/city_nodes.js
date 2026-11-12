 const nodeData=__CITY_MODELS__,nodeObjects=[];let selectedNode='nanjing';
 function nodeLabel(node){
  const el=document.createElement('button');el.className='mapLabel city atlasNode';el.type='button';el.title=node.name;el.innerHTML='<span class="cityIcon">·</span><strong>'+node.name+'</strong>';el.onclick=e=>{e.stopPropagation();focusNode(node.id)};nextScene.append(el);labels.push({el,p:at(node.lon,node.lat,.035),node});return el;
 }
 for(const node of nodeData)nodeObjects.push({node,el:nodeLabel(node)});
 const card=document.querySelector('.exploreCard');
 card.innerHTML='<div class="cardArt modelStage" aria-label="地标三维自动旋转展示"><button class="modelSpin" aria-pressed="true">暂停旋转</button></div><div class="cardText"><h2></h2><p class="nodeChapter"></p><p class="nodeNote"></p></div><div class="nodeList" aria-label="地点列表"></div>';
 const stage=card.querySelector('.modelStage'),previewScene=new THREE.Scene();
 const previewRenderer=new THREE.WebGLRenderer({antialias:true,alpha:true});previewRenderer.setPixelRatio(Math.min(devicePixelRatio,1.5));previewRenderer.outputColorSpace=THREE.SRGBColorSpace;previewRenderer.toneMapping=THREE.ACESFilmicToneMapping;previewRenderer.toneMappingExposure=1.25;stage.prepend(previewRenderer.domElement);
 const previewCamera=new THREE.PerspectiveCamera(32,1,.01,100);
 previewScene.add(new THREE.HemisphereLight(0xe5f4ff,0x59616a,2));
 const previewKey=new THREE.DirectionalLight(0xffedcf,3);previewKey.position.set(3,5,4);previewScene.add(previewKey);
 const previewFill=new THREE.DirectionalLight(0xb0dfff,1.5);previewFill.position.set(-4,2,-3);previewScene.add(previewFill);
 const modelCache=new Map(),preview={renderer:previewRenderer,scene:previewScene,camera:previewCamera,stage,group:null,spinning:true,elapsed:0};
 function sizePreview(){const w=stage.clientWidth,h=stage.clientHeight;if(w<1||h<1)return;previewRenderer.setSize(w,h,false);previewCamera.aspect=w/h;previewCamera.updateProjectionMatrix();}
 new ResizeObserver(sizePreview).observe(stage);sizePreview();
 function showModel(node){
  if(preview.group)previewScene.remove(preview.group);
  let pivot=modelCache.get(node.id);
  if(!pivot){
   const model=new THREE.Group();
   for(const part of node.model.meshes){const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(new Float32Array(unpack(part.positions).buffer),3));geo.setAttribute('normal',new THREE.BufferAttribute(new Float32Array(unpack(part.normals).buffer),3));model.add(new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:new THREE.Color(...part.color),roughness:.82,metalness:.03})));}
   const box=new THREE.Box3().setFromObject(model),center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3());model.position.sub(center);const scale=2/Math.max(size.x,size.y,size.z,.001);model.scale.setScalar(scale);model.position.multiplyScalar(scale);pivot=new THREE.Group();pivot.add(model);modelCache.set(node.id,pivot);
  }
  pivot.rotation.set(0,.5,0);preview.group=pivot;previewScene.add(pivot);previewCamera.position.set(0,1.15,4.5);previewCamera.lookAt(0,0,0);sizePreview();previewRenderer.render(previewScene,previewCamera);
 }
 const spin=card.querySelector('.modelSpin');spin.onclick=e=>{e.stopPropagation();preview.spinning=!preview.spinning;spin.textContent=preview.spinning?'暂停旋转':'继续旋转';spin.setAttribute('aria-pressed',String(preview.spinning));};
 const list=card.querySelector('.nodeList');for(const node of nodeData){const b=document.createElement('button');b.type='button';b.dataset.node=node.id;b.textContent=node.name;b.title=node.building;b.onclick=()=>focusNode(node.id);list.append(b)}
 function focusNode(id){
  const node=nodeData.find(n=>n.id===id);if(!node)return;selectedNode=id;showModel(node);
  card.querySelector('h2').textContent=node.name+' · '+node.building;card.querySelector('.nodeChapter').textContent=node.chapter;card.querySelector('.nodeNote').textContent=node.note;
  for(const o of nodeObjects)o.el.classList.toggle('selected',o.node.id===id);
  for(const b of list.children)b.setAttribute('aria-pressed',String(b.dataset.node===id));
 }
 document.querySelector('.refTimeline').innerHTML='<span>1931—1945 · 历史探索地点</span><span>点击地名 · 左侧查看三维地标</span><span>11处地点</span>';
 window.focusAtlasNode=focusNode;focusNode('nanjing');
