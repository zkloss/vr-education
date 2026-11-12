(()=>{
const b=document.createElement('button');b.id='njSkipIntro';b.textContent='跳过开场动画 · Esc';b.setAttribute('aria-label','跳过开场动画，直接进入中国地图');document.body.append(b);
function active(){return window.earthTour&&!window.atlasImmersiveActive&&window.earthTour.time<(window.earthTransition?.timing?.end||6.3)&&!window.earthTour.manual;}
function skip(){if(active()&&window.seekEarthTour){window.seekEarthTour(window.earthTransition?.timing?.end||6.3);b.hidden=true;}}
b.onclick=skip;document.addEventListener('keydown',e=>{if(e.key==='Escape'&&active()){e.preventDefault();e.stopImmediatePropagation();skip();}},true);
let previous=0;function update(now){requestAnimationFrame(update);if(now-previous<150)return;previous=now;b.hidden=!active();}requestAnimationFrame(update);
window.skipEarthIntro=skip;
})();
