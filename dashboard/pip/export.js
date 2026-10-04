// Re-layout the unedited episode for a 1080 × 1920 video. Browser-only export.
// Every original scene remains fully visible; captions sit below the illustration.
if(vertical&&!embedded){
  const button=document.createElement('button');button.type='button';button.id='export-video';
  button.textContent='Download vertical video';document.querySelector('.extra-controls').append(button);
  let recorder=null, exportFrame=0, drawing=false, output=null, audioOutput=null;
  const mime=window.MediaRecorder&&['video/mp4;codecs=avc1.42001E,mp4a.40.2','video/mp4','video/webm;codecs=vp9,opus','video/webm;codecs=vp8,opus'].find(type=>MediaRecorder.isTypeSupported(type));
  if(!mime){button.disabled=true;button.textContent='Video export needs a supported browser';}
  function lines(ctx,text,x,y,width,size,weight=500){
    ctx.font=weight+' '+size+'px system-ui, sans-serif';
    let line='';for(const word of text.split(/\s+/)){
      if(ctx.measureText(line+' '+word).width>width&&line){ctx.fillText(line,x,y);y+=size*1.35;line=word;}
      else line+=(line?' ':'')+word;
    }ctx.fillText(line,x,y);return y+size*1.35;
  }
  async function paint(ctx,canvas){
    if(drawing)return;drawing=true;
    try{
      const clone=stage.cloneNode(true);clone.setAttribute('xmlns','http://www.w3.org/2000/svg');
      clone.setAttribute('width','960');clone.setAttribute('height','540');
      const originals=stage.querySelectorAll('*'),copies=clone.querySelectorAll('*');
      originals.forEach((el,i)=>{
        const style=getComputedStyle(el),copy=copies[i];
        for(const prop of ['opacity','transform','transform-origin','transform-box','fill','stroke','font-family','font-size','font-weight','letter-spacing'])copy.style.setProperty(prop,style.getPropertyValue(prop));
        copy.style.setProperty('animation','none','important');
      });
      const svgURL=URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(clone)],{type:'image/svg+xml'}));
      const image=new Image();
      try{image.src=svgURL;await image.decode();
        ctx.fillStyle='#f4f4f7';ctx.fillRect(0,0,1080,1920);
        ctx.fillStyle='#2f5bea';lines(ctx,'NORTHSTAR / TEN TO ZERO',70,145,940,28,700);
        ctx.fillStyle='#1d1d1f';lines(ctx,EPS[ep].title,70,250,940,64,700);
        ctx.drawImage(image,60,445,960,540);
        lines(ctx,S()[idx].cap,70,1100,940,49,500);
        let done=elapsed;for(let i=0;i<idx;i++)done+=S()[i].d;
        ctx.fillStyle='#dedee5';ctx.fillRect(70,1695,940,6);ctx.fillStyle='#2f5bea';ctx.fillRect(70,1695,940*Math.min(1,done/total()),6);
        ctx.fillStyle='#1d1d1f';lines(ctx,idx===S().length-1?PIP_META[ep].evidenceLabel+' →':'Pip breaks the rules.',70,1770,940,34,650);
        ctx.fillStyle='#5e5e66';lines(ctx,'anto-blit.github.io/northstar-ai-control/',70,1835,940,28);
      }finally{URL.revokeObjectURL(svgURL);}
    }catch(error){$('player-status').textContent='Video frame could not be rendered: '+error.message;}
    finally{drawing=false;}
  }
  function stop(){if(recorder&&recorder.state!=='inactive')recorder.stop();}
  button.addEventListener('click',async()=>{
    if(recorder){stop();return;}
    if(!mime||!Sound.ensure())return;
    const canvas=document.createElement('canvas');canvas.width=1080;canvas.height=1920;
    const ctx=canvas.getContext('2d');const stream=canvas.captureStream(30);
    audioOutput=Sound.ctx.createMediaStreamDestination();Sound.master.connect(audioOutput);
    audioOutput.stream.getAudioTracks().forEach(track=>stream.addTrack(track));
    const chunks=[];const current=new MediaRecorder(stream,{mimeType:mime,videoBitsPerSecond:4500000,audioBitsPerSecond:128000});
    recorder=current;
    current.addEventListener('dataavailable',event=>{if(event.data.size)chunks.push(event.data);});
    current.addEventListener('stop',()=>{
      cancelAnimationFrame(exportFrame);Sound.master.disconnect(audioOutput);stream.getTracks().forEach(track=>track.stop());
      if(output)URL.revokeObjectURL(output);output=URL.createObjectURL(new Blob(chunks,{type:current.mimeType}));
      const link=document.createElement('a');link.href=output;link.download='pip-'+PIP_META[ep].slug+'-vertical.'+(mime.startsWith('video/mp4')?'mp4':'webm');
      link.textContent='Save vertical video';link.id='video-download';$('video-download')?.remove();document.querySelector('.extra-controls').append(link);link.click();
      $('player-status').textContent='Vertical video ready. Captions are included.';button.textContent='Download vertical video';recorder=null;
    });
    current.addEventListener('error',()=>{$('player-status').textContent='This browser could not finish the video export.';stop();});
    function draw(){if(current.state==='inactive')return;paint(ctx,canvas);exportFrame=requestAnimationFrame(draw);}
    Sound.setOn(true);restart();await paint(ctx,canvas);current.start(1000);draw();
    button.textContent='Stop and save video';$('player-status').textContent='Recording the full episode. Keep this tab visible; the download starts when it finishes.';
  });
  window.addEventListener('pip-ended',stop);
  document.addEventListener('visibilitychange',()=>{if(document.hidden&&recorder){stop();$('player-status').textContent='Recording stopped because the tab was hidden. Restart the export for the full episode.';}});
}
