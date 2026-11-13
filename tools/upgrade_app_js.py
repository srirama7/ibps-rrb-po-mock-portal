# Precise upgrade of app.js
with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update millisLeft
old_millis = """  function millisLeft() {
    return active ? active.sectionEndAt - Date.now() : 0;
  }"""

new_millis = """  function millisLeft() {
    if (!active) return 0;
    if (active.isPaused) return (active.timeRemainingSec || 0) * 1000;
    return active.testEndAt ? active.testEndAt - Date.now() : 0;
  }"""

assert old_millis in code, "old_millis not found"
code = code.replace(old_millis, new_millis, 1)

# 2. Update startTest, add continueTest, pauseTest, unpauseTest
old_start_resume = """  function startTest(id) {
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
  }"""

new_start_resume = """  function startTest(id) {
    if (active && active.testId !== id) {
      if (!confirm('Another mock test is already in progress. Starting this mock will discard your previous unfinished attempt. Do you want to continue?')) return;
    }
    const now = Date.now();
    const totalDurationSec = 45 * 60; // 45 Minutes composite time (IBPS RRB PO standard)
    active = {
      testId: id,
      startedAt: now,
      testEndAt: now + totalDurationSec * 1000,
      timeRemainingSec: totalDurationSec,
      isPaused: false,
      sectionIndex: 0,
      currentIndex: 0,
      paletteSectionIndex: 0,
      answers: {},
      visited: [getTest(id).questions[0].id],
      marked: []
    };
    storeActive();
    page = 'exam';
    renderExam();
  }

  function continueTest(att) {
    if (!att) return;
    const t = getTest(att.testId);
    if (!t) return;

    let targetIdx = t.questions.findIndex(q => att.answers[q.id] === undefined);
    if (targetIdx === -1) targetIdx = 40;

    const now = Date.now();
    const timeAllowedSec = Math.max(1500, att.timeRemainingSec || 1500);

    active = {
      testId: att.testId,
      startedAt: att.startedAt || now,
      testEndAt: now + timeAllowedSec * 1000,
      timeRemainingSec: timeAllowedSec,
      isPaused: false,
      sectionIndex: targetIdx < 40 ? 0 : 1,
      currentIndex: targetIdx,
      paletteSectionIndex: targetIdx < 40 ? 0 : 1,
      answers: { ...(att.answers || {}) },
      visited: t.questions.filter(q => att.answers[q.id] !== undefined).map(q => q.id),
      marked: [],
      resumedFromAttemptId: att.attemptId
    };

    const targetQ = t.questions[targetIdx];
    if (targetQ && !active.visited.includes(targetQ.id)) {
      active.visited.push(targetQ.id);
    }

    storeActive();
    page = 'exam';
    renderExam();
  }

  function pauseTest() {
    if (!active || active.isPaused) return;
    const remainingSec = Math.max(0, Math.ceil(millisLeft() / 1000));
    active.isPaused = true;
    active.timeRemainingSec = remainingSec;
    storeActive();
    renderExam();
  }

  function unpauseTest() {
    if (!active || !active.isPaused) return;
    active.isPaused = false;
    const sec = active.timeRemainingSec || 60;
    active.testEndAt = Date.now() + sec * 1000;
    storeActive();
    renderExam();
  }

  function resumeTest() {
    if (active) {
      if (active.isPaused && active.timeRemainingSec) {
        active.isPaused = false;
        active.testEndAt = Date.now() + active.timeRemainingSec * 1000;
        storeActive();
      }
      page = 'exam';
      syncDeadline();
      if (active) renderExam();
    }
  }"""

assert old_start_resume in code, "old_start_resume not found"
code = code.replace(old_start_resume, new_start_resume, 1)

# 3. Update instructions to mention 45-min composite time & free section switching
old_instr_text = """          <ul style="padding-left: 20px;">
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
          </ul>"""

