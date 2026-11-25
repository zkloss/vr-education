// Chapter collection: explicit reading confirmation; assessed chapters retain their own criteria.
const albumKey='historyLesson:chapterAlbum:v1';
let albumProgress={};try{albumProgress=JSON.parse(localStorage.getItem(albumKey)||'{}')||{};}catch{}
const album=document.createElement('dialog');album.id='historyChapterAlbum';album.setAttribute('aria-label','抗战历程 · 章节纪念册');document.body.append(album);
let albumCurrent=0,albumOrigin=null;
const albumEsc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const isNanjing=i=>chapters[i]?.nodes[0]==='nanjing_surrender';
const albumDone=i=>!!albumProgress[chapters[i].nodes[0]]?.at;
function saveAlbum(){try{localStorage.setItem(albumKey,JSON.stringify(albumProgress));}catch{}paintAlbumEntry();}
function paintAlbumEntry(){const n=chapters.filter((_,i)=>albumDone(i)).length;albumEntry.innerHTML='<span>✦</span> 章节纪念册 <small>'+n+' / '+chapters.length+'</small>';}
function albumRead(i){if(!Number.isInteger(i)||!chapters[i]||isNanjing(i))return;const id=chapters[i].nodes[0];albumProgress[id]={at:new Date().toISOString(),kind:'reading-confirmed'};saveAlbum();openChapterAlbum(i,true);}
function openAlbumChapter(i){
 if(!chapters[i])return;album.close();
 const nj=document.getElementById('nanjingImmersive');if(nj?.open)nj.querySelector('[data-action=back]').click();
 focusNode(chapters[i].nodes[0],{reveal:false});
 if(isNanjing(i))window.openNanjingImmersive();else window.openAtlasBookChapter(i);
}
function openChapterAlbum(index=selectedChapter,celebrate=false,selectionOnly=false){
 albumCurrent=Number.isInteger(index)&&chapters[index]?index:0;
 if(!album.open)albumOrigin=document.activeElement;
 const i=albumCurrent,c=chapters[i],done=chapters.filter((_,k)=>albumDone(k)).length,all=done===chapters.length;
 let nextIndex=!albumDone(i)?i:chapters.findIndex((_,k)=>k>i&&!albumDone(k));if(nextIndex<0)nextIndex=chapters.findIndex((_,k)=>!albumDone(k));
 const currentDone=albumDone(i),art=chapterArt[i];
 album.innerHTML=`<div class="albumFrame ${celebrate?'albumCelebrate':''} ${selectionOnly?'albumBrowsing':''}"><header class="albumHeader"><div><small>山河之间 · 1931—1945</small><h1>抗战历程<span>章节纪念册</span></h1></div><div class="albumCount"><b>${String(done).padStart(2,'0')}</b><span>/ ${String(chapters.length).padStart(2,'0')} 章</span><button data-album-close aria-label="关闭纪念册" title="关闭纪念册" type="button"><svg class="albumCloseIcon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 6L18 18M18 6L6 18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></button></div></header><div class="albumBody"><section class="albumHero"><img src="${art.src}" alt="${albumEsc(art.alt)}"><div class="albumHeroShade"></div><span class="albumChapterNo">第 ${String(i+1).padStart(2,'0')} 章</span><div class="albumHeroText"><small>${albumEsc(c.years)} / ${albumEsc(c.place)}</small><h2>${albumEsc(c.name)}</h2><p>${currentDone?'这一页，已经留下你的足迹。':'沿着历史的脉络，继续走近这一页。'}</p></div>${currentDone?'<div class="albumStamp"><span>山河之间</span><b>本章完成</b><span>铭记来路</span></div>':''}</section><section class="albumCollection"><div class="albumLead"><span class="albumRule"></span><small>${all?'历程已完整点亮':'每走过一章，留下一个印记'}</small><h2>${all?'山河重光，铭记来路':currentDone?'收好这一章，继续向前':'你的历史足迹'}</h2><p>${all?'愿我们记得来路，也珍惜今日的和平。':`已完成 ${done} 章 · 点击图片选封面，再从右下角进入。`}</p></div><div class="albumTrack" role="progressbar" aria-label="章节完成进度" aria-valuenow="${done}" aria-valuemin="0" aria-valuemax="${chapters.length}"><i style="width:${done/chapters.length*100}%"></i></div><div class="albumGrid">${chapters.map((ch,k)=>`<button class="albumTile ${albumDone(k)?'isDone':''} ${k===i?'isCurrent':''} ${k===nextIndex?'isNext':''}" style="--order:${k}" data-album-chapter="${k}" aria-pressed="${k===i}" aria-label="${albumEsc(ch.name)} · ${albumDone(k)?'已完成':'待学习'}"><div class="albumTileImage"><img src="${chapterArt[k].previewSrc||chapterArt[k].src}" alt=""><em>${String(k+1).padStart(2,'0')}</em>${albumDone(k)?'<span class="albumTileSeal">✓</span>':''}</div><strong>${albumEsc(ch.name)}</strong><small>${albumDone(k)?(isNanjing(k)?'已通关':'已读完'):k===nextIndex?'下一站 →':'待学习'}</small></button>`).join('')}</div><p class="albumFine">图片为教学情境插画。图文章节按确认读完记录，南京章按实际通关记录。</p></section></div><footer class="albumFooter"><span>${all?'十四年抗战 · 胜利来之不易':'一章一印记 · 一步一回望'}</span><div><button data-album-map>返回历史地图</button><button data-album-back>返回当前内容</button><button class="albumPrimary" data-album-next>${currentDone?'重温本章':'进入本章'} · ${albumEsc(c.name)} <span>→</span></button></div></footer></div>`;
 album.querySelector('[data-album-close]').onclick=album.querySelector('[data-album-back]').onclick=()=>{album.close();if(albumOrigin?.isConnected)albumOrigin.focus();};
 album.querySelector('[data-album-map]').onclick=()=>{album.close();const book=document.getElementById('atlasBook');if(book?.open)book.querySelector('.bookClose').click();const nj=document.getElementById('nanjingImmersive');if(nj?.open)nj.querySelector('[data-action=back]').click();};
 album.querySelector('[data-album-next]').onclick=()=>openAlbumChapter(albumCurrent);
 album.querySelectorAll('[data-album-chapter]').forEach(b=>b.onclick=()=>{const scroll=album.querySelector('.albumBody').scrollTop,index=Number(b.dataset.albumChapter);openChapterAlbum(index,false,true);album.querySelector('.albumBody').scrollTop=scroll;album.querySelector('[data-album-chapter="'+index+'"]').focus({preventScroll:true});});
 if(!album.open)album.showModal();album.querySelector('[data-album-close]').focus();
}
const albumEntry=document.createElement('button');albumEntry.className='albumEntry';albumEntry.onclick=()=>openChapterAlbum(selectedChapter);sidebar.querySelector('.sidebarHeading').append(albumEntry);paintAlbumEntry();
window.openHistoryChapterAlbum=openChapterAlbum;
window.openNanjingChapterAlbum=()=>openChapterAlbum(chapters.findIndex((_,i)=>isNanjing(i)));
window.confirmHistoryChapterRead=albumRead;
window.recordNanjingAlbumCompletion=()=>{
 if(!window.nanjingAlbumEligible?.())return false;
 const i=chapters.findIndex((_,k)=>isNanjing(k));if(i<0)return false;
 const id=chapters[i].nodes[0],fresh=!albumProgress[id];albumProgress[id]={at:albumProgress[id]?.at||new Date().toISOString(),kind:'assessed-completion'};saveAlbum();
 if(fresh)openChapterAlbum(i,true);return true;
};
window.historyChapterAlbumInfo=()=>({total:chapters.length,completed:chapters.filter((_,i)=>albumDone(i)).length,current:albumCurrent,open:album.open,records:JSON.parse(JSON.stringify(albumProgress))});
