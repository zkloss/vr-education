// Camera framing only: this opening does not depict a military movement route.
function journey(t){
 // One camera track with a nonzero zoom speed across all visible stages.
 const u=THREE.MathUtils.clamp(t/transitionTiming.sceneSwap,0,1),turn=u*u*(3-2*u);
 state.lat=THREE.MathUtils.lerp(22,35,turn);state.lon=THREE.MathUtils.lerp(128,104,turn);
 state.distance=5.5*Math.pow(2.35/5.5,u);
}
function updateFlight(){
 flightProgress=THREE.MathUtils.clamp(state.time/transitionTiming.sceneSwap,0,1);
 futureRoute.visible=false;travelled.visible=false;plane.visible=false;
 const cam=camera.position.clone().normalize();
 for(const [lat,lon,id] of [[35,104,'chinaContextTag'],[36,138,'japanContextTag']]){
  const w=pos(lat,lon,1.012),v=w.clone().normalize().dot(cam)>1/state.distance+.015,p=w.project(camera),node=document.getElementById(id);
  const isChina=id==='chinaContextTag';
  const showTime=isChina?(state.manual||state.time>=.35):(!state.manual&&state.time>=.8&&state.time<3.6);
  node.style.display=showTime&&v&&Math.abs(p.x)<.9&&Math.abs(p.y)<.9?'block':'none';
  if(isChina)node.querySelector('strong').style.fontSize=THREE.MathUtils.clamp(15+(5.5-state.distance)*3,15,24)+'px';
  node.style.left=((p.x*.5+.5)*innerWidth)+'px';node.style.top=((-p.y*.5+.5)*innerHeight)+'px';
 }
 const stage=state.manual?'自由浏览':state.time<1.5?'01 / 地球远景':state.time<3.6?'02 / 东亚 · 中国与日本':'03 / 中国全景';
 document.getElementById('flightStage').textContent=stage;
 document.getElementById('flightSub').textContent=state.manual?'拖动旋转 · 滚轮缩放':state.time<1.5?'从世界看向东亚':state.time<3.6?'观察中国与日本的地理位置':'1931年 · 从沈阳的九一八事变开始';
 document.getElementById('flightProgress').style.width=(flightProgress*100)+'%';
 window.earthFlight={progress:flightProgress,from:'地球远景',via:'东亚 · 中国与日本',to:'中国全景',firstEvent:'沈阳 · 九一八事变',cameraOnly:true,duration:transitionTiming.end,manual:state.manual};
}