new_instr_text = """          <ul style="padding-left: 20px;">
            <li><strong>Total Questions:</strong> 80 Objective Multiple Choice Questions (5 options each).</li>
            <li><strong>Total Marks:</strong> 80 Marks (+1.00 for Correct, −0.25 for Incorrect, 0 for Unattempted).</li>
            <li><strong>Composite 45:00 Minutes Timing:</strong> 45 minutes total composite duration for both sections (official IBPS RRB PO standard).</li>
            <li><strong>Free Section Switching:</strong> Switch freely between <strong>Section 1 (Reasoning Ability, Q1–Q40)</strong> and <strong>Section 2 (Quantitative Aptitude, Q41–Q80)</strong> at any time.</li>
            <li><strong>Pause & Take a Break:</strong> Need a pause? Click <strong>"⏸ Pause / Take Break"</strong> in the exam toolbar to freeze the timer without losing progress.</li>
            <li><strong>Continue & Complete Later:</strong> You can always resume an incomplete attempt to complete Quantitative Aptitude or remaining questions.</li>
            <li><strong>Evaluation of Marked Questions:</strong> Questions that are <em>Answered and Marked for Review</em> WILL be evaluated.</li>
            <li><strong>Question-by-Question Solutions:</strong> Full step-by-step mathematical and logical solutions will be revealed immediately upon submission.</li>
          </ul>"""

assert old_instr_text in code, "old_instr_text not found"
code = code.replace(old_instr_text, new_instr_text, 1)

# 4. Update syncDeadline in app.js
old_sync = """  function syncDeadline() {
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
  }"""

new_sync = """  function syncDeadline() {
    if (!active) return;
    if (active.isPaused) return;
    if (millisLeft() <= 0) {
      alert('Time is up for your examination! Submitting your test now.');
      submitTest(true);
    }
  }"""

assert old_sync in code, "old_sync not found"
code = code.replace(old_sync, new_sync, 1)

# 5. Update tick in app.js
old_tick = """  function tick() {
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
  }"""

new_tick = """  function tick() {
    if (!active) return;
    if (active.isPaused) return;
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
  }"""

assert old_tick in code, "old_tick not found"
code = code.replace(old_tick, new_tick, 1)

# 6. Update goTo in app.js
old_goto = """  function goTo(nextIdx) {
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
  }"""

new_goto = """  function goTo(nextIdx) {
    if (!active) return;
    const t = getTest(active.testId);
    if (nextIdx < 0 || nextIdx >= t.questions.length) return;

    if (active.currentIndex < 40) {
      active.lastReasoningIndex = active.currentIndex;
    } else {
      active.lastQuantIndex = active.currentIndex;
    }

    active.currentIndex = nextIdx;
    active.sectionIndex = nextIdx < 40 ? 0 : 1;
    active.paletteSectionIndex = active.sectionIndex;
    const nextQId = getCurrentQuestion().id;
    if (!active.visited.includes(nextQId)) {
      active.visited.push(nextQId);
    }
    storeActive();
    renderExam();
  }"""

assert old_goto in code, "old_goto not found"
code = code.replace(old_goto, new_goto, 1)

# 7. Update renderExam top bar in app.js
old_exam_markup = """        <!-- TOP SECTION NAVIGATION & TIMING BAR -->
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
        </div>"""

new_exam_markup = """        <!-- TOP SECTION NAVIGATION & TIMING BAR -->
        <div class="section-nav-bar">
          <div class="section-tabs">
            <button type="button" class="section-tab ${active.sectionIndex === 0 ? 'active' : ''}" id="tabReasoning" style="cursor:pointer;">
              Section 1: Reasoning Ability
              <span class="badge-count">${t.questions.filter(x => x.section === 'reasoning' && x.id in active.answers).length}/40</span>
            </button>
            <button type="button" class="section-tab ${active.sectionIndex === 1 ? 'active' : ''}" id="tabQuant" style="cursor:pointer;">
              Section 2: Quantitative Aptitude
              <span class="badge-count">${t.questions.filter(x => x.section === 'quant' && x.id in active.answers).length}/40</span>
            </button>
          </div>
          <div style="display:flex; align-items:center; gap:12px;">
            <button type="button" class="btn btn-secondary" id="btnPauseExam" style="padding: 7px 14px; font-size: 12px; display:inline-flex; align-items:center; gap:6px;">
              ⏸ Pause / Take Break
            </button>
            <div id="examTimer" class="${secs <= 60 ? 'timer-box' : 'timer-box normal'}">
              ${timeText(secs)}
            </div>
            <button type="button" class="btn btn-submit" id="submitExamBtn" style="padding: 8px 18px;">
              Submit Exam
            </button>
          </div>
        </div>"""

