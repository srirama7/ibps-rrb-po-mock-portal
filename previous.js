(() => {
  'use strict';
  const bank=window.PREVIOUS_CBT_BANK, app=document.querySelector('#app');
  const ACTIVE='rrbpo_previous_cbt_active_v1', HISTORY='rrbpo_previous_cbt_history_v1';
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const read=(k,d)=>{try{return JSON.parse(localStorage.getItem(k))??d;}catch{return d;}};
  let storageError=false;
  const write=(k,v)=>{try{v===null?localStorage.removeItem(k):localStorage.setItem(k,JSON.stringify(v));}catch{storageError=true;}};
  const paper=id=>bank.papers.find(p=>p.id===id);
  let active=read(ACTIVE,null), screen='home', review=null, reviewIndex=0;
  if(active&&(!paper(active.paperId)||!Number.isFinite(active.deadline)||![0,1].includes(active.section)||!Number.isInteger(active.index)||!active.answers||!Array.isArray(active.marked)||!Array.isArray(active.visited)))active=null;
  const save=()=>write(ACTIVE,active);
  const sectionName=s=>s===0?'Reasoning Ability':'Quantitative Aptitude';
  const button=(label,action,cls='btn-ghost')=>`<button class="btn ${cls}" data-action="${action}">${label}</button>`;
  function confirmAction(title,body,action){
    document.querySelector('dialog')?.remove();
    const d=document.createElement('dialog');d.innerHTML=`<h2>${esc(title)}</h2><p>${esc(body)}</p><div class="cbt-actions"><button class="btn btn-primary" id="confirmAction">Confirm</button><button class="btn btn-ghost" id="cancelAction">Cancel</button></div>`;document.body.append(d);d.showModal();
    d.querySelector('#confirmAction').onclick=()=>{d.close();d.remove();action();};d.querySelector('#cancelAction').onclick=()=>{d.close();d.remove();};
  }
  function home(){
    screen='home';document.body.classList.remove('taking-exam');
    const rows=read(HISTORY,[]);
    app.innerHTML=`<section class="cbt-intro"><p class="eyebrow">PREVIOUS YEAR PRACTICE</p><h1>Your RRB exam room</h1><p>Full computer-based mocks with individual questions, five answer choices and timed sections.</p><div class="cbt-facts"><span>80 questions</span><span>Reasoning · 25 minutes</span><span>Quant · 20 minutes</span><span>+1 / −0.25 marks</span></div></section>${active?`<div class="cbt-resume"><strong>Test in progress: ${esc(paper(active.paperId).title)}</strong>${button('Resume test','resume','btn-primary')}<small>The timer continues while you are away.</small></div>`:''}<div class="cbt-library">${bank.papers.map(p=>`<article class="cbt-card"><small>${esc(p.date)}</small><h2>${esc(p.title)}</h2><p>40 Reasoning + 40 Quant · 45 minutes</p><p class="muted">Memory-based paper. Ambiguous source questions have clarified practice wording.</p>${button('Start mock',`instructions:${p.id}`,'btn-primary')} ${button('Study questions',`study:${p.id}`)}</article>`).join('')}</div>${rows.length?`<section><h2>Your results</h2><div class="cbt-history">${rows.map((r,i)=>`<article><strong>${esc(paper(r.paperId)?.title)}</strong><span>${r.score} / 80 · ${r.correct} correct · ${r.wrong} wrong</span>${button('Review answers',`history:${i}`)}</article>`).join('')}</div></section>`:''}`;
  }
  function instructions(id){
    screen='instructions';const p=paper(id);
    app.innerHTML=`<section class="cbt-instructions"><p class="eyebrow">EXAM INSTRUCTIONS</p><h1>${esc(p.title)}</h1><table><thead><tr><th>Section</th><th>Questions</th><th>Time</th></tr></thead><tbody><tr><td>Reasoning Ability</td><td>40</td><td>25 minutes</td></tr><tr><td>Quantitative Aptitude</td><td>40</td><td>20 minutes</td></tr></tbody></table><ul><li>Each correct answer earns 1 mark; each wrong answer deducts 0.25. Unanswered questions score zero.</li><li>Reasoning comes first. Once you finish a section, you cannot return to it.</li><li>Select an option, then use Save &amp; Next. Your choice is also saved immediately.</li><li>Mark for Review &amp; Next flags a question. Marked answers count towards your score.</li><li>The timer continues if you close the tab. Progress is saved in this browser.</li><li>All 80 questions are included. Clarified questions are labelled. Answers and explanations appear after submission.</li></ul><label class="cbt-check"><input type="checkbox" id="ready"> I have read the instructions and am ready to begin.</label><div class="cbt-actions">${button('Begin test',`start:${id}`,'btn-primary')}${button('Back to papers','home')}</div></section>`;
    app.querySelector('[data-action^="start:"]').disabled=true;app.querySelector('#ready').onchange=e=>app.querySelector('[data-action^="start:"]').disabled=!e.target.checked;
  }
  function start(id){
    active={paperId:id,section:0,index:0,deadline:Date.now()+25*60000,startedAt:Date.now(),answers:{},marked:[],visited:[0],version:bank.version};save();screen='exam';renderExam();
  }
  function state(i){return active.marked.includes(i)?(active.answers[i]!==undefined?'marked answered-marked':'marked'):active.answers[i]!==undefined?'answered':active.visited.includes(i)?'visited':'';}
  function chartMarkup(table){
    if(!table?.chart)return '';
    const colors=['#2469a5','#e59837','#54966c','#a05ca5','#c65c60','#61a8b8'];
    if(table.chart==='pie'){
      let angle=-Math.PI/2;
      const arcs=table.rows.map((row,i)=>{const next=angle+row[1]/100*Math.PI*2;const x=130+100*Math.cos(angle),y=125+100*Math.sin(angle),xx=130+100*Math.cos(next),yy=125+100*Math.sin(next);const path=`<path d="M130 125 L${x} ${y} A100 100 0 ${row[1]>50?1:0} 1 ${xx} ${yy} Z" fill="${colors[i]}" stroke="white" stroke-width="2"/><text x="270" y="${40+i*31}" font-size="14" fill="${colors[i]}">${esc(row[0])}: ${row[1]}%</text>`;angle=next;return path;}).join('');
      return `<svg class="cbt-chart" viewBox="0 0 380 250" role="img" aria-label="Student distribution pie chart. Values are listed in the table below.">${arcs}</svg>`;
    }
    const max=Math.max(...table.rows.flatMap(r=>r.slice(1))), step=430/table.rows.length, series=table.columns.length-1;
    let content='';
    for(let i=0;i<=4;i++){const y=220-i*47.5;content+=`<line x1="50" y1="${y}" x2="490" y2="${y}" stroke="#dce4ed"/><text x="44" y="${y+4}" text-anchor="end" font-size="11">${Math.round(max*i/4)}</text>`;}
    table.rows.forEach((row,i)=>{row.slice(1).forEach((v,j)=>{const h=v/max*190,x=55+i*step+j*(step-14)/series;content+=`<rect x="${x}" y="${220-h}" width="${(step-14)/series}" height="${h}" fill="${colors[j]}"/>`;});content+=`<text x="${55+i*step+(step-14)/2}" y="240" text-anchor="middle" font-size="11">${esc(row[0])}</text>`;});
    return `<svg class="cbt-chart" viewBox="0 0 510 280" role="img" aria-label="Data chart. Exact values are listed in the table below.">${content}${table.columns.slice(1).map((c,i)=>`<rect x="${55+i*210}" y="259" width="12" height="12" fill="${colors[i]}"/><text x="${73+i*210}" y="270" font-size="12">${esc(c)}</text>`).join('')}</svg>`;
  }
  function questionMarkup(q,answer,showAnswer=false){
    const table=q.table?`${chartMarkup(q.table)}<div class="cbt-table-wrap"><table><thead><tr>${q.table.columns.map(c=>`<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>${q.table.rows.map(row=>`<tr>${row.map(c=>`<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`:'';
    const context=q.context||table?`<aside class="cbt-passage"><h3>Information for this question</h3><p>${esc(q.context)}</p>${table}</aside>`:'';
    return `<div class="cbt-question-layout ${context?'has-passage':''}">${context}<section class="cbt-question"><div class="cbt-question-heading"><strong>Question ${q.number}</strong>${q.amended?'<small class="cbt-amended">Clarified wording</small>':''}</div><p class="cbt-stem">${esc(q.stem)}</p><fieldset class="cbt-options"><legend class="sr-only">Choose one answer</legend>${q.options.map((o,i)=>`<label class="cbt-option ${showAnswer&&i===q.answerIndex?'correct-option':''} ${showAnswer&&i===answer&&i!==q.answerIndex?'wrong-option':''}"><input type="radio" name="answer" value="${i}" ${answer===i?'checked':''} ${showAnswer?'disabled':''}><span class="cbt-letter">${'ABCDE'[i]}</span><span>${esc(o)}</span>${showAnswer&&i===q.answerIndex?'<strong>Correct answer</strong>':''}</label>`).join('')}</fieldset>${showAnswer?`<div class="cbt-explanation"><strong>${answer===undefined?'Not answered':answer===q.answerIndex?'Correct':'Incorrect'} · Correct option ${'ABCDE'[q.answerIndex]}</strong><p>${esc(q.explanation)}</p><small>Source question ${q.sourceNumber}</small></div>`:''}</section></div>`;
  }
  function renderExam(){
    if(!active)return home();screen='exam';document.body.classList.add('taking-exam');
    const p=paper(active.paperId),q=p.questions[active.index],base=active.section*40;
    if(!active.visited.includes(active.index))active.visited.push(active.index);save();
    app.innerHTML=`<div class="cbt-exam"><header class="cbt-exam-header"><div><small>${esc(p.title)}</small><h1>${sectionName(active.section)}</h1></div><div class="cbt-timer" role="timer" aria-label="Section time remaining"><small>Section time left</small><strong id="timer"></strong></div></header><div class="cbt-tabs"><span class="${active.section===0?'selected':''}">1. Reasoning ${active.section===1?'· locked':''}</span><span class="${active.section===1?'selected':''}">2. Quant ${active.section===0?'· locked':''}</span></div>${storageError?'<p role="alert">Browser storage is unavailable. Keep this tab open to retain your answers.</p>':''}<div class="cbt-workspace"><div class="cbt-content">${questionMarkup(q,active.answers[active.index])}<nav class="cbt-controls" aria-label="Question controls">${button('Clear response','clear')}${button('Mark for Review &amp; Next','mark')}${button('Save &amp; Next','next','btn-primary')}</nav></div><aside class="cbt-sidebar"><h2>Question palette</h2><div class="cbt-legend"><span class="answered">Answered</span><span class="visited">Not answered</span><span class="marked">Review</span><span class="answered-marked">Answered + review</span><span>Not visited</span></div><div class="cbt-palette">${Array.from({length:40},(_,n)=>{let i=base+n;return `<button class="${state(i)} ${i===active.index?'current':''}" data-action="jump:${i}" aria-label="Question ${i+1}, ${state(i)||'not visited'}" ${i===active.index?'aria-current="true"':''}>${i+1}</button>`;}).join('')}</div><p id="answeredCount">${Object.keys(active.answers).filter(i=>+i>=base&&+i<base+40).length} of 40 answered</p>${button(active.section===0?'Finish Reasoning section':'Submit test','finish','btn-primary')}${button('Save &amp; leave','leave')}<small>Your timer keeps running.</small></aside></div></div>`;
    app.querySelectorAll('input[name="answer"]').forEach(input=>input.onchange=()=>{active.answers[active.index]=Number(input.value);save();renderExam();});updateTimer();
  }
  function next(mark){
    const i=active.index;if(mark&&!active.marked.includes(i))active.marked.push(i);if(!mark)active.marked=active.marked.filter(n=>n!==i);
    active.index=active.section*40+(i+1)%40;save();renderExam();
  }
  function advance(deadline){active.section=1;active.index=40;active.deadline=deadline;save();if(screen==='exam')renderExam();}
  function grade(p,answers){let correct=0,wrong=0;p.questions.forEach((q,i)=>{if(answers[i]!==undefined){if(answers[i]===q.answerIndex)correct++;else wrong++;}});return {correct,wrong,unanswered:80-correct-wrong,score:correct-wrong*.25};}
  function submit(){
    const r={...active,...grade(paper(active.paperId),active.answers),endedAt:Date.now()};const rows=read(HISTORY,[]);rows.unshift(r);write(HISTORY,rows.slice(0,100));active=null;save();review=r;reviewIndex=0;results();
  }
  function updateTimer(){
    if(!active)return;
    if(Date.now()>=active.deadline){if(active.section===0)advance(active.deadline+20*60000);if(active&&Date.now()>=active.deadline)return submit();}
    const el=document.querySelector('#timer');if(el){const s=Math.max(0,Math.ceil((active.deadline-Date.now())/1000));el.textContent=`${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;el.classList.toggle('urgent',s<120);}
  }
  function results(){
    screen='review';document.body.classList.remove('taking-exam');const p=paper(review.paperId),q=p.questions[reviewIndex];
    app.innerHTML=`<section class="cbt-results"><p class="eyebrow">${review.study?'STUDY MODE':'TEST RESULT'}</p><h1>${esc(p.title)}</h1>${!review.study?`<div class="cbt-score"><strong>${review.score} <small>/ 80</small></strong><span>${review.correct} correct</span><span>${review.wrong} wrong</span><span>${review.unanswered} unanswered</span></div><p>Scoring: +1 for correct answers, −0.25 for wrong answers. All 80 questions count.</p>`:'<p>Browse the questions with their correct answers and explanations.</p>'}<div class="cbt-review-nav"><label>Review question <select id="reviewSelect">${p.questions.map((q,i)=>`<option value="${i}" ${i===reviewIndex?'selected':''}>${i+1} · ${sectionName(i<40?0:1)}${review.study?'':review.answers[i]===undefined?' · unanswered':review.answers[i]===q.answerIndex?' · correct':' · wrong'}</option>`).join('')}</select></label>${button('Previous','reviewPrev')}${button('Next','reviewNext')}${button('Back to papers','home')}</div>${questionMarkup(q,review.answers[reviewIndex],true)}<p><a href="${esc(p.sourcePdf)}" target="_blank" rel="noopener">Original source PDF</a> · Source order differs for papers regrouped into exam sections.</p></section>`;
    document.querySelector('#reviewSelect').onchange=e=>{reviewIndex=+e.target.value;results();};
  }
  app.addEventListener('click',e=>{
    const target=e.target.closest('[data-action]');if(!target)return;const [action,arg]=target.dataset.action.split(':');
    if(action==='home')home();
    if(action==='instructions')instructions(arg);
    if(action==='start'){if(active)confirmAction('Replace your ongoing test?','Starting this mock replaces your unfinished test.',()=>start(arg));else start(arg);}
    if(action==='resume'){screen='exam';updateTimer();if(active)renderExam();}
    if(action==='jump'){active.index=+arg;renderExam();}
    if(action==='next')next(false);
    if(action==='mark')next(true);
    if(action==='clear'){delete active.answers[active.index];save();renderExam();}
    if(action==='leave')home();
    if(action==='finish')confirmAction(active.section===0?'Finish Reasoning?':'Submit your test?',active.section===0?'You cannot return to Reasoning. Quantitative Aptitude will begin with 20 minutes.':'Your answers will be evaluated and explanations will be shown.',()=>active.section===0?advance(Date.now()+20*60000):submit());
    if(action==='study'){review={paperId:arg,answers:{},study:true};reviewIndex=0;results();}
    if(action==='history'){review=read(HISTORY,[])[+arg];reviewIndex=0;results();}
    if(action==='reviewPrev'){reviewIndex=Math.max(0,reviewIndex-1);results();}
    if(action==='reviewNext'){reviewIndex=Math.min(79,reviewIndex+1);results();}
  });
  document.querySelector('#previousHome').onclick=home;
  setInterval(updateTimer,500);home();updateTimer();
})();
