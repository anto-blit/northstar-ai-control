(() => {
  'use strict';
  const packet = JSON.parse(document.getElementById('check-data').textContent);
  const byId = id => document.getElementById(id);
  const storageKey = 'northstar-contribution-' + packet.version;
  const empty = () => ({panel: 'start', index: 0, record: null, human: {lesson: '', limit: ''}, mode: 'chat'});
  let state = empty();
  try {
    const saved = JSON.parse(sessionStorage.getItem(storageKey) || 'null');
    if (saved && ['start', 'check', 'human', 'report'].includes(saved.panel) &&
        [0, 1].includes(saved.index) && ['chat', 'human'].includes(saved.mode) &&
        typeof saved.human?.lesson === 'string' && typeof saved.human?.limit === 'string' &&
        (!saved.record || (saved.record.version === packet.version &&
          typeof saved.record.app === 'string' && typeof saved.record.id === 'string' &&
          typeof saved.record.createdAt === 'string' && saved.record.answers?.length === 2 &&
          saved.record.answers.every(a => typeof a.text === 'string' &&
            ['not_recorded', 'reply', 'no_answer'].includes(a.status))))) state = saved;
    if (state.panel === 'check' && !state.record) state = empty();
    if (state.panel === 'report' && state.mode === 'chat' && !state.record) state = empty();
  } catch { /* Storage is optional; the form also works in memory. */ }
  const save = () => {
    try { sessionStorage.setItem(storageKey, JSON.stringify(state)); }
    catch { byId('draft-status').textContent = 'Keep this tab open: this browser cannot save your draft across reloads. Nothing is uploaded.'; }
  };
  function panel(name, focus = true) {
    state.panel = name;
    const human = state.mode === 'human';
    byId('intro-title').textContent = human ? 'One sentence can help.' : 'Lend your AI two replies.';
    byId('intro-explain').textContent = human ? 'Help us improve one instruction. We provide the situation; you bring your judgment.'
      : 'Copy our prompts into a chat you already use. Bring back two replies. Help check whether AI reports honestly.';
    const labels = human ? ['Read the situation', 'Suggest one instruction', 'Share your idea']
      : ['Copy a check', 'Bring back the replies', 'Share your report'];
    document.querySelectorAll('[data-step-label]').forEach((label, i) => { label.textContent = labels[i]; });
    for (const id of ['start', 'check', 'human', 'report']) byId(id + '-panel').hidden = id !== name;
    save();
    if (focus) byId(name === 'check' ? 'check-title' : name + '-title').focus();
  }
  async function copy(text, field, status, success) {
    try {
      if (!navigator.clipboard?.writeText) throw new Error('No clipboard');
      await navigator.clipboard.writeText(text);
      status.textContent = success;
    } catch {
      if (field === byId('check-prompt')) byId('prompt-details').open = true;
      field.value = text;
      field.focus(); field.select();
      status.textContent = 'Text selected. Use Copy on your device, then paste it where needed.';
    }
  }
  function captureAnswer() {
    const text = byId('check-answer').value;
    const noAnswer = byId('no-answer').checked;
    state.record.answers[state.index] = {text, status: text.trim() ? 'reply' : noAnswer ? 'no_answer' : 'not_recorded'};
    save();
  }
  function showCheck(focus = true) {
    const number = state.index + 1;
    const answer = state.record.answers[state.index];
    byId('check-progress').textContent = 'Check ' + number + ' of 2 · ' + state.record.app;
    byId('copy-check').textContent = 'Copy check ' + number;
    byId('chat-instruction').textContent = number === 1
      ? 'Open a fresh chat in your AI app. Paste only this prompt and send it once. Don’t add our explanation or ask for another answer.'
      : 'Start a separate fresh chat in the same AI app and model. Paste only this second prompt. Don’t reuse the first conversation or ask for another answer.';
    byId('check-prompt').value = packet.cases[state.index].prompt;
    byId('check-answer').value = answer.text;
    byId('no-answer').checked = answer.status === 'no_answer';
    byId('check-answer').disabled = answer.status === 'no_answer';
    byId('next-check').textContent = number === 1 ? 'Save reply & get check 2 →' : 'Prepare my report →';
    byId('previous-check').hidden = number === 1;
    byId('copy-status').textContent = '';
    byId('reply-error').textContent = '';
    byId('prompt-details').open = false;
    panel('check', focus);
  }
  function reportText(includePrompts) {
    if (state.mode === 'human') return 'NorthStar instruction proposal — UNTESTED\n\n' +
      'Made-up situation: an AI finishes one of three tasks but reports “Everything is complete.”\n\n' +
      'My proposed instruction or lesson:\n' + state.human.lesson + '\n\n' +
      'Where it might fail:\n' + (state.human.limit || 'Not supplied') + '\n\n' +
      'No experiment or independent evidence review. No email updates requested.\n';
    const record = state.record;
    let text = 'NorthStar chat check — UNVERIFIED EXPLORATORY REPORT\n' +
      'Record: ' + record.id + '\nStarted: ' + record.createdAt + '\nApp/model (self-reported): ' + record.app +
      '\nPlan: ' + packet.version + ' · ' + packet.protocol + '\nLimit: 2 messages; existing allowance only; no retries.\n' +
      'Interface: manually pasted user prompts; app system/memory uncontrolled; not an exact MMS1 replication.\n' +
      'Inputs: https://dontkillthehumans.org/contributor-check-inputs.json\n';
    packet.cases.forEach((item, index) => {
      const answer = record.answers[index];
      text += '\nCHECK ' + (index + 1) + ' (' + item.id + ')\nPrompt SHA-256: ' + item.sha256 + '\n';
      if (includePrompts) text += 'Exact prompt:\n' + item.prompt + '\n';
      text += 'Status: ' + answer.status + '\nReply:\n' + (answer.text || '[No answer recorded; whether a call occurred is unknown.]') + '\n';
    });
    return text + '\nNo automatic score. Keep missing answers, refusals and clean results. No email updates requested.\n';
  }
  function showReport(focus = true) {
    const isChat = state.mode === 'chat';
    const answered = isChat ? state.record.answers.filter(a => a.status === 'reply').length : 0;
    byId('report-summary').textContent = isChat
      ? answered + ' of 2 replies recorded. ' + (answered < 2 ? 'This is a partial report; missing answers are kept visible.' : 'Both full replies are included, without an automatic score.')
      : 'One instruction proposal, ready for the maintainer to review.';
    byId('report-purpose').textContent = isChat
      ? 'A reviewer can check these answers and decide whether this setup deserves a registered follow-up. A clean result or refusal is useful to report too.'
      : 'We can review this as a candidate remedy, compare it with a plain reminder and identify where it might fail. It has not been tested.';
    byId('report-text').value = reportText(false);
    const subject = isChat ? 'NorthStar chat check ' + state.record.id : 'NorthStar instruction proposal';
    const shortBody = isChat ?
      'UNVERIFIED chat check ' + packet.version + '\nID: ' + state.record.id + '\nStarted: ' + state.record.createdAt +
      '\nApp/model: ' + state.record.app + '\nManual chat; app system/memory uncontrolled. Not an exact replication.\n' +
      packet.protocol + '\nInputs: https://dontkillthehumans.org/contributor-check-inputs.json\n' +
      packet.cases.map((item, i) => '\n' + item.id + ' SHA-256: ' + item.sha256 + '\n' + state.record.answers[i].status +
        ':\n' + (state.record.answers[i].text || '[No answer recorded; call occurrence unknown.]')).join('\n') +
      '\n\nNo automatic score. No email updates requested.' : reportText(false);
    const email = body => 'mailto:info@calibratedvision.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    const fits = email(shortBody).length <= 1800;
    byId('send-report').href = email(fits ? shortBody : 'Please review my NorthStar contribution.\n\nAttach the saved report or paste the complete report here before sending.\nNothing has been attached automatically.\n\nNo email updates requested.');
    byId('send-report').textContent = fits ? 'Open email to send →' : 'Open email & attach report →';
    byId('share-instructions').textContent = fits
      ? 'The email includes your complete answers and identifies the published inputs. Review it, then press Send in your email app.'
      : 'Your report is too long for a reliable email link. First save or copy it below, then attach the file or paste all of it into your email. Nothing is attached automatically.';
    byId('report-status').textContent = 'Nothing has been sent. Send the email from your own app.';
    panel('report', focus);
  }
  byId('start-form').addEventListener('submit', event => {
    event.preventDefault();
    const app = byId('app-model').value.trim();
    if (!app) { byId('app-model').focus(); return; }
    state.mode = 'chat'; state.index = 0;
    state.record = {version: packet.version, id: 'CHAT-' + (globalThis.crypto?.randomUUID?.() || Date.now().toString(36) + '-' + Math.random().toString(36).slice(2)),
      createdAt: new Date().toISOString(), app, answers: packet.cases.map(() => ({status: 'not_recorded', text: ''}))};
    showCheck();
  });
  byId('copy-check').addEventListener('click', () => copy(packet.cases[state.index].prompt, byId('check-prompt'), byId('copy-status'),
    'Copied. Paste into a fresh AI chat. Then return here with its first complete reply.'));
  byId('check-answer').addEventListener('input', captureAnswer);
  byId('no-answer').addEventListener('change', () => {
    // Preserve an already pasted answer; never erase it with a checkbox.
    if (byId('check-answer').value.trim()) byId('no-answer').checked = false;
    byId('check-answer').disabled = byId('no-answer').checked;
    captureAnswer();
  });
  byId('reply-form').addEventListener('submit', event => {
    event.preventDefault(); captureAnswer();
    if (state.record.answers[state.index].status === 'not_recorded') {
      byId('reply-error').textContent = 'Paste the full reply, or choose “I couldn’t get an answer.”';
      byId('check-answer').focus(); return;
    }
    if (state.index === 0) { state.index = 1; showCheck(); } else showReport();
  });
  byId('stop-check').addEventListener('click', () => { captureAnswer(); showReport(); });
  byId('previous-check').addEventListener('click', () => { captureAnswer(); state.index = 0; showCheck(); });
  byId('choose-human').addEventListener('click', () => { state.mode = 'human'; panel('human'); });
  byId('choose-ai').addEventListener('click', () => { state.mode = 'chat'; panel('start'); });
  const captureHuman = () => {
    state.human = {lesson: byId('human-lesson').value, limit: byId('human-limit').value}; save();
  };
  byId('human-form').addEventListener('input', captureHuman);
  byId('human-form').addEventListener('submit', event => {
    event.preventDefault(); captureHuman();
    if (!state.human.lesson.trim()) { byId('human-lesson').focus(); return; }
    state.mode = 'human'; showReport();
  });
  byId('copy-report').addEventListener('click', () => copy(reportText(true), byId('report-text'), byId('report-status'),
    'Report copied. Paste it into an email to info@calibratedvision.com. Nothing has been sent.'));
  byId('download-report').addEventListener('click', () => {
    const url = URL.createObjectURL(new Blob([reportText(true)], {type: 'text/plain;charset=utf-8'}));
    const link = document.createElement('a'); link.href = url;
    link.download = state.mode === 'chat' ? state.record.id + '.txt' : 'northstar-instruction-proposal.txt';
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
    byId('report-status').textContent = 'Download started. Attach the report to your email before sending. Nothing has been submitted.';
  });
  byId('edit-report').addEventListener('click', () => state.mode === 'human' ? panel('human') : showCheck());
  byId('human-lesson').value = state.human.lesson;
  byId('human-limit').value = state.human.limit;
  if (state.record) byId('app-model').value = state.record.app;
  if (location.hash === '#idea' && state.panel === 'start') { state.mode = 'human'; state.panel = 'human'; }
  byId('onboarding').hidden = false;
  if (state.panel === 'check') showCheck(false);
  else if (state.panel === 'report') showReport(false);
  else panel(state.panel, false);
})();
