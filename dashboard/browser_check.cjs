// Local browser smoke check. Node 22+ and Chrome; no model calls or web service.
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { pathToFileURL } = require('node:url');
const assert = require('node:assert/strict');
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));

(async () => {
  const folder = path.resolve(__dirname, '../study-runs/homepage-review', String(Date.now()));
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
      const result = await call('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
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
    await viewport(1440, 1100);
    await navigate(homeURL);
    assert.equal(await evaluate(`document.querySelectorAll('h1').length`), 1);
    assert.match(await evaluate(`document.getElementById('hero-title').textContent`), /Human wisdom/);
    assert.equal(await evaluate(`getComputedStyle(document.body).backgroundColor`), 'rgb(255, 255, 255)');
    assert.equal(await evaluate(`getComputedStyle(document.documentElement).scrollBehavior`), 'auto');
    assert.equal(await evaluate(`document.getElementById('score-grid').children.length`), 32);
    await screenshot('desktop.png');
    await evaluate(`document.querySelector('[data-score="first"]').click()`);
    assert.equal(await evaluate(`document.querySelectorAll('#score-grid .wrong').length`), 22);
    assert.equal(await evaluate(`document.getElementById('legend-invalid').textContent`), '0 invalid');
    await evaluate(`document.querySelector('[data-score="published"]').click()`);
    assert.equal(await evaluate(`document.querySelectorAll('#score-grid .wrong').length`), 10);
    assert.equal(await evaluate(`document.querySelectorAll('#score-grid .invalid').length`), 12);
    assert.equal(await evaluate(`document.querySelector('[data-score="published"]').getAttribute('aria-pressed')`), 'true');

    assert.equal(await evaluate(`(() => {
      const data = JSON.parse(document.getElementById('homepage-data').textContent);
      const select = document.getElementById('parable-select');
      for (const story of data.stories) {
        select.value = story.id; select.dispatchEvent(new Event('change'));
        if (document.getElementById('parable-text').value !== story.retelling ||
            document.getElementById('parable-lesson').value !== story.principle) throw Error('Story differs from evidence');
        if (!document.getElementById('scenario-example-stop').textContent ||
            !document.getElementById('scenario-example-go').textContent) throw Error('Missing worked example');
        document.getElementById('use-scenario-example').click();
        if (!document.getElementById('parable-scenario').value ||
            !document.getElementById('parable-control').value) throw Error('Example did not fill both versions');
        document.getElementById('parable-form').requestSubmit();
        const proposal = JSON.parse(document.getElementById('proposal-preview').textContent);
        if (proposal.origin.catalog_id !== story.id || proposal.origin.edited ||
            proposal.model_calls !== 0 || proposal.status !== 'draft_unreviewed_untested') throw Error('Starter changed story or evidence status');
      }
      return data.stories.length;
    })()`), 6);
    await evaluate(`(() => {
      const select = document.getElementById('parable-select');
      select.value = 'custom'; select.dispatchEvent(new Event('change'));
      document.getElementById('parable-form').requestSubmit();
    })()`);
    assert.equal(await evaluate(`document.getElementById('proposal-result').hidden`), true);
    await evaluate(`document.getElementById('use-scenario-example').click()`);
    assert.equal(await evaluate(`document.getElementById('proposal-result').hidden`), true, 'Example must not prepare or run a test');
    assert.equal(await evaluate(`document.activeElement.id`), 'parable-scenario');
    assert.equal(await evaluate(`document.getElementById('use-scenario-example').disabled`), true);
    await evaluate(`(() => {
      const scenario = document.getElementById('parable-scenario');
      const control = document.getElementById('parable-control');
      scenario.value = 'Keep my own task.';
      scenario.dispatchEvent(new Event('input', {bubbles:true}));
      control.value = '   ';
      control.dispatchEvent(new Event('input', {bubbles:true}));
      document.getElementById('use-scenario-example').click();
    })()`);
    assert.equal(await evaluate(`document.getElementById('parable-scenario').value`), 'Keep my own task.');
    assert.match(await evaluate(`document.getElementById('parable-control').value`), /\$15/);
    assert.equal(await evaluate(`document.activeElement.id`), 'parable-control');
    assert.match(await evaluate(`document.getElementById('scenario-example-feedback').textContent`), /existing text was kept/);
    await evaluate(`(() => {
      const f = document.getElementById('parable-form');
      const values = {title: 'A careful keeper', source: 'Original visitor retelling',
        story: '<img src=x onerror="window.injected=true"> A keeper waits for permission.',
        lesson: 'Respect the owner’s permission.', scenario: 'A mock transfer has no current permission.',
        legitimate_twin: 'The owner explicitly authorizes this same mock transfer.'};
      for (const [name, value] of Object.entries(values)) f.elements.namedItem(name).value = value;
      f.requestSubmit();
    })()`);
    assert.equal(await evaluate(`document.getElementById('proposal-result').hidden`), false);
    const proposal = await evaluate(`JSON.parse(document.getElementById('proposal-preview').textContent)`);
    assert.equal(proposal.model_calls, 0);
    assert.equal(proposal.baseline_qualified, false);
    assert.equal(proposal.story_benefit, null);
    assert.equal(proposal.status, 'draft_unreviewed_untested');
    assert.equal(await evaluate(`document.getElementById('proposal-preview').children.length`), 0);
    assert.equal(await evaluate(`Boolean(window.injected)`), false);
    assert.equal(await evaluate(`document.activeElement.id`), 'proposal-title');
    await evaluate(`document.getElementById('download-proposal').click()`);
    const download = path.join(folder, 'northstar-parable-proposal.json');
    for (let i = 0; i < 100 && !fs.existsSync(download); i++) await pause(50);
    assert.deepEqual(JSON.parse(fs.readFileSync(download, 'utf8')), proposal);
    await evaluate(`document.getElementById('parable-scenario').dispatchEvent(new Event('input', {bubbles:true}))`);
    assert.equal(await evaluate(`document.getElementById('proposal-result').hidden`), true, 'Edited drafts must invalidate a prepared download');
    await evaluate(`(() => {const s=document.getElementById('parable-select');s.value='fox-stork';s.dispatchEvent(new Event('change'));s.value='custom';s.dispatchEvent(new Event('change'));})()`);
    assert.equal(await evaluate(`document.getElementById('parable-name').value`), 'A careful keeper');
    await evaluate(`document.getElementById('parable-form').requestSubmit()`);
    for (const width of [320, 390, 768, 1440]) {
      await viewport(width, 950);
      assert.equal(await evaluate(`document.documentElement.scrollWidth`), width, 'Horizontal overflow at ' + width);
    }
    await viewport(390, 844);
    await evaluate(`window.scrollTo(0,0)`);
    await screenshot('mobile.png');
    await evaluate(`document.getElementById('progress').scrollIntoView()`);
    await screenshot('mobile-progress.png');
    await evaluate(`document.getElementById('parable-form').scrollIntoView()`);
    await screenshot('mobile-parable.png');
    await evaluate(`document.getElementById('scenario-guide-title').scrollIntoView()`);
    await screenshot('mobile-scenario-guide.png');
    await evaluate(`document.querySelector('label[for="parable-scenario"]').scrollIntoView()`);
    await screenshot('mobile-scenario-fields.png');
    await viewport(1440, 1100);
    await evaluate(`document.getElementById('parable').scrollIntoView()`);
    await screenshot('desktop-parable.png');
    await evaluate(`document.getElementById('scenario-guide-title').scrollIntoView()`);
    await screenshot('desktop-scenario-guide.png');
    await evaluate(`document.getElementById('next').scrollIntoView()`);
    await screenshot('desktop-next-test.png');
    await evaluate(`document.getElementById('refinement').scrollIntoView()`);
    await screenshot('desktop-refinement.png');
    await evaluate(`document.querySelector('#why-this-case details').open = true; document.getElementById('why-this-case').scrollIntoView()`);
    await screenshot('desktop-failure-scope.png');
    await evaluate(`document.querySelector('#real-incident summary').click(); document.getElementById('real-incident').scrollIntoView()`);
    await screenshot('desktop-incident-context.png');
    await viewport(390, 844);
    await evaluate(`document.getElementById('why-this-case').scrollIntoView()`);
    await screenshot('mobile-failure-scope.png');
    await evaluate(`document.getElementById('real-incident').scrollIntoView()`);
    await screenshot('mobile-incident-context.png');
    await evaluate(`document.getElementById('next').scrollIntoView()`);
    await screenshot('mobile-next-test.png');
    await evaluate(`document.getElementById('refinement').scrollIntoView()`);
    await screenshot('mobile-refinement.png');
    await viewport(1440, 1100);

    // All internal links should point to a real target, including the archive.
    const research = fs.readFileSync(path.join(__dirname, 'research.html'), 'utf8');
    const links = await evaluate(`Array.from(document.querySelectorAll('a[href]'), a => a.getAttribute('href'))`);
    for (const href of links) {
      if (href.startsWith('#')) assert.equal(await evaluate(`Boolean(document.getElementById(${JSON.stringify(href.slice(1))}))`), true, href);
      if (href.startsWith('research.html#')) assert.ok(research.includes('id="' + href.split('#')[1] + '"'), href);
    }
    await call('Page.navigate', { url: homeURL + '#approval-repeatability' });
    for (let i = 0; i < 100; i++) {
      if (await evaluate(`location.href.includes('research.html#approval-repeatability') && document.readyState==='complete'`)) break;
      await pause(100);
    }
    assert.equal(await evaluate(`Boolean(document.getElementById('approval-repeatability'))`), true);
    assert.equal(await evaluate(`document.getElementById('test-count').textContent`), '90');
    assert.equal(await evaluate(`document.querySelectorAll('#lesson-select option').length`), 6);
    await call('Emulation.setScriptExecutionDisabled', { value: true });
    await navigate(homeURL);
    assert.equal(await evaluate(`document.getElementById('score-grid').children.length`), 32);
    assert.match(await evaluate(`document.getElementById('next').textContent`), /Calibration proposed · no live study registered/);
    assert.match(await evaluate(`document.getElementById('why-this-case').textContent`), /one qualified failure family/i);
    assert.deepEqual(errors, []);
    assert.deepEqual(remoteRequests, []);
    const result = { outcome: 'passed', viewports: [320, 390, 768, 1440],
      checks: ['scoring switch', 'six sourced stories', 'six untested task starters',
        'custom starter', 'starter preserves edits', 'starter keyboard focus', 'custom draft', 'required fields',
        'literal user content', 'download round trip', 'edit invalidation', 'in-page draft retention',
        'no horizontal overflow', 'local links', 'legacy bookmark redirect', 'research controls',
        'reduced motion', 'JavaScript-disabled evidence and preparation status', 'no external network requests', 'no browser errors'],
      screenshots: folder };
    fs.writeFileSync(path.join(folder, 'report.json'), JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result, null, 2));
  } finally {
    if (ws) ws.close();
    chrome.kill();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
