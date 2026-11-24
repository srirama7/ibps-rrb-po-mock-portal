(() => {
  'use strict';
  const bank = window.KARNATAKA_BANK;
  const ACTIVE = 'karnataka_csa_active_v1', HISTORY = 'karnataka_csa_history_v1';
  const $ = s => document.querySelector(s);
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const read = (key, fallback) => { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } };
  let storageError = false;
  const write = (key, value) => { try { value === null ? localStorage.removeItem(key) : localStorage.setItem(key, JSON.stringify(value)); } catch { storageError = true; } };
  let active = read(ACTIVE, null), view = 'home', lastResult = null, filter = 'all';
  const testFor = id => bank.tests.find(t => t.id === id);

  if (active && (!testFor(active.testId) || !active.answers || !Array.isArray(active.marked) || !Array.isArray(active.visited))) active = null;
  if (active) {
    if (active.timeRemainingSec === undefined && Number.isFinite(active.endAt)) {
      active.timeRemainingSec = Math.max(0, Math.ceil((active.endAt - Date.now()) / 1000));
    }
    if (active.isPaused === undefined) active.isPaused = false;
  }

  const syncRemaining = () => {
    if (active && !active.isPaused && Number.isFinite(active.endAt)) {
      active.timeRemainingSec = Math.max(0, Math.ceil((active.endAt - Date.now()) / 1000));
    }
  };
  const save = () => { syncRemaining(); write(ACTIVE, active); };
  const history = () => { const h = read(HISTORY, []); return Array.isArray(h) ? h : []; };

  const fmtScore = n => {
    const val = Number(n ?? 0);
    return Number.isInteger(val) ? String(val) : val.toFixed(2);
  };

  const clock = () => {
    if (!active) return '60:00';
    const seconds = active.isPaused
      ? Math.max(0, active.timeRemainingSec ?? Math.max(0, Math.ceil((active.endAt - Date.now()) / 1000)))
      : Math.max(0, Math.ceil((active.endAt - Date.now()) / 1000));
    return `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
  };

  const warning = () => storageError ? '<p class="kb-storage" role="alert">Browser storage is unavailable. Keep this tab open; progress cannot be saved after closing it.</p>' : '';
  const status = q => active.marked.includes(q.id) ? (active.answers[q.id] !== undefined ? 'marked-answered' : 'marked') : active.answers[q.id] !== undefined ? 'answered' : active.visited.includes(q.id) ? 'visited' : '';
  const source = () => `<a href="${esc(bank.patternSource)}" target="_blank" rel="noopener">Bank’s 2026 campus recruitment notice ↗</a>`;

  function pauseTest() {
    if (!active || active.isPaused) return;
    active.timeRemainingSec = Math.max(0, Math.ceil((active.endAt - Date.now()) / 1000));
    active.isPaused = true;
    save();
    exam();
  }

  function unpauseTest() {
    if (!active || !active.isPaused) return;
    const remaining = Math.max(0, active.timeRemainingSec ?? 3600);
    active.endAt = Date.now() + remaining * 1000;
    active.isPaused = false;
    save();
    exam();
  }

  function home() {
    view = 'home';
    const attempts = history();
    const isP = Boolean(active && active.isPaused);
    $('#app').innerHTML = `${warning()}<section class="kb-hero">
      <span class="kb-label" style="color:#cfe68c">YOUR KARNATAKA BANK PRACTICE SPACE</span>
      <h1>Karnataka Bank Exam<span style="color:#cfe68c">.</span></h1>
      <p>Customer Service Associates · 2026 campus recruitment. Practise the papers you supplied with <strong>unlimited retakes</strong> — work against the clock, pause and resume anytime, and learn from every answer without being capped at 3 attempts.</p>
      <div class="kb-pills">
        <span>10 full mocks</span>
        <span>75 questions each</span>
        <span>60 minutes</span>
        <span>6 sections</span>
        <span>−0.25 negative marking</span>
        <span>⏸ Pause clock on every mock</span>
        <span style="border-color:#cfe68c; color:#cfe68c; font-weight:750; background:rgba(207,230,140,0.18);">♾️ Unlimited retakes (no 3-attempt limit)</span>
      </div>
      <a class="btn btn-primary" href="#kbMocks">Choose your mock ↓</a>
    </section>
    ${active ? `
      <div class="kb-note" style="border-left:4px solid #173c34; background:#eef5e9;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
          <div>
            <strong>${isP ? '☕ ' + esc(testFor(active.testId).title) + ' is paused.' : '⏱ ' + esc(testFor(active.testId).title) + ' is in progress.'}</strong><br>
            <span>${isP ? `Pause clock is frozen at <strong>${clock()}</strong>. All ${Object.keys(active.answers).length} responses preserved.` : `The 60-minute countdown continues while away. Time left: <strong>${clock()}</strong>.`}</span>
          </div>
          <button class="btn btn-primary" id="kbResume">${!isP && Date.now() >= active.endAt ? 'View timed-out result' : isP ? '▶ Resume paused test' : 'Resume test'}</button>
        </div>
      </div>
    ` : ''}
    <div class="kb-note">
      <strong>Timing & Marking Scheme · ${bank.patternChecked}</strong><br>
      75 questions across six sections with one 60-minute timer. Illustrative 12 / 15 / 15 / 11 / 11 / 11 split. <strong>Marking scheme: +1.00 for correct answers, −0.25 penalty for wrong answers, 0 for unattempted questions.</strong> ${source()}<br>
      <strong>⏸ Interactive Pause Clock:</strong> Every Karnataka Bank mock includes a <strong>Pause Clock</strong>. Click directly on the clock or the pause button during any test to freeze time safely without losing answers.<br>
      <strong>♾️ Unlimited Retakes (Zero Limits):</strong> Unlike official recruitment platforms (such as L&T EduTech) that restrict candidates to only 3 test attempts, this portal offers <strong>100% UNLIMITED retakes</strong> on every mock paper. You can practice as many times as you need (Attempt #4, #5, #10+) with full attempt history tracking.<br>
      The 200-question, 135-minute general CSA recruitment is a different exam pattern.
    </div>
    <div class="kb-heading" id="kbMocks">
      <h2>Full-length practice mocks</h2>
      <span>750 questions · keys & brief explanations · unlimited retakes</span>
    </div>
    <div class="kb-grid">${bank.tests.map((t, i) => {
      const rows = attempts.filter(a => a.testId === t.id);
      const isOngoing = Boolean(active && active.testId === t.id);
      const cardIsP = Boolean(isOngoing && active.isPaused);
      const nextAttempt = rows.length + 1;
      return `<article class="kb-card ${isOngoing ? 'active-test-card ' + (cardIsP ? 'paused' : '') : ''}">
        <span class="kb-label">PAPER ${String(i + 1).padStart(2, '0')} / 10 · UNLIMITED RETAKES</span>
        <h3>${esc(t.title)}</h3>
        <p>75 questions · 60 minutes<br>Verbal, Quant, Reasoning, GK, Computer & Sales</p>
        <p>${rows.length ? `<strong>${rows.length} attempt(s) completed</strong> · Best: <strong>${fmtScore(Math.max(...rows.map(r => r.score)))}/75</strong><br><span style="color:#245943; font-weight:700;">♾️ Unlimited retakes (Next: Attempt #${nextAttempt})</span>` : '<span style="color:#245943; font-weight:700;">Ready for Attempt #1 · ♾️ Unlimited retakes</span>'}</p>
        
        ${isOngoing ? `
          <div class="kb-card-pause-clock" id="cardPauseClock" title="Active test · Click toggle to ${cardIsP ? 'Resume' : 'Pause'}">
            <span class="kb-card-clock-icon" style="font-size:20px;">${cardIsP ? '☕' : '⏱'}</span>
            <div class="kb-card-clock-details">
              <strong>${cardIsP ? 'Paused Clock:' : 'Exam Clock:'} <span class="kb-card-clock-digits">${clock()}</span></strong>
              <small>${cardIsP ? 'Timer is frozen safely' : 'Countdown active'}</small>
            </div>
            <button type="button" class="btn ${cardIsP ? 'btn-primary' : 'btn-secondary'} btn-sm" id="btnCardPauseToggle">
              ${cardIsP ? '▶ Resume' : '⏸ Pause Clock'}
            </button>
          </div>
        ` : ''}

        <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;">
          <button class="btn btn-primary" data-start="${t.id}">
            ${isOngoing ? (cardIsP ? '▶ Resume Paused Test' : 'Continue Test →') : (rows.length ? `🔄 Retake mock (Attempt #${nextAttempt})` : 'Start mock →')}
          </button>
          <a class="btn btn-ghost" href="${t.pdf}" target="_blank" rel="noopener">Source PDF ↗</a>
          ${rows.length ? `<button class="btn btn-ghost" data-result="${t.id}">Latest result</button>` : ''}
          ${rows.length ? `<button class="btn btn-ghost" data-reset="${t.id}" title="Reset attempts for this mock" style="color:#8b3a30; border-color:#f0c4be;">Reset</button>` : ''}
        </div>
      </article>`;
    }).join('')}</div>
    <div class="kb-heading">
      <h2>Previous-paper practice links</h2>
      <span>10 external PDFs</span>
    </div>
    <p class="kb-note">Your ZIP contains links to <strong>IBPS Clerk memory-based papers</strong>. These are supplementary practice, not verified Karnataka Bank past papers. They open the publisher’s website and may require internet access.</p>
    <div class="kb-grid">${bank.paperLinks.map((l, i) => `
      <article class="kb-card">
        <span class="kb-label">SUPPLEMENTARY PAPER ${i + 1}</span>
        <h3>${esc(l.title)}</h3>
        <a href="${esc(l.url)}" target="_blank" rel="noopener">Open publisher PDF ↗</a>
      </article>
    `).join('')}</div>
    ${attempts.length ? `
      <div class="kb-heading">
        <h2>Your attempt history (${attempts.length} attempt${attempts.length > 1 ? 's' : ''} · Unlimited Retakes)</h2>
        <div>
          <button class="btn btn-ghost btn-sm" id="kbClearHistory" style="border:1px solid #e2a499; color:#9c2a1b;">🗑 Clear all history</button>
        </div>
      </div>
      <div class="kb-table-wrap">
        <table class="kb-table">
          <thead>
            <tr><th>Paper</th><th>Attempt</th><th>Completed</th><th>Score</th><th>Review</th></tr>
          </thead>
          <tbody>
            ${attempts.slice(0, 50).map((r, i) => {
              const testAttempts = attempts.filter(a => a.testId === r.testId);
              const testAttemptIndex = testAttempts.findIndex(a => a === r);
              const attemptNum = testAttemptIndex !== -1 ? (testAttempts.length - testAttemptIndex) : 1;
              return `<tr>
                <td><strong>${esc(testFor(r.testId)?.title)}</strong></td>
                <td><span style="font-size:11.5px; font-weight:750; padding:3px 8px; background:#eef5e9; border:1px solid #b8cbb8; border-radius:4px; color:#173c34;">Attempt #${attemptNum}</span></td>
                <td>${esc(new Date(r.completedAt).toLocaleString())}</td>
                <td><strong>${fmtScore(r.score)}</strong>/75</td>
                <td><button class="btn btn-ghost" data-history="${i}">Review</button></td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>
    ` : ''}`;

    $('[id="kbResume"]')?.addEventListener('click', () => {
      if (!expire()) {
        if (active && active.isPaused) unpauseTest();
        else exam();
      }
    });

    const cardToggle = $('#btnCardPauseToggle');
    if (cardToggle) {
      cardToggle.onclick = (e) => {
        e.stopPropagation();
        if (active.isPaused) {
          unpauseTest();
        } else {
          pauseTest();
        }
        home();
      };
    }

    document.querySelectorAll('[data-start]').forEach(b => b.onclick = () => {
      const id = b.dataset.start;
      if (active && active.testId === id) {
        if (!expire()) {
          if (active.isPaused) unpauseTest();
          else exam();
        }
      } else {
        instructions(id);
      }
    });
    document.querySelectorAll('[data-result]').forEach(b => b.onclick = () => result(attempts.find(a => a.testId === b.dataset.result)));
    document.querySelectorAll('[data-history]').forEach(b => b.onclick = () => result(attempts[Number(b.dataset.history)]));
    document.querySelectorAll('[data-reset]').forEach(b => b.onclick = (e) => {
      e.stopPropagation();
      const id = b.dataset.reset;
      const t = testFor(id);
      const count = attempts.filter(a => a.testId === id).length;
      confirmAction(
        `Reset attempts for ${t.title}?`,
        `This will remove past attempts for this mock only (${count} attempt${count > 1 ? 's' : ''}). You can retake it afresh anytime with unlimited attempts.`,
        () => {
          const remaining = attempts.filter(a => a.testId !== id);
          write(HISTORY, remaining);
          home();
        }
      );
    });

    $('#kbClearHistory')?.addEventListener('click', () => {
      confirmAction(
        'Clear all attempt history?',
        'This will erase all recorded attempt scores and review records from your browser. This action cannot be undone.',
        () => {
          write(HISTORY, []);
          home();
        }
      );
    });
    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  function instructions(id) {
    view = 'instructions';
    const t = testFor(id);
    const mockAttempts = history().filter(a => a.testId === id);
    const nextAttempt = mockAttempts.length + 1;
    $('#app').innerHTML = `<div class="kb-result">
      <span class="kb-label">BEFORE YOU BEGIN · ATTEMPT #${nextAttempt}</span>
      <h1>${esc(t.title)}</h1>
      <p>Answer 75 questions in 60 minutes. Your test submits automatically when time runs out.</p>
      <div class="kb-table-wrap">
        <table class="kb-table">
          <thead>
            <tr><th>Section</th><th>Practice questions</th></tr>
          </thead>
          <tbody>
            ${t.sections.map(s => `<tr><td>${esc(s.name)}</td><td>${s.count}</td></tr>`).join('')}
            <tr><th>Total</th><th>75 · 60 minutes</th></tr>
          </tbody>
        </table>
      </div>
      <div class="kb-note" style="border-left:4px solid #245943; background:#edf5ea;">
        <strong>♾️ Unlimited Retakes Supported (Attempt #${nextAttempt}):</strong><br>
        • Unlike official recruitment portals (such as L&T EduTech) that restrict candidates to only 3 attempts, you can retake all mocks on this portal an <strong>unlimited number of times</strong>.<br>
        • ${mockAttempts.length ? `You have already completed <strong>${mockAttempts.length} attempt(s)</strong> for this paper (Best: <strong>${fmtScore(Math.max(...mockAttempts.map(a => a.score)))}/75</strong>).` : 'This is your first attempt on this paper.'} All previous attempt scores and review solutions remain saved in your browser history.<br>
        • <strong>Scoring:</strong> +1.00 for each correct answer, −0.25 penalty for each wrong answer, 0 for unanswered.<br>
        • <strong>⏸ Pause Clock:</strong> You can pause the countdown clock anytime by clicking directly on the <strong>Pause Clock</strong> widget or <strong>"⏸ Pause Clock / Take Break"</strong> in the exam toolbar.<br>
        • Answers marked for review will be scored.<br>
        ${source()}
      </div>
      ${active ? '<p class="kb-storage">Starting a new mock will replace your current unfinished Karnataka Bank attempt.</p>' : ''}
      <p>This is independently authored practice material, not an official question paper. Keys and brief explanations follow your supplied PDF.</p>
      <div class="kb-actions">
        <button class="btn btn-primary" id="kbBegin">${mockAttempts.length ? `Begin Attempt #${nextAttempt} (60 min)` : 'Begin 60-minute test'}</button>
        <button class="btn btn-ghost" id="kbBack">Back to library</button>
      </div>
    </div>`;
    $('#kbBack').onclick = home;
    $('#kbBegin').onclick = () => {
      if (active) {
        confirmAction('Replace unfinished attempt?', 'Your current unfinished Karnataka Bank attempt will be replaced.', () => start(t));
      } else {
        start(t);
      }
    };
    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  function start(t) {
    const durationSec = t.durationMinutes * 60;
    active = {
      testId: t.id,
      startedAt: Date.now(),
      endAt: Date.now() + durationSec * 1000,
      timeRemainingSec: durationSec,
      isPaused: false,
      index: 0,
      answers: {},
      marked: [],
      visited: []
    };
    save();
    exam();
    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  function expire() {
    if (active && !active.isPaused && Date.now() >= active.endAt) {
      finish(true);
      return true;
    }
    return false;
  }

  function exam() {
    if (!active || expire()) return;
    view = 'exam';
    const t = testFor(active.testId), q = t.questions[active.index];
    if (!active.visited.includes(q.id)) active.visited.push(q.id);
    save();
    const section = t.sections.find(s => s.id === q.section);
    const answeredCount = Object.keys(active.answers).length;
    const isPaused = Boolean(active.isPaused);

    $('#app').innerHTML = `${warning()}
      <div class="kb-exam-title">
        <div>
          <span class="kb-label">${esc(t.title)}</span>
          <h1>${esc(section.name)}</h1>
        </div>
        <div class="kb-exam-header-right">
          <button type="button" class="kb-pause-btn" id="kbPauseBtn" title="Pause exam clock">
            ⏸ Pause Clock / Take Break
          </button>
          <div class="kb-pause-clock-widget ${isPaused ? 'paused' : ''}" id="kbPauseClockWidget" role="button" tabindex="0" aria-label="Pause Clock: ${clock()}" title="Click clock to ${isPaused ? 'resume' : 'pause'} exam">
            <div class="kb-pause-clock-top">
              <span class="kb-pause-clock-icon">${isPaused ? '☕' : '⏸'}</span>
              <span class="kb-pause-clock-label">${isPaused ? 'CLOCK PAUSED' : 'PAUSE CLOCK'}</span>
            </div>
            <div class="kb-clock ${isPaused ? 'paused' : ''}" id="kbClock">${clock()}</div>
            <span class="kb-pause-clock-sub">${isPaused ? '▶ Click to resume' : '⏸ Click to pause'}</span>
          </div>
        </div>
      </div>
      <nav class="kb-sections" aria-label="Test sections">
        ${t.sections.map(s => `<button type="button" data-section="${s.id}" aria-pressed="${s.id === q.section}">${esc(s.name)}</button>`).join('')}
      </nav>
      <div class="kb-layout">
        <section class="kb-question" aria-label="Current question">
          <span class="kb-label">QUESTION ${q.number} OF 75 · +1.00 / −0.25</span>
          ${q.passage ? `<div class="kb-passage"><strong>Read the passage for questions 1–3</strong><p>${esc(q.passage)}</p></div>` : ''}
          <h2 class="kb-stem">${esc(q.stem)}</h2>
          <fieldset class="kb-options">
            <legend class="sr-only">Choose one answer</legend>
            ${q.options.map((o, i) => `
              <label class="kb-option">
                <input type="radio" name="kbAnswer" value="${i}" ${active.answers[q.id] === i ? 'checked' : ''} ${isPaused ? 'disabled' : ''}>
                <span><strong>${String.fromCharCode(65 + i)}.</strong> ${esc(o)}</span>
              </label>
            `).join('')}
          </fieldset>
          <div class="kb-actions">
            <button class="btn btn-ghost" id="kbPrev" ${active.index === 0 ? 'disabled' : ''}>Previous</button>
            <button class="btn btn-ghost" id="kbClear" ${isPaused ? 'disabled' : ''}>Clear answer</button>
            <button class="btn btn-ghost" id="kbMark" ${isPaused ? 'disabled' : ''}>${active.marked.includes(q.id) ? 'Unmark review' : 'Mark for review'} & next</button>
            <button class="btn btn-primary" id="kbNext">${active.index === 74 ? 'Save answer' : 'Save & next'}</button>
          </div>
        </section>
        <aside class="kb-sidebar">
          <strong>Question palette</strong>
          <p id="kbCounts"></p>
          <div class="kb-palette">
            ${t.questions.map((x, i) => `
              <button class="kb-pal ${status(x)} ${i === active.index ? 'current' : ''}" data-jump="${i}" aria-label="Question ${x.number}: ${status(x) || 'not visited'}" ${i === active.index ? 'aria-current="true"' : ''}>
                ${x.number}
              </button>
            `).join('')}
          </div>
          <div class="kb-legend">
            <span><i></i>Not visited</span>
            <span class="visited"><i></i>Unanswered</span>
            <span class="answered"><i></i>Answered</span>
            <span class="marked"><i></i>Review</span>
            <span class="marked-answered"><i></i>Answered + review</span>
          </div>
          <p><small>Answers marked for review are included in scoring with −0.25 penalty if wrong.</small></p>
          <div class="kb-actions">
            <button class="btn btn-primary" id="kbSubmit">Submit test</button>
            <button class="btn btn-ghost" id="kbPauseSidebarBtn" style="border:1px solid #b8cbb8;">⏸ Pause Clock</button>
            <button class="btn btn-ghost" id="kbSaveExit">Save & exit</button>
          </div>
          <p><small>${isPaused ? 'Exam clock is paused.' : 'Exiting keeps the timer running unless paused.'}</small></p>
        </aside>
      </div>

      <!-- Pause Break Modal Overlay -->
      ${isPaused ? `
        <div class="cbt-pause-overlay" id="kbPauseOverlay" role="dialog" aria-modal="true" aria-labelledby="kbPauseTitle">
          <div class="cbt-pause-card">
            <div style="font-size:44px; margin-bottom:8px;">☕</div>
            <h2 id="kbPauseTitle">Test Paused — Take a Break!</h2>
            <p>
              Your exam clock is safely paused and all responses are preserved.<br>
              Take a breather, rest your eyes, and resume whenever you're ready.
            </p>
            <div class="cbt-pause-stats-grid">
              <div class="cbt-pause-stat-item">
                <div class="cbt-pause-stat-label">Pause Clock Left</div>
                <div class="cbt-pause-stat-val" style="color:#173c34;">${clock()}</div>
              </div>
              <div class="cbt-pause-stat-item">
                <div class="cbt-pause-stat-label">Answered</div>
                <div class="cbt-pause-stat-val" style="color:#245943;">${answeredCount} / 75</div>
              </div>
              <div class="cbt-pause-stat-item">
                <div class="cbt-pause-stat-label">Marked for Review</div>
                <div class="cbt-pause-stat-val" style="color:#785298;">${active.marked.length}</div>
              </div>
            </div>
            <div style="display:flex; justify-content:center; gap:12px; flex-wrap:wrap;">
              <button type="button" id="kbResumeModalBtn" class="btn btn-primary" style="padding:12px 28px; font-size:15px; font-weight:750;">
                ▶ Resume Test Now
              </button>
              <button type="button" id="kbExitModalBtn" class="btn btn-ghost" style="padding:12px 20px; font-size:14px; border:1px solid #b8cbb8;">
                Save & Exit (Resume Later)
              </button>
            </div>
          </div>
        </div>
      ` : ''}
    `;

    updateCounts();

    document.querySelectorAll('[name="kbAnswer"]').forEach(input => {
      input.onchange = () => {
        if (expire() || (active && active.isPaused)) return;
        active.answers[q.id] = Number(input.value);
        save();
        const p = $(`[data-jump="${active.index}"]`);
        if (p) {
          p.className = `kb-pal ${status(q)} current`;
          p.setAttribute('aria-label', `Question ${q.number}: ${status(q)}`);
        }
        updateCounts();
      };
    });

    document.querySelectorAll('[data-jump]').forEach(b => b.onclick = () => jump(Number(b.dataset.jump)));
    document.querySelectorAll('[data-section]').forEach(b => b.onclick = () => jump(t.questions.findIndex(x => x.section === b.dataset.section)));
    $('#kbPrev').onclick = () => jump(active.index - 1);
    $('#kbNext').onclick = () => jump(Math.min(74, active.index + 1));
    $('#kbClear').onclick = () => {
      if (expire() || (active && active.isPaused)) return;
      delete active.answers[q.id];
      save();
      exam();
    };
    $('#kbMark').onclick = () => {
      if (expire() || (active && active.isPaused)) return;
      active.marked = active.marked.includes(q.id) ? active.marked.filter(id => id !== q.id) : [...active.marked, q.id];
      jump(Math.min(74, active.index + 1));
    };
    $('#kbSaveExit').onclick = () => { save(); home(); };
    $('#kbSubmit').onclick = () => {
      if (expire()) return;
      confirmAction('Submit your test?', `${Object.keys(active.answers).length} answered · ${75 - Object.keys(active.answers).length} unanswered. Answers marked for review will count with −0.25 penalty if incorrect.`, () => finish(false));
    };

    // Pause Clock Event Handlers
    const togglePause = () => {
      if (active.isPaused) unpauseTest();
      else pauseTest();
    };
    $('#kbPauseClockWidget')?.addEventListener('click', togglePause);
    $('#kbPauseClockWidget')?.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        togglePause();
      }
    });
    $('#kbPauseBtn')?.addEventListener('click', pauseTest);
    $('#kbPauseSidebarBtn')?.addEventListener('click', pauseTest);
    $('#kbResumeModalBtn')?.addEventListener('click', unpauseTest);
    $('#kbExitModalBtn')?.addEventListener('click', () => { save(); home(); });
  }

  function updateCounts() {
    if (active && $('#kbCounts')) $('#kbCounts').textContent = `${Object.keys(active.answers).length}/75 answered · ${active.marked.length} marked`;
  }

  function jump(i) {
    if (expire() || (active && active.isPaused)) return;
    active.index = Math.max(0, Math.min(74, i));
    save();
    exam();
    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  function confirmAction(title, text, action) {
    document.querySelector('.kb-dialog')?.remove();
    const dialog = document.createElement('dialog');
    dialog.className = 'kb-dialog';
    dialog.setAttribute('aria-label', title);
    dialog.innerHTML = `<h2>${esc(title)}</h2><p>${esc(text)}</p><div class="kb-actions"><button class="btn btn-primary" id="kbConfirm">Confirm</button><button class="btn btn-ghost" id="kbCancel">Cancel</button></div>`;
    document.body.appendChild(dialog);
    dialog.showModal();
    $('#kbCancel').onclick = () => dialog.remove();
    $('#kbConfirm').onclick = () => { dialog.remove(); action(); };
    dialog.addEventListener('cancel', () => dialog.remove());
  }

  function finish(timedOut) {
    if (!active) return;
    const t = testFor(active.testId);
    const correct = t.questions.filter(q => active.answers[q.id] === q.answerIndex).length;
    const answered = Object.keys(active.answers).length;
    const wrong = answered - correct;
    const penalty = Math.round(wrong * 0.25 * 100) / 100;
    const rawScore = correct - penalty;
    const score = Math.round(rawScore * 100) / 100;

    const r = {
      testId: t.id,
      answers: { ...active.answers },
      startedAt: active.startedAt,
      completedAt: Math.min(Date.now(), active.endAt),
      timedOut,
      correct,
      wrong,
      penalty,
      score
    };

    write(HISTORY, [r, ...history()].slice(0, 500));
    active = null;
    save();
    document.querySelector('.kb-dialog')?.remove();
    result(r);
  }

  function result(r) {
    view = 'result';
    lastResult = r;
    filter = 'all';
    const t = testFor(r.testId);
    const answered = Object.keys(r.answers).length;
    const correct = r.correct !== undefined ? r.correct : t.questions.filter(q => r.answers[q.id] === q.answerIndex).length;
    const wrong = r.wrong !== undefined ? r.wrong : (answered - correct);
    const penalty = r.penalty !== undefined ? r.penalty : Math.round(wrong * 0.25 * 100) / 100;
    const score = r.score !== undefined ? r.score : Math.round((correct - penalty) * 100) / 100;
    const accuracy = answered ? (100 * correct / answered).toFixed(1) : '0.0';

    const testAttempts = history().filter(a => a.testId === t.id);
    const testAttemptIndex = testAttempts.findIndex(a => a === r || (a.startedAt === r.startedAt && a.completedAt === r.completedAt));
    const currentAttemptNum = testAttemptIndex !== -1 ? (testAttempts.length - testAttemptIndex) : (testAttempts.length || 1);
    const nextAttemptNum = testAttempts.length + 1;

    $('#app').innerHTML = `${warning()}<section class="kb-result">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:8px;">
        <span class="kb-label">${r.timedOut ? 'TIME COMPLETE · AUTO-SUBMITTED' : 'TEST COMPLETE'} · ATTEMPT #${currentAttemptNum}</span>
        <span style="font-size:12px; font-weight:750; color:#245943; background:#eef5e9; padding:4px 10px; border-radius:20px; border:1px solid #b8cbb8;">♾️ Unlimited Retakes</span>
      </div>
      <h1>${esc(t.title)}</h1>
      <div class="kb-score">${fmtScore(score)}<small> / 75</small></div>
      <p>
        <strong>${correct}</strong> correct (+${correct}) · 
        <strong>${wrong}</strong> wrong (−${(wrong * 0.25).toFixed(2)}) · 
        <strong>${75 - answered}</strong> unanswered · 
        <strong>${accuracy}%</strong> accuracy
      </p>
      <p>
        Time used: ${Math.min(60, Math.max(0, (r.completedAt - r.startedAt) / 60000)).toFixed(1)} minutes. 
        Marking: +1.00 for correct, −0.25 penalty for wrong answers, 0 for unanswered.
      </p>

      <div class="kb-note" style="border-left:4px solid #245943; background:#eef5e9; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin:18px 0;">
        <div>
          <strong style="color:#173c34; font-size:14.5px;">Attempt #${currentAttemptNum} Recorded · ♾️ Unlimited Retakes Available</strong><br>
          <span style="font-size:13px; color:#526354;">Unlike official exam portals limited to 3 attempts, you can retake this mock as many times as you like.</span>
        </div>
        <button class="btn btn-primary" id="kbRetakeTop" style="padding:10px 18px; font-weight:750;">
          🔄 Retake Mock (Attempt #${nextAttemptNum}) →
        </button>
      </div>

      <div class="kb-table-wrap">
        <table class="kb-table">
          <thead>
            <tr>
              <th>Section</th>
              <th>Correct (+1)</th>
              <th>Wrong (−0.25)</th>
              <th>Unanswered</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            ${t.sections.map(s => {
              const qs = t.questions.filter(q => q.section === s.id);
              const secCorrect = qs.filter(q => r.answers[q.id] === q.answerIndex).length;
              const secDone = qs.filter(q => r.answers[q.id] !== undefined).length;
              const secWrong = secDone - secCorrect;
              const secScore = fmtScore(secCorrect - (secWrong * 0.25));
              return `<tr>
                <td>${esc(s.name)}</td>
                <td>${secCorrect}/${qs.length}</td>
                <td>${secWrong}</td>
                <td>${qs.length - secDone}</td>
                <td><strong>${secScore}</strong></td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>
      <div class="kb-actions">
        <button class="btn btn-primary" id="kbResultHome">Back to library</button>
        <button class="btn btn-ghost" id="kbRetake">🔄 Retake mock (Attempt #${nextAttemptNum})</button>
        <a class="btn btn-ghost" href="${t.pdf}" target="_blank" rel="noopener">Source PDF ↗</a>
      </div>
    </section>
    <div class="kb-heading">
      <h2>Answer review</h2>
      <label class="kb-filter">Show 
        <select id="kbFilter">
          <option value="all">All questions</option>
          <option value="wrong">Wrong answers</option>
          <option value="skipped">Unanswered</option>
          <option value="correct">Correct answers</option>
        </select>
      </label>
    </div>
    <p>Answer keys and brief explanations come from your supplied practice PDF.</p>
    <div id="kbReview"></div>`;

    $('#kbResultHome').onclick = home;
    const triggerRetake = () => instructions(t.id);
    $('#kbRetakeTop')?.addEventListener('click', triggerRetake);
    $('#kbRetake')?.addEventListener('click', triggerRetake);
    $('#kbFilter').onchange = e => { filter = e.target.value; reviews(); };
    reviews();
    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  function reviews() {
    const r = lastResult, t = testFor(r.testId);
    const qs = t.questions.filter(q => filter === 'all' || (filter === 'skipped' ? r.answers[q.id] === undefined : filter === 'correct' ? r.answers[q.id] === q.answerIndex : r.answers[q.id] !== undefined && r.answers[q.id] !== q.answerIndex));
    $('#kbReview').innerHTML = qs.map(q => {
      const a = r.answers[q.id];
      return `<article class="kb-review">
        <span class="kb-label">QUESTION ${q.number} · ${a === undefined ? 'UNANSWERED (0)' : a === q.answerIndex ? 'CORRECT (+1.00)' : 'WRONG (−0.25)'}</span>
        ${q.passage ? `<div class="kb-passage">${esc(q.passage)}</div>` : ''}
        <h3>${esc(q.stem)}</h3>
        <ol type="A">
          ${q.options.map((o, i) => `<li class="${i === q.answerIndex ? 'kb-correct' : i === a ? 'kb-wrong' : ''}">${esc(o)} ${i === q.answerIndex ? '<strong>✓ Correct (+1.00)</strong>' : ''} ${i === a && i !== q.answerIndex ? '<strong>· Your answer (−0.25)</strong>' : i === a ? '<strong>· Your answer</strong>' : ''}</li>`).join('')}
        </ol>
        <p><strong>Explanation:</strong> ${esc(q.explanation)}</p>
        <a class="kb-source" href="${t.pdf}#page=${q.sourcePage}" target="_blank" rel="noopener">Source question · PDF page ${q.sourcePage} ↗</a>
      </article>`;
    }).join('') || '<p class="kb-empty">No questions match this filter.</p>';
  }

  $('#kbHome').onclick = () => { save(); home(); window.scrollTo({ top: 0, behavior: 'instant' }); };

  setInterval(() => {
    if (!active) return;
    if (active.isPaused) {
      if (view === 'home') {
        const c = $('.kb-card-clock-digits');
        if (c) c.textContent = clock();
      }
      return;
    }
    if (Date.now() >= active.endAt) {
      finish(true);
      return;
    }
    syncRemaining();
    if (view === 'exam') {
      if ($('#kbClock')) {
        $('#kbClock').textContent = clock();
        $('#kbClock').classList.toggle('low', active.endAt - Date.now() < 300000);
      }
    } else if (view === 'home') {
      const c = $('.kb-card-clock-digits');
      if (c) c.textContent = clock();
    }
  }, 250);

  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && active && !active.isPaused && Date.now() >= active.endAt) {
      finish(true);
    }
  });

  if (!expire()) home();
})();
