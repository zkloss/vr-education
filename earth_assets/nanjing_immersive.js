function installNanjingImmersive(){
 const imageSrc=__NANJING_SCENE_IMAGE__;
 const modal=document.createElement('dialog');modal.id='nanjingImmersive';modal.setAttribute('aria-labelledby','surrenderTitle');
 modal.innerHTML=`<div class="surrenderViewport"><img class="surrenderScene" alt="南京受降大厅历史情境插画：受降席、日方代表与观礼人员" draggable="false"><div class="surrenderShade"></div></div>
 <header class="surrenderHeader"><button data-action="back">← 返回地图</button><span>山河之间 / 历史现场</span><div><button data-action="pause" aria-pressed="false">暂停巡视</button><button data-action="replay">回到受降席</button></div></header>
 <section class="surrenderTitle"><p>1945.09.09 · 上午九时</p><h1 id="surrenderTitle">南京受降</h1><div class="surrenderRule"></div><p class="surrenderPlace">南京 · 原中央军校大礼堂</p><p class="surrenderIntro">山河重光，铭记胜利。<br>走近中国战区受降仪式现场。</p></section>
 <div class="surrenderFocus" aria-live="polite"><span></span><h2></h2><p></p></div>
 <footer class="surrenderFooter"><nav aria-label="现场观察"><button data-step="0" aria-current="step"><small>01</small> 仪式现场</button><button data-step="1"><small>02</small> 签署降书</button><button data-step="2"><small>03</small> 铭记胜利</button></nav><div class="surrenderProgress"><i></i></div><div class="surrenderBottom"><span>拖动环视 · 滚轮缩放 · 方向键转动</span><div><button data-action="quiz">想一想</button><button data-action="book">查看史料 ↗</button></div></div><small class="surrenderCredit">AI 全景情境插画 · 非史料照片或精确复原</small></footer>
 <section class="surrenderQuiz" hidden aria-labelledby="surrenderQuestion"><div><button class="surrenderQuizClose" aria-label="关闭问题">×</button><small>现场思考</small><h2 id="surrenderQuestion">南京受降仪式举行于哪一天？</h2><p>注意区分宣布投降、签署投降书和中国战区受降的日期。</p><div class="surrenderAnswers"><button data-answer="0">1945年8月15日</button><button data-answer="1">1945年9月2日</button><button data-answer="2">1945年9月9日</button></div><p class="surrenderFeedback" aria-live="polite"></p><button data-action="continue">继续观察 →</button></div></section>`;
 document.body.append(modal);
 const image=modal.querySelector('.surrenderScene'),view=modal.querySelector('.surrenderViewport'),quiz=modal.querySelector('.surrenderQuiz');image.src=imageSrc;
 const warm=()=>image.decode().catch(()=>{});if(window.requestIdleCallback)requestIdleCallback(warm,{timeout:3000});else setTimeout(warm,1500);
 const reduced=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;
 const notes=[['01 / 仪式现场','见证受降','1945年9月9日上午9时，中国战区日军投降签字仪式在南京举行。'],['02 / 签署降书','战争结束的见证','冈村宁次代表日军签署降书，何应钦代表中国战区接受投降。'],['03 / 铭记胜利','铭记历史，珍爱和平','从1931年到1945年，十四年艰苦抗战。胜利来之不易，和平值得珍惜。']];
 let raf=0,elapsed=0,last=0,paused=false,step=-1,origin=null,panX=0,panY=0,zoom=0,drag=null,wasPaused=false;

 let panoRenderer=null,panoScene=null,panoCamera=null,panoTexture=null,panoReady=false,dirty=true,yaw=0,pitch=4,fov=80;
 const spots=[{yaw:-12,pitch:1,label:'受降席',step:0},{yaw:17,pitch:-10,label:'降书与代表席',step:1},{yaw:150,pitch:0,label:'观礼区',step:2}];
 const hotspotLayer=document.createElement('div');hotspotLayer.className='surrenderHotspots';view.append(hotspotLayer);
 spots.forEach((spot,i)=>{const b=document.createElement('button');b.className='surrenderHotspot';b.textContent='＋ '+spot.label;b.dataset.hotspot=i;b.onclick=()=>{setPaused(true);elapsed=spot.step*10;setStep(spot.step);dirty=true;};b.onpointerdown=e=>e.stopPropagation();hotspotLayer.append(b);spot.button=b;});
 function direction(lon,lat,r=10){const l=lon*Math.PI/180,p=lat*Math.PI/180;return new THREE.Vector3(r*Math.cos(p)*Math.cos(l),r*Math.sin(p),r*Math.cos(p)*Math.sin(l));}
 function resizePano(){if(!panoRenderer)return;const w=view.clientWidth,h=view.clientHeight;panoRenderer.setSize(w,h,false);panoCamera.aspect=w/h;panoCamera.updateProjectionMatrix();dirty=true;}
 function initPano(){if(panoRenderer)return;try{
   panoRenderer=new THREE.WebGLRenderer({antialias:true,alpha:false});panoRenderer.setPixelRatio(Math.min(devicePixelRatio,2));panoRenderer.domElement.className='surrenderPanoCanvas';view.prepend(panoRenderer.domElement);
   panoScene=new THREE.Scene();panoCamera=new THREE.PerspectiveCamera(fov,1,.1,30);
   panoRenderer.outputColorSpace=THREE.SRGBColorSpace;panoTexture=new THREE.Texture(image);panoTexture.colorSpace=THREE.SRGBColorSpace;panoTexture.anisotropy=Math.min(8,panoRenderer.capabilities.getMaxAnisotropy());panoTexture.wrapS=THREE.RepeatWrapping;panoTexture.repeat.x=-1;panoTexture.offset.x=1;panoTexture.minFilter=THREE.LinearFilter;panoTexture.magFilter=THREE.LinearFilter;
   panoScene.add(new THREE.Mesh(new THREE.SphereGeometry(10,96,64),new THREE.MeshBasicMaterial({map:panoTexture,side:THREE.BackSide})));
   resizePano();image.decode().then(()=>{panoTexture.needsUpdate=true;panoReady=true;image.style.display='none';dirty=true;}).catch(()=>{modal.querySelector('.surrenderBottom>span').textContent='全景图加载失败，请返回后重试';});
 }catch(error){modal.querySelector('.surrenderBottom>span').textContent='当前设备无法显示全景，暂以平面图预览';hotspotLayer.hidden=true;}}
 function renderPano(){if(!panoReady||!dirty)return;dirty=false;panoCamera.fov=fov;panoCamera.updateProjectionMatrix();const front=direction(yaw,pitch,1);panoCamera.lookAt(front);panoCamera.updateMatrixWorld();panoRenderer.render(panoScene,panoCamera);
   spots.forEach(spot=>{const point=direction(spot.yaw,spot.pitch,1),inFront=point.dot(front)>.1,ndc=point.clone().project(panoCamera);const visible=inFront&&Math.abs(ndc.x)<.94&&Math.abs(ndc.y)<.76;spot.button.hidden=!visible;spot.button.style.left=((ndc.x+1)*50)+'%';spot.button.style.top=((1-ndc.y)*50)+'%';});
 }
 window.addEventListener('resize',resizePano);
 function setStep(i){if(i===step)return;step=i;const n=notes[i],box=modal.querySelector('.surrenderFocus');box.querySelector('span').textContent=n[0];box.querySelector('h2').textContent=n[1];box.querySelector('p').textContent=n[2];modal.querySelectorAll('[data-step]').forEach((b,j)=>b.setAttribute('aria-current',j===i?'step':'false'));}
 function setPaused(value){paused=value;const b=modal.querySelector('[data-action="pause"]');b.textContent=value?'继续巡视':'暂停巡视';b.setAttribute('aria-pressed',String(value));}
 function draw(now){if(!modal.open)return;const dt=last?Math.min((now-last)/1000,.05):0;last=now;if(!paused&&!reduced()&&!document.hidden){yaw=(yaw+dt*.7)%360;elapsed+=dt;dirty=true;}renderPano();modal.querySelector('.surrenderProgress i').style.transform=`scaleX(${((yaw%360)+360)%360/360})`;raf=requestAnimationFrame(draw);}
 function close(){if(!modal.open)return;cancelAnimationFrame(raf);drag=null;modal.close();window.atlasImmersiveActive=false;origin?.focus();}
 function restart(){elapsed=0;last=0;panX=panY=zoom=0;yaw=0;pitch=4;fov=80;dirty=true;setStep(0);setPaused(reduced());}
 function open(){if(modal.open)return;origin=document.activeElement;quiz.hidden=true;restart();modal.showModal();initPano();resizePano();window.atlasImmersiveActive=true;if(!reduced())modal.animate([{opacity:0},{opacity:1}],{duration:500,easing:'ease-out'});raf=requestAnimationFrame(draw);}
 modal.querySelector('[data-action="back"]').onclick=close;
 modal.querySelector('[data-action="pause"]').onclick=()=>setPaused(!paused);
 modal.querySelector('[data-action="replay"]').onclick=restart;
 modal.querySelectorAll('[data-step]').forEach(b=>b.onclick=()=>{elapsed=Number(b.dataset.step)*10;setStep(Number(b.dataset.step));const spot=spots[Number(b.dataset.step)];yaw=spot.yaw;pitch=spot.pitch;dirty=true;setPaused(true);});
 modal.querySelector('[data-action="book"]').onclick=()=>{close();window.openAtlasBookChapter(10);};
 function closeQuiz(){quiz.hidden=true;setPaused(wasPaused);modal.querySelector('[data-action="quiz"]').focus();}
 modal.querySelector('[data-action="quiz"]').onclick=()=>{wasPaused=paused;setPaused(true);quiz.hidden=false;modal.querySelector('.surrenderFeedback').textContent='';modal.querySelectorAll('[data-answer]').forEach(b=>{b.removeAttribute('aria-pressed');b.classList.remove('correct','incorrect');});modal.querySelector('[data-answer]').focus();};
 modal.querySelector('.surrenderQuizClose').onclick=closeQuiz;modal.querySelector('[data-action="continue"]').onclick=closeQuiz;
 modal.querySelectorAll('[data-answer]').forEach(b=>b.onclick=()=>{modal.querySelectorAll('[data-answer]').forEach(a=>{a.classList.remove('correct','incorrect');a.setAttribute('aria-pressed',String(a===b));});const yes=b.dataset.answer==='2';b.classList.add(yes?'correct':'incorrect');modal.querySelector('.surrenderFeedback').textContent=yes?'回答正确。1945年9月9日，中国战区受降仪式在南京举行。':'再想一想：8月15日是日本宣布无条件投降的日期，9月2日是日本在“密苏里”号上签署投降书的日期。';});
 modal.addEventListener('cancel',e=>{e.preventDefault();if(!quiz.hidden)closeQuiz();else close();});
 modal.addEventListener('keydown',e=>{if(!quiz.hidden)return;if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){e.preventDefault();setPaused(true);if(e.key==='ArrowLeft')yaw-=5;if(e.key==='ArrowRight')yaw+=5;if(e.key==='ArrowUp')pitch=Math.min(80,pitch+5);if(e.key==='ArrowDown')pitch=Math.max(-80,pitch-5);dirty=true;}});
 view.addEventListener('pointerdown',e=>{if(e.button!==0)return;drag={id:e.pointerId,x:e.clientX,y:e.clientY,px:yaw,py:pitch};view.setPointerCapture(e.pointerId);setPaused(true);view.classList.add('dragging');});
 view.addEventListener('pointermove',e=>{if(!drag||e.pointerId!==drag.id)return;yaw=drag.px-(e.clientX-drag.x)/view.clientWidth*fov*1.7;pitch=Math.max(-80,Math.min(80,drag.py+(e.clientY-drag.y)/view.clientHeight*fov));dirty=true;});
 for(const type of ['pointerup','pointercancel','lostpointercapture'])view.addEventListener(type,()=>{drag=null;view.classList.remove('dragging');});
 view.addEventListener('wheel',e=>{e.preventDefault();fov=Math.max(40,Math.min(90,fov+e.deltaY*.035));dirty=true;setPaused(true);},{passive:false});
 window.openNanjingImmersive=open;window.nanjingImmersiveInfo=()=>({open:modal.open,elapsed,paused,step,quiz:!quiz.hidden,imageReady:image.complete&&image.naturalWidth>0,panX,panY,zoom,yaw,pitch,fov,panoReady,textureSize:[image.naturalWidth,image.naturalHeight],mode:panoReady?'spherical-panorama':'loading'});
}
installNanjingImmersive();
