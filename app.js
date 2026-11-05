/* Offline-first independent RRB PO prelims mock interface.
   For personal practice only: client-side data includes answer keys after download.
   A production exam service must keep answers on a trusted server. */
(() => {
  'use strict';
  const ACTIVE_KEY='rrbpo_active_v1', HISTORY_KEY='rrbpo_history_v1';
  const $ = (sel) => document.querySelector(sel);
  const esc = (str) => String(str ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let data=null, active=null, page='home', lastRenderedSecond=-1;
  const colors=['#2c72b8','#f69e4a','#47a88e','#8b69bf','#d35d74'];
  const tests = () => data.tests;
  const getTest = (id) => tests().find(t => t.id === id);
  const storeActive = () => {try {if(active)localStorage.setItem(ACTIVE_KEY,JSON.stringify(active));else localStorage.removeItem(ACTIVE_KEY);}catch(err){console.warn('Could not save progress',err);}};
  const history = () => {try {return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');}catch{return [];}};
  function storeHistory(rows) {try {localStorage.setItem(HISTORY_KEY,JSON.stringify(rows));}catch(err){console.warn('History storage unavailable',err);}}
  function getSection(){return getTest(active.testId).sections[active.sectionIndex];}
  function getCurrentQuestion(){return getTest(active.testId).questions[active.currentIndex];}
  function timeText(s){s=Math.max(0,Math.ceil(s));return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');}
  function millisLeft(){return active ? active.sectionEndAt-Date.now():0;}
  function statusFor(id){return active.marked.includes(id)?'marked':active.answers[id]!==undefined?'answered':active.visited.includes(id)?'visited':'';}
  function enterHome(){page='home';renderHome();}
  function startTest(id){
    const existing = active && active.testId===id;
    if(active && active.testId!==id && !confirm('A previous mock is in progress. Starting this mock will discard that unfinished attempt. Continue?'))return;
    if(!existing){
      const now=Date.now();active={testId:id,startedAt:now,sectionIndex:0,sectionEndAt:now+1500000,currentIndex:0,
        answers:{},visited:[getTest(id).questions[0].id],marked:[]};storeActive();
    }
    page='exam';renderExam();
  }
  function resumeTest(){if(active){page='exam';syncDeadline();if(active)renderExam();}}
  function showInstructions(id){
    page='instructions';const t=getTest(id);
    $('#app').innerHTML=`<div class="panel instructions"><span class="pill">Full-length mock ${t.number} / 20</span>
      <h1>${esc(t.title)}</h1><p class="muted">This is an independently authored practice paper, not a leaked or official IBPS paper.</p>
      <ul><li><strong>80 questions for 80 marks</strong>: 40 Reasoning + 40 Quantitative Aptitude.</li>
      <li><strong>Section timers:</strong> Reasoning 25 minutes, then Quantitative Aptitude 20 minutes (45 minutes in total).</li>
      <li><strong>Marking:</strong> +1 correct, −0.25 wrong, zero if unanswered.</li>
      <li>You may move among questions <em>within the current section</em>. You cannot return to Reasoning after its timer ends.</li>
      <li>There is no pause. This is a locally timed practice session; it will auto-submit after the second section.</li>
      <li>Solutions and the answer key appear only <strong>after submission</strong>.</li>
      <li>No email, phone number, login or payment. Your progress is saved to this browser only.</li></ul>
      <div class="actions"><button id="start" class="btn">Begin timed mock</button><button id="back" class="btn btn-outline">Back</button></div></div>`;
    $('#start').onclick=()=>startTest(id);$('#back').onclick=enterHome;
  }
  function renderHome(){
    page='home';
    const attempts=history();
    const best={};for(const row of attempts){if(!best[row.testId]||row.score>best[row.testId])best[row.testId]=row.score;}
    $('#app').innerHTML=`<section class="hero"><span class="pill">2026 Officer Scale I • Prelims</span>
       <h1>20 complete RRB PO mock papers</h1><p>Practise with 1,600 original multiple-choice questions, real section timers, negative marking, navigation palettes and detailed result reviews. No registration required.</p></section>
       <div class="stats"><div class="stat"><b>20</b><small>Full-length papers</small></div><div class="stat"><b>1,600</b><small>Total questions</small></div><div class="stat"><b>45 min</b><small>Per full mock</small></div><div class="stat"><b>${attempts.length}</b><small>Completed attempts</small></div></div>
       ${active?`<section class="message"><strong>Unfinished attempt:</strong> ${esc(getTest(active.testId).title)}. Your section timer is still running. <button class="btn btn-outline" id="resume">Resume now</button></section>`:''}
       <h2>Choose your mock</h2><div class="cards">${tests().map(t=>`<article class="card"><small>OFFICER SCALE I • PAPER ${String(t.number).padStart(2,'0')}</small>
       <h2>${esc(t.title)}</h2><div class="muted">40 Reasoning • 40 Quant • 45 min</div>
       ${best[t.id]===undefined?'<div class="progress"><span style="width:0%"></span></div>':`<div class="status">Best score ${Number(best[t.id]).toFixed(2)}/80</div><div class="progress"><span style="width:${Math.max(0,Math.min(100,best[t.id]*100/80))}%"></span></div>`}
       <div class="footer-actions"><button class="btn" data-start="${t.id}">${active&&active.testId===t.id?'Continue mock':'Start mock'}</button></div></article>`).join('')}</div>
       ${attempts.length?`<section class="history"><h2>Previous attempts</h2><div class="history-list">${attempts.slice(0,10).map(row=>`<div class="history-row"><span>${esc(row.title)} • ${esc(new Date(row.completedAt).toLocaleString())}</span><span><strong>${Number(row.score).toFixed(2)}/80</strong> <button class="btn btn-outline" data-review="${esc(row.attemptId)}">Review</button></span></div>`).join('')}</div></section>`:''}`;
    $('#app').querySelectorAll('[data-start]').forEach(b=>b.onclick=()=>active&&active.testId===b.dataset.start?resumeTest():showInstructions(b.dataset.start));
    $('#app').querySelectorAll('[data-review]').forEach(b=>b.onclick=()=>showResult(b.dataset.review));
    if($('#resume'))$('#resume').onclick=resumeTest;
  }
  function renderTable(st){return `<table class="data-table"><thead><tr>${st.columns.map(c=>`<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>${st.rows.map(r=>`<tr><td>${esc(r.label)}</td><td>${esc(r.a)}</td><td>${esc(r.b)}</td></tr>`).join('')}</tbody></table>`;}
  function renderBars(st){
    const max=Math.max(...st.rows.flatMap(r=>[r.a,r.b]));
    return `<div class="chart-legend"><span><i class="legend-dot"></i>${esc(st.columns[1])}</span><span><i class="legend-dot alt"></i>${esc(st.columns[2])}</span></div>`+
      st.rows.map(r=>`<div class="bar-row"><b>${esc(r.label)}</b><div class="bar-area"><div title="${r.a}" class="bar-item" style="width:${r.a*100/max}%"></div><div title="${r.b}" class="bar-item alt" style="width:${r.b*100/max}%"></div></div></div>`).join('');
  }
  function renderLine(st){
    const w=520,h=185,pad=22,max=Math.max(...st.rows.flatMap(r=>[r.a,r.b]))*1.08;
    const pt=(col)=>st.rows.map((r,i)=>`${pad+i*(w-2*pad)/4},${(h-pad)-r[col]*(h-2*pad)/max}`).join(' ');
    const dots=col=>st.rows.map((r,i)=>`<circle cx="${pad+i*(w-2*pad)/4}" cy="${(h-pad)-r[col]*(h-2*pad)/max}" r="3.5" fill="${col==='a'?colors[0]:colors[1]}"/>`).join('');
    return `<div class="chart-legend"><span><i class="legend-dot"></i>${esc(st.columns[1])}</span><span><i class="legend-dot alt"></i>${esc(st.columns[2])}</span></div><svg viewBox="0 0 ${w} ${h}" style="width:100%;height:auto" role="img" aria-label="Two-series line graph, exact values listed in the table"><line x1="${pad}" x2="${w-pad}" y1="${h-pad}" y2="${h-pad}" stroke="#90a1b4"/><polyline fill="none" stroke="${colors[0]}" stroke-width="3" points="${pt('a')}"/><polyline fill="none" stroke="${colors[1]}" stroke-width="3" points="${pt('b')}"/>${dots('a')}${dots('b')}${st.rows.map((r,i)=>`<text x="${pad+i*(w-2*pad)/4}" y="${h-5}" font-size="11" text-anchor="middle" fill="#5a6b80">${i+1}</text>`).join('')}</svg><small>Regions 1–5 are listed in table order.</small>`;
  }
  function renderPie(st){
    function pie(k,title){const total=st.rows.reduce((a,r)=>a+r[k],0);let offset=0;
      const stops=st.rows.map((r,i)=>{const start=offset;offset+=100*r[k]/total;return `${colors[i]} ${start.toFixed(3)}% ${offset.toFixed(3)}%`;}).join(',');
      return `<div><div class="chart-title">${esc(title)}</div><div class="pie" style="background:conic-gradient(${stops})" role="img" aria-label="Distribution of ${esc(title)}"></div></div>`;}
    return `<div class="chart-wrap">${pie('a',st.columns[1])}${pie('b',st.columns[2])}</div><div class="chart-legend">${st.rows.map((r,i)=>`<span><i class="legend-dot" style="background:${colors[i]}"></i>${esc(r.label)}</span>`).join('')}</div>`;
  }
  function renderStimulus(st){
    if(!st)return '';
    if(st.type!=='data_interpretation')return `<div class="stimulus"><h3>${esc(st.title)}</h3><pre>${esc(st.body)}</pre></div>`;
    const chart=st.visualization==='bar'?renderBars(st):st.visualization==='line'?renderLine(st):st.visualization==='pie'?renderPie(st):'';
    return `<div class="stimulus"><h3>${esc(st.title)}</h3>${st.visualization==='caselet'?`<p>${esc(st.body)}</p>`:''}${chart}${renderTable(st)}</div>`;
  }
  function syncDeadline(){
    if(!active)return;
    if(Date.now() < active.sectionEndAt)return;
    if(active.sectionIndex===0){
      const firstEnd=active.sectionEndAt;
      active.sectionIndex=1;active.sectionEndAt=firstEnd+1200000;active.currentIndex=40;
      const q=getCurrentQuestion();if(!active.visited.includes(q.id))active.visited.push(q.id);
      storeActive();
      if(Date.now()>=active.sectionEndAt){submitTest(true);return;}
      if(page==='exam'){alert('Reasoning time is over. Quantitative Aptitude has started. Reasoning is now locked.');}
    } else {submitTest(true);}
  }
  function tick(){
    if(!active)return;
    syncDeadline();
    if(!active)return;
    if(page==='exam'){
      const seconds=Math.max(0,Math.ceil(millisLeft()/1000));
      if(seconds!==lastRenderedSecond){
        lastRenderedSecond=seconds;
        const timer=$('#timer');if(timer){timer.textContent=timeText(seconds);timer.classList.toggle('critical',seconds<=60);}
      }
    }
  }
  function renderExam(){
    if(!active)return enterHome();syncDeadline();if(!active)return;
    page='exam';const t=getTest(active.testId),section=getSection(),question=getCurrentQuestion();
    const stim=question.stimulusId?t.stimuli.find(x=>x.id===question.stimulusId):null;
    const answered=question.id in active.answers;
    const secs=Math.max(0,Math.ceil(millisLeft()/1000));
    const answeredSection=t.questions.filter(x=>x.section===section.id && x.id in active.answers).length;
    $('#app').innerHTML=`<div class="exam-header"><div><h1>${esc(t.title)}</h1><small>${esc(section.name)} • ${answeredSection}/40 answered • Question ${active.currentIndex+1}/80</small></div>
       <div class="timer ${secs<=60?'critical':''}" id="timer" aria-live="polite">${timeText(secs)}</div><button class="btn btn-danger" id="submitButton">Submit test</button></div>
       <div class="exam-grid"><section class="panel question-panel"><div class="question-heading"><b>Question ${active.currentIndex+1}</b><span>${esc(question.topic)} • +1 / −0.25</span></div>
       ${renderStimulus(stim)}<p class="question-stem">${esc(question.stem)}</p>
       <div class="options">${question.options.map((opt,i)=>`<button class="option ${active.answers[question.id]===i?'selected':''}" data-answer="${i}" aria-pressed="${active.answers[question.id]===i}"><span class="opt-letter">${'ABCDE'[i]}</span><span>${esc(opt)}</span></button>`).join('')}</div>
       <div class="exam-actions"><button id="prev" class="btn btn-outline" ${active.currentIndex===section.start-1?'disabled':''}>Previous</button>
       <button id="clear" class="btn btn-outline" ${!answered?'disabled':''}>Clear response</button>
       <button id="mark" class="btn btn-outline">${active.marked.includes(question.id)?'Unmark review':'Mark for review'}</button>
       <button id="next" class="btn">${active.currentIndex===section.end-1?'Save':'Save & Next'}</button></div></section>
       <aside class="panel question-side"><h2>Question palette</h2><div class="palette">${t.questions.slice(section.start-1,section.end).map((x,i)=>`<button class="${statusFor(x.id)} ${x.id===question.id?'current':''}" data-jump="${section.start+i}" aria-label="Go to question ${section.start+i}">${section.start+i}</button>`).join('')}</div>
       <div class="legend"><span><i class="dot done"></i>Answered</span><span><i class="dot mark"></i>Marked</span><span><i class="dot not"></i>Visited / blank</span><span><i class="dot"></i>Not visited</span></div>
       <p class="advice">You may return to questions in this section until its timer expires. The next section starts automatically. Review material is hidden until final submission.</p></aside></div>`;
    $('#submitButton').onclick=()=>{if(confirm('Submit the entire mock now? Unanswered questions will remain blank and you cannot return.'))submitTest(false);};
    $('#app').querySelectorAll('[data-answer]').forEach(b=>b.onclick=()=>{active.answers[question.id]=Number(b.dataset.answer);storeActive();renderExam();});
    $('#app').querySelectorAll('[data-jump]').forEach(b=>b.onclick=()=>goTo(Number(b.dataset.jump)-1));
    $('#prev').onclick=()=>goTo(active.currentIndex-1);
    $('#next').onclick=()=>goTo(Math.min(section.end-1,active.currentIndex+1));
    $('#clear').onclick=()=>{delete active.answers[question.id];storeActive();renderExam();};
    $('#mark').onclick=()=>{const ix=active.marked.indexOf(question.id);if(ix>=0)active.marked.splice(ix,1);else active.marked.push(question.id);storeActive();renderExam();};
    lastRenderedSecond=secs;
  }
  function goTo(nextIndex){
    if(!active)return;const s=getSection();if(nextIndex<s.start-1||nextIndex>s.end-1)return;
    active.currentIndex=nextIndex;const id=getCurrentQuestion().id;if(!active.visited.includes(id))active.visited.push(id);storeActive();renderExam();
  }
  function scoreFor(questions,answerMap){
    let correct=0,wrong=0,blank=0;
    for(const item of questions){const guess=answerMap[item.id];if(guess===undefined)blank++;else if(guess===item.answerIndex)correct++;else wrong++;}
    return {correct,wrong,blank,attempted:correct+wrong,score:Math.round((correct-0.25*wrong)*100)/100};
  }
  function submitTest(auto){
    if(!active)return;
    const t=getTest(active.testId),tot=scoreFor(t.questions,active.answers);
    const attempt={attemptId:'A-'+Date.now()+'-'+t.number,testId:t.id,title:t.title,score:tot.score,
      answers:{...active.answers},correct:tot.correct,wrong:tot.wrong,blank:tot.blank,
      startedAt:active.startedAt,completedAt:Date.now(),automatic:!!auto};
    const all=history();all.unshift(attempt);storeHistory(all);
    active=null;storeActive();showResult(attempt.attemptId);
  }
  function showResult(attemptId){
    page='results';const att=history().find(x=>x.attemptId===attemptId);if(!att)return enterHome();
    const t=getTest(att.testId),r=scoreFor(t.questions,att.answers),reason=scoreFor(t.questions.slice(0,40),att.answers),quant=scoreFor(t.questions.slice(40),att.answers);
    const byTopic={};for(const q of t.questions){(byTopic[q.topic] ||= []).push(q);}
    const sortedTopics=Object.entries(byTopic).sort((a,b)=>a[0].localeCompare(b[0]));
    $('#app').innerHTML=`<section class="results-header"><span class="pill">Mock completed • ${esc(t.title)}</span><h1>Your exam analysis</h1>
      <div class="result-score">${r.score.toFixed(2)} <small style="font-size:19px;color:#7a879b">/ 80</small></div><p>${r.correct} correct • ${r.wrong} wrong • ${r.blank} unanswered • ${r.attempted} attempted</p></section>
      <div class="subscores"><div><small>Reasoning (40 marks)</small><b>${reason.score.toFixed(2)}</b><small>${reason.correct} correct / ${reason.wrong} wrong</small></div>
        <div><small>Quantitative Aptitude (40 marks)</small><b>${quant.score.toFixed(2)}</b><small>${quant.correct} correct / ${quant.wrong} wrong</small></div>
        <div><small>Accuracy on attempted</small><b>${r.attempted?(100*r.correct/r.attempted).toFixed(1):'0.0'}%</b><small>Wrong answers lose 0.25 each</small></div>
        <div><small>Questions answered</small><b>${r.attempted}/80</b><small>Attempt coverage</small></div></div>
      <div class="panel question-panel"><h2>Performance by topic</h2><table class="data-table"><thead><tr><th>Topic</th><th>Correct</th><th>Wrong</th><th>Blank</th></tr></thead><tbody>
      ${sortedTopics.map(([topic,qs])=>{const s=scoreFor(qs,att.answers);return `<tr><td>${esc(topic)}</td><td>${s.correct}</td><td>${s.wrong}</td><td>${s.blank}</td></tr>`;}).join('')}</tbody></table></div>
      <div class="actions"><button class="btn" id="homeAfter">All mock papers</button><button class="btn btn-outline" id="reviewToggle">Show only wrong/unanswered</button><button class="btn btn-outline" id="retake">Retake this mock</button></div>
      <div class="review"><h2>Question-by-question solutions</h2><div id="reviewQuestions">${renderReview(t,att,false)}</div></div>`;
    $('#homeAfter').onclick=enterHome;
    $('#retake').onclick=()=>{if(confirm('Retake this paper? Your previous completed score will remain in history.')){active=null;storeActive();showInstructions(t.id);}};
    let onlyErrors=false;$('#reviewToggle').onclick=()=>{onlyErrors=!onlyErrors;$('#reviewToggle').textContent=onlyErrors?'Show all questions':'Show only wrong/unanswered';$('#reviewQuestions').innerHTML=renderReview(t,att,onlyErrors);};
  }
  function renderReview(t,att,onlyErrors){
    let qs=t.questions;
    if(onlyErrors)qs=qs.filter(q=>att.answers[q.id]!==q.answerIndex);
    if(!qs.length)return '<div class="message">No incorrect or unanswered questions. Excellent work!</div>';
    return qs.map(q=>{
      const got=att.answers[q.id],correct=got===q.answerIndex;
      const st=q.stimulusId?t.stimuli.find(x=>x.id===q.stimulusId):null;
      return `<article class="panel review-card"><h3>Q${q.number}. ${esc(q.topic)} <span class="${correct?'answer-ok':'answer-wrong'}">${correct?'✓ Correct':got===undefined?'— Unanswered':'✗ Incorrect'}</span></h3>
         ${st?`<details><summary>Show common passage/data</summary>${renderStimulus(st)}</details>`:''}
         <p>${esc(q.stem)}</p><div class="muted">Your answer: ${got===undefined?'Not answered':esc('ABCDE'[got]+'. '+q.options[got])}</div>
         <p class="answer-ok">Correct: ${'ABCDE'[q.answerIndex]}. ${esc(q.options[q.answerIndex])}</p>
         <p><strong>Explanation:</strong> ${esc(q.explanation)}</p></article>`;
    }).join('');
  }
  $('#homeButton').onclick=()=>{if(active && page==='exam' && !confirm('Leave the test view? Your timer will continue and your responses will stay saved.'))return;enterHome();};
  window.addEventListener('keydown',e=>{
    if(page!=='exam'||!active||e.altKey||e.ctrlKey||e.metaKey)return;
    if(['INPUT','TEXTAREA'].includes(document.activeElement?.tagName))return;
    if('12345'.includes(e.key) && e.key.length===1){e.preventDefault();const q=getCurrentQuestion();active.answers[q.id]=Number(e.key)-1;storeActive();renderExam();}
    if(e.key==='ArrowRight'){e.preventDefault();goTo(active.currentIndex+1);}
    if(e.key==='ArrowLeft'){e.preventDefault();goTo(active.currentIndex-1);}
  });
  function initApp(result){
    data=result;if(data.tests.length!==20)throw Error('Invalid paper count');
    try {active=JSON.parse(localStorage.getItem(ACTIVE_KEY)||'null');}catch{active=null;}
    if(active&&!getTest(active.testId))active=null;
    if(active)syncDeadline();enterHome();setInterval(tick,1000);
  }

  if (window.__IBPS_MOCK_DATA__) {
    initApp(window.__IBPS_MOCK_DATA__);
  } else {
    fetch('data/tests.json').then(res=>{if(!res.ok)throw Error('HTTP '+res.status);return res.json();}).then(initApp).catch(err=>{$('#app').innerHTML=`<div class="message"><strong>Could not load mock-test data.</strong><p>${esc(err.message)}</p><p>If opening this folder locally, run <code>python -m http.server 8000</code> and open <code>http://localhost:8000</code>. Or double click <code>START_WEBSITE_WINDOWS.bat</code>.</p></div>`;});
  }
})();
