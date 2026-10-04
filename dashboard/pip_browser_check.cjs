// Local browser smoke check. Node 22+ and Chrome; no model calls or web service.
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { pathToFileURL } = require('node:url');
const assert = require('node:assert/strict');
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));

(async () => {
  const folder = path.resolve(__dirname, '../study-runs/pip-review', String(Date.now()));
  fs.mkdirSync(folder, { recursive: true });
  const executable = process.env.CHROME_PATH || (process.platform === 'win32'
    ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : 'google-chrome');
  const chrome = spawn(executable, ['--headless=new', '--disable-gpu', '--no-first-run',
    '--no-default-browser-check', '--disable-background-networking', '--remote-debugging-port=0',
    '--hide-scrollbars', `--user-data-dir=${path.join(folder, 'profile')}`, 'about:blank'],
  { windowsHide: true, stdio: 'ignore' });
  let spawnError;
  chrome.on('error', error => { spawnError = error; });
  let ws;
  try {
    const portFile = path.join(folder, 'profile', 'DevToolsActivePort');
    for (let i = 0; i < 150 && !fs.existsSync(portFile) && !spawnError; i++) await pause(100);
    if (spawnError) throw spawnError;
    const [port, route] = fs.readFileSync(portFile, 'utf8').trim().split(/\r?\n/);
    ws = new WebSocket(`ws://127.0.0.1:${port}${route}`);
    await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
    let sequence = 0;
    const pending = new Map(), errors = [], remoteRequests = [];
    ws.onmessage = event => {
      const message = JSON.parse(event.data);
      if (message.id) {
        const task = pending.get(message.id);
        pending.delete(message.id);
        if (message.error) task.reject(new Error(JSON.stringify(message.error)));
        else task.resolve(message.result);
      } else if (message.method === 'Runtime.exceptionThrown') errors.push(message.params.exceptionDetails);
      else if (message.method === 'Network.requestWillBeSent' && /^https?:/.test(message.params.request.url)) remoteRequests.push(message.params.request.url);
    };
    const send = (method, params = {}, sessionId) => new Promise((resolve, reject) => {
      const id = ++sequence;
      pending.set(id, { resolve, reject });
      ws.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
    });
    const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
    const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
    const call = (method, params) => send(method, params, sessionId);
    const evaluate = async expression => {
      const result = await call('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true, userGesture: true });
      if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
      return result.result.value;
    };
    await call('Page.enable');
    await call('Runtime.enable');
    await call('Network.enable');
    await call('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
    await send('Browser.setDownloadBehavior', { behavior: 'allow', downloadPath: folder });
    const homeURL = pathToFileURL(path.join(__dirname, 'index.html')).href;
    const viewport = (width, height) => call('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: width < 600 });
    const navigate = async url => {
      await call('Page.navigate', { url });
      for (let i = 0; i < 100; i++) {
        if (await evaluate(`document.readyState === 'complete' && location.href === ${JSON.stringify(url)}`)) return;
        await pause(50);
      }
      throw new Error('Navigation did not finish: ' + url);
    };
    const screenshot = async name => {
      const result = await call('Page.captureScreenshot', { format: 'png' });
      fs.writeFileSync(path.join(folder, name), Buffer.from(result.data, 'base64'));
    };

    const server = require('node:http').createServer((req,res)=>{
      let file=path.resolve(__dirname,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
      if(file!==__dirname&&!file.startsWith(__dirname+path.sep)){res.writeHead(403).end();return;}
      if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');
      if(!fs.existsSync(file)){res.writeHead(404).end();return;}
      const mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.png':'image/png'};
      res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream'});res.end(fs.readFileSync(file));
    });
    await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
    const base='http://127.0.0.1:'+server.address().port+'/';
    try {
      await viewport(1440,1000);
      await navigate(base);
      await pause(300);
      assert.equal(await evaluate(`document.querySelectorAll('.pip-embed').length`),3);
      assert.equal(await evaluate(`document.querySelector('#correction').closest('details')`),null);
      assert.equal(await evaluate(`!!(document.querySelector('#correction').compareDocumentPosition(document.querySelector('#algorithm')) & Node.DOCUMENT_POSITION_FOLLOWING)`),true);
      assert.equal(await evaluate(`document.querySelector('#episode-3 iframe').hasAttribute('src')`),false,'offscreen players remain unloaded');
      await screenshot('homepage-hero.png');
      for(const width of [320,390,768,1440]){
        await viewport(width,1000);
        for(let ep=1;ep<=3;ep++){
          await evaluate(`document.querySelector('#episode-${ep}').scrollIntoView()`);
          await pause(500);
          assert.equal(await evaluate(`document.documentElement.scrollWidth<=innerWidth`),true,'homepage overflow at '+width);
          const state=await evaluate(`(()=>{const f=document.querySelector('#episode-${ep} iframe'),d=f.contentDocument;return {caption:d?.querySelector('#caption')?.textContent,paused:d?.querySelector('#box')?.classList.contains('paused'),overflow:d?.documentElement.scrollWidth>f.clientWidth};})()`);
          assert.ok(state.caption,'loaded caption');assert.equal(state.paused,true);assert.equal(state.overflow,false);
          if(width===390||width===1440)await screenshot(`homepage-${width}-episode-${ep}.png`);
        }
      }
      await evaluate(`document.querySelector('#episode-1 iframe').contentDocument.querySelector('#overlay').click()`);
      await pause(100);
      assert.equal(await evaluate(`window.dataLayer.filter(x=>x.event==='pip_play').length`),1);
      await evaluate(`document.querySelector('#episode-2 iframe').contentDocument.querySelector('#overlay').click()`);
      await pause(100);
      assert.equal(await evaluate(`document.querySelector('#episode-1 iframe').contentDocument.querySelector('#box').classList.contains('paused')`),true,'only one episode plays');
      await evaluate(`document.querySelector('#episode-2 iframe').contentDocument.querySelector('#playBtn').click()`);
      // Complete an end scene through the actual timer; verify finish and conversion events.
      await evaluate(`document.querySelector('#episode-1 iframe').contentDocument.querySelector('#segs button:last-child').click()`);
      await pause(7300);
      assert.equal(await evaluate(`window.dataLayer.filter(x=>x.event==='pip_finish').length`),1);
      assert.equal(await evaluate(`document.querySelector('#episode-1 iframe').contentDocument.querySelector('#end-actions').hidden`),false);
      await evaluate(`(()=>{const d=document.querySelector('#episode-1 iframe').contentDocument; d.querySelector('#evidence-link').addEventListener('click',e=>e.preventDefault()); d.querySelector('#evidence-link').click();})()`);
      await pause(100);
      assert.equal(await evaluate(`window.dataLayer.filter(x=>x.event==='pip_evidence_click').length`),1);
      await viewport(1440,1000);
      await navigate(base+'watch/too-easy-test/#verdict');
      await pause(600);
      assert.match(await evaluate(`document.querySelector('iframe').contentDocument.querySelector('#caption').textContent`),/One person caught/);
      assert.equal(await evaluate(`document.querySelector('iframe').contentDocument.querySelector('#box').classList.contains('paused')`),true,'deep links never autoplay');
      await screenshot('shared-verdict.png');
      for(let ep=1;ep<=3;ep++){
        await navigate(base+`watch/player.html?ep=${ep}#next`);
        assert.equal(await evaluate(`document.querySelector('#end-actions').hidden`),false);
        assert.equal(await evaluate(`document.querySelector('#evidence-link').textContent.length>0`),true);
        await evaluate(`document.querySelector('#transcript-toggle').click()`);
        assert.equal(await evaluate(`document.querySelector('#transcript-toggle').getAttribute('aria-expanded')`),'true');
        await evaluate(`document.querySelector('#transcript-toggle').click();document.querySelector('#fullscreen').click()`);
        await pause(150);
        assert.equal(await evaluate(`!!document.fullscreenElement`),true);
        await evaluate(`document.exitFullscreen()`);
        await viewport(390,844);
        await navigate(base+`watch/player.html?ep=${ep}&format=vertical`);
        assert.equal(await evaluate(`document.documentElement.scrollWidth<=innerWidth`),true);
        const ratio=await evaluate(`(()=>{const r=document.querySelector('.player').getBoundingClientRect();return r.width/r.height;})()`);
        assert.ok(Math.abs(ratio-9/16)<0.01,'9:16 relayout');
        await screenshot(`vertical-${ep}.png`);
      }
      await evaluate(`document.querySelector('#export-video').click()`);
      await pause(3000);
      await evaluate(`document.querySelector('#export-video').click()`);
      await pause(500);
      const exportInfo=await evaluate(`new Promise(resolve=>{const link=document.querySelector('#video-download'),v=document.createElement('video');v.onloadedmetadata=()=>resolve({width:v.videoWidth,height:v.videoHeight,name:link.download});v.src=link.href;})`);
      assert.equal(exportInfo.width,1080);assert.equal(exportInfo.height,1920);
      assert.match(exportInfo.name,/vertical\.(mp4|webm)$/);
      if(process.argv.includes('--previews')){
        const names=['holding-message','wrong-label','too-easy-test'],scenes=['completed','wrong-label','verdict'];
        fs.mkdirSync(path.join(__dirname,'pip/previews'),{recursive:true});
        await viewport(1200,630);
        for(let ep=1;ep<=3;ep++){
          await navigate(base+`watch/player.html?ep=${ep}#${scenes[ep-1]}`);
          await evaluate(`(()=>{const svg=document.querySelector('#stage').outerHTML,title=document.querySelector('#episode-title').textContent;document.body.innerHTML='<div class="preview-copy"><span>NORTHSTAR / TEN TO ZERO</span><h1>'+title+'</h1><p>Pip breaks the rules.</p><b>▶ Watch the episode</b></div><div class="preview-art">'+svg+'</div>';const style=document.createElement('style');style.textContent='body{background:#fbfbfd;width:1200px;height:630px;display:flex;align-items:center;padding:50px;gap:24px}.preview-copy{width:330px;flex:none}.preview-copy span{font-size:14px;letter-spacing:.1em}.preview-copy h1{font-size:52px;line-height:1.03;margin:26px 0}.preview-copy p{font-size:21px;color:#64646c}.preview-copy b{display:inline-block;color:#2f5bea;margin-top:30px;font-size:18px}.preview-art{width:746px;flex:none}.preview-art svg{width:100%;height:auto;border-radius:24px}.preview-art *{animation:none!important}';document.head.append(style);})()`);
          const result=await call('Page.captureScreenshot',{format:'png'});
          fs.writeFileSync(path.join(__dirname,'pip/previews',names[ep-1]+'.png'),Buffer.from(result.data,'base64'));
        }
      }
      await call('Emulation.setScriptExecutionDisabled',{value:true});
      await navigate(base+'watch/holding-message/');
      assert.equal(await evaluate(`document.querySelectorAll('.pip-transcript li').length`),11);
      assert.deepEqual(errors,[]);
      assert.deepEqual(remoteRequests.filter(url=>!url.startsWith(base)),[]);
      console.log(JSON.stringify({outcome:'passed',screenshots:folder,checks:['three inline placements','lazy load','mobile overflow','click-to-play','one active player','play/finish/evidence events','paused scene deep links','end-card links','fullscreen','transcripts without JS','9:16 layout','no external requests','original content preserved']},null,2));
    } finally {server.closeAllConnections();server.close();}
  } finally {
    ws?.close();
    chrome.kill();
  }
})().catch(error => { console.error(error); process.exit(1); });
