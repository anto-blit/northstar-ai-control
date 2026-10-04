// The scene definitions, dialogue, durations and sound above are the original source.
const $ = id => document.getElementById(id);
const params = new URLSearchParams(location.search);
let ep = Math.max(0, Math.min(2, (Number(params.get('ep')) || 1) - 1));
ep = Math.floor(ep);
let idx = 0, elapsed = 0, playing = false, last = 0, raf = 0, ended = false;
let started = false, finished = false, watched = 0;
const embedded = params.get('embed') === '1';
const vertical = params.get('format') === 'vertical';
document.body.classList.toggle('embedded', embedded);
document.body.classList.toggle('vertical', vertical);
const stage=$('stage'), box=$('box'), cap=$('caption'), overlay=$('overlay');
const playBtn=$('playBtn'), segsEl=$('segs'), timeEl=$('time');
const S=()=>EPS[ep].scenes;
const total=()=>S().reduce((a,s)=>a+s.d,0);
const fmt=ms=>{const s=Math.floor(ms/1000);return Math.floor(s/60)+':'+String(s%60).padStart(2,'0');};
const siteBase = new URL('../', location.href);
const watchURL = new URL(PIP_META[ep].slug+'/', location.href);
function message(type, extra={}) {
  const data={source:'northstar-pip',type,episode:ep+1,scene:PIP_META[ep].scenes[idx].slug,...extra};
  if(parent!==window) parent.postMessage(data, location.origin==='null'?'*':location.origin);
  else window.dispatchEvent(new CustomEvent('northstar:pip',{detail:data}));
}
function track(event) { message('metric',{event,watchedSeconds:Math.round(watched/1000),durationSeconds:total()/1000,placement:embedded?'embedded':'player'}); }
function notifyHeight(){message('resize',{height:Math.ceil(document.documentElement.getBoundingClientRect().height)});}
function progress(){
  segsEl.querySelectorAll('i').forEach((f,i)=>f.style.width=(i<idx?100:i===idx?Math.min(100,elapsed/S()[i].d*100):0)+'%');
  let done=elapsed;for(let i=0;i<idx;i++)done+=S()[i].d;
  timeEl.textContent=fmt(done)+' / '+fmt(total());
}
function render(){
  const sc=S()[idx];stage.innerHTML=sc.svg();cap.textContent=sc.cap;stage.setAttribute('aria-label',sc.cap);
  $('end-actions').hidden=idx!==S().length-1;
  progress();Sound.key=null;
  if(playing)Sound.scheduleScene(0,idx===S().length-1,sc.d);
  notifyHeight();
}
function setPlaying(p){
  playing=p;box.classList.toggle('paused',!p);if(p)box.classList.remove('is-poster');playBtn.textContent=p?'Ⅱ':'▶';playBtn.setAttribute('aria-label',p?'Pause':'Play');
  cancelAnimationFrame(raf);
  if(p){
    if(!started){started=true;track('play');}
    message('playing');overlay.hidden=true;Sound.start();
    if(Sound.key!==ep+':'+idx)Sound.scheduleScene(elapsed,idx===S().length-1,S()[idx].d);
    last=performance.now();raf=requestAnimationFrame(tick);
  }else Sound.pause();
}
function tick(t){
  if(!playing)return;
  const delta=t-last;elapsed+=delta;watched+=delta;last=t;
  if(elapsed>=S()[idx].d){
    if(idx<S().length-1){idx++;elapsed=0;render();}
    else{
      elapsed=S()[idx].d;ended=true;progress();Sound.stopMusic();setPlaying(false);
      if(!finished){finished=true;track('finish');}
      window.dispatchEvent(new Event('pip-ended'));
      $('olabel').textContent='Replay '+EPS[ep].label;$('osub').textContent='';overlay.hidden=false;notifyHeight();return;
    }
  }
  progress();raf=requestAnimationFrame(tick);
}
function go(i,play=true){
  idx=Math.max(0,Math.min(S().length-1,i));elapsed=0;ended=false;
  setPlaying(false);render();overlay.hidden=play;
  box.classList.toggle('is-poster',!play);
  $('olabel').textContent='Play '+EPS[ep].label;
  $('osub').textContent=fmt(total())+' · captions + sound';
  if(play)setPlaying(true);
}
function seekScene(slug,play=false){const i=PIP_META[ep].scenes.findIndex(s=>s.slug===slug);if(i>=0)go(i,play);}
function restart(){started=false;finished=false;watched=0;go(0);}
S().forEach((sc,i)=>{
  const b=document.createElement('button');b.className='seg';b.type='button';b.style.flex=String(sc.d);
  b.setAttribute('aria-label','Scene '+(i+1)+': '+sc.cap);b.innerHTML='<span><i></i></span>';
  b.addEventListener('click',()=>go(i));segsEl.appendChild(b);
});
$('episode-title').textContent=EPS[ep].title;
$('aboutTitle').textContent=EPS[ep].title;$('aboutText').textContent=EPS[ep].about;
$('evidence-link').textContent=PIP_META[ep].evidenceLabel+' ↗';
$('evidence-link').href=ep===1?new URL('index.html#reproducer-commands',siteBase).href:PIP_META[ep].evidence;
$('evidence-link').addEventListener('click',()=>{setPlaying(false);track('evidence_click');});
const next=(ep+1)%3;
$('next-episode').href=embedded?new URL('index.html#episode-'+(next+1),siteBase).href:new URL(PIP_META[next].slug+'/',location.href).href;
$('next-episode').addEventListener('click',()=>setPlaying(false));
$('vertical-link').href='player.html?ep='+(ep+1)+(vertical?'':'&format=vertical');
$('vertical-link').textContent=vertical?'16:9 version':'9:16 version';
overlay.addEventListener('click',()=>ended?restart():setPlaying(true));
playBtn.addEventListener('click',()=>ended?restart():setPlaying(!playing));
$('prevBtn').addEventListener('click',()=>go(elapsed>1500?idx:idx-1));
$('nextBtn').addEventListener('click',()=>go(Math.min(idx+1,S().length-1)));
$('restartBtn').addEventListener('click',restart);
$('soundBtn').addEventListener('click',()=>{
  Sound.setOn(!Sound.on);$('soundBtn').setAttribute('aria-pressed',String(Sound.on));
  $('soundBtn').setAttribute('aria-label',Sound.on?'Mute sound':'Turn sound on');
  $('soundBtn').querySelector('.waves').style.display=Sound.on?'':'none';$('soundBtn').querySelector('.mute').style.display=Sound.on?'none':'';
});
$('fullscreen').addEventListener('click',async()=>{
  try{if(document.fullscreenElement)await document.exitFullscreen();else await $('pip-main').requestFullscreen();}
  catch{$('player-status').textContent='Fullscreen is unavailable here. Open the episode using its share link.';}
});
document.addEventListener('fullscreenchange',()=>{$('fullscreen').textContent=document.fullscreenElement?'Exit fullscreen':'Fullscreen';notifyHeight();});
$('share-scene').addEventListener('click',async()=>{
  const url=new URL(watchURL);url.hash=PIP_META[ep].scenes[idx].slug;
  try{await navigator.clipboard.writeText(url.href);$('player-status').textContent='Scene link copied.';}
  catch{$('player-status').textContent=url.href;}
  notifyHeight();
});
const list=document.createElement('ol');
PIP_META[ep].scenes.forEach((scene,i)=>{
  const li=document.createElement('li'),button=document.createElement('button');
  button.type='button';button.textContent=fmt(scene.start);button.setAttribute('aria-label','Play scene '+(i+1));
  button.addEventListener('click',()=>go(i));li.append(button,document.createTextNode(' '+scene.caption));list.append(li);
});
$('player-transcript').append(list);
$('transcript-toggle').addEventListener('click',()=>{
  const open=$('player-transcript').hidden;$('player-transcript').hidden=!open;$('transcript-toggle').setAttribute('aria-expanded',String(open));notifyHeight();
});
window.addEventListener('message',e=>{
  if(e.source!==parent||e.data?.source!=='northstar-pip-host'||(location.origin!=='null'&&e.origin!==location.origin))return;
  if(e.data.type==='pause')setPlaying(false);
  if(e.data.type==='seek')seekScene(e.data.scene,e.data.play===true);
});
document.addEventListener('visibilitychange',()=>{if(document.hidden)setPlaying(false);});
window.addEventListener('hashchange',()=>seekScene(location.hash.slice(1)));
new ResizeObserver(notifyHeight).observe($('pip-main'));
go(0,false);seekScene(location.hash.slice(1));
message('ready');
