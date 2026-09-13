(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('homepage-data').textContent);
  // Preserve bookmarks to the existing research dashboard after the homepage move.
  const followResearchBookmark = () => {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    if (id && !document.getElementById(id) && data.researchAnchors.includes(id)) {
      location.replace('research.html#' + encodeURIComponent(id));
    }
  };
  followResearchBookmark();
  window.addEventListener('hashchange', followResearchBookmark);

  const buttons = document.querySelectorAll('[data-score]');
  for (const button of buttons) {
    button.addEventListener('click', () => {
      const key = button.dataset.score;
      const result = data.scoring[key];
      for (const item of buttons) item.setAttribute('aria-pressed', String(item === button));
      const count = document.getElementById('score-count');
      count.firstChild.textContent = result.wrong + ' ';
      document.getElementById('legend-wrong').textContent = result.wrong + ' wrong';
      document.getElementById('legend-invalid').textContent = result.invalid + ' invalid';
      document.getElementById('score-note').textContent = result.note;
      const cells = document.getElementById('score-grid').children;
      for (let i = 0; i < cells.length; i++) {
        cells[i].className = 'score-cell ' + (i < result.wrong ? 'wrong' :
          i < result.wrong + result.correct ? 'correct' : 'invalid');
      }
    });
  }

  // The reduction model. Sliders move stated assumptions only; the earned
  // figure is not wired to anything, because no term has been validated.
  const factors = document.getElementById('model-factors');
  if (factors) {
    const reference = 10;
    const readFactor = id => Number(document.getElementById('factor-' + id).value) / 100;
    const setText = (id, value) => { document.getElementById(id).textContent = value; };
    const updateModel = () => {
      const s = readFactor('s'), e = readFactor('e'), a = readFactor('a');
      const available = reference * s * e * a;
      for (const [key, value] of [['s', s], ['e', e], ['a', a]]) {
        setText('out-' + key, value.toFixed(2));
        setText('eq-' + key, value.toFixed(2));
      }
      setText('eq-result', available.toFixed(2));
      setText('value-available', available.toFixed(2) + ' pp');
      setText('value-floor', (reference - available).toFixed(2) + '%');
      // The axis rescales rather than clamping, so a maxed-out model stays readable.
      const axisMaximum = available > 0.5 ? reference : 0.5;
      setText('axis-mid', (axisMaximum / 2).toFixed(2));
      setText('axis-max', axisMaximum.toFixed(2) + ' pp');
      document.getElementById('bar-available').style.width =
        Math.min(100, (available / axisMaximum) * 100) + '%';
    };
    const aspiration = document.getElementById('show-aspiration');
    if (aspiration) {
      aspiration.addEventListener('click', () => {
        for (const id of ['s', 'e', 'a']) document.getElementById('factor-' + id).value = '100';
        updateModel();
      });
    }
    factors.addEventListener('input', updateModel);
    factors.addEventListener('submit', event => event.preventDefault());
    updateModel();
  }

  const form = document.getElementById('parable-form');
  const select = document.getElementById('parable-select');
  const output = document.getElementById('proposal-result');
  const feedback = document.getElementById('draft-feedback');
  let proposal = null;
  let selection = '';
  const drafts = new Map();
  const fieldNames = ['title', 'source', 'story', 'lesson', 'scenario', 'legitimate_twin'];
  const fields = () => Object.fromEntries(fieldNames.map(name => [name, form.elements.namedItem(name).value]));
  const invalidateProposal = () => {
    proposal = null;
    output.hidden = true;
    feedback.textContent = '';
  };
  select.addEventListener('change', () => {
    if (selection) drafts.set(selection, fields());
    selection = select.value;
    const story = data.stories.find(item => item.id === selection);
    const values = drafts.get(selection) || {
      title: story?.title || '', source: story?.source_url || '',
      story: story?.retelling || '', lesson: story?.principle || '',
      scenario: '', legitimate_twin: '',
    };
    for (const name of fieldNames) form.elements.namedItem(name).value = values[name];
    document.getElementById('parable-fields').hidden = !selection;
    for (const name of fieldNames) form.elements.namedItem(name).disabled = !selection;
    document.getElementById('parable-interpretation').textContent = story ?
      'Existing interpretation: ' + story.disagreements.join(' ') + ' Human review pending.' :
      'This is your proposed interpretation. Other readings may disagree.';
    invalidateProposal();
  });
  for (const name of fieldNames) form.elements.namedItem(name).disabled = true;
  form.addEventListener('input', invalidateProposal);
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!selection || !form.reportValidity()) return;
    const values = Object.fromEntries(Object.entries(fields()).map(([key, value]) => [key, value.trim()]));
    if (fieldNames.filter(name => name !== 'source').some(name => !values[name])) {
      feedback.textContent = 'Please fill in the story, lesson, test situation and permitted counterpart.';
      return;
    }
    const story = data.stories.find(item => item.id === selection);
    proposal = {
      schema_version: 1,
      kind: 'NorthStar parable test proposal',
      status: 'draft_unreviewed_untested',
      model_calls: 0,
      baseline_qualified: false,
      story_benefit: null,
      origin: story ? { catalog_id: story.id, edited: values.story !== story.retelling || values.lesson !== story.principle || values.title !== story.title || values.source !== story.source_url,
        original_source: story.source_url, recorded_disagreements: story.disagreements } : { catalog_id: null },
      ...values,
      proposed_comparison: ['original instructions', 'matched factual guidance', 'story guidance', 'simple reasoning repair'],
      review_needed: ['source and reuse rights', 'interpretation and disagreements',
        'explicit expected decisions and legitimate counterpart', 'facts matched across guidance conditions',
        'qualified recurring baseline on the exact target', 'published budget, scoring and stop rule before model calls'],
    };
    document.getElementById('proposal-preview').textContent = JSON.stringify(proposal, null, 2);
    output.hidden = false;
    feedback.textContent = 'Draft prepared. No AI test has run and nothing has been submitted.';
    document.getElementById('proposal-title').focus({ preventScroll: true });
    output.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
  });
  document.getElementById('download-proposal').addEventListener('click', () => {
    if (!proposal) return;
    const blob = new Blob([JSON.stringify(proposal, null, 2) + '\n'], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'northstar-parable-proposal.json';
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    feedback.textContent = 'Download requested. The proposal is still untested and has not been submitted.';
  });
})();
