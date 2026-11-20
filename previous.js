(() => {
  'use strict';
  const bank = window.PREVIOUS_PAPERS;
  const ACTIVE = 'rrbpo_previous_active_v1', HISTORY = 'rrbpo_previous_history_v1';
  const $ = s => document.querySelector(s);
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const read = (key, fallback) => { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } };
  let storageFailed = false;
  const write = (key, value) => { try { value === null ? localStorage.removeItem(key) : localStorage.setItem(key, JSON.stringify(value)); } catch { storageFailed = true; } };
  const paperFor = id => bank.papers.find(t => t.id === id);
  const excluded = (t,n) => t.excludedQuestions?.[n];
  const maxScore = t => 80-Object.keys(t.excludedQuestions || {}).length;
  const sourceWarning = t => {
    const entries = Object.entries(t.excludedQuestions || {});
    return entries.length ? `<details class="py-note py-warning"><summary>${entries.length} source question(s) excluded. Maximum score: ${maxScore(t)}.</summary>${entries.map(([n,note])=>`<p><strong>Q${n}:</strong> ${esc(note)}</p>`).join('')}</details>` : '';
  };
  const answeredCount = (t, answers) => Object.keys(answers).filter(n => !excluded(t,n) && Number(n)>=1 && Number(n)<=80).length;
  const history = () => {
    const saved = read(HISTORY, []);
    if (!Array.isArray(saved)) return [];
    let changed = false;
    const rows = saved.map(row => {
      const t = paperFor(row.paperId);
      if (!t || row.reviewVersion === bank.auditVersion) return row;
      changed = true;
      return {...row, ...grade(t, row.answers || {}), previousScore: row.score, reviewVersion: bank.auditVersion};
    });
    if (changed) write(HISTORY, rows);
    return rows;
  };
  let active = read(ACTIVE, null), view = 'home';
  if (active && (!paperFor(active.paperId) || !Number.isFinite(active.endAt) || !active.answers || !Array.isArray(active.marked) || !Array.isArray(active.visited) || !Number.isInteger(active.number) || active.number < 1 || active.number > 80 || !Number.isInteger(active.pageIndex) || active.pageIndex < 0 || active.pageIndex >= paperFor(active.paperId).pages.length)) active = null;
  const save = () => write(ACTIVE, active);
  const warning = () => storageFailed ? '<p class="py-note py-warning" role="alert">Browser storage is unavailable. Keep this tab open to retain your answers.</p>' : '';
  const clock = () => { const n = Math.max(0, Math.ceil((active.endAt-Date.now())/1000)); return `${String(Math.floor(n/60)).padStart(2,'0')}:${String(n%60).padStart(2,'0')}`; };
  const status = n => active.marked.includes(n) ? (active.answers[n] !== undefined ? 'marked-answered' : 'marked') : active.answers[n] !== undefined ? 'answered' : active.visited.includes(n) ? 'visited' : '';

  function ask(title, message, action) {
    $('#pyDialog')?.remove();
    const dialog = document.createElement('dialog'); dialog.id = 'pyDialog'; dialog.className = 'py-modal';
    dialog.setAttribute('aria-labelledby', 'pyDialogTitle');
    dialog.innerHTML = `<h2 id="pyDialogTitle">${esc(title)}</h2><p>${esc(message)}</p><div class="py-actions"><button class="btn btn-primary" id="pyConfirm">Confirm</button><button class="btn btn-ghost" id="pyCancel">Cancel</button></div>`;
    document.body.append(dialog);
    $('#pyConfirm').onclick = () => { dialog.close(); dialog.remove(); action(); };
    $('#pyCancel').onclick = () => { dialog.close(); dialog.remove(); };
    dialog.showModal(); $('#pyCancel').focus();
  }

  function home() {
    view = 'home';
    window.history.replaceState(null, '', location.pathname + location.search);
    const attempts = history();
    $('#app').innerHTML = `${warning()}<section class="py-hero"><span class="py-label">FROM YOUR DOWNLOAD PACK</span><h1>Previous year papers.</h1><p>Work through the original memory-based papers in an exam-style PDF workspace. Read each page, record your answers, and review your attempt against the reviewed key.</p><div class="py-pills"><span>12 papers · 2021–2025</span><span>80-question answer sheets</span><span>45-minute practice timer</span><span>12 reviewed answer keys</span></div></section>
      ${active ? `<div class="py-note"><strong>${esc(paperFor(active.paperId).title)} is in progress.</strong> The clock continues while you are away. <button class="btn btn-primary" id="pyResume">${Date.now() >= active.endAt ? 'View timed-out result' : 'Resume paper'}</button></div>` : ''}
      <p class="py-note">${esc(bank.sourceNote)} These PDFs use different question orders, so this workspace uses one <strong>45-minute practice timer</strong>, with free question navigation. It does not simulate sectional timing. Questions, diagrams and options retain the source layout. Printed answer labels are hidden during practice. Scoring with the reviewed key: +1 correct, −0.25 wrong, 0 unanswered. The 2021 answers have now been derived. Defective questions are excluded from scoring; each paper shows its adjusted maximum.</p>
      <p class="py-note"><strong>Answer audit complete:</strong> 960 slots reviewed, 928 usable answers and 32 source questions excluded. Two publisher keys are corrected. Saved attempts are recalculated with the reviewed key. <a href="data/previous/reviewed_answers.csv" download>Download all reviewed answers (CSV)</a></p><div class="py-heading"><h2>Choose a paper</h2><label>Year <select id="pyYear" aria-label="Filter papers by year"><option value="all">All years</option>${[2025,2024,2023,2022,2021].map(y=>`<option value="${y}">${y}</option>`).join('')}</select></label></div>
      <div class="py-grid">${bank.papers.map(t => {
        const attemptsFor = attempts.filter(a => a.paperId === t.id), last = attemptsFor[0];
        return `<article class="py-card" data-year="${t.date.slice(0,4)}"><span class="py-label">${t.date.slice(0,4)} · Memory-based</span><h3>${esc(t.title)}</h3><p>80 question slots · ${t.pages.length} source pages<br>${Object.keys(t.answers).length === 80 ? 'Reviewed answers and explanations' : 'No reviewed answer key · ungraded practice'}</p>${last ? `<p>Last attempt: ${last.score === null ? `${Object.keys(last.answers).length} answered · ungraded` : `${last.score}/${maxScore(t)}`}</p>` : ''}${sourceWarning(t)}<div class="py-actions"><button class="btn btn-primary" data-start="${t.id}">Start paper</button><button class="btn btn-ghost" data-key="${t.id}">Right answers & explanations</button><a href="${esc(t.pdf)}" target="_blank" rel="noopener">Practice PDF</a>${last ? `<button class="btn btn-ghost" data-latest="${t.id}">Latest result</button>` : ''}</div></article>`;
      }).join('')}</div>
      ${attempts.length ? `<div class="py-heading"><h2>Your recent attempts</h2></div><div class="py-table-wrap"><table class="py-table"><thead><tr><th>Paper</th><th>Completed</th><th>Score</th><th>Review</th></tr></thead><tbody>${attempts.slice(0,20).map((r,i)=>`<tr><td>${esc(paperFor(r.paperId)?.title)}</td><td>${esc(new Date(r.completedAt).toLocaleString())}</td><td>${r.score === null ? 'Ungraded' : `${r.score}/${maxScore(paperFor(r.paperId))}`}</td><td><button class="btn btn-ghost" data-history="${i}">Review attempt</button></td></tr>`).join('')}</tbody></table></div>` : ''}`;
    $('#pyYear').onchange = e => document.querySelectorAll('[data-year]').forEach(card => card.hidden = e.target.value !== 'all' && card.dataset.year !== e.target.value);
    $('#pyResume')?.addEventListener('click', () => { if (!expire()) exam(); });
    document.querySelectorAll('[data-key]').forEach(b => b.onclick = () => answerKey(paperFor(b.dataset.key)));
    document.querySelectorAll('[data-start]').forEach(b => b.onclick = () => instructions(b.dataset.start));
    document.querySelectorAll('[data-latest]').forEach(b => b.onclick = () => result(attempts.find(a=>a.paperId === b.dataset.latest)));
    document.querySelectorAll('[data-history]').forEach(b => b.onclick = () => result(attempts[Number(b.dataset.history)]));
  }

  function instructions(id) {
    view = 'instructions'; const t = paperFor(id);
    $('#app').innerHTML = `<section class="py-result"><span class="py-label">BEFORE YOU BEGIN</span><h1>${esc(t.title)}</h1>${sourceWarning(t)}<p class="py-note">80 question slots · one 45-minute practice timer. The test submits automatically at the deadline, including after a refresh or a return to the library. Your answers save immediately in this browser. Marked answers are included in scoring.</p><p class="py-note">Read the paper in the document panel. Select a question number on the answer sheet, then choose A–E (the first through fifth source options). Use the page controls to move through the PDF; the answer sheet and PDF can be navigated independently. This preserves shared passages, tables and diagrams. ${Object.keys(t.questionPages).length ? 'Selecting a question also opens its source page.' : 'For this scanned paper, find the matching question using the page controls.'}</p><p class="py-note ${Object.keys(t.answers).length ? '' : 'py-warning'}">${Object.keys(t.answers).length ? 'Scoring with the reviewed key: +1 correct, −0.25 wrong and 0 unanswered, using the reviewed answer key. Review shows checked answers, brief explanations, and source issues.' : 'No answer key was included for this paper. You can complete a timed attempt and review your answers, but no score or correct/incorrect labels will be invented.'}</p>${active ? '<p class="py-note py-warning">Starting this paper will replace your unfinished previous-paper attempt.</p>' : ''}<div class="py-actions"><button class="btn btn-primary" id="pyBegin">Begin 45-minute paper</button><button class="btn btn-ghost" id="pyBack">Back to papers</button></div></section>`;
    $('#pyBack').onclick = home;
    $('#pyBegin').onclick = () => active ? ask('Replace unfinished attempt?', 'Your unfinished previous-paper attempt will be replaced.', () => start(t)) : start(t);
    window.scrollTo(0,0);
  }

  function start(t) {
    active = {paperId:t.id, startedAt:Date.now(), endAt:Date.now()+t.durationMinutes*60000, number:1, pageIndex:0, answers:{}, marked:[], visited:[]};
    save(); exam(); window.scrollTo(0,0);
  }
  function expire() { if (active && Date.now() >= active.endAt) { finish(true); return true; } return false; }

  function documentPanel(t, pageIndex, review=false) {
    return `<section class="py-document" aria-label="Original question paper"><div class="py-toolbar"><button class="btn btn-ghost" id="pyPrevPage" ${pageIndex === 0 ? 'disabled' : ''}>Previous page</button><label>Page <input id="pyPage" type="number" min="1" max="${t.pages.length}" value="${pageIndex+1}"> of ${t.pages.length}</label><button class="btn btn-ghost" id="pyNextPage" ${pageIndex === t.pages.length-1 ? 'disabled' : ''}>Next page</button><a href="${esc(t.pdf)}#page=${pageIndex+1}" target="_blank" rel="noopener">Open PDF</a></div><p class="py-help">${review ? 'Question paper for checking your answers.' : 'Read the question here, then record its option on the answer sheet. PDF pages and question numbers navigate independently for scanned papers.'}</p><img id="pyPageImage" src="${esc(t.pages[pageIndex])}" alt="${esc(t.title)}, question-paper page ${pageIndex+1}. Use Open PDF for the source document."><p class="py-help" id="pyImageError" hidden>Page image could not load. Use Open PDF to read the paper.</p></section>`;
  }
  function bindDocument(t, pageIndex, update) {
    $('#pyPrevPage').onclick = () => update(pageIndex-1);
    $('#pyNextPage').onclick = () => update(pageIndex+1);
    $('#pyPage').onchange = e => { const n = Number(e.target.value); if (Number.isInteger(n) && n >= 1 && n <= t.pages.length) update(n-1); else e.target.value=pageIndex+1; };
    $('#pyPageImage').onerror = () => { $('#pyImageError').hidden=false; };
  }
  function jump(n) {
    if (expire()) return;
    active.number = Math.min(80,Math.max(1,n));
    const pageIndex = paperFor(active.paperId).questionPages[active.number];
    if (pageIndex !== undefined) active.pageIndex=pageIndex;
    save(); exam();
  }
  function exam() {
    if (!active || expire()) return;
    view='exam'; const t = paperFor(active.paperId), n = active.number;
    if (!active.visited.includes(n)) active.visited.push(n); save();
    $('#app').innerHTML = `${warning()}<div class="py-heading"><h1>${esc(t.title)}</h1><button class="btn btn-ghost" id="pyLeave">Save & return to papers</button></div><div class="py-layout">${documentPanel(t,active.pageIndex)}<aside class="py-sheet" aria-label="Answer sheet"><span class="py-label">Time left</span><div class="py-timer" id="pyTimer" role="timer">${clock()}</div><h2>Answer sheet · Q${n} of 80</h2>${excluded(t,n) ? `<p class="py-note py-warning">${esc(excluded(t,n))}</p>` : ''}<div class="py-choices" role="group" aria-label="Answer for question ${n}">${[0,1,2,3,4].map(i=>`<button data-choice="${i}" ${excluded(t,n) ? 'disabled' : ''} class="${active.answers[n] === i ? 'selected' : ''}" aria-pressed="${active.answers[n] === i}">${'ABCDE'[i]}</button>`).join('')}</div><p class="py-help">A–E correspond to the first–fifth options in the PDF. Your answer saves when selected.</p><div class="py-actions"><button class="btn btn-ghost" id="pyClear">Clear answer</button><button class="btn btn-ghost" id="pyMark" aria-pressed="${active.marked.includes(n)}">${active.marked.includes(n) ? 'Unmark review' : 'Mark for review'}</button></div><div class="py-actions" style="margin-top:12px"><button class="btn btn-ghost" id="pyPrevious" ${n===1 ? 'disabled' : ''}>Previous Q</button><button class="btn btn-primary" id="pyNext" ${n===80 ? 'disabled' : ''}>Next Q</button></div><div class="py-palette" aria-label="Question navigation">${Array.from({length:80},(_,i)=>i+1).map(q=>`<button data-question="${q}" class="${status(q)} ${q===n ? 'current' : ''}" aria-label="Question ${q}, ${status(q) || 'not visited'}" ${q===n ? 'aria-current="true"' : ''}>${q}</button>`).join('')}</div><p class="py-help">Green: answered · Purple: review · Purple with green edge: answered & review · Cream: visited · Grey: not visited</p><p id="pyAnswered">${answeredCount(paperFor(active.paperId), active.answers)}/80 answered · ${active.marked.length} marked</p><button class="btn btn-primary" id="pySubmit">Submit paper</button></aside></div>`;
    bindDocument(t,active.pageIndex,index=>{if(expire())return; active.pageIndex=index;save();exam();});
    document.querySelectorAll('[data-choice]').forEach(b=>b.onclick=()=>{if(expire())return;active.answers[n]=Number(b.dataset.choice);save();exam();});
    document.querySelectorAll('[data-question]').forEach(b=>b.onclick=()=>jump(Number(b.dataset.question)));
    $('#pyClear').onclick=()=>{if(expire())return;delete active.answers[n];save();exam();};
    $('#pyMark').onclick=()=>{if(expire())return;active.marked=active.marked.includes(n)?active.marked.filter(q=>q!==n):[...active.marked,n];save();exam();};
    $('#pyPrevious').onclick=()=>jump(n-1); $('#pyNext').onclick=()=>jump(n+1);
    $('#pyLeave').onclick=home;
    $('#pySubmit').onclick=()=>ask('Submit this paper?', `${answeredCount(paperFor(active.paperId), active.answers)} of 80 answered. Marked answers are scored. Submission ends this attempt.`,()=>finish(false));
  }
  function grade(t, answers) {
    if (Object.keys(t.answers).length !== 80) return {score:null,correct:null,wrong:null,skipped:80-Object.keys(answers).length};
    let correct=0,wrong=0;
    for(let n=1;n<=80;n++){if(excluded(t,n))continue;if(answers[n]===undefined)continue;if(answers[n]===t.answers[n])correct++;else wrong++;}
    return {score:correct-wrong*.25,correct,wrong,skipped:maxScore(t)-correct-wrong};
  }
  function finish(timedOut) {
    if (!active) return;
    $('#pyDialog')?.remove();
    const t=paperFor(active.paperId), row={...active,...grade(t,active.answers),timedOut,reviewVersion:bank.auditVersion,completedAt:new Date().toISOString()};
    write(HISTORY,[row,...history()].slice(0,100)); active=null;save();result(row);
  }
  function reviewTable(t, row, filter) {
    const answers = row?.answers || {};
    const marked = row?.marked || [];
    return `<div class="py-table-wrap"><table class="py-table py-review-table"><thead><tr><th>Question</th>${row ? '<th>Your choice</th>' : ''}<th>Right answer</th>${row ? '<th>Evaluation</th>' : ''}<th>Explanation & source</th></tr></thead><tbody>${Array.from({length:80},(_,i)=>i+1).map(n => {
      const detail = t.answerDetails[n], a = answers[n], k = t.answers[n];
      const state = excluded(t,n) ? 'excluded' : a === undefined ? 'skipped' : a === k ? 'correct' : 'wrong';
      if (filter !== 'all' && filter !== state && !(filter === 'answered' && a !== undefined && state !== 'excluded') && !(filter === 'corrected' && detail.correctedPublisherKey)) return '';
      const page = t.questionPages[n];
      const publisher = t.sourceAnswers?.[n];
      return `<tr><td>Q${n}${marked.includes(n) ? ' (marked)' : ''}</td>${row ? `<td>${a === undefined ? '-' : 'ABCDE'[a]}</td>` : ''}<td>${detail.status === 'excluded' ? 'Excluded' : `<strong>${'ABCDE'[k]}</strong>`}${detail.correctedPublisherKey ? `<br><span class="py-correct">Corrected from publisher ${'ABCDE'[publisher]}</span>` : ''}</td>${row ? `<td class="${state === 'correct' ? 'py-correct' : state === 'wrong' ? 'py-wrong' : ''}">${state === 'excluded' ? 'Not scored' : state === 'skipped' ? 'Unanswered (0)' : state === 'correct' ? 'Correct (+1)' : 'Wrong (-0.25)'}</td>` : ''}<td class="py-explanation"><details ${detail.correctedPublisherKey || detail.status === 'excluded' ? 'open' : ''}><summary>${detail.status === 'excluded' ? 'Why this cannot be graded' : 'Show explanation'}</summary><p>${esc(detail.explanation)}</p></details>${page === undefined ? '' : `<button class="btn btn-ghost" data-review-page="${page}">View source page ${page+1}</button>`}</td></tr>`;
    }).join('')}</tbody></table></div>`;
  }

  function bindReviewDocument(t, pageIndex, render) {
    bindDocument(t,pageIndex,i=>{render(i);$('#pyReviewDocument').scrollIntoView({block:'start'});});
    document.querySelectorAll('[data-review-page]').forEach(b=>b.onclick=()=>{render(Number(b.dataset.reviewPage));$('#pyReviewDocument').scrollIntoView({block:'start'});});
  }

  function answerKey(t) {
    window.history.replaceState(null, '', '#answers=' + encodeURIComponent(t.id));
    view='key';let pageIndex=0,filter='all';
    function render(index=pageIndex) {
      pageIndex=index;
      $('#app').innerHTML=`<section class="py-result"><span class="py-label">REVIEWED ANSWER KEY</span><h1>${esc(t.title)}</h1><h2>Right answers & explanations</h2><p>All 80 question slots reviewed. ${maxScore(t)} questions can be scored; ${80-maxScore(t)} are excluded because the source information is defective or incomplete.</p><p class="py-help">These are checked practice answers. Original publisher keys are retained for comparison. Syllogisms use the usual exam convention that the named sets exist.</p><div class="py-actions"><button class="btn btn-primary" id="pyKeyBack">Back to papers</button><button class="btn btn-ghost" id="pyKeyStart">Start timed paper</button><a href="data/previous/reviewed_answers.csv" download>Download reviewed answers (CSV)</a></div></section><div class="py-heading"><h2>Answer key</h2><label>Show <select id="pyKeyFilter"><option value="all">All questions</option><option value="corrected">Corrected publisher keys</option><option value="excluded">Excluded questions</option></select></label></div>${reviewTable(t,null,filter)}<div id="pyReviewDocument" style="margin-top:24px">${documentPanel(t,pageIndex,true)}</div>`;
      $('#pyKeyBack').onclick=home;$('#pyKeyStart').onclick=()=>instructions(t.id);
      $('#pyKeyFilter').value=filter;$('#pyKeyFilter').onchange=e=>{filter=e.target.value;render();};
      bindReviewDocument(t,pageIndex,render);
    }
    render();window.scrollTo(0,0);
  }

  function result(row) {
    view='result';const t=paperFor(row.paperId);row={...row,...grade(t,row.answers)};let pageIndex=0,filter='all';
    function render(index=pageIndex) {
      pageIndex=index;
      $('#app').innerHTML=`${warning()}<section class="py-result"><span class="py-label">${row.timedOut ? 'TIME COMPLETED - AUTOMATICALLY SUBMITTED' : 'PAPER EVALUATED'}</span><h1>${esc(t.title)}</h1><h2 id="pyScore">${row.score}/${maxScore(t)}</h2><p>${row.correct} correct, ${row.wrong} wrong, ${row.skipped} unanswered; ${80-maxScore(t)} source questions excluded. +1 correct, -0.25 wrong.</p><p class="py-help">Evaluated with reviewed key ${esc(bank.auditVersion)}. ${row.previousScore !== undefined && row.previousScore !== row.score ? `Previous score: ${row.previousScore === null ? 'ungraded' : esc(row.previousScore)}. ` : ''}Saved choices are preserved; excluded questions do not affect the score.</p><div class="py-actions"><button class="btn btn-primary" id="pyResultHome">Back to papers</button><button class="btn btn-ghost" id="pyRetake">Retake paper</button><button class="btn btn-ghost" id="pyOpenKey">Full answer key</button>${t.keyPdf ? `<a href="${esc(t.keyPdf)}" target="_blank" rel="noopener">Original publisher key (uncorrected)</a>` : ''}<a href="${esc(t.sourceUrl)}" target="_blank" rel="noopener">Original publisher PDF</a></div></section><div class="py-heading"><h2>Your answer evaluation</h2><label>Show <select id="pyReviewFilter"><option value="all">All questions</option><option value="answered">Answered</option><option value="skipped">Unanswered</option><option value="correct">Correct</option><option value="wrong">Wrong</option><option value="excluded">Excluded</option><option value="corrected">Corrected keys</option></select></label></div>${reviewTable(t,row,filter)}<div style="margin-top:24px" id="pyReviewDocument">${documentPanel(t,pageIndex,true)}</div>`;
      $('#pyReviewFilter').value=filter;$('#pyReviewFilter').onchange=e=>{filter=e.target.value;render();};
      $('#pyResultHome').onclick=home;$('#pyRetake').onclick=()=>instructions(t.id);$('#pyOpenKey').onclick=()=>answerKey(t);
      bindReviewDocument(t,pageIndex,render);
    }
    render();window.scrollTo(0,0);
  }
  $('#previousHome').onclick=home;
  setInterval(()=>{if(!active)return;if(expire())return;if(view==='exam'&&$('#pyTimer'))$('#pyTimer').textContent=clock();},1000);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)expire();});
  window.addEventListener('pageshow',()=>expire());
  const initialKey = new URLSearchParams(location.hash.slice(1)).get('answers');
  home();
  if (initialKey && paperFor(initialKey)) answerKey(paperFor(initialKey));
  expire();
  window.PreviousPortal={grade,history};
})();