assert old_exam_markup in code, "old_exam_markup not found"
code = code.replace(old_exam_markup, new_exam_markup, 1)

# Palette section toggle in app.js
old_pal_header = """            <div class="palette-header">
              Question Palette • ${esc(section.name)}
            </div>"""

new_pal_header = """            <div class="palette-header" style="display:flex; justify-content:space-between; align-items:center;">
              <span>Palette • ${esc(section.name)}</span>
              <div style="display:flex; gap:4px;">
                <button type="button" id="palOrigReason" class="pal-tab-btn ${palSectionIndex === 0 ? 'active' : ''}">
                  Reasoning (1-40)
                </button>
                <button type="button" id="palOrigQuant" class="pal-tab-btn ${palSectionIndex === 1 ? 'active' : ''}">
                  Quant (41-80)
                </button>
              </div>
            </div>"""

assert old_pal_header in code, "old_pal_header not found"
code = code.replace(old_pal_header, new_pal_header, 1)

# In renderExam in app.js: compute palSectionIndex and secQuestions
old_sec_def = """    const secQuestions = t.questions.slice(section.start - 1, section.end);"""
new_sec_def = """    const palSectionIndex = (active.paletteSectionIndex !== undefined) ? active.paletteSectionIndex : active.sectionIndex;
    const secQuestions = palSectionIndex === 0 ? t.questions.slice(0, 40) : t.questions.slice(40, 80);"""

assert old_sec_def in code, "old_sec_def not found"
code = code.replace(old_sec_def, new_sec_def, 1)

# In palette buttons: use sq.number
old_pal_btn = """                ${secQuestions.map((sq, i) => {
                  const num = section.start + i;
                  const st = statusFor(sq.id);
                  const isCurrent = sq.id === q.id;
                  return `
                    <button class="pal-btn ${st} ${isCurrent ? 'current' : ''}" data-jump="${num}">
                      ${num}
                    </button>
                  `;
                }).join('')}"""

new_pal_btn = """                ${secQuestions.map((sq) => {
                  const num = sq.number;
                  const st = statusFor(sq.id);
                  const isCurrent = sq.id === q.id;
                  return `
                    <button type="button" class="pal-btn ${st} ${isCurrent ? 'current' : ''}" data-jump="${num}">
                      ${num}
                    </button>
                  `;
                }).join('')}"""

assert old_pal_btn in code, "old_pal_btn not found"
code = code.replace(old_pal_btn, new_pal_btn, 1)

# Add Pause Modal overlay to app.js renderExam uniquely at the end of exam-layout
old_exam_end = """            <div class="palette-body">
              <div class="palette-buttons">
                ${secQuestions.map((sq) => {
                  const num = sq.number;
                  const st = statusFor(sq.id);
                  const isCurrent = sq.id === q.id;
                  return `
                    <button type="button" class="pal-btn ${st} ${isCurrent ? 'current' : ''}" data-jump="${num}">
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

    // Event Handlers"""

