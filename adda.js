(() => {
  'use strict';

  const ACTIVE_KEY = 'rrbpo_adda_active_v1';
  const HISTORY_KEY = 'rrbpo_adda_history_v1';
  const PREF_KEY = 'rrbpo_adda_tab_preference_v1';

  const $ = (sel) => document.querySelector(sel);
  const esc = (str) => String(str ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));

  let catalog = null;
  let testsData = null;
  let active = null;
  let page = 'home'; // 'home' | 'instructions' | 'exam' | 'result'
  let currentTab = 'original'; // 'original' | 'adda'
  let reviewFilter = 'all'; // 'all' | 'wrong' | 'correct' | 'skipped'
  let timerInterval = null;

  // Helpers
  const getCatalog = () => catalog?.papers || [];
  const getAddaTests = () => testsData?.tests || [];
  const getAddaTest = (id) => getAddaTests().find(t => t.id === id);

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
      console.warn('Could not store Adda history', err);
    }
  };

  const storeActive = () => {
    try {
      if (active) localStorage.setItem(ACTIVE_KEY, JSON.stringify(active));
      else localStorage.removeItem(ACTIVE_KEY);
    } catch (err) {
      console.warn('Could not save Adda active state', err);
    }
  };

  function timeText(s) {
    s = Math.max(0, Math.ceil(s));
    return String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
  }

  function getSection() {
    const t = getAddaTest(active.testId);
    return t.sections[active.sectionIndex];
  }

  function getCurrentQuestion() {
    const t = getAddaTest(active.testId);
    return t.questions[active.currentIndex];
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

  function syncDeadline() {
    if (!active) return;
    const now = Date.now();
    if (now < active.sectionEndAt) return;

    if (active.sectionIndex === 0) {
      // Transition from Reasoning (25m) to Quant (20m)
      const firstEnd = active.sectionEndAt;
      active.sectionIndex = 1;
      active.sectionEndAt = firstEnd + 20 * 60 * 1000;
      active.currentIndex = 40;
      const q = getCurrentQuestion();
      if (q && !active.visited.includes(q.id)) active.visited.push(q.id);
      storeActive();
      alert('Section 1 (Reasoning Ability) time is up! The section is now locked.\n\nBeginning Section 2: Quantitative Aptitude (20:00 Minutes).');
    } else {
      // Both sections over -> Auto submit
      alert('Time is up for Section 2 (Quantitative Aptitude)! Your test is submitting now.');
      submitTest(true);
    }
  }

  function tick() {
    if (page !== 'exam' || !active) return;
    syncDeadline();
    if (!active) return;

    const remainingSec = Math.max(0, Math.ceil((active.sectionEndAt - Date.now()) / 1000));
    const timerEl = $('#addaTimerDisplay');
    if (timerEl) {
      timerEl.textContent = timeText(remainingSec);
      if (remainingSec <= 120) {
        timerEl.classList.add('urgent');
      } else {
        timerEl.classList.remove('urgent');
      }
    }
  }

  // --- NAVIGATION & TABS ---

  function setupTabs() {
    const sectionTitle = $('#mockCards');
    if (!sectionTitle) return;

    // Check if tabs already exist
    if ($('#librarySwitchContainer')) return;

    try {
      const savedTab = localStorage.getItem(PREF_KEY);
      if (savedTab === 'adda') currentTab = 'adda';
    } catch {}

    if (window.location.hash.startsWith('#adda-mocks')) {
      currentTab = 'adda';
    }

    const switchHtml = document.createElement('div');
    switchHtml.id = 'librarySwitchContainer';
    switchHtml.className = 'library-switch-container';
    switchHtml.innerHTML = `
      <div class="library-switch" role="tablist" aria-label="Mock Test Categories">
        <button class="library-tab-btn ${currentTab === 'original' ? 'active' : ''}" id="tabOriginal" role="tab" aria-selected="${currentTab === 'original'}" data-tab="original">
          Original Mocks <span class="tab-badge">20</span>
        </button>
        <button class="library-tab-btn ${currentTab === 'adda' ? 'active' : ''}" id="tabAdda" role="tab" aria-selected="${currentTab === 'adda'}" data-tab="adda">
          Adda Mocks <span class="tab-badge">10</span>
        </button>
      </div>
      <div style="font-size: 12.5px; color: var(--text-muted);">
        ${currentTab === 'original' 
          ? '80 Questions · 80 Marks · 45 Minutes per mock'
          : '10 Memory-Based Prelims Papers · English Interactive CBT & Timed Practice'}
      </div>
    `;

    sectionTitle.parentNode.insertBefore(switchHtml, sectionTitle);

    $('#tabOriginal').onclick = () => switchTab('original');
    $('#tabAdda').onclick = () => switchTab('adda');

    // Create container for Adda cards right after existing cards grid
    const cardsGrid = $('.cards-grid');
    if (cardsGrid) {
      const addaGrid = document.createElement('div');
      addaGrid.id = 'addaCardsGrid';
      addaGrid.className = 'cards-grid';
      addaGrid.style.display = currentTab === 'adda' ? 'grid' : 'none';
      cardsGrid.parentNode.insertBefore(addaGrid, cardsGrid.nextSibling);

      // Add banner before adda grid
      const addaBanner = document.createElement('div');
      addaBanner.id = 'addaBanner';
      addaBanner.className = 'adda-banner';
      addaBanner.style.display = currentTab === 'adda' ? 'block' : 'none';
      addaBanner.innerHTML = `
        <strong>Adda Mocks — Memory-Based Practice Papers:</strong> 10 authentic IBPS RRB Officer Scale I prelims memory-based question papers linked from Adda247. Every question has been extracted in clean English, verified with 5 options, correct answer keys, and step-by-step solution analysis. Not an official IBPS release.
      `;
      addaGrid.parentNode.insertBefore(addaBanner, addaGrid);

      // Add Adda ongoing test notice if any
      const addaNotice = document.createElement('div');
      addaNotice.id = 'addaOngoingNotice';
      addaGrid.parentNode.insertBefore(addaNotice, addaBanner);

      renderAddaCards();
      applyTabVisibility();
    }
  }

  function switchTab(tab) {
    currentTab = tab;
    try {
      localStorage.setItem(PREF_KEY, tab);
    } catch {}

    const tabOrig = $('#tabOriginal');
    const tabAd = $('#tabAdda');
    if (tabOrig && tabAd) {
      if (tab === 'original') {
        tabOrig.classList.add('active');
        tabOrig.setAttribute('aria-selected', 'true');
        tabAd.classList.remove('active');
        tabAd.setAttribute('aria-selected', 'false');
      } else {
        tabAd.classList.add('active');
        tabAd.setAttribute('aria-selected', 'true');
        tabOrig.classList.remove('active');
        tabOrig.setAttribute('aria-selected', 'false');
      }
    }
    applyTabVisibility();
  }

  function applyTabVisibility() {
    const origCards = $('.cards-grid:not(#addaCardsGrid)');
    const addaCards = $('#addaCardsGrid');
    const addaBanner = $('#addaBanner');
    const addaNotice = $('#addaOngoingNotice');

    if (origCards) origCards.style.display = currentTab === 'original' ? 'grid' : 'none';
    if (addaCards) addaCards.style.display = currentTab === 'adda' ? 'grid' : 'none';
    if (addaBanner) addaBanner.style.display = currentTab === 'adda' ? 'block' : 'none';
    if (addaNotice) addaNotice.style.display = currentTab === 'adda' ? 'block' : 'none';

    renderAddaOngoingNotice();
  }

  function renderAddaOngoingNotice() {
    const container = $('#addaOngoingNotice');
    if (!container) return;
    if (active && currentTab === 'adda') {
      const t = getAddaTest(active.testId);
      container.innerHTML = `
        <div style="background: #fffbeb; border: 1px solid #fef3c7; border-left: 5px solid #f59e0b; border-radius: 8px; padding: 18px 24px; margin-bottom: 24px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
          <div>
            <strong style="color: #92400e; font-size: 15px;">Ongoing Adda Mock in Progress:</strong>
            <p style="color: #78350f; font-size: 13px; margin-top: 2px;">${esc(t.title)} (${esc(t.paperLabel)}) — Section timer is active.</p>
          </div>
          <button id="resumeAddaActiveBtn" class="btn btn-primary">Resume Test Now →</button>
        </div>
      `;
      const btn = $('#resumeAddaActiveBtn');
      if (btn) btn.onclick = resumeTest;
    } else {
      container.innerHTML = '';
    }
  }

  function renderAddaCards() {
    const grid = $('#addaCardsGrid');
    if (!grid) return;

    const attempts = history();
    const bestScores = {};
    for (const a of attempts) {
      if (bestScores[a.testId] === undefined || a.score > bestScores[a.testId]) {
        bestScores[a.testId] = a.score;
      }
    }

    const papers = getCatalog();
    grid.innerHTML = papers.map(p => {
      const best = bestScores[p.id];
      const test = getAddaTest(p.id);
      const isOngoing = active && active.testId === p.id;

      return `
        <div class="adda-card">
          <div class="adda-card-header">
            <span class="adda-paper-num">${String(p.number).padStart(2, '0')}</span>
            <span class="adda-source-pill">Adda247 PDF</span>
          </div>
          <h3 class="adda-card-title">${esc(p.title)}</h3>
          <p class="adda-card-subtitle">${esc(p.paperLabel)}</p>
          <div class="adda-tag-row">
            <span class="adda-tag">Officer Scale I</span>
            <span class="adda-tag">Prelims</span>
            <span class="adda-tag">Memory-based</span>
            <span class="adda-tag" style="background:#e8f5e9; color:#2e7d32; border-color:#c8e6c9;">English CBT</span>
          </div>
          <div class="adda-spec-list">
            <div>• 40 Reasoning Ability (25 Min)</div>
            <div>• 40 Quantitative Aptitude (20 Min)</div>
            <div>• +1.00 / −0.25 Marking Scheme</div>
            <div>• Full English Questions & Analysis</div>
          </div>
          <div class="adda-card-actions">
            <div style="font-size: 12px; margin-bottom: 4px;">
              ${best !== undefined ? `
                <strong style="color: var(--c-answered);">Best Score: ${best.toFixed(2)} / 80</strong>
              ` : `
                <span style="color: var(--text-muted); font-size: 11px;">Not Attempted Yet</span>
              `}
            </div>
            <div class="adda-btn-row">
              <button class="btn btn-primary" style="flex:1;" data-adda-start="${esc(p.id)}">
                ${isOngoing ? 'Continue Test →' : 'Start Mock Test ↗'}
              </button>
              <button class="btn btn-ghost" style="padding: 8px 10px;" title="Timed PDF Companion Sheet" data-adda-companion="${esc(p.id)}">
                ⏱ Sheet
              </button>
            </div>
            <a href="${esc(p.pdfUrl)}" target="_blank" rel="noopener noreferrer" class="adda-pdf-link">
              <span>View / Download Original PDF ↗</span>
            </a>
          </div>
        </div>
      `;
    }).join('');

    grid.querySelectorAll('[data-adda-start]').forEach(btn => {
      btn.onclick = () => {
        const id = btn.dataset.addaStart;
        if (active && active.testId === id) resumeTest();
        else showInstructions(id, 'cbt');
      };
    });

    grid.querySelectorAll('[data-adda-companion]').forEach(btn => {
      btn.onclick = () => {
        const id = btn.dataset.addaCompanion;
        showInstructions(id, 'companion');
      };
    });
  }

  // --- INSTRUCTIONS ---

  function showInstructions(id, mode = 'cbt') {
    page = 'instructions';
    const t = getAddaTest(id);
    const p = getCatalog().find(p => p.id === id);

    $('#app').innerHTML = `
      <div class="instructions-card" style="max-width: 860px; margin: 30px auto; background: #ffffff; border: 1px solid var(--border); border-radius: 12px; padding: 36px; box-shadow: 0 4px 16px rgba(0,0,0,0.06);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
          <span class="badge-official">Before you begin</span>
          <span class="adda-source-pill">Memory-based paper</span>
        </div>
        <h1 style="font-size: 26px; font-weight: 800; color: var(--primary); margin: 8px 0 6px;">${esc(t.title)}</h1>
        <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 20px;">${esc(t.paperLabel)} · Source PDF hosted by Adda247</p>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 22px; margin-bottom: 24px; font-size: 13.5px; line-height: 1.8;">
          <h3 style="color: var(--primary); font-size: 15px; margin-bottom: 12px;">Exam Pattern & Rules:</h3>
          <ul style="padding-left: 20px;">
            <li><strong>Total Questions:</strong> 80 Objective Multiple Choice Questions in pure English.</li>
            <li><strong>Marking Scheme:</strong> +1.00 for Correct, −0.25 for Incorrect, 0 for Unattempted.</li>
            <li><strong>Strict Sectional Timers:</strong>
              <ul style="margin: 6px 0;">
                <li><strong>Section 1 (Reasoning Ability):</strong> Q1–Q40 (40 Marks), <strong>25:00 Minutes</strong>.</li>
                <li><strong>Section 2 (Quantitative Aptitude):</strong> Q41–Q80 (40 Marks), <strong>20:00 Minutes</strong>.</li>
              </ul>
            </li>
            <li><strong>Section Lock:</strong> When the 25-minute timer expires, Reasoning is locked and Quantitative Aptitude starts immediately. You cannot return to Section 1.</li>
            <li><strong>Question-by-Question Solution Analysis:</strong> Complete step-by-step mathematical and logical solutions will be revealed immediately after submission pointing out which is right and wrong.</li>
            <li><strong>PDF Companion Link:</strong> You can also access the original publisher PDF at any time.</li>
          </ul>
        </div>

        <div style="display: flex; gap: 14px; justify-content: space-between; align-items: center; flex-wrap:wrap;">
          <a href="${esc(t.pdfUrl)}" target="_blank" rel="noopener noreferrer" class="btn btn-ghost" style="padding: 10px 16px;">
            Open Original PDF in New Tab ↗
          </a>
          <div style="display:flex; gap:12px;">
            <button id="addaBackHome" class="btn btn-secondary" style="padding: 10px 20px;">Back to Library</button>
            <button id="addaBeginMock" class="btn btn-primary" style="padding: 10px 24px; font-size: 14px;">I am Ready to Begin</button>
          </div>
        </div>
      </div>
    `;

    $('#addaBeginMock').onclick = () => startTest(id, mode);
    $('#addaBackHome').onclick = enterHome;
  }

  // --- START & RESUME TEST ---

  function startTest(id, mode = 'cbt') {
    if (active && active.testId !== id) {
      if (!confirm('Another Adda mock test is in progress. Discard it and start this new test?')) return;
    }
    const now = Date.now();
    const t = getAddaTest(id);
    active = {
      testId: id,
      mode: mode,
      startedAt: now,
      sectionIndex: 0,
      sectionEndAt: now + 25 * 60 * 1000, // 25 Min for Reasoning
      currentIndex: 0,
      answers: {},
      visited: [t.questions[0].id],
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

  // --- EXAM INTERFACE ---

  function renderExam() {
    page = 'exam';
    if (!active) return enterHome();

    const t = getAddaTest(active.testId);
    const q = getCurrentQuestion();
    const sec = getSection();
    const isAnswered = active.answers[q.id] !== undefined;
    const userChoice = active.answers[q.id];

    // Ensure visited
    if (!active.visited.includes(q.id)) {
      active.visited.push(q.id);
      storeActive();
    }

    const startIdx = active.sectionIndex === 0 ? 0 : 40;
    const endIdx = active.sectionIndex === 0 ? 40 : 80;
    const secQuestions = t.questions.slice(startIdx, endIdx);

    const answeredCount = secQuestions.filter(sq => active.answers[sq.id] !== undefined).length;
    const markedCount = secQuestions.filter(sq => active.marked.includes(sq.id)).length;
    const notVisitedCount = secQuestions.filter(sq => !active.visited.includes(sq.id)).length;
    const notAnsweredCount = secQuestions.length - answeredCount - notVisitedCount;

    $('#app').innerHTML = `
      <div class="exam-wrapper">
        <!-- Section Bar -->
        <div class="section-nav-bar" style="margin-bottom: 16px; background:#ffffff; border:1px solid var(--border); border-radius:12px; padding:12px 18px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
          <div style="display:flex; align-items:center; gap:10px;">
            <div style="font-weight:750; color:var(--primary); font-size:15px;">
              ${esc(t.title)}
            </div>
            <div style="display:flex; gap:6px;">
              <span class="section-tab ${active.sectionIndex === 0 ? 'active' : ''}" style="padding:6px 14px; border-radius:6px; font-size:12px; font-weight:700; ${active.sectionIndex === 0 ? 'background:#edf3e9; color:var(--primary); border:1px solid #9bb490;' : 'background:#f1f5f9; color:#94a3b8;'}">
                1. Reasoning (Q1–Q40) ${active.sectionIndex > 0 ? '🔒' : ''}
              </span>
              <span class="section-tab ${active.sectionIndex === 1 ? 'active' : ''}" style="padding:6px 14px; border-radius:6px; font-size:12px; font-weight:700; ${active.sectionIndex === 1 ? 'background:#edf3e9; color:var(--primary); border:1px solid #9bb490;' : 'background:#f1f5f9; color:#94a3b8;'}">
                2. Quantitative (Q41–Q80)
              </span>
            </div>
          </div>
          <div style="display:flex; align-items:center; gap:16px;">
            <a href="${esc(t.pdfUrl)}" target="_blank" rel="noopener noreferrer" style="font-size:11.5px; color:var(--accent); text-decoration:none; font-weight:600;">
              📄 View PDF ↗
            </a>
            <div class="timer-box normal" style="font-family:monospace; font-size:18px; font-weight:800; padding:6px 14px; border-radius:8px; border:1px solid #cfdbc8; background:#edf3e9; color:var(--primary);">
              ⏱ <span id="addaTimerDisplay">--:--</span>
            </div>
          </div>
        </div>

        <!-- Main Exam Grid -->
        <div class="exam-main-grid" style="display:grid; grid-template-columns: minmax(0,1fr) 280px; gap:20px;">
          <!-- Left: Question Body -->
          <div class="question-container" style="background:#ffffff; border:1px solid var(--border); border-radius:12px; display:flex; flex-direction:column;">
            <div class="question-header" style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
              <div>
                <span class="q-topic" style="font-size:11px; text-transform:uppercase; letter-spacing:0.8px; color:#7c8971; font-weight:700;">
                  ${esc(q.topic || sec.name)}
                </span>
                <h2 style="font-size:16px; font-weight:750; color:var(--primary); margin-top:2px;">
                  Question ${q.number} of 80
                </h2>
              </div>
              <div style="font-size:12px; color:var(--text-muted); font-weight:600;">
                Marks: <strong style="color:var(--c-answered);">+1.00</strong> / <strong style="color:var(--c-not-answered);">-0.25</strong>
              </div>
            </div>

            <div class="question-body" style="padding:24px; flex:1; min-height:360px;">
              <div class="q-stem" style="font-size:14.5px; font-weight:550; line-height:1.8; color:#24382f; margin-bottom:24px; white-space:pre-wrap;">${esc(q.stem)}</div>

              <div class="options-list" style="display:flex; flex-direction:column; gap:10px;">
                ${q.options.map((opt, oIdx) => `
                  <button class="option-item ${userChoice === oIdx ? 'selected' : ''}" data-opt="${oIdx}" style="text-align:left; padding:12px 16px; border:1px solid ${userChoice === oIdx ? '#67905d' : 'var(--border)'}; background:${userChoice === oIdx ? '#edf3e8' : '#ffffff'}; border-radius:8px; cursor:pointer; font-size:13.5px; display:flex; align-items:center; gap:12px; font-family:inherit;">
                    <span style="font-weight:750; font-size:12px; color:var(--primary); width:20px;">(${'ABCDE'[oIdx]})</span>
                    <span style="flex:1;">${esc(opt)}</span>
                  </button>
                `).join('')}
              </div>
            </div>

            <!-- Footer Controls -->
            <div class="exam-footer" style="padding:16px 20px; border-top:1px solid var(--border); background:#fcfdfb; border-bottom-left-radius:12px; border-bottom-right-radius:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
              <div style="display:flex; gap:8px;">
                <button id="addaMarkNext" class="btn btn-secondary" style="font-size:12px;">Mark for Review & Next</button>
                <button id="addaClear" class="btn btn-ghost" style="font-size:12px;">Clear Response</button>
              </div>
              <div style="display:flex; gap:8px;">
                <button id="addaPrev" class="btn btn-secondary" style="font-size:12px;" ${active.currentIndex === startIdx ? 'disabled' : ''}>Previous</button>
                <button id="addaSaveNext" class="btn btn-primary" style="font-size:12px;">Save & Next →</button>
                <button id="addaSubmitBtn" class="btn btn-primary" style="background:#2e7d32; border-color:#2e7d32; font-size:12px;">Submit Test</button>
              </div>
            </div>
          </div>

          <!-- Right: Question Palette -->
          <div class="palette-sidebar" style="background:#ffffff; border:1px solid var(--border); border-radius:12px; display:flex; flex-direction:column;">
            <div style="padding:14px; background:#edf2e8; border-bottom:1px solid var(--border); font-size:12px; font-weight:700; color:var(--primary);">
              Question Palette · ${sec.name}
            </div>

            <div style="padding:12px; display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:10px; border-bottom:1px solid var(--border);">
              <div style="display:flex; align-items:center; gap:6px;"><span class="legend-color-dot answered" style="width:14px; height:14px; border-radius:3px; background:#2e7d32; display:inline-block;"></span> Answered (${answeredCount})</div>
              <div style="display:flex; align-items:center; gap:6px;"><span class="legend-color-dot not-answered" style="width:14px; height:14px; border-radius:3px; background:#c62828; display:inline-block;"></span> Not Answered (${notAnsweredCount})</div>
              <div style="display:flex; align-items:center; gap:6px;"><span class="legend-color-dot marked" style="width:14px; height:14px; border-radius:3px; background:#6a1b9a; display:inline-block;"></span> Marked (${markedCount})</div>
              <div style="display:flex; align-items:center; gap:6px;"><span class="legend-color-dot not-visited" style="width:14px; height:14px; border-radius:3px; background:#94a3b8; display:inline-block;"></span> Not Visited (${notVisitedCount})</div>
            </div>

            <div style="padding:14px; flex:1; max-height:480px; overflow-y:auto;">
              <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:6px;">
                ${secQuestions.map(sq => {
                  const st = statusFor(sq.id);
                  const isCurrent = sq.number === q.number;
                  return `
                    <button class="pal-btn ${st} ${isCurrent ? 'current' : ''}" data-adda-jump="${sq.number - 1}" style="width:100%; height:34px; font-size:11px; border-radius:6px; font-weight:700; cursor:pointer; ${isCurrent ? 'outline:2px solid var(--primary); outline-offset:1px;' : ''}">
                      ${sq.number}
                    </button>
                  `;
                }).join('')}
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    // Bind option click
    $('#app').querySelectorAll('[data-opt]').forEach(btn => {
      btn.onclick = () => {
        const optIdx = Number(btn.dataset.opt);
        active.answers[q.id] = optIdx;
        storeActive();
        renderExam();
      };
    });

    // Save & Next
    $('#addaSaveNext').onclick = () => {
      goTo(active.currentIndex + 1);
    };

    // Mark & Next
    $('#addaMarkNext').onclick = () => {
      if (!active.marked.includes(q.id)) active.marked.push(q.id);
      goTo(active.currentIndex + 1);
    };

    // Clear Response
    $('#addaClear').onclick = () => {
      delete active.answers[q.id];
      const mIdx = active.marked.indexOf(q.id);
      if (mIdx !== -1) active.marked.splice(mIdx, 1);
      storeActive();
      renderExam();
    };

    // Previous
    $('#addaPrev').onclick = () => {
      if (active.currentIndex > startIdx) {
        goTo(active.currentIndex - 1);
      }
    };

    // Jump buttons
    $('#app').querySelectorAll('[data-adda-jump]').forEach(btn => {
      btn.onclick = () => {
        goTo(Number(btn.dataset.addaJump));
      };
    });

    // Submit button
    $('#addaSubmitBtn').onclick = () => {
      const totalAnswered = Object.keys(active.answers).length;
      if (confirm(`You have answered ${totalAnswered} of 80 questions.\n\nAre you sure you want to submit your test and view solutions?`)) {
        submitTest(false);
      }
    };

    tick();
  }

  function goTo(idx) {
    if (!active) return;
    const startIdx = active.sectionIndex === 0 ? 0 : 40;
    const endIdx = active.sectionIndex === 0 ? 40 : 80;

    if (idx < startIdx || idx >= endIdx) return;
    active.currentIndex = idx;
    const q = getCurrentQuestion();
    if (q && !active.visited.includes(q.id)) active.visited.push(q.id);
    storeActive();
    renderExam();
  }

  // --- SUBMIT & ANALYSIS ---

  function submitTest(auto = false) {
    if (!active) return;
    const t = getAddaTest(active.testId);
    const answers = active.answers;
    let correctCount = 0, wrongCount = 0, skippedCount = 0;
    let reasoningScore = 0, quantScore = 0;

    const details = t.questions.map(q => {
      const userChoice = answers[q.id];
      const isCorrect = userChoice === q.answerIndex;
      const isAttempted = userChoice !== undefined;
      let marks = 0;

      if (!isAttempted) {
        skippedCount++;
      } else if (isCorrect) {
        correctCount++;
        marks = 1.0;
        if (q.section === 'reasoning') reasoningScore += 1.0;
        else quantScore += 1.0;
      } else {
        wrongCount++;
        marks = -0.25;
        if (q.section === 'reasoning') reasoningScore -= 0.25;
        else quantScore -= 0.25;
      }

      return {
        questionId: q.id,
        number: q.number,
        section: q.section,
        topic: q.topic,
        userChoice: userChoice,
        correctIndex: q.answerIndex,
        isCorrect: isCorrect,
        isAttempted: isAttempted,
        marks: marks
      };
    });

    const totalScore = Math.max(0, correctCount * 1.0 - wrongCount * 0.25);
    const accuracy = (correctCount + wrongCount) > 0 ? (correctCount / (correctCount + wrongCount) * 100) : 0;

    const attemptRecord = {
      attemptId: 'adda_att_' + Date.now(),
      testId: t.id,
      title: t.title,
      paperLabel: t.paperLabel,
      score: totalScore,
      correctCount: correctCount,
      wrongCount: wrongCount,
      skippedCount: skippedCount,
      reasoningScore: Math.max(0, reasoningScore),
      quantScore: Math.max(0, quantScore),
      accuracy: accuracy,
      completedAt: Date.now(),
      answers: answers
    };

    const hist = history();
    hist.unshift(attemptRecord);
    storeHistory(hist);

    // Clear active
    active = null;
    storeActive();

    // Show result dashboard
    showResult(attemptRecord);
  }

  function showResult(attempt) {
    page = 'result';
    const t = getAddaTest(attempt.testId);

    const questionsWithStatus = t.questions.map(q => {
      const userChoice = attempt.answers[q.id];
      const isCorrect = userChoice === q.answerIndex;
      const isAttempted = userChoice !== undefined;
      return {
        ...q,
        userChoice,
        isCorrect,
        isAttempted
      };
    });

    function renderResultContent() {
      const filtered = questionsWithStatus.filter(q => {
        if (reviewFilter === 'wrong') return q.isAttempted && !q.isCorrect;
        if (reviewFilter === 'correct') return q.isAttempted && q.isCorrect;
        if (reviewFilter === 'skipped') return !q.isAttempted;
        return true;
      });

      $('#app').innerHTML = `
        <div class="result-dashboard" style="max-width: 1100px; margin: 20px auto;">
          <!-- Score Hero Banner -->
          <div class="score-hero-card" style="background: var(--primary); color: #ffffff; border-radius: 14px; padding: 36px 40px; margin-bottom: 28px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:24px;">
            <div>
              <span style="font-size: 11px; letter-spacing: 2px; text-transform:uppercase; color: #a6bda4; font-weight:750;">Performance Summary · Officer Scale I</span>
              <h1 style="font-size: 28px; font-weight: 800; margin: 6px 0 10px;">${esc(attempt.title)}</h1>
              <p style="color: #cbd5e1; font-size: 13.5px;">${esc(attempt.paperLabel)} · Completed on ${esc(new Date(attempt.completedAt).toLocaleString())}</p>
            </div>
            <div style="text-align:right;">
              <div style="font-size: 12px; color: #94a3b8; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Your Total Score</div>
              <div class="hero-score-value" style="font-size: 56px; font-weight: 800; line-height:1; color: #ffffff;">
                ${attempt.score.toFixed(2)} <span style="font-size: 20px; color: #94a3b8; font-weight: 500;">/ 80.00</span>
              </div>
              <div style="font-size: 13px; color: #a6bda4; margin-top: 6px;">
                Accuracy: <strong>${attempt.accuracy.toFixed(1)}%</strong>
              </div>
            </div>
          </div>

          <!-- Section Summary Cards -->
          <div class="stats-grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 28px;">
            <div class="stat-card">
              <span class="stat-number" style="color: var(--c-answered);">✓</span>
              <div>
                <strong style="color: var(--c-answered);">${attempt.correctCount}</strong>
                <span>Correct Questions (+1.00 each)</span>
              </div>
            </div>
            <div class="stat-card">
              <span class="stat-number" style="color: var(--c-not-answered);">✗</span>
              <div>
                <strong style="color: var(--c-not-answered);">${attempt.wrongCount}</strong>
                <span>Incorrect Questions (−0.25 penalty)</span>
              </div>
            </div>
            <div class="stat-card">
              <span class="stat-number" style="color: var(--text-muted);">○</span>
              <div>
                <strong>${attempt.skippedCount}</strong>
                <span>Unattempted (0 marks)</span>
              </div>
            </div>
            <div class="stat-card">
              <span class="stat-number" style="color: var(--accent);">📊</span>
              <div>
                <strong>${attempt.reasoningScore.toFixed(2)} | ${attempt.quantScore.toFixed(2)}</strong>
                <span>Reasoning | Quant Sectional</span>
              </div>
            </div>
          </div>

          <!-- Filter & Actions Bar -->
          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom: 20px;">
            <div>
              <h2 style="font-size: 20px; font-weight: 800; color: var(--primary);">Question-by-Question Detailed Solutions</h2>
              <p style="font-size: 13px; color: var(--text-muted);">Step-by-step mathematical and logical analysis pointing out which is right and wrong.</p>
            </div>
            <div style="display:flex; gap:10px;">
              <button id="addaRetakeBtn" class="btn btn-secondary">Retake Test</button>
              <button id="addaReturnHomeBtn" class="btn btn-primary">Mock Library ↗</button>
            </div>
          </div>

          <!-- Filter Buttons -->
          <div class="review-filter-bar">
            <button class="review-filter-btn ${reviewFilter === 'all' ? 'active' : ''}" data-rf="all">
              All Questions (80)
            </button>
            <button class="review-filter-btn ${reviewFilter === 'wrong' ? 'active' : ''}" data-rf="wrong">
              Incorrect Only (${attempt.wrongCount})
            </button>
            <button class="review-filter-btn ${reviewFilter === 'correct' ? 'active' : ''}" data-rf="correct">
              Correct Only (${attempt.correctCount})
            </button>
            <button class="review-filter-btn ${reviewFilter === 'skipped' ? 'active' : ''}" data-rf="skipped">
              Unattempted (${attempt.skippedCount})
            </button>
          </div>

          <!-- Questions List -->
          <div style="display:flex; flex-direction:column; gap:18px;">
            ${filtered.length === 0 ? `
              <div style="padding: 30px; text-align:center; background:#ffffff; border-radius:10px; border:1px solid var(--border); color:var(--text-muted);">
                No questions found under this filter.
              </div>
            ` : ''}

            ${filtered.map(q => {
              const isCorrect = q.isCorrect;
              const isAttempted = q.isAttempted;
              const userChoice = q.userChoice;

              let statusTag = '';
              if (!isAttempted) {
                statusTag = `<span class="sol-status-tag skipped">Unattempted · 0.00</span>`;
              } else if (isCorrect) {
                statusTag = `<span class="sol-status-tag correct">✓ Correct · +1.00</span>`;
              } else {
                statusTag = `<span class="sol-status-tag wrong">✗ Incorrect · −0.25</span>`;
              }

              return `
                <div class="solution-card" style="background:#ffffff; border:1px solid ${!isAttempted ? 'var(--border)' : isCorrect ? '#c8e6c9' : '#ffcdd2'}; border-left: 5px solid ${!isAttempted ? '#94a3b8' : isCorrect ? 'var(--c-answered)' : 'var(--c-not-answered)'}; border-radius:10px; padding:24px;">
                  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <div style="font-size:12px; font-weight:700; color:var(--text-muted);">
                      Question ${q.number} of 80 · <span style="text-transform:uppercase; color:var(--primary);">${esc(q.topic || q.section)}</span>
                    </div>
                    <div>${statusTag}</div>
                  </div>

                  <div style="font-size:14.5px; font-weight:550; line-height:1.8; color:#24382f; margin-bottom:18px; white-space:pre-wrap;">${esc(q.stem)}</div>

                  <div style="display:flex; flex-direction:column; gap:8px; margin-bottom:16px;">
                    ${q.options.map((opt, oIdx) => {
                      const isUser = userChoice === oIdx;
                      const isAns = q.answerIndex === oIdx;
                      let rowBg = '#ffffff';
                      let rowBorder = 'var(--border)';
                      let tag = '';

                      if (isAns) {
                        rowBg = '#e8f5e9';
                        rowBorder = '#81c784';
                        tag = '<span style="font-size:11px; font-weight:750; color:#2e7d32; margin-left:auto;">[CORRECT ANSWER]</span>';
                      } else if (isUser && !isAns) {
                        rowBg = '#ffebee';
                        rowBorder = '#e57373';
                        tag = '<span style="font-size:11px; font-weight:750; color:#c62828; margin-left:auto;">[YOUR WRONG CHOICE]</span>';
                      }

                      return `
                        <div style="padding:10px 14px; border:1px solid ${rowBorder}; background:${rowBg}; border-radius:6px; font-size:13px; display:flex; align-items:center; gap:10px;">
                          <strong style="color:var(--primary); width:24px;">(${'ABCDE'[oIdx]})</strong>
                          <span style="flex:1;">${esc(opt)}</span>
                          ${tag}
                        </div>
                      `;
                    }).join('')}
                  </div>

                  <div class="expl-box" style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:16px; font-size:13.5px; line-height:1.8;">
                    <strong style="color:var(--primary); display:block; margin-bottom:6px;">Step-by-Step Analysis & Solution:</strong>
                    <div style="white-space:pre-wrap; color:#334155;">${esc(q.explanation)}</div>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      `;

      // Bind filter buttons
      $('#app').querySelectorAll('[data-rf]').forEach(btn => {
        btn.onclick = () => {
          reviewFilter = btn.dataset.rf;
          renderResultContent();
        };
      });

      $('#addaRetakeBtn').onclick = () => {
        if (confirm('Retake this mock test now?')) {
          startTest(attempt.testId, 'cbt');
        }
      };

      $('#addaReturnHomeBtn').onclick = enterHome;
    }

    renderResultContent();
  }

  function enterHome() {
    page = 'home';
    if (window.renderOriginalHome) {
      window.renderOriginalHome();
    } else {
      window.location.reload();
    }
    setTimeout(setupTabs, 50);
  }

  // --- INITIALIZATION ---

  function initAdda() {
    if (window.__ADDA_MOCKS_CATALOG__) {
      catalog = window.__ADDA_MOCKS_CATALOG__;
    }
    if (window.__ADDA_TESTS_DATA__) {
      testsData = window.__ADDA_TESTS_DATA__;
    }

    try {
      active = JSON.parse(localStorage.getItem(ACTIVE_KEY) || 'null');
    } catch {
      active = null;
    }

    if (active && !getAddaTest(active.testId)) active = null;
    if (active) syncDeadline();

    setInterval(tick, 1000);

    // Watch for DOM changes to inject tabs
    const checkTimer = setInterval(() => {
      if ($('#mockCards') && !$('#librarySwitchContainer')) {
        setupTabs();
      }
    }, 150);

    // Expose API for app.js or tests
    window.AddaPortal = {
      getCatalog,
      getAddaTests,
      getAddaTest,
      switchTab,
      showInstructions,
      startTest,
      resumeTest,
      history
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAdda);
  } else {
    initAdda();
  }
})();
