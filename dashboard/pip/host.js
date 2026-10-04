(() => {
  'use strict';
  const embeds=[...document.querySelectorAll('.pip-embed')];
  const frames=embeds.map(el=>el.querySelector('iframe'));
  const pending=new Map();
  // Provider-neutral funnel events. No network requests, identifiers or cookies.
  function metric(detail){
    window.dispatchEvent(new CustomEvent('northstar:pip',{detail}));
    window.dataLayer=window.dataLayer||[];
    window.dataLayer.push({event:'pip_'+detail.event,pip_episode:detail.episode,pip_scene:detail.scene,pip_watched_seconds:detail.watchedSeconds||0,pip_placement:detail.placement||'evidence'});
  }
  function send(frame,type,extra={}){frame.contentWindow?.postMessage({source:'northstar-pip-host',type,...extra},location.origin==='null'?'*':location.origin);}
  function load(frame){if(!frame.src){frame.src=frame.dataset.src;delete frame.dataset.src;}}
  if('IntersectionObserver' in window){
    const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){load(entry.target);observer.unobserve(entry.target);}}),{rootMargin:'240px'});
    frames.forEach(frame=>observer.observe(frame));
  }else frames.forEach(load);
  function seek(frame,scene,play=false){load(frame);pending.set(frame,{scene,play});send(frame,'seek',{scene,play});}
  window.addEventListener('message',event=>{
    const frame=frames.find(frame=>frame.contentWindow===event.source),data=event.data;
    if(!frame||data?.source!=='northstar-pip'||(location.origin!=='null'&&event.origin!==location.origin))return;
    if(data.episode!==Number(frame.closest('.pip-embed').dataset.episode))return;
    if(data.type==='resize'&&Number.isFinite(data.height)&&data.height>=200&&data.height<6000)frame.style.height=data.height+'px';
    if(data.type==='ready'&&pending.has(frame)){send(frame,'seek',pending.get(frame));pending.delete(frame);}
    if(data.type==='playing')frames.filter(other=>other!==frame).forEach(other=>send(other,'pause'));
    if(data.type==='metric'&&['play','finish','evidence_click'].includes(data.event))metric(data);
  });
  embeds.forEach(el=>{
    const frame=el.querySelector('iframe');
    el.querySelectorAll('[data-pip-seek]').forEach(link=>link.addEventListener('click',event=>{
      event.preventDefault();seek(frame,link.dataset.pipSeek,true);frame.scrollIntoView({block:'center'});
      if(document.body.classList.contains('pip-watch'))history.replaceState(null,'','#'+link.dataset.pipSeek);
    }));
    el.querySelector('[data-pip-evidence]')?.addEventListener('click',()=>{frames.forEach(f=>send(f,'pause'));metric({event:'evidence_click',episode:Number(el.dataset.episode),placement:'below_player'});});
  });
  function hash(){
    if(document.body.classList.contains('pip-watch')&&frames.length===1&&location.hash)seek(frames[0],location.hash.slice(1));
    else{const target=document.getElementById(location.hash.slice(1));const frame=target?.querySelector('iframe[data-src]');if(frame)load(frame);}
  }
  window.addEventListener('hashchange',hash);hash();
})();