new_exam_end = """            <div class="palette-body">
              <div class="palette-buttons">
                ${secQuestions.map((sq) => {
                  const num = sq.number;
                  const st = statusFor(sq.id);
                  const isCurrent = sq.id === q.id;
                  return `
                    <button type="button" class="pal-btn ${st} ${isCurrent ? 'current' : ''}" data-jump="${num}">
                      ${num}
                    </button>
                  `;
                }).join('')}
              </div>
            </div>
          </div>
        </div>
        ${active.isPaused ? `
          <div class="cbt-pause-overlay">
            <div class="cbt-pause-card">
              <div style="font-size:44px; margin-bottom:12px;">☕</div>
              <h2 style="font-size:22px; font-weight:800; color:var(--primary); margin:0 0 8px;">
                Test Paused — Take a Break!
              </h2>
              <p style="color:var(--text-muted); font-size:13.5px; margin:0 0 16px; line-height:1.6;">
                Your exam timer is safely paused and all your responses are saved.<br>
                Rest your eyes, take a breather, and click below when you're ready to continue.
              </p>
              <div class="cbt-pause-stats-grid">
                <div class="cbt-pause-stat-item">
                  <div style="font-size:10.5px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Time Remaining</div>
                  <div style="font-size:20px; font-weight:800; color:var(--primary); font-family:monospace; margin-top:4px;">
                    ${timeText(active.timeRemainingSec || secs)}
                  </div>
                </div>
                <div class="cbt-pause-stat-item">
                  <div style="font-size:10.5px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Reasoning Done</div>
                  <div style="font-size:20px; font-weight:800; color:#2e7d32; margin-top:4px;">
                    ${t.questions.filter(x => x.section === 'reasoning' && x.id in active.answers).length}/40
                  </div>
                </div>
                <div class="cbt-pause-stat-item">
                  <div style="font-size:10.5px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Quant Done</div>
                  <div style="font-size:20px; font-weight:800; color:#2e7d32; margin-top:4px;">
                    ${t.questions.filter(x => x.section === 'quant' && x.id in active.answers).length}/40
                  </div>
                </div>
              </div>
              <div style="display:flex; justify-content:center; gap:12px; flex-wrap:wrap;">
                <button type="button" id="resumeFromPauseBtn" class="btn btn-primary" style="padding:12px 28px; font-size:15px; font-weight:750;">
                  ▶ Resume Test Now
                </button>
                <button type="button" id="exitToHomePauseBtn" class="btn btn-secondary" style="padding:12px 18px; font-size:13.5px;">
                  Save & Exit (Resume Later)
                </button>
              </div>
            </div>
          </div>
        ` : ''}
      </div>
    `;

    // Event Handlers"""

assert old_exam_end in code, "old_exam_end not found"
code = code.replace(old_exam_end, new_exam_end, 1)

# Handlers in renderExam for section switching, prev/next cross section, pause
old_handlers = """    $('#app').querySelectorAll('[data-jump]').forEach(btn => {
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
    };"""

new_handlers = """    $('#app').querySelectorAll('[data-jump]').forEach(btn => {
      btn.onclick = () => goTo(Number(btn.dataset.jump) - 1);
    });

    // Top Section Tabs
    $('#tabReasoning').onclick = () => {
      if (active.sectionIndex !== 0) {
        active.sectionIndex = 0;
        active.paletteSectionIndex = 0;
        const target = active.lastReasoningIndex !== undefined ? active.lastReasoningIndex : 0;
        goTo(target);
      }
    };

    $('#tabQuant').onclick = () => {
      if (active.sectionIndex !== 1) {
        active.sectionIndex = 1;
        active.paletteSectionIndex = 1;
        const target = active.lastQuantIndex !== undefined ? active.lastQuantIndex : 40;
        goTo(target);
      }
    };

    // Palette Toggles
    const palR = $('#palOrigReason');
    if (palR) palR.onclick = () => { active.paletteSectionIndex = 0; storeActive(); renderExam(); };
    const palQ = $('#palOrigQuant');
    if (palQ) palQ.onclick = () => { active.paletteSectionIndex = 1; storeActive(); renderExam(); };

    // Pause Controls
    $('#btnPauseExam').onclick = pauseTest;
    const resPause = $('#resumeFromPauseBtn');
    if (resPause) resPause.onclick = unpauseTest;
    const exitPause = $('#exitToHomePauseBtn');
    if (exitPause) exitPause.onclick = enterHome;

    $('#btnPrev').onclick = () => {
      if (active.currentIndex > 0) goTo(active.currentIndex - 1);
    };

    $('#btnSaveNext').onclick = () => {
      if (active.currentIndex === t.questions.length - 1) {
        if (confirm('You have reached the final question. Would you like to submit your exam now?')) {
          submitTest(false);
        }
      } else {
        goTo(active.currentIndex + 1);
      }
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
      if (active.currentIndex === t.questions.length - 1) {
        if (confirm('You have reached the final question. Would you like to submit your exam now?')) {
          submitTest(false);
        }
      } else {
        goTo(active.currentIndex + 1);
      }
    };"""

assert old_handlers in code, "old_handlers not found"
code = code.replace(old_handlers, new_handlers, 1)

# In disabled state for prev button:
old_prev_disabled = "${active.currentIndex === section.start - 1 ? 'disabled' : ''}"
new_prev_disabled = "${active.currentIndex === 0 ? 'disabled' : ''}"
assert old_prev_disabled in code
code = code.replace(old_prev_disabled, new_prev_disabled, 1)

