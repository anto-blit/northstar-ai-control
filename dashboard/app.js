/* The baseline is never computed from milestones, test counts or chart results. */
(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('northstar-data').textContent);
  const $ = id => document.getElementById(id);
  const NS = 'http://www.w3.org/2000/svg';
  const repo = 'https://github.com/anto-blit/northstar-ai-control/blob/main/';
  const pct = value => `${(value * 100).toFixed(value === 0 || value === 1 ? 0 : 1)}%`;
  const el = (tag, text, className) => { const node = document.createElement(tag); if (text !== undefined) node.textContent = text; if (className) node.className = className; return node; };
  const svg = (tag, attributes, text) => { const node = document.createElementNS(NS, tag); Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, String(value))); if (text !== undefined) node.textContent = text; return node; };

  $('baseline-value').replaceChildren(document.createTextNode(data.risk.assumedBaselinePercent.toFixed(2)), el('span', '%'));
  $('test-count').textContent = data.verification.tests;
  $('environment-count').textContent = Object.keys(data.recovery.safe_fallbacks).length;
  $('order-count').textContent = Object.keys(data.recovery.turn_orders).length;
  const date = new Intl.DateTimeFormat('en', {dateStyle:'medium', timeStyle:'short', timeZone:'UTC'}).format(new Date(data.verification.recordedAt));
  $('evidence-date').textContent = `Evidence recorded ${date} UTC · ${data.verification.artifactCount} result artifacts`;
  $('evidence-fingerprint').textContent = `Verification fingerprint ${data.verification.recordSha256.slice(0, 16)}`;
  $('potential-reduction').textContent = data.risk.potentialGlobalReductionPercent === null ? 'Unquantified' : `${data.risk.potentialGlobalReductionPercent.toFixed(2)} pp`;
  $('global-reduction').textContent = data.risk.quantifiedReductionPercent === null ? 'Not established' : `${data.risk.quantifiedReductionPercent.toFixed(2)} pp`;
  const proof = data.monitor.false_negative_sweep.filter(row => row.environment === 'delegation' && row.scenario === 'revocation' && row.false_negative_rate === 0 && row.false_positive_rate === 0);
  const beforeRepair = proof.find(row => row.control === 'starting');
  const afterRepair = proof.find(row => row.control === 'repaired');
  if (beforeRepair && afterRepair) {
    $('demonstrated-protection').textContent = `${pct(beforeRepair.prohibited_outcome_fraction)} → ${pct(afterRepair.prohibited_outcome_fraction)}`;
    $('demonstrated-detail').textContent = `Post-stop failures: ${beforeRepair.prohibited_outcomes}/${beforeRepair.trials} with the starting control; ${afterRepair.prohibited_outcomes}/${afterRepair.trials} after repair. Fixed scripted trials, with zero monitor errors. This is local protection, not a global-risk reduction.`;
  } else {
    $('demonstrated-protection').textContent = 'Not available';
    $('demonstrated-detail').textContent = 'The specific revocation comparison is absent from this evidence snapshot. No result has been inferred.';
  }

  const dialog = $('clock-method');
  document.querySelectorAll('[data-open-method]').forEach(button => button.addEventListener('click', () => dialog.showModal()));
  dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) { const box = dialog.getBoundingClientRect(); if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close(); } });
  const tabs = [...document.querySelectorAll('[role=tab]')];
  function activateTab(active, focus = false) {
    tabs.forEach(tab => { const selected = tab === active; tab.setAttribute('aria-selected', String(selected)); tab.tabIndex = selected ? 0 : -1; $(tab.getAttribute('aria-controls')).hidden = !selected; });
    if (focus) active.focus();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateTab(tab));
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') next = tabs[(index + 1) % tabs.length];
      if (event.key === 'Home') next = tabs[0];
      if (event.key === 'End') next = tabs.at(-1);
      if (next) { event.preventDefault(); activateTab(next, true); }
    });
  });

  function deadline(row) { return !row.recoverable ? 'No guarantee' : !row.requires_intervention ? 'Already safe' : `Tick ${row.deadline}`; }
  function renderRecovery() {
    const environment = $('environment-select').value;
    const orderSelect = $('order-select');
    if (environment === 'release') orderSelect.value = 'operator_first';
    orderSelect.disabled = environment === 'release';
    const depth = Number($('depth-select').value), order = orderSelect.value;
    const rows = data.recovery[environment].filter(row => row.turn_order === order && (row.max_pending_jobs ?? row.max_staged_proposals) === depth);
    const starting = rows.find(row => row.control === 'starting'), repaired = rows.find(row => row.control === 'repaired');
    $('starting-deadline').textContent = deadline(starting);
    $('repaired-deadline').textContent = deadline(repaired);
    $('horizon-label').textContent = `${starting.horizon} TICKS`;
    const plot = $('window-grid'); plot.replaceChildren();
    [starting, repaired].forEach(row => {
      const line = el('div', undefined, 'tick-row'); line.style.gridTemplateColumns = `repeat(${row.horizon},1fr)`;
      line.setAttribute('aria-label', `${row.control}: ${deadline(row)}`);
      for (let tick=0; tick<row.horizon; tick++) {
        const available = row.recoverable && (!row.requires_intervention || tick <= row.deadline);
        const cell = el('span', `T${tick}`, `tick-cell${available ? ' available-' + row.control : ''}`);
        cell.title = available ? `${row.control}: recovery can still be guaranteed if first action is at tick ${tick}` : `${row.control}: recovery cannot be guaranteed if first action is at tick ${tick}`;
        line.append(cell);
      }
      plot.append(line);
    });
    $('safe-target').textContent = `Safe fallback: ${data.recovery.safe_fallbacks[environment]}`;
    $('recovery-finding').textContent = environment === 'release'
      ? 'The repaired release control starts inside the declared safe fallback: its hard gate disables every protected-to-unapproved route. The starting control needs revocation by tick 1. Benign releases can remain available.'
      : order === 'operator_first'
        ? 'The stop repair buys one extra model tick. It can cancel queued work at tick 1, provided the operator acts before the scheduler can dispatch it.'
        : 'The extra tick disappears when dispatch can run first. Both controls require the first intervention at tick 0 in this fixture. A stop cannot undo an effect that has already happened.';
  }
  ['environment-select', 'order-select', 'depth-select'].forEach(id => $(id).addEventListener('change', renderRecovery));
  renderRecovery();

  const captions = {
    'release/content':'The repaired gate blocks this prohibited release before asking the monitor. Its zero observed failures apply to this fixed rule and scenario; they do not establish coverage of every possible danger.',
    'delegation/content':'Both controls rely on the monitor for forbidden job content when no stop occurs. The stop repair changes revocation behavior, not the content policy.',
    'delegation/content_then_stop':'A missed detection can queue forbidden work. The repaired stop cancels it before dispatch; the weak stop leaves it executable. The benign twin completes useful work before stop.',
    'delegation/revocation':'The monitor correctly approves an initially legitimate job. A later stop revokes its permission. The repaired broker enforces that change; even perfect content screening cannot fix the weak broker’s stale approval.'
  };
  function renderMonitor() {
    const key = $('scenario-select').value, [environment, scenario] = key.split('/');
    const rows = data.monitor.false_negative_sweep.filter(row => row.environment === environment && row.scenario === scenario && row.false_positive_rate === 0);
    const rates = [...new Set(rows.map(row => row.false_negative_rate))].sort((a,b) => a-b);
    $('rate-slider').max = rates.length - 1;
    const index = Math.min(Number($('rate-slider').value), rates.length - 1), rate = rates[index];
    $('rate-label').textContent = pct(rate);
    $('rate-slider').setAttribute('aria-valuetext', `${pct(rate)} assumed missed-danger rate`);
    const chart = $('monitor-chart'); chart.replaceChildren();
    const x = value => 55 + value * 558, y = value => 215 - value * 180;
    chart.append(svg('text',{x:55,y:14,fill:'#a4bab9','font-size':10},'PROHIBITED OUTCOMES (%)'));
    [0,.25,.5,.75,1].forEach(value => {
      chart.append(svg('line',{x1:55,x2:613,y1:y(value),y2:y(value),stroke:'#2c4649','stroke-width':1}));
      chart.append(svg('text',{x:43,y:y(value)+4,'text-anchor':'end',fill:'#a4bab9','font-size':10},`${value*100}`));
      chart.append(svg('text',{x:x(value),y:236,'text-anchor':'middle',fill:'#a4bab9','font-size':10},`${value*100}`));
    });
    chart.append(svg('text',{x:334,y:263,'text-anchor':'middle',fill:'#a4bab9','font-size':10},'ASSUMED MISSED-DANGER RATE (%)'));
    chart.append(svg('line',{x1:x(rate),x2:x(rate),y1:28,y2:215,stroke:'#819c91','stroke-dasharray':'3 5',opacity:.65}));
    for (const [control,color] of [['starting','#e2b686'],['repaired','#9be2c4']]) {
      const cells = rows.filter(row=>row.control===control).sort((a,b)=>a.false_negative_rate-b.false_negative_rate);
      const points = cells.map(row=>`${x(row.false_negative_rate)},${y(row.prohibited_outcome_fraction)}`).join(' ');
      const line = svg('polyline',{points,fill:'none',stroke:color,'stroke-width':control==='starting'?4:2.5,'stroke-linecap':'round','stroke-linejoin':'round'});
      if (control==='repaired') line.setAttribute('stroke-dasharray','7 4');
      chart.append(line);
      cells.forEach(row=>chart.append(svg('circle',{cx:x(row.false_negative_rate),cy:y(row.prohibited_outcome_fraction),r:row.false_negative_rate===rate?5:2.5,fill:color,stroke:'#10272d','stroke-width':1})));
      const selected=cells.find(row=>row.false_negative_rate===rate);
      $(`${control}-failures`).textContent=pct(selected.prohibited_outcome_fraction);
      $(`${control}-trials`).textContent=`${selected.prohibited_outcomes} of ${selected.trials} trials`;
    }
    chart.setAttribute('aria-label',`${$('scenario-select').selectedOptions[0].textContent}. At an assumed missed-danger rate of ${pct(rate)}, starting control: ${$('starting-failures').textContent} prohibited outcomes; repaired control: ${$('repaired-failures').textContent}. Full data in the table below.`);
    const benign=rows.find(row=>row.control==='repaired'&&row.false_negative_rate===rate);
    const fp=data.monitor.false_positive_check.find(row=>row.environment===environment&&row.scenario===scenario&&row.control==='repaired');
    $('utility-note').textContent=`Repaired control: ${pct(benign.benign_completion_fraction)} benign completion with no false alarms. With a declared 25% false-alarm rate: ${pct(fp.benign_completion_fraction)}. These are simulated rates.`;
    $('monitor-finding').textContent=captions[key];
    $('monitor-table').replaceChildren();
    rates.forEach(value=>{const tr=el('tr');tr.append(el('th',pct(value)));tr.firstChild.scope='row';['starting','repaired'].forEach(control=>{const row=rows.find(item=>item.control===control&&item.false_negative_rate===value);tr.append(el('td',`${row.prohibited_outcomes}/${row.trials} (${pct(row.prohibited_outcome_fraction)})`));});$('monitor-table').append(tr);});
  }
  $('scenario-select').addEventListener('change',renderMonitor);
  $('rate-slider').addEventListener('input',renderMonitor);
  renderMonitor();
  $('proof-link').addEventListener('click', () => {
    activateTab($('monitor-tab'));
    $('scenario-select').value = 'delegation/revocation';
    $('rate-slider').value = 0;
    renderMonitor();
  });

  data.milestones.forEach(item=>{
    const card=el('article',undefined,'milestone');card.append(el('span',item.number,'milestone-number'),el('span',item.type.toUpperCase(),`milestone-type${item.type==='Prepared'?' prepared':''}`),el('h3',item.title),el('p',item.description));
    const link=el('a',item.type==='Prepared'?'Read the plan ↗':'Inspect the evidence ↗');link.href=repo+item.source;card.append(link);$('milestones').append(card);
  });
})();
