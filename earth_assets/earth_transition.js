// Single timeline; only replace the nextScene contents when the map is built.
const transitionTiming=Object.freeze({arrival:8,zoomStart:8,zoomEnd:10,blackStart:9.4,blackFull:10.4,sceneSwap:10.5,end:11.3});
const nextScene=document.createElement('section');nextScene.id='nextScene';nextScene.setAttribute('aria-hidden','true');
nextScene.innerHTML='<div class="nextSceneCenter"><div class="nextSceneRule"></div><h1>下一场景</h1><p>中国地图 · 待制作</p></div><button id="transitionReplay">重新体验</button><button id="backToGlobe">返回地球</button>';
document.body.append(nextScene);
const blackout=document.createElement('div');blackout.id='sceneBlackout';blackout.setAttribute('aria-hidden','true');document.body.append(blackout);
const smooth01=t=>{t=THREE.MathUtils.clamp(t,0,1);return t*t*t*(t*(t*6-15)+10)};
const between=(t,a,b)=>smooth01((t-a)/(b-a));
let sceneEventSent=false;
function updateSceneTransition(){
 const t=state.time,active=!state.manual,zoom=active?between(t,transitionTiming.zoomStart,transitionTiming.zoomEnd):0;
 const swapped=active&&t>=transitionTiming.sceneSwap;
 const black=active?(t<transitionTiming.sceneSwap?between(t,transitionTiming.blackStart,transitionTiming.blackFull):1-between(t,transitionTiming.sceneSwap,transitionTiming.end)):0;
 const quiet=active?1-between(t,transitionTiming.zoomStart,transitionTiming.zoomStart+.65):1;
 document.querySelector('.flightOverlay').style.opacity=swapped?'0':String(quiet);
 document.querySelector('.flightOverlay').style.pointerEvents=active&&quiet===0?'none':'';
 futureRoute.material.opacity=.3*quiet;travelled.material.opacity=.48*quiet;
 for(const m of cityMarkers){m.visible=quiet>0;m.material.transparent=true;m.material.opacity=quiet;}
 markerGroup.visible=markerGroup.visible&&!swapped;markerGroup.scale.setScalar(1-zoom*.7);
 markerRing.material.opacity*=quiet;markerPulse.material.opacity*=quiet;markerDot.material.transparent=true;markerDot.material.opacity=quiet;
 blackout.style.opacity=String(black);blackout.style.pointerEvents=black>0?'auto':'none';
 nextScene.classList.toggle('visible',swapped);nextScene.setAttribute('aria-hidden',String(!swapped));
 renderer.domElement.style.visibility=swapped?'hidden':'visible';
 document.querySelector('.flightOverlay').setAttribute('aria-hidden',String(swapped||quiet===0));
 if(swapped&&!sceneEventSent){sceneEventSent=true;document.dispatchEvent(new CustomEvent('earth:next-scene',{detail:{destination:'南京',placeholder:true}}));}
 if(!swapped)sceneEventSent=false;
 window.earthTransition={time:t,phase:state.manual?'manual':t<transitionTiming.zoomStart?'flight':t<transitionTiming.blackStart?'zoom':t<transitionTiming.blackFull?'fade-out':t<transitionTiming.sceneSwap?'black':t<transitionTiming.end?'fade-in':'next-scene',zoom,blackOpacity:black,nextScene:swapped,timing:transitionTiming};
}
document.getElementById('transitionReplay').onclick=()=>{replay();draw(0)};
document.getElementById('backToGlobe').onclick=()=>{state.time=8;state.playing=false;state.manual=false;journey(8);state.manual=true;state.arrived=true;draw(0)};