# In submitTest in app.js: update existing attempt if resumedFromAttemptId
old_submit_hist = """    const allAttempts = history();
    allAttempts.unshift(attempt);
    storeHistory(allAttempts);"""

new_submit_hist = """    const allAttempts = history();
    if (active.resumedFromAttemptId) {
      attempt.attemptId = active.resumedFromAttemptId;
      const exIdx = allAttempts.findIndex(a => a.attemptId === active.resumedFromAttemptId);
      if (exIdx !== -1) allAttempts[exIdx] = attempt;
      else allAttempts.unshift(attempt);
    } else {
      allAttempts.unshift(attempt);
    }
    storeHistory(allAttempts);"""

assert old_submit_hist in code, "old_submit_hist not found"
code = code.replace(old_submit_hist, new_submit_hist, 1)

# In showResult in app.js: add "Continue Test & Complete Quant" buttons
old_res_btns = """            <div style="display:flex; gap:10px;">
              <button class="btn btn-secondary" id="toggleOnlyWrong">Show Only Incorrect / Unanswered</button>
              <button class="btn btn-primary" id="retakeBtn">Retake This Mock</button>
              <button class="btn btn-secondary" id="backToAllMocks">All Mock Papers</button>
            </div>"""

new_res_btns = """            <div style="display:flex; gap:10px; flex-wrap:wrap;">
              ${overall.blank > 0 ? `
                <button type="button" class="btn btn-primary" id="continueAttemptBtn" style="background:#2e7d32; border-color:#2e7d32; font-weight:750;">
                  ▶ Complete Quant & Remaining (${overall.blank} Skipped)
                </button>
              ` : ''}
              <button class="btn btn-secondary" id="toggleOnlyWrong">Show Only Incorrect / Unanswered</button>
              <button class="btn btn-primary" id="retakeBtn">Retake This Mock</button>
              <button class="btn btn-secondary" id="backToAllMocks">All Mock Papers</button>
            </div>"""

assert old_res_btns in code, "old_res_btns not found"
code = code.replace(old_res_btns, new_res_btns, 1)

# In showResult hero card: add helpful tip banner if blank > 0
old_hero_cutoff = """          <div class="cutoff-box"><h4>Your practice checkpoint</h4><p>Use topic accuracy and missed questions to plan your next session.</p><p style="margin-top:12px;font-size:12px;opacity:.8">Official cutoffs vary by state, category and year. This score does not predict qualification.</p></div>"""

new_hero_cutoff = """          <div class="cutoff-box">
            <h4>Your practice checkpoint</h4>
            <p>Use topic accuracy and missed questions to plan your next session.</p>
            ${overall.blank > 0 ? `
              <div style="margin-top: 10px; padding: 8px 12px; background: rgba(255,255,255,0.18); border-radius:6px; font-size:12.5px;">
                Took a break or skipped Quant? You have <strong>${overall.blank} unattempted questions</strong>.
                <button type="button" id="heroContinueOrigBtn" style="margin-top:6px; width:100%; padding:6px; background:#cfe68c; color:#173c34; border:none; border-radius:4px; font-weight:800; font-size:11.5px; cursor:pointer;">
                  ▶ Continue / Complete Quant Now →
                </button>
              </div>
            ` : '<p style="margin-top:12px;font-size:12px;opacity:.8">Official cutoffs vary by state, category and year. This score does not predict qualification.</p>'}
          </div>"""

assert old_hero_cutoff in code, "old_hero_cutoff not found"
code = code.replace(old_hero_cutoff, new_hero_cutoff, 1)

# Bind continueAttemptBtn in showResult
old_bind_res = """    $('#backToAllMocks').onclick = enterHome;"""
new_bind_res = """    const contBtn = $('#continueAttemptBtn');
    if (contBtn) contBtn.onclick = () => continueTest(att);
    const heroContBtn = $('#heroContinueOrigBtn');
    if (heroContBtn) heroContBtn.onclick = () => continueTest(att);

    $('#backToAllMocks').onclick = enterHome;"""

assert old_bind_res in code, "old_bind_res not found"
code = code.replace(old_bind_res, new_bind_res, 1)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Successfully upgraded app.js!")
