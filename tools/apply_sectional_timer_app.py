import re

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update millisLeft, startTest, continueTest, pauseTest, unpauseTest, resumeTest
old_block_1 = """  function millisLeft() {
    if (!active) return 0;
    if (active.isPaused) return (active.timeRemainingSec || 0) * 1000;
    return active.testEndAt ? active.testEndAt - Date.now() : 0;
  }"""

new_block_1 = """  function currentSectionSecLeft() {
    if (!active) return 0;
    return active.sectionIndex === 0
      ? (active.reasoningSecLeft ?? 25 * 60)
      : (active.quantSecLeft ?? 20 * 60);
  }

  function totalSecLeft() {
    if (!active) return 0;
    return (active.reasoningSecLeft ?? 25 * 60) + (active.quantSecLeft ?? 20 * 60);
  }

  function millisLeft() {
    return currentSectionSecLeft() * 1000;
  }"""

assert old_block_1 in code, "old_block_1 not found"
code = code.replace(old_block_1, new_block_1, 1)

old_block_2 = """  function startTest(id) {
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

new_block_2 = """  function startTest(id) {
    if (active && active.testId !== id) {
      if (!confirm('Another mock test is already in progress. Starting this mock will discard your previous unfinished attempt. Do you want to continue?')) return;
    }
    const now = Date.now();
    active = {
      testId: id,
      startedAt: now,
      lastTickAt: now,
      reasoningSecLeft: 25 * 60, // Official 25:00 Minutes Reasoning
      quantSecLeft: 20 * 60,     // Official 20:00 Minutes Quantitative Aptitude
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

    // Prioritize the first unattempted question in Section 2 (Quantitative Aptitude, index >= 40)
    let quantUnattempted = t.questions.slice(40).findIndex(q => att.answers[q.id] === undefined);
    let targetIdx;
    if (quantUnattempted !== -1) {
      targetIdx = 40 + quantUnattempted;
    } else {
      targetIdx = t.questions.findIndex(q => att.answers[q.id] === undefined);
      if (targetIdx === -1) targetIdx = 40;
    }

    const now = Date.now();
    const isTargetQuant = targetIdx >= 40;

    active = {
      testId: att.testId,
      startedAt: att.startedAt || now,
      lastTickAt: now,
      sectionIndex: isTargetQuant ? 1 : 0,
      currentIndex: targetIdx,
      paletteSectionIndex: isTargetQuant ? 1 : 0,
      // Official IBPS RRB Sectional Timing: 25m Reasoning, 20m Quant
      reasoningSecLeft: att.reasoningSecLeft !== undefined ? att.reasoningSecLeft : (isTargetQuant ? 0 : 25 * 60),
      quantSecLeft: att.quantSecLeft !== undefined && att.quantSecLeft > 0 ? att.quantSecLeft : 20 * 60,
      isPaused: false,
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
    syncDeadline();
    active.isPaused = true;
    storeActive();
    renderExam();
  }

  function unpauseTest() {
    if (!active || !active.isPaused) return;
    active.isPaused = false;
    active.lastTickAt = Date.now();
    storeActive();
    renderExam();
  }

  function resumeTest() {
    if (active) {
      if (active.isPaused) {
        active.isPaused = false;
        active.lastTickAt = Date.now();
        storeActive();
      }
      page = 'exam';
      syncDeadline();
      if (active) renderExam();
    }
  }"""

assert old_block_2 in code, "old_block_2 not found"
code = code.replace(old_block_2, new_block_2, 1)

# 2. Update Instructions
old_inst = """          <h3 style="color: var(--primary); font-size: 15px; margin-bottom: 10px;">Exam Scheme & Sectional Rules:</h3>
          <ul style="padding-left: 20px;">
            <li><strong>Total Questions:</strong> 80 Objective Multiple Choice Questions (5 options each).</li>
            <li><strong>Total Marks:</strong> 80 Marks (+1.00 for Correct, −0.25 for Incorrect, 0 for Unattempted).</li>
            <li><strong>Composite 45:00 Minutes Timing:</strong> 45 minutes total composite duration for both sections (official IBPS RRB PO standard).</li>
            <li><strong>Free Section Switching:</strong> Switch freely between <strong>Section 1 (Reasoning Ability, Q1–Q40)</strong> and <strong>Section 2 (Quantitative Aptitude, Q41–Q80)</strong> at any time.</li>"""

new_inst = """          <h3 style="color: var(--primary); font-size: 15px; margin-bottom: 10px;">Official IBPS RRB PO Exam Scheme & Sectional Rules:</h3>
          <ul style="padding-left: 20px;">
            <li><strong>Total Questions:</strong> 80 Objective Multiple Choice Questions (5 options each).</li>
            <li><strong>Total Marks:</strong> 80 Marks (+1.00 for Correct, −0.25 for Incorrect, 0 for Unattempted).</li>
            <li><strong>Official Sectional Timing:</strong> <strong>25:00 Minutes</strong> for Section 1 (Reasoning Ability, 40 Qs) and <strong>20:00 Minutes</strong> for Section 2 (Quantitative Aptitude, 40 Qs). Total 45:00 Minutes composite.</li>
            <li><strong>TCS iON CBT Clock:</strong> Displays live <code>Time Left : MM:SS</code> countdown for the active section, switching seamlessly between Reasoning (25m) and Quant (20m).</li>
            <li><strong>Free Section Switching:</strong> Switch freely between <strong>Section 1 (Reasoning Ability, Q1–Q40)</strong> and <strong>Section 2 (Quantitative Aptitude, Q41–Q80)</strong> at any time.</li>
            <li><strong>Pause & Take Break:</strong> Click <strong>"⏸ Pause / Take Break"</strong> anytime to pause the timer and review your sectional progress.</li>
            <li><strong>Continue & Complete Quant Later:</strong> If you take a break after completing Reasoning (or skip Quant), you can always click <strong>"▶ Complete Quant & Remaining"</strong> on your scorecard to finish with its full 20:00 minutes!</li>"""

assert old_inst in code, "old_inst not found"
code = code.replace(old_inst, new_inst, 1)

# 3. Update syncDeadline & tick
old_sync_tick = """  function syncDeadline() {
    if (!active) return;
    if (active.isPaused) return;
    if (millisLeft() <= 0) {
      alert('Time is up for your examination! Submitting your test now.');
      submitTest(true);
    }
  }

  function tick() {
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

new_sync_tick = """  function syncDeadline() {
    if (!active || active.isPaused) return;

    const now = Date.now();
    const lastTick = active.lastTickAt || now;
    const elapsed = Math.max(0, Math.floor((now - lastTick) / 1000));
    if (elapsed <= 0) return;

    active.lastTickAt = now;

    if (active.sectionIndex === 0) {
      active.reasoningSecLeft = Math.max(0, (active.reasoningSecLeft ?? 25 * 60) - elapsed);
      if (active.reasoningSecLeft <= 0) {
        if ((active.quantSecLeft ?? 20 * 60) > 0) {
          active.sectionIndex = 1;
          active.paletteSectionIndex = 1;
          active.currentIndex = 40;
          const t = getTest(active.testId);
          if (t && t.questions[40] && !active.visited.includes(t.questions[40].id)) {
            active.visited.push(t.questions[40].id);
          }
          storeActive();
          alert('Section 1 (Reasoning Ability) time is up (25:00 Minutes)!\\n\\nNow beginning Section 2: Quantitative Aptitude (20:00 Minutes).');
          renderExam();
          return;
        } else {
          alert('Time is up for both examination sections! Your mock test is submitting now.');
          submitTest(true);
          return;
        }
      }
    } else {
      active.quantSecLeft = Math.max(0, (active.quantSecLeft ?? 20 * 60) - elapsed);
      if (active.quantSecLeft <= 0) {
        if ((active.reasoningSecLeft ?? 0) > 0) {
          active.sectionIndex = 0;
          active.paletteSectionIndex = 0;
          active.currentIndex = 0;
          const t = getTest(active.testId);
          if (t && t.questions[0] && !active.visited.includes(t.questions[0].id)) {
            active.visited.push(t.questions[0].id);
          }
          storeActive();
          alert('Section 2 (Quantitative Aptitude) time is up (20:00 Minutes)!\\n\\nReturning to Section 1: Reasoning Ability.');
          renderExam();
          return;
        } else {
          alert('Time is up for both examination sections! Your mock test is submitting now.');
          submitTest(true);
          return;
        }
      }
    }

    storeActive();
  }

  function tick() {
    if (!active) return;
    if (active.isPaused) return;
    syncDeadline();
    if (!active) return;
    if (page === 'exam') {
      const curSecLeft = currentSectionSecLeft();
      const totSecLeft = totalSecLeft();

      const timer = $('#examTimer');
      if (timer) {
        timer.textContent = timeText(curSecLeft);
        if (curSecLeft <= 120) {
          timer.classList.add('urgent');
        } else {
          timer.classList.remove('urgent');
        }
      }

      const secLabel = $('#examTimerSecLabel');
      if (secLabel) {
        secLabel.textContent = active.sectionIndex === 0 ? 'Reasoning (25:00)' : 'Quantitative (20:00)';
      }

      const totLabel = $('#examTimerTotalLabel');
      if (totLabel) {
        totLabel.textContent = `Total: ${timeText(totSecLeft)}`;
      }
    }
  }"""

assert old_sync_tick in code, "old_sync_tick not found"
code = code.replace(old_sync_tick, new_sync_tick, 1)

# 4. Update renderExam timer & pause modal
old_render_timer_start = """    const stim = q.stimulusId ? t.stimuli.find(x => x.id === q.stimulusId) : null;
    const answered = q.id in active.answers;
    const secs = Math.max(0, Math.ceil(millisLeft() / 1000));"""

new_render_timer_start = """    const stim = q.stimulusId ? t.stimuli.find(x => x.id === q.stimulusId) : null;
    const answered = q.id in active.answers;
    const curSecLeft = currentSectionSecLeft();
    const totSecLeft = totalSecLeft();
    const secs = curSecLeft;"""

assert old_render_timer_start in code, "old_render_timer_start not found"
code = code.replace(old_render_timer_start, new_render_timer_start, 1)

old_timer_widget = """            <button type="button" class="btn btn-secondary" id="btnPauseExam" style="padding: 7px 14px; font-size: 12px; display:inline-flex; align-items:center; gap:6px;">
              ⏸ Pause / Take Break
            </button>
            <div id="examTimer" class="${secs <= 60 ? 'timer-box' : 'timer-box normal'}">
              ${timeText(secs)}
            </div>
            <button type="button" class="btn btn-submit" id="submitExamBtn" style="padding: 8px 18px;">
              Submit Exam
            </button>"""

new_timer_widget = """            <button type="button" class="btn btn-secondary" id="btnPauseExam" style="padding: 7px 14px; font-size: 12px; display:inline-flex; align-items:center; gap:6px;">
              ⏸ Pause / Take Break
            </button>
            <div class="tcs-timer-widget">
              <div class="tcs-timer-main">
                <span class="tcs-timer-label">Time Left :</span>
                <span id="examTimer" class="tcs-timer-digits ${curSecLeft <= 120 ? 'urgent' : ''}">${timeText(curSecLeft)}</span>
              </div>
              <div class="tcs-timer-meta">
                <span id="examTimerSecLabel" class="tcs-sec-label">${active.sectionIndex === 0 ? 'Reasoning (25:00)' : 'Quantitative (20:00)'}</span>
                <span id="examTimerTotalLabel" class="tcs-total-label">Total: ${timeText(totSecLeft)}</span>
              </div>
            </div>
            <button type="button" class="btn btn-submit" id="submitExamBtn" style="padding: 8px 18px;">
              Submit Exam
            </button>"""

assert old_timer_widget in code, "old_timer_widget not found"
code = code.replace(old_timer_widget, new_timer_widget, 1)

old_pause_stats = """              <div class="cbt-pause-stats-grid">
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
              </div>"""

new_pause_stats = """              <div class="cbt-pause-stats-grid">
                <div class="cbt-pause-stat-item">
                  <div style="font-size:10.5px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Reasoning Time</div>
                  <div style="font-size:18px; font-weight:800; color:var(--primary); font-family:monospace; margin-top:4px;">
                    ${timeText(active.reasoningSecLeft ?? 25 * 60)}
                  </div>
                </div>
                <div class="cbt-pause-stat-item">
                  <div style="font-size:10.5px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Quant Time</div>
                  <div style="font-size:18px; font-weight:800; color:var(--primary); font-family:monospace; margin-top:4px;">
                    ${timeText(active.quantSecLeft ?? 20 * 60)}
                  </div>
                </div>
                <div class="cbt-pause-stat-item">
                  <div style="font-size:10.5px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Total Remaining</div>
                  <div style="font-size:18px; font-weight:800; color:#2e7d32; font-family:monospace; margin-top:4px;">
                    ${timeText((active.reasoningSecLeft ?? 0) + (active.quantSecLeft ?? 0))}
                  </div>
                </div>
              </div>"""

assert old_pause_stats in code, "old_pause_stats not found"
code = code.replace(old_pause_stats, new_pause_stats, 1)

# 5. In submitTest, record reasoningSecLeft and quantSecLeft
old_attempt_record = """      reasonScore: reason.score,
      quantScore: quant.score,
      answers: { ...active.answers },"""

new_attempt_record = """      reasonScore: reason.score,
      quantScore: quant.score,
      reasoningSecLeft: active.reasoningSecLeft,
      quantSecLeft: active.quantSecLeft,
      answers: { ...active.answers },"""

assert old_attempt_record in code, "old_attempt_record not found"
code = code.replace(old_attempt_record, new_attempt_record, 1)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print(f"Successfully upgraded app.js with official IBPS RRB sectional timing ({len(code)} chars)!")
