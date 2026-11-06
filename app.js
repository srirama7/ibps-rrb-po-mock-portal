(() => {
  'use strict';
  const ACTIVE_KEY = 'rrbpo_active_v3', HISTORY_KEY = 'rrbpo_history_v3';
  const $ = (sel) => document.querySelector(sel);
  const esc = (str) => String(str ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

  let data = null, active = null, page = 'home', lastRenderedSecond = -1;

  const tests = () => data.tests;
  const getTest = (id) => tests().find(t => t.id === id);

  const storeActive = () => {
    try {
      if (active) localStorage.setItem(ACTIVE_KEY, JSON.stringify(active));
      else localStorage.removeItem(ACTIVE_KEY);
    } catch (err) {
      console.warn('Could not save progress', err);
    }
  };

  const history = () => {
    try {
      return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
    } catch {
      return [];
    }
  };

  const storeHistory = (rows) => {
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(rows));
    } catch (err) {
      console.warn('History storage unavailable', err);
    }
  };

  function getSection() {
    return getTest(active.testId).sections[active.sectionIndex];
  }

  function getCurrentQuestion() {
    return getTest(active.testId).questions[active.currentIndex];
  }

  function timeText(s) {
    s = Math.max(0, Math.ceil(s));
    return String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
  }

  function millisLeft() {
    return active ? active.sectionEndAt - Date.now() : 0;
  }

  function statusFor(id) {
    const isAnswered = active.answers[id] !== undefined;
    const isMarked = active.marked.includes(id);
    const isVisited = active.visited.includes(id);

    if (isMarked && isAnswered) return 'marked-answered';
    if (isMarked) return 'marked';
    if (isAnswered) return 'answered';
    if (isVisited) return 'not-answered';
    return 'not-visited';
  }

  function enterHome() {
    page = 'home';
    renderHome();
  }

  function startTest(id) {
    if (active && active.testId !== id) {
      if (!confirm('Another mock test is already in progress. Starting this mock will discard your previous unfinished attempt. Do you want to continue?')) return;
    }
    const now = Date.now();
    active = {
      testId: id,
      startedAt: now,
      sectionIndex: 0,
      sectionEndAt: now + 25 * 60 * 1000, // 25 Minutes for Reasoning
      currentIndex: 0,
      answers: {},
      visited: [getTest(id).questions[0].id],
      marked: []
    };
    storeActive();
    page = 'exam';
    renderExam();
  }

  function resumeTest() {
    if (active) {
      page = 'exam';
      syncDeadline();
      if (active) renderExam();
    }
  }

  function showInstructions(id) {
    page = 'instructions';
    const t = getTest(id);
    $('#app').innerHTML = `
      <div class="instructions-card" style="max-width: 840px; margin: 30px auto; background: #ffffff; border: 1px solid var(--border); border-radius: 12px; padding: 36px; box-shadow: 0 4px 16px rgba(0,0,0,0.06);">
        <span class="badge-official">Before you begin</span>
        <h1 style="font-size: 26px; font-weight: 800; color: var(--primary); margin: 8px 0 16px;">${esc(t.title)}</h1>
        <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 24px;">Please read the examination instructions carefully before starting the test.</p>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 24px; font-size: 13.5px; line-height: 1.8;">
          <h3 style="color: var(--primary); font-size: 15px; margin-bottom: 10px;">Exam Scheme & Sectional Rules:</h3>
          <ul style="padding-left: 20px;">
            <li><strong>Total Questions:</strong> 80 Objective Multiple Choice Questions (5 options each).</li>
            <li><strong>Total Marks:</strong> 80 Marks (+1.00 for Correct, −0.25 for Incorrect, 0 for Unattempted).</li>
            <li><strong>Strict Sectional Timing:</strong>
              <ul style="margin: 6px 0;">
                <li><strong>Section 1 (Reasoning Ability):</strong> 40 Questions, 40 Marks, <strong>25:00 Minutes</strong>.</li>
                <li><strong>Section 2 (Quantitative Aptitude):</strong> 40 Questions, 40 Marks, <strong>20:00 Minutes</strong>.</li>
              </ul>
            </li>
            <li><strong>Section Lock:</strong> When the 25-minute timer for Reasoning expires, the section is locked automatically and Quantitative Aptitude starts immediately. You cannot return to Reasoning.</li>
            <li><strong>Evaluation of Marked Questions:</strong> Questions that are <em>Answered and Marked for Review</em> WILL be considered for evaluation under this mock’s scoring rules.</li>
            <li><strong>Question-by-Question Solutions:</strong> Full step-by-step mathematical and logical solutions will be revealed immediately upon submission.</li>
          </ul>
        </div>

        <div style="display: flex; gap: 14px; justify-content: flex-end; flex-wrap:wrap;">
          <button id="backHome" class="btn btn-secondary" style="padding: 10px 20px;">Back to All Mocks</button>
          <button id="beginMock" class="btn btn-primary" style="padding: 10px 24px; font-size: 14px;">I am Ready to Begin</button>
        </div>
      </div>
    `;
    $('#beginMock').onclick = () => startTest(id);
    $('#backHome').onclick = enterHome;
  }

  function renderHome() {
    page = 'home';
    const attempts = history();
    const bestScores = {};
    for (const a of attempts) {
      if (bestScores[a.testId] === undefined || a.score > bestScores[a.testId]) {
        bestScores[a.testId] = a.score;
      }
    }

    $('#app').innerHTML = `
      <section class="hero-banner">
        <div class="hero-content">
          <span class="eyebrow"><span class="live-dot"></span> YOUR NEXT CHAPTER STARTS HERE</span>
          <h1>Practice with purpose.<br><em>Walk in prepared.</em></h1>
          <p>A focused practice space for IBPS RRB Officer Scale I. Take a full mock, find your weak spots, and make your next attempt count.</p>
          <div class="hero-actions"><a href="#mockCards" class="btn btn-primary">Find your next mock <span>↗</span></a><a href="#practiceNotes" class="text-link">Explore the exam format ↓</a></div>
          <div class="hero-proof"><span>✓ No login needed</span><span>✓ Full explanations</span><span>✓ Progress on this device</span></div>
        </div>
        <div class="hero-aside"><span class="eyebrow">THE PRELIMS, AT A GLANCE</span><div class="time-ring"><strong>45<span>MINUTES</span></strong></div><div class="time-split"><span><i></i> Reasoning <b>25 min</b></span><span><i></i> Quantitative <b>20 min</b></span></div><small>One question at a time. One step closer.</small></div>
      </section>
      <div class="stats-grid">
        <div class="stat-card"><span class="stat-number">01 /</span><div><strong>20</strong><span>Full-length papers</span></div></div>
        <div class="stat-card"><span class="stat-number">02 /</span><div><strong>1,600</strong><span>Original practice MCQs</span></div></div>
        <div class="stat-card"><span class="stat-number">03 /</span><div><strong>+1 / −0.25</strong><span>Exam-style scoring</span></div></div>
        <div class="stat-card"><span class="stat-number">04 /</span><div><strong>${attempts.length}</strong><span>Your completed attempts</span></div></div>
      </div>

      ${active ? `
        <div style="background: #fffbeb; border: 1px solid #fef3c7; border-left: 5px solid #f59e0b; border-radius: 8px; padding: 18px 24px; margin-bottom: 28px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
          <div>
            <strong style="color: #92400e; font-size: 15px;">Ongoing Mock in Progress:</strong>
            <p style="color: #78350f; font-size: 13px; margin-top: 2px;">${esc(getTest(active.testId).title)} — Section timer is currently active.</p>
          </div>
          <button id="resumeActiveBtn" class="btn btn-primary">Resume Test Now →</button>
        </div>
      ` : ''}

      <div class="section-title" id="mockCards">
        <div><span class="eyebrow">THE PRACTICE LIBRARY</span><h2>Make today a little better.</h2><p class="library-caption">Choose a paper. Stay focused. Review what matters.</p></div>
        <small style="font-size: 13px; font-weight: normal; color: var(--text-muted);">80 Questions • 80 Marks • 45 Minutes</small>
      </div>

      <div class="cards-grid">
        ${tests().map(t => {
          const best = bestScores[t.id];
          return `
            <div class="mock-card"><div class="paper-number">${String(t.number).padStart(2, '0')}<span>FULL MOCK</span></div>
              <span class="mock-badge">OFFICER SCALE I · PAPER ${String(t.number).padStart(2, '0')}</span>
              <h3>Mock test ${String(t.number).padStart(2, '0')}</h3><p class="paper-subtitle">${t.number % 2 ? 'Linear seating & indirect DI' : 'Parallel rows & arithmetic'}${t.number % 3 === 0 ? ' · Circular seating' : ' · Box puzzle'}</p>
              <div class="mock-details">
                <span>• 40 Reasoning Ability (25 Min)</span>
                <span>• 40 Quantitative Aptitude (20 Min)</span>
                <span>• Marking: +1.00 / −0.25 penalty</span>
              </div>
              <div class="footer-action">
                <div>
                  ${best !== undefined ? `
                    <span style="font-size: 12px; font-weight: 700; color: var(--c-answered);">Best: ${best.toFixed(2)}/80</span>
                  ` : `
                    <span style="font-size: 11px; color: var(--text-muted);">Not Attempted</span>
                  `}
                </div>
                <button class="btn btn-primary" data-start="${t.id}">
                  ${active && active.testId === t.id ? 'Continue' : 'Start practice ↗'}
                </button>
              </div>
            </div>

    `;
        }).join('')}
      </div>

            <section id="practiceNotes" class="practice-notes"><div><span class="eyebrow">BUILT FOR FOCUSED PREPARATION</span><h2>Know the format.<br>Build your own strategy.</h2><p>Each paper includes 40 reasoning and 40 quantitative aptitude questions. Sections run on separate timers. Answered questions marked for review are scored.</p></div><div><h3>Variety that makes you think</h3><p>Seating and floor puzzles, coding, inequalities, syllogisms, indirect tables, bar charts, caselets and multi-step arithmetic. Review every solution after submitting.</p><h3>About these questions</h3><p>Original practice informed by published exam structure and candidate-reported topic trends. These are independent mocks; difficulty has not been officially calibrated. Scores are practice feedback, not a predicted cutoff.</p><p><a href="https://www.ibps.in/index.php/rural-bank-xv/" target="_blank" rel="noopener">IBPS notification hub ↗</a> · <a href="https://www.practicemock.com/blog/ibps-rrb-po-exam-analysis-2025/" target="_blank" rel="noopener">2025 topic analysis ↗</a> · <a href="data/answer_keys.csv" download>Download answer keys ↓</a></p></div></section>

      ${attempts.length ? `
        <div style="background:#ffffff; border:1px solid var(--border); border-radius:10px; padding:24px; margin-top:20px;">
          <h3 style="font-size: 17px; font-weight: 800; color: var(--primary); margin-bottom: 16px;">Your Previous Mock Attempts</h3>
          <div style="display:flex; flex-direction:column; gap:10px;">
            ${attempts.slice(0, 10).map(att => `
              <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; padding:12px 16px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; font-size:13px;">
                <div>
                  <strong>${esc(att.title)}</strong>
                  <span style="color:var(--text-muted); margin-left:12px;">${esc(new Date(att.completedAt).toLocaleString())}</span>
                </div>
                <div style="display:flex; align-items:center; gap:16px;">
                  <strong style="color:var(--primary); font-size:15px;">${att.score.toFixed(2)} / 80</strong>
                  <button class="btn btn-secondary" data-review="${esc(att.attemptId)}">Review Solutions</button>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}
    `;

    $('#app').querySelectorAll('[data-start]').forEach(b => {
      b.onclick = () => active && active.testId === b.dataset.start ? resumeTest() : showInstructions(b.dataset.start);
    });
    $('#app').querySelectorAll('[data-review]').forEach(b => {
      b.onclick = () => showResult(b.dataset.review);
    });
    if ($('#resumeActiveBtn')) $('#resumeActiveBtn').onclick = resumeTest;
  }

  function syncDeadline() {
    if (!active) return;
    if (Date.now() < active.sectionEndAt) return;

    if (active.sectionIndex === 0) {
      const firstEnd = active.sectionEndAt;
      active.sectionIndex = 1;
      active.sectionEndAt = firstEnd + 20 * 60 * 1000;
      active.currentIndex = 40;
      const q = getCurrentQuestion();
      if (!active.visited.includes(q.id)) active.visited.push(q.id);
      storeActive();
      if (Date.now() >= active.sectionEndAt) {
        submitTest(true);
        return;
      }
      if (page === 'exam') {
        alert('Reasoning time has expired (25 Minutes). Quantitative Aptitude has started. Reasoning questions (1 to 40) are now locked.');
        renderExam();
      }
    } else {
      submitTest(true);
    }
  }

  function tick() {
    if (!active) return;
    syncDeadline();
    if (!active) return;
    if (page === 'exam') {
      const secs = Math.max(0, Math.ceil(millisLeft() / 1000));
      if (secs !== lastRenderedSecond) {
        lastRenderedSecond = secs;
        const timer = $('#examTimer');
        if (timer) {
          timer.innerHTML = `${timeText(secs)}`;
          timer.className = secs <= 60 ? 'timer-box' : 'timer-box normal';
        }
      }
    }
  }

  function renderStimulus(st) {
    if (!st) return '';
    if (st.type !== 'data_interpretation') {
      return `
        <div class="stimulus-card">
          <h4>${esc(st.title)}</h4>
          <pre>${esc(st.body)}</pre>
        </div>
      `;
    }

    let chartHtml = '';
    if (st.visualization === 'bar' && st.rows) {
      const maxVal = Math.max(...st.rows.flatMap(r => [r.a, r.b]));
      chartHtml = `
        <div style="margin: 14px 0;">
          <div style="display:flex; gap:16px; font-size:12px; margin-bottom:10px;">
            <span style="display:flex; align-items:center; gap:6px;"><i style="width:12px; height:12px; background:#1976d2; display:inline-block; border-radius:2px;"></i> ${esc(st.columns[1])}</span>
            <span style="display:flex; align-items:center; gap:6px;"><i style="width:12px; height:12px; background:#f59e0b; display:inline-block; border-radius:2px;"></i> ${esc(st.columns[2])}</span>
          </div>
          ${st.rows.map(r => `
            <div style="display:grid; grid-template-columns: 80px 1fr; gap:10px; margin: 6px 0; align-items:center; font-size:12px;">
              <b>${esc(r.label)}</b>
              <div style="display:flex; flex-direction:column; gap:3px;">
                <div style="height:12px; width:${(r.a * 100 / maxVal).toFixed(1)}%; background:#1976d2; border-radius:3px;" title="${r.a}"><span class="bar-value">${r.a}</span></div>
                <div style="height:12px; width:${(r.b * 100 / maxVal).toFixed(1)}%; background:#f59e0b; border-radius:3px;" title="${r.b}"><span class="bar-value">${r.b}</span></div>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }

    let tableHtml = '';
    const cells = st.cells || (st.rows ? st.rows.map(r => [r.label, r.a, r.b]) : null);
    if (cells && st.columns) {
      tableHtml = `<div class="table-scroll"><table class="cbt-table"><thead><tr>${st.columns.map(c => `<th scope="col">${esc(c)}</th>`).join('')}</tr></thead><tbody>${cells.map(row => `<tr>${row.map(value => `<td>${esc(value)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
    }

    return `
      <div class="stimulus-card">
        <h4>${esc(st.title)}</h4>
        ${st.variant === 'caselet' ? `<p style="margin-bottom:12px;">${esc(st.body)}</p>` : ''}
        ${chartHtml}
        ${st.variant !== 'caselet' && st.visualization !== 'bar' && tableHtml ? tableHtml : ''}
      </div>
    `;
  }

  function renderExam() {
    if (!active) return enterHome();
    syncDeadline();
    if (!active) return;

    page = 'exam';
    const t = getTest(active.testId);
    const section = getSection();
    const q = getCurrentQuestion();
    const stim = q.stimulusId ? t.stimuli.find(x => x.id === q.stimulusId) : null;
    const answered = q.id in active.answers;
    const secs = Math.max(0, Math.ceil(millisLeft() / 1000));

    // Compute palette summary counts for current section
    const secQuestions = t.questions.slice(section.start - 1, section.end);
    let cntAnswered = 0, cntNotAnswered = 0, cntMarked = 0, cntMarkedAnswered = 0, cntNotVisited = 0;
    for (const sq of secQuestions) {
      const st = statusFor(sq.id);
      if (st === 'marked-answered') cntMarkedAnswered++;
      else if (st === 'marked') cntMarked++;
      else if (st === 'answered') cntAnswered++;
      else if (st === 'not-answered') cntNotAnswered++;
      else cntNotVisited++;
    }

    $('#app').innerHTML = `
      <div class="exam-layout">
        <!-- TOP SECTION NAVIGATION & TIMING BAR -->
        <div class="section-nav-bar">
          <div class="section-tabs">
            <button class="section-tab ${active.sectionIndex === 0 ? 'active' : 'locked'}" id="tabReasoning">
              Section 1: Reasoning Ability
              <span class="badge-count">${t.questions.filter(x => x.section === 'reasoning' && x.id in active.answers).length}/40</span>
            </button>
            <button class="section-tab ${active.sectionIndex === 1 ? 'active' : 'locked'}" id="tabQuant">
              Section 2: Quantitative Aptitude
              <span class="badge-count">${t.questions.filter(x => x.section === 'quant' && x.id in active.answers).length}/40</span>
            </button>
          </div>
          <div style="display:flex; align-items:center; gap:16px;">
            <div id="examTimer" class="${secs <= 60 ? 'timer-box' : 'timer-box normal'}">
              ${timeText(secs)}
            </div>
            <button class="btn btn-submit" id="submitExamBtn" style="padding: 8px 18px;">
              Submit Exam
            </button>
          </div>
        </div>

        <!-- MAIN SPLIT SCREEN: QUESTION ON LEFT, PALETTE ON RIGHT -->
        <div class="exam-main-grid">
          <!-- LEFT: QUESTION PANEL -->
          <div class="question-container">
            <div class="question-header">
              <span class="q-title">Question No. ${active.currentIndex + 1}</span>
              <span class="q-marks">Marks: <b>+1.00</b> | Negative: <span>−0.25</span></span>
            </div>

            <div class="question-body ${stim ? 'has-stimulus' : ''}">
              ${renderStimulus(stim)}
              <div class="answer-pane"><div class="q-topic">${esc(q.topic)}</div><div class="q-stem">${esc(q.stem)}</div>
              <div class="options-list">
                ${q.options.map((opt, i) => `
                  <button type="button" class="option-item ${active.answers[q.id] === i ? 'selected' : ''}" data-ans="${i}" aria-pressed="${active.answers[q.id] === i}">
                    <div class="opt-radio"></div>
                    <span class="opt-letter">(${'ABCDE'[i]})</span>
                    <span class="opt-text">${esc(opt)}</span>
                  </button>
                `).join('')}
              </div></div>
            </div>

            <!-- ACTION TOOLBAR -->
            <div class="exam-footer">
              <div class="footer-left">
                <button id="btnMarkNext" class="btn btn-review">
                  ${active.marked.includes(q.id) ? 'Unmark Review' : 'Mark for Review & Next'}
                </button>
                <button id="btnClear" class="btn btn-secondary" ${!answered ? 'disabled' : ''}>
                  Clear Response
                </button>
              </div>
              <div class="footer-right">
                <button id="btnPrev" class="btn btn-secondary" ${active.currentIndex === section.start - 1 ? 'disabled' : ''}>
                  Previous
                </button>
                <button id="btnSaveNext" class="btn btn-primary" style="padding: 9px 22px;">
                  ${active.currentIndex === section.end - 1 ? 'Save & Review' : 'Save & Next'}
                </button>
              </div>
            </div>
          </div>

          <!-- RIGHT: TCS iON PALETTE SIDEBAR -->
          <div class="palette-sidebar">
            <div class="palette-header">
              Question Palette • ${esc(section.name)}
            </div>

            <div class="legend-grid">
              <div class="legend-item">
                <span class="pill-status pill-answered">${cntAnswered}</span>
                <span>Answered</span>
              </div>
              <div class="legend-item">
                <span class="pill-status pill-not-answered">${cntNotAnswered}</span>
                <span>Not Answered</span>
              </div>
              <div class="legend-item">
                <span class="pill-status pill-not-visited">${cntNotVisited}</span>
                <span>Not Visited</span>
              </div>
              <div class="legend-item">
                <span class="pill-status pill-marked">${cntMarked}</span>
                <span>Marked for Review</span>
              </div>
              <div class="legend-item" style="grid-column: span 2;">
                <span class="pill-status pill-marked-answered">${cntMarkedAnswered}</span>
                <span>Answered & Marked (Evaluated)</span>
              </div>
            </div>

            <div class="palette-body">
              <div class="palette-buttons">
                ${secQuestions.map((sq, i) => {
                  const num = section.start + i;
                  const st = statusFor(sq.id);
                  const isCurrent = sq.id === q.id;
                  return `
                    <button class="pal-btn ${st} ${isCurrent ? 'current' : ''}" data-jump="${num}">
                      ${num}
                    </button>
                  `;
                }).join('')}
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    // Event Handlers
    $('#app').querySelectorAll('[data-ans]').forEach(item => {
      item.onclick = () => {
        active.answers[q.id] = Number(item.dataset.ans);
        storeActive();
        renderExam();
      };
    });

    $('#app').querySelectorAll('[data-jump]').forEach(btn => {
      btn.onclick = () => goTo(Number(btn.dataset.jump) - 1);
    });

    $('#btnPrev').onclick = () => goTo(active.currentIndex - 1);

    $('#btnSaveNext').onclick = () => {
      goTo(Math.min(section.end - 1, active.currentIndex + 1));
    };

    $('#btnClear').onclick = () => {
      delete active.answers[q.id];
      storeActive();
      renderExam();
    };

    $('#btnMarkNext').onclick = () => {
      const idx = active.marked.indexOf(q.id);
      if (idx >= 0) active.marked.splice(idx, 1);
      else active.marked.push(q.id);
      storeActive();
      goTo(Math.min(section.end - 1, active.currentIndex + 1));
    };

    $('#submitExamBtn').onclick = () => {
      const ansCount = Object.keys(active.answers).length;
      if (confirm(`You have answered ${ansCount} out of 80 questions.\n\nAre you sure you want to submit your test for final evaluation? You will not be able to change your responses afterwards.`)) {
        submitTest(false);
      }
    };

    lastRenderedSecond = secs;
  }

  function goTo(nextIdx) {
    if (!active) return;
    const s = getSection();
    if (nextIdx < s.start - 1 || nextIdx > s.end - 1) return;
    active.currentIndex = nextIdx;
    const nextQId = getCurrentQuestion().id;
    if (!active.visited.includes(nextQId)) {
      active.visited.push(nextQId);
    }
    storeActive();
    renderExam();
  }

  function scoreFor(questions, answerMap) {
    let correct = 0, wrong = 0, blank = 0;
    for (const item of questions) {
      const guess = answerMap[item.id];
      if (guess === undefined) blank++;
      else if (guess === item.answerIndex) correct++;
      else wrong++;
    }
    return {
      correct,
      wrong,
      blank,
      attempted: correct + wrong,
      score: Math.round((correct - 0.25 * wrong) * 100) / 100
    };
  }

  function submitTest(isAuto) {
    if (!active) return;
    const t = getTest(active.testId);
    const overall = scoreFor(t.questions, active.answers);
    const reason = scoreFor(t.questions.slice(0, 40), active.answers);
    const quant = scoreFor(t.questions.slice(40), active.answers);

    const attempt = {
      attemptId: 'ATT-' + Date.now() + '-' + t.number,
      testId: t.id,
      title: t.title,
      score: overall.score,
      correct: overall.correct,
      wrong: overall.wrong,
      blank: overall.blank,
      attempted: overall.attempted,
      accuracy: overall.attempted ? Math.round((overall.correct * 100 / overall.attempted) * 10) / 10 : 0,
      reasonScore: reason.score,
      quantScore: quant.score,
      answers: { ...active.answers },
      startedAt: active.startedAt,
      completedAt: Date.now(),
      isAutomatic: !!isAuto
    };

    const allAttempts = history();
    allAttempts.unshift(attempt);
    storeHistory(allAttempts);

    const targetId = attempt.attemptId;
    active = null;
    storeActive();
    showResult(targetId);
  }

  function showResult(attemptId) {
    page = 'results';
    const att = history().find(x => x.attemptId === attemptId);
    if (!att) return enterHome();

    const t = getTest(att.testId);
    const overall = scoreFor(t.questions, att.answers);
    const reason = scoreFor(t.questions.slice(0, 40), att.answers);
    const quant = scoreFor(t.questions.slice(40), att.answers);

    // Topic Performance Breakdown
    const byTopic = {};
    for (const q of t.questions) {
      (byTopic[q.topic] ||= []).push(q);
    }
    const sortedTopics = Object.entries(byTopic).sort((a, b) => a[0].localeCompare(b[0]));

    $('#app').innerHTML = `
      <div class="results-container">
        <!-- SCORE HERO CARD -->
        <div class="score-hero-card">
          <div>
            <span class="badge-official">Mock Evaluation Report • ${esc(t.title)}</span>
            <div class="hero-score-value">${overall.score.toFixed(2)} <span style="font-size: 24px; color: #94a3b8;">/ 80.00</span></div>
            <p style="color: #cbd5e1; font-size: 14px;">
              ${overall.correct} Correct • ${overall.wrong} Incorrect (−${(overall.wrong * 0.25).toFixed(2)}) • ${overall.blank} Unattempted
            </p>
          </div>

          <div class="cutoff-box"><h4>Your practice checkpoint</h4><p>Use topic accuracy and missed questions to plan your next session.</p><p style="margin-top:12px;font-size:12px;opacity:.8">Official cutoffs vary by state, category and year. This score does not predict qualification.</p></div>
        </div>

        <!-- SUMMARY STATS -->
        <div class="summary-cards-grid">
          <div class="sum-card">
            <small>Reasoning Ability (40 Marks)</small>
            <strong>${reason.score.toFixed(2)}</strong>
            <small style="color:var(--c-answered);">${reason.correct} Correct / ${reason.wrong} Wrong</small>
          </div>
          <div class="sum-card">
            <small>Quantitative Aptitude (40 Marks)</small>
            <strong>${quant.score.toFixed(2)}</strong>
            <small style="color:var(--c-answered);">${quant.correct} Correct / ${quant.wrong} Wrong</small>
          </div>
          <div class="sum-card">
            <small>Attempt Accuracy Rate</small>
            <strong style="color: ${att.accuracy >= 85 ? 'var(--c-answered)' : '#e11d48'};">${att.accuracy}%</strong>
            <small>Benchmark: ≥ 85% Accuracy</small>
          </div>
          <div class="sum-card">
            <small>Exam Coverage</small>
            <strong>${overall.attempted} / 80</strong>
            <small>${((overall.attempted * 100) / 80).toFixed(1)}% Questions Attempted</small>
          </div>
        </div>

        <!-- TOPIC WISE BREAKDOWN -->
        <div class="topic-analysis-card">
          <h3 style="font-size: 16px; font-weight: 800; color: var(--primary); margin-bottom: 14px;">Topic-Wise Performance Analysis</h3>
          <table class="cbt-table">
            <thead>
              <tr>
                <th style="text-align: left;">Syllabus Topic</th>
                <th>Total Questions</th>
                <th>Correct</th>
                <th>Incorrect</th>
                <th>Unattempted</th>
                <th>Accuracy</th>
              </tr>
            </thead>
            <tbody>
              ${sortedTopics.map(([topic, qs]) => {
                const s = scoreFor(qs, att.answers);
                const acc = s.attempted ? ((s.correct * 100) / s.attempted).toFixed(0) + '%' : '—';
                return `
                  <tr>
                    <td style="text-align: left;"><strong>${esc(topic)}</strong></td>
                    <td>${qs.length}</td>
                    <td style="color: var(--c-answered); font-weight: 700;">${s.correct}</td>
                    <td style="color: var(--c-not-answered); font-weight: 700;">${s.wrong}</td>
                    <td style="color: var(--text-muted);">${s.blank}</td>
                    <td><b>${acc}</b></td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>

        <!-- SOLUTIONS REVIEW SECTION -->
        <div style="margin-top: 10px;">
          <div class="review-header-bar">
            <h2 style="font-size: 20px; font-weight: 800; color: var(--primary);">Detailed Solutions & Step-by-Step Explanations</h2>
            <div style="display:flex; gap:10px;">
              <button class="btn btn-secondary" id="toggleOnlyWrong">Show Only Incorrect / Unanswered</button>
              <button class="btn btn-primary" id="retakeBtn">Retake This Mock</button>
              <button class="btn btn-secondary" id="backToAllMocks">All Mock Papers</button>
            </div>
          </div>

          <div id="solutionsList" style="margin-top: 16px;">
            ${renderSolutions(t, att, false)}
          </div>
        </div>
      </div>
    `;

    $('#backToAllMocks').onclick = enterHome;
    $('#retakeBtn').onclick = () => {
      if (confirm('Do you want to retake this mock test? Your previous score will remain saved in your history.')) {
        active = null;
        storeActive();
        showInstructions(t.id);
      }
    };

    let showErrorsOnly = false;
    $('#toggleOnlyWrong').onclick = () => {
      showErrorsOnly = !showErrorsOnly;
      $('#toggleOnlyWrong').textContent = showErrorsOnly ? 'Show All 80 Questions' : 'Show Only Incorrect / Unanswered';
      $('#solutionsList').innerHTML = renderSolutions(t, att, showErrorsOnly);
    };
  }

  function renderSolutions(t, att, filterErrors) {
    let qs = t.questions;
    if (filterErrors) {
      qs = qs.filter(q => att.answers[q.id] !== q.answerIndex);
    }
    if (!qs.length) {
      return '<div style="padding:30px; text-align:center; background:#ffffff; border:1px solid var(--border); border-radius:8px; color:var(--c-answered); font-weight:700;">Congratulations! You answered every question correctly in this section!</div>';
    }

    return qs.map(q => {
      const userChoice = att.answers[q.id];
      const isCorrect = userChoice === q.answerIndex;
      const stim = q.stimulusId ? t.stimuli.find(x => x.id === q.stimulusId) : null;

      return `
        <div class="solution-card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <span style="font-size: 14px; font-weight: 700; color: var(--primary);">
              Q${q.number}. ${esc(q.topic)}
            </span>
            <span class="${isCorrect ? 'solution-badge-ok' : 'solution-badge-wrong'}">
              ${isCorrect ? '✓ Correct (+1.00)' : userChoice === undefined ? '— Unattempted (0.00)' : '✗ Incorrect (−0.25)'}
            </span>
          </div>

          ${stim ? `
            <details style="margin-bottom: 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 14px;">
              <summary style="font-size: 12px; font-weight: 700; color: var(--accent); cursor: pointer;">View Common Puzzle / DI Data</summary>
              <div style="margin-top: 10px;">
                ${renderStimulus(stim)}
              </div>
            </details>
          ` : ''}

          <div style="font-size: 15px; font-weight: 600; line-height: 1.6; margin-bottom: 14px; white-space:pre-wrap;">
            ${esc(q.stem)}
          </div>

          <div style="display:flex; flex-direction:column; gap:6px; font-size:13.5px; margin-bottom:12px;">
            <div style="color: ${userChoice === undefined ? 'var(--text-muted)' : isCorrect ? 'var(--c-answered)' : 'var(--c-not-answered)'};">
              <strong>Your Response:</strong> ${userChoice === undefined ? 'Not Attempted' : `(${'ABCDE'[userChoice]}) ${esc(q.options[userChoice])}`}
            </div>
            <div style="color: var(--c-answered); font-weight: 700;">
              <strong>Correct Option:</strong> (${'ABCDE'[q.answerIndex]}) ${esc(q.options[q.answerIndex])}
            </div>
          </div>

          <div class="expl-box">
            <strong style="color: var(--primary);">Step-by-Step Explanation:</strong><br>
            ${esc(q.explanation)}
          </div>
        </div>
      `;
    }).join('');
  }

  $('#homeButton').onclick = () => {
    if (active && page === 'exam') {
      if (!confirm('Leave the exam view? Your session timer will keep running.')) return;
    }
    enterHome();
  };

  // Keyboard Navigation: keys 1-5 for options, Left/Right arrows for questions
  window.addEventListener('keydown', (e) => {
    if (page !== 'exam' || !active || e.altKey || e.ctrlKey || e.metaKey) return;
    if (['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) return;
    if ('12345'.includes(e.key) && e.key.length === 1) {
      e.preventDefault();
      const q = getCurrentQuestion();
      active.answers[q.id] = Number(e.key) - 1;
      storeActive();
      renderExam();
    }
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      goTo(active.currentIndex + 1);
    }
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      goTo(active.currentIndex - 1);
    }
  });

  function initApp(result) {
    data = result;
    if (data.tests.length !== 20) throw Error('Invalid paper count in question bank');
    try {
      active = JSON.parse(localStorage.getItem(ACTIVE_KEY) || 'null');
    } catch {
      active = null;
    }
    if (active && !getTest(active.testId)) active = null;
    if (active) syncDeadline();
    enterHome();
    setInterval(tick, 1000);
  }

  if (window.__IBPS_MOCK_DATA__) {
    initApp(window.__IBPS_MOCK_DATA__);
  } else {
    fetch('data/tests.json')
      .then(res => {
        if (!res.ok) throw Error('HTTP ' + res.status);
        return res.json();
      })
      .then(initApp)
      .catch(err => {
        $('#app').innerHTML = `
          <div style="max-width: 600px; margin: 40px auto; padding: 24px; background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; color: #9f1239;">
            <h3 style="margin-bottom: 8px;">Could not load mock test data</h3>
            <p>${esc(err.message)}</p>
            <p style="margin-top: 10px; font-size: 12px;">If opening locally, run <code>python -m http.server 8000</code> or open the standalone Desktop HTML file.</p>
          </div>
        `;
      });
  }
})();
