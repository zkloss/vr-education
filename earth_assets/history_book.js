 function installHistoryBook(){
 const records=__BOOK_DATA__,bookArt=__BOOK_ART__,trigger=document.querySelector('#atlasBookOpen');
 const modal=document.createElement('dialog');modal.id='atlasBook';modal.setAttribute('aria-labelledby','bookTitle');
 modal.innerHTML=`<div class="bookToolbar"><div><small>山河之间 · 抗战史料册</small><b id="bookTitle">探索图志</b></div><button class="bookClose" aria-label="合上史料书">合上</button></div><nav class="bookTabs" aria-label="史料书事件目录"></nav><div class="bookDesk"><div class="bookVolume"><div class="bookSpread"><article class="bookPage bookLeft"></article><article class="bookPage bookRight"></article></div><div class="bookCover" aria-hidden="true"><div class="bookCoverFront"><span>山河之间</span><strong>探索图志</strong><i>1931 — 1945</i><small>事件与地点 · 一一对应</small></div><article class="bookPage bookLeft bookCoverInside"></article></div></div></div><footer class="bookFooter"><button class="bookPrev">← 上一事件</button><span class="bookCounter" aria-live="polite"></span><button class="bookNext">下一事件 →</button></footer>`;
 document.body.append(modal);const tabs=modal.querySelector('.bookTabs'),spread=modal.querySelector('.bookSpread'),volume=modal.querySelector('.bookVolume'),left=modal.querySelector('.bookLeft'),right=modal.querySelector('.bookRight'),prev=modal.querySelector('.bookPrev'),next=modal.querySelector('.bookNext');
 let current=0,busy=false,origin=null,phase='closed',lifeToken=0,queuedOpen=null;const lifeAnimations=[];const reduced=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;
 const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function render(){const c=records[current];left.innerHTML=`<div class="bookRunning">事件脉络 <span>${esc(c.years)}</span></div><div class="bookChapter">事件 ${String(current+1).padStart(2,'0')} · ${esc(c.place)}</div><h2>${esc(c.title)}</h2><p class="bookLead">${esc(c.lead)}</p><section class="bookBackground"><small>背景</small><p>${esc(c.background)}</p></section><ol class="bookEvents">${c.events.map(e=>`<li><time>${esc(e[0])}</time><div><h3>${esc(e[1])} <sup>[${e[3]}]</sup></h3><p>${esc(e[2])}</p></div></li>`).join('')}</ol><aside class="bookTakeaway"><small>事件要点</small><p>${esc(c.takeaway)}</p></aside><div class="bookPageNo">${current*2+1}</div>`;
 right.innerHTML=`<div class="bookRunning">图解与理解 <span>${esc(c.years)}</span></div><figure class="bookIllustration"><img src="${bookArt[current].src}" alt="${esc(c.artCaption)}"><figcaption>${esc(c.artCaption)}<small>AI 历史情境插画 · 非史料照片</small></figcaption></figure><aside class="bookQuestion"><small>想一想</small><p>${esc(c.question)}</p></aside><details class="bookMore"><summary>再读一步 · 补充理解</summary><p>${esc(c.extension)}</p></details><details class="bookSourceDetails"><summary>查证资料 · ${c.sources.length} 条出处</summary><p class="bookSourceIntro">正文为依据资料编写的概述，非史料逐字引文。下列链接可联网查阅。</p><div class="bookSources">${c.sources.map((s,i)=>`<section><div class="bookSourceType">[${i+1}] ${esc(s.kind)}</div><h3>${esc(s.title)}</h3><p class="bookOrg">${esc(s.org)}</p><p>${esc(s.note)}</p><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">查阅原文 ↗</a></section>`).join('')}</div></details><div class="bookChecked">正文与插画逐章对应 · 正文概述，插画辅助理解</div><div class="bookPageNo">${current*2+2}</div>`;
 [...tabs.children].forEach((b,i)=>b.setAttribute('aria-current',i===current?'page':'false'));prev.disabled=current===0||busy||phase!=='open';next.disabled=current===records.length-1||busy||phase!=='open';modal.querySelector('.bookCounter').textContent=`第 ${current+1} / ${records.length} 个事件　·　第 ${current*2+1}—${current*2+2} 页`;left.scrollTop=right.scrollTop=0;
 }
 let activeTurn=null;
 async function turn(index){
  if(phase!=='open'||busy||index===current||index<0||index>=records.length)return;
  busy=true;
  const forward=index>current,oldLeft=left.innerHTML,oldRight=right.innerHTML;
  const oldScroll={left:left.scrollTop,right:right.scrollTop};
  current=index;render();
  const newLeft=left.innerHTML,newRight=right.innerHTML;
  const leaf=document.createElement('div');leaf.className='bookLeaf '+(forward?'leafForward':'leafBackward');leaf.setAttribute('aria-hidden','true');
  const front=document.createElement('article'),back=document.createElement('article');
  front.className='bookPage bookLeafFace bookLeafFront '+(forward?'bookRight':'bookLeft');
  back.className='bookPage bookLeafFace bookLeafBack '+(forward?'bookLeft':'bookRight');
  front.innerHTML=forward?oldRight:oldLeft;back.innerHTML=forward?newLeft:newRight;
  leaf.append(front,back);volume.append(leaf);
  front.scrollTop=forward?oldScroll.right:oldScroll.left;
  // Keep the stationary old page underneath until the turning sheet lands.
  if(forward){left.innerHTML=oldLeft;left.scrollTop=oldScroll.left;}
  else{right.innerHTML=oldRight;right.scrollTop=oldScroll.right;}
  const duration=reduced()?1:1100;
  try{
   const animation=leaf.animate([{transform:'rotateY(0deg)'},{transform:`rotateY(${forward?-180:180}deg)`}],{duration,easing:'cubic-bezier(.35,.05,.25,1)',fill:'forwards'});
   activeTurn=animation;
   for(const face of [front,back])face.animate([{boxShadow:'0 2px 8px #30211325'},{boxShadow:'0 12px 38px #30211388',offset:.5},{boxShadow:'0 2px 8px #30211325'}],{duration,easing:'ease-in-out'});
   await animation.finished;
  }catch{}finally{
   leaf.remove();activeTurn=null;busy=false;render();
  }
 }
 records.forEach((c,i)=>{const b=document.createElement('button');b.type='button';b.textContent=String(i+1).padStart(2,'0')+' · '+c.title;b.onclick=()=>turn(i);tabs.append(b);});
 const cover=modal.querySelector('.bookCover'),inside=modal.querySelector('.bookCoverInside');
 const chrome=[tabs,modal.querySelector('.bookFooter')];
 function phaseTo(value){
  phase=value;modal.classList.toggle('bookInMotion',value==='opening'||value==='closing');
  tabs.inert=spread.inert=value!=='open';prev.disabled=current===0||busy||value!=='open';next.disabled=current===records.length-1||busy||value!=='open';
 }
 function stopLife(){for(const a of lifeAnimations)a.cancel();lifeAnimations.length=0;}
 function motion(el,frames,duration,delay=0){
  const a=el.animate(frames,{duration:reduced()?1:duration,delay:reduced()?0:delay,easing:'cubic-bezier(.25,.65,.25,1)',fill:'both'});lifeAnimations.push(a);return a;
 }
 function copyInside(){inside.innerHTML=left.innerHTML;inside.scrollTop=left.scrollTop;}
 async function open(index=0){
  if(modal.open){if(phase==='closing')queuedOpen=index;return;}
  origin=document.activeElement;current=Number.isInteger(index)&&index>=0&&index<records.length?index:0;
  const ticket=++lifeToken;stopLife();phaseTo('opening');render();copyInside();modal.showModal();cover.style.display='block';
  motion(modal,[{opacity:0},{opacity:1}],180);
  motion(volume,[{transform:'translateY(65px) rotateX(18deg) scale(.86)'},{transform:'translateY(0) rotateX(0deg) scale(1)'}],1100);
  motion(left,[{opacity:0},{opacity:0,offset:.22},{opacity:1}],900,140);
  for(const el of chrome)motion(el,[{opacity:0,transform:'translateY(6px)'},{opacity:1,transform:'translateY(0)'}],360,600);
  const flip=motion(cover,[{transform:'rotateY(0deg)'},{transform:'rotateY(-180deg)'}],880,180);
  modal.querySelector('.bookClose').focus();
  try{await Promise.all(lifeAnimations.map(a=>a.finished));}catch{}
  if(ticket!==lifeToken)return;
  cover.style.display='none';stopLife();phaseTo('open');
 }
 async function close(){
  if(!modal.open||phase==='closing')return;
  activeTurn?.finish();await Promise.resolve();
  if(!modal.open||phase==='closing')return;
  const coverFrom=phase==='opening'?getComputedStyle(cover).transform:'rotateY(-180deg)';
  const volumeFrom=getComputedStyle(volume).transform;
  const leftFrom=getComputedStyle(left).opacity;
  const ticket=++lifeToken;stopLife();phaseTo('closing');copyInside();cover.style.display='block';
  for(const el of chrome)motion(el,[{opacity:1},{opacity:0}],220);
  motion(left,[{opacity:leftFrom},{opacity:0}],340,100);
  motion(volume,[{transform:volumeFrom==='none'?'translateY(0) scale(1)':volumeFrom},{transform:'translateY(8px) rotateX(7deg) scale(.97)'}],680);
  const flip=motion(cover,[{transform:coverFrom==='none'?'rotateY(0deg)':coverFrom},{transform:'rotateY(0deg)'}],680);
  try{await flip.finished;}catch{}
  if(ticket!==lifeToken)return;
  const exit=motion(volume,[{transform:'translateY(8px) rotateX(7deg) scale(.97)',opacity:1},{transform:'translateY(85px) rotateX(15deg) scale(.86)',opacity:0}],260);
  motion(modal,[{opacity:1},{opacity:0}],240,20);
  try{await exit.finished;}catch{}
  if(ticket!==lifeToken)return;
  modal.close();cover.style.display='none';stopLife();phaseTo('closed');(origin?.isConnected?origin:trigger).focus();
  if(queuedOpen!==null){const next=queuedOpen;queuedOpen=null;open(next);}
 }
 window.openAtlasBookChapter=index=>open(index);trigger.onclick=()=>open(0);prev.onclick=()=>turn(current-1);next.onclick=()=>turn(current+1);modal.querySelector('.bookClose').onclick=close;modal.addEventListener('cancel',e=>{e.preventDefault();close();});modal.addEventListener('click',e=>{if(e.target===modal)close();});
 modal.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();close();}else if(['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();e.stopPropagation();turn(current+(e.key==='ArrowRight'?1:-1));}});
 window.atlasBookInfo=()=>({open:modal.open,phase,chapter:current+1,busy,pages:records.length*2,sources:records.reduce((n,c)=>n+c.sources.length,0)});
 }
 installHistoryBook();
