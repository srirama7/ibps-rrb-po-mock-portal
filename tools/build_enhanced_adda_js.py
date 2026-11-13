# Script to generate the enhanced adda.js with exact getters and keys
import os

content = r'''/**
 * IBPS RRB PO Prelims Mock Portal - Adda247 Mocks Integration Module
 * Full English CBT Simulation, Free Section Switching, Pause & Break Support,
 * Continue / Complete Remaining Quant Questions, and Step-by-Step Analysis.
 */

(() => {
  'use strict';

  const ACTIVE_KEY = 'rrbpo_adda_active_v1';
  const HISTORY_KEY = 'rrbpo_adda_history_v1';
  const PREF_KEY = 'rrbpo_adda_tab_preference_v1';

  let page = 'home'; // 'home' | 'instructions' | 'exam' | 'result'
  let currentTab = 'original'; // 'original' | 'adda'
  let catalog = null;
  let testsData = null;
  let active = null;
  let reviewFilter = 'all'; // 'all' | 'wrong' | 'correct' | 'skipped'

  // --- HELPERS ---

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  const esc = (str) => String(str ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));

  const getCatalog = () => catalog?.papers || window.__ADDA_MOCKS_CATALOG__?.papers || [];
  const getAddaTests = () => testsData?.tests || window.__ADDA_TESTS_DATA__?.tests || [];
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

  function formatMathText(raw) {
    if (!raw) return '';
    let text = esc(raw);

    // Render markdown tables if present
    if (text.includes('|') && text.includes('---')) {
      const lines = text.split('\n');
      const tableLines = [];
      const before = [];
      const after = [];
      let inTable = false;
      let finishedTable = false;

      for (const line of lines) {
        if (!finishedTable && (line.trim().startsWith('|') || (line.includes('|') && (line.includes('---') || inTable)))) {
          inTable = true;
          tableLines.push(line.trim());
        } else if (inTable) {
          finishedTable = true;
          inTable = false;
          after.push(line);
        } else {
          before.push(line);
        }
      }

      if (tableLines.length >= 2) {
        let headers = [];
        let rows = [];
        for (let i = 0; i < tableLines.length; i++) {
          const parts = tableLines[i].split('|').map(s => s.trim()).filter(Boolean);
          if (i === 0) headers = parts;
          else if (tableLines[i].includes('---')) continue;
          else rows.push(parts);
        }

        const tableHtml = `
          <div class="cbt-table-box">
            <table class="cbt-rendered-table">
              <thead>
                <tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>
              </thead>
              <tbody>
                ${rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}
              </tbody>
            </table>
          </div>
        `;
        text = before.join('\n') + '\n' + tableHtml + '\n' + after.join('\n');
      }
    }

    // Format mathematical fractions: (a/b), a/b, 33 1/3, 3/8th
    text = text.replace(/(\()?(\d+(?:\.\d+)?|\?)\s*\/\s*(\d+(?:\.\d+)?|\?)(\))?(th|st|nd|rd)?(?!\w)/gi, (match, openParen, num, den, closeParen, ord) => {
      const ordHtml = ord ? `<sup>${ord}</sup>` : '';
      return `<span class="cbt-frac"><span class="cbt-num">${num}</span><span class="cbt-den">${den}</span></span>${ordHtml}`;
    });

    // Format powers: ² -> <sup>2</sup>, ³ -> <sup>3</sup>
    text = text.replace(/²/g, '<sup>2</sup>').replace(/³/g, '<sup>3</sup>');

    // Format square roots: √X or ∛X
    text = text.replace(/√([0-9\.\?]+)/g, '<span style="font-family:serif;">√<span style="border-top:1.5px solid currentColor; padding-top:1px;">$1</span></span>');
    text = text.replace(/∛([0-9\.\?]+)/g, '<span style="font-family:serif;">∛<span style="border-top:1.5px solid currentColor; padding-top:1px;">$1</span></span>');

    return text;
  }

  function renderQuestionStemWithDiagrams(q) {
    let html = `<div class="q-stem" style="font-size:14.5px; font-weight:550; line-height:1.8; color:#24382f; margin-bottom:20px; white-space:pre-wrap;">${formatMathText(q.stem)}</div>`;

    if (q.diagrams && q.diagrams.length > 0) {
      html += `
        <div class="cbt-diagram-box">
          <div style="font-size:11.5px; text-transform:uppercase; letter-spacing:1px; color:#4b6353; font-weight:800; margin-bottom:12px;">
            📊 ${esc(q.diagramCaption || 'Reference Data Chart / Diagram')}
          </div>
          <div style="display:flex; justify-content:center; gap:16px; flex-wrap:wrap; align-items:center;">
            ${q.diagrams.map(src => `
              <div style="max-width:100%;">
                <img src="${esc(src)}" class="cbt-diagram-img" alt="Diagram for Question ${q.number}" onclick="window.open('${esc(src)}', '_blank')" title="Click to view full image in a new tab">
              </div>
            `).join('')}
          </div>
          <div class="cbt-diagram-caption">🔍 Click image to enlarge in high resolution ↗</div>
        </div>
      `;
    }
    return html;
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

  // --- TIMER & PAUSE SUPPORT ---

  function syncDeadline() {
    if (!active) return;
    if (active.isPaused) return;
    const now = Date.now();
    if (now >= active.testEndAt) {
      alert('Time is up for your examination! Your mock test is now submitting.');
      submitTest(true);
    }
  }

  function tick() {
    if (page !== 'exam' || !active) return;
    if (active.isPaused) return;
    syncDeadline();
    if (!active) return;

    const remainingSec = Math.max(0, Math.ceil((active.testEndAt - Date.now()) / 1000));
    active.timeRemainingSec = remainingSec;
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

  function pauseTest() {
    if (!active || active.isPaused) return;
    const remainingSec = Math.max(0, Math.ceil((active.testEndAt - Date.now()) / 1000));
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

    // Add hero button if present
    const heroActions = $('.hero-actions');
    if (heroActions && !$('#heroAddaBtn')) {
      const addaBtn = document.createElement('a');
      addaBtn.id = 'heroAddaBtn';
      addaBtn.className = 'btn btn-primary';
      addaBtn.href = '#adda-mocks';
      addaBtn.style.background = '#285747';
      addaBtn.style.borderColor = '#285747';
      addaBtn.innerHTML = 'Adda Mocks (10) <span style="background:#cfe68c; color:#173c34; font-size:9px; font-weight:800; padding:2px 6px; border-radius:4px; margin-left:6px;">NEW</span> <span>↗</span>';
      addaBtn.onclick = (e) => {
        e.preventDefault();
        switchTab('adda');
        $('#mockCards')?.scrollIntoView({ behavior: 'smooth' });
      };
      heroActions.appendChild(addaBtn);
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
          Adda Mocks <span class="tab-badge" style="background:#cfe68c; color:#173c34;">10 NEW</span>
        </button>
      </div>
      <div style="font-size: 12.5px; color: var(--text-muted);">
        ${currentTab === 'original' 
          ? '80 Questions · 80 Marks · 45 Minutes per mock'
          : '10 Memory-Based Prelims Papers · English Interactive CBT & Free Section Switching'}
      </div>
    `;

    sectionTitle.parentNode.insertBefore(switchHtml, sectionTitle);

    // Insert Adda Cards Grid Container after original mock grid
    const origCards = $('#mockCards');
    if (origCards && !$('#addaCardsGrid')) {
      const addaContainer = document.createElement('div');
      addaContainer.id = 'addaCardsContainer';
      addaContainer.style.display = currentTab === 'adda' ? 'block' : 'none';
      addaContainer.innerHTML = `
        <div id="addaOngoingNotice"></div>
        <div class="adda-banner">
          <strong>Adda247 Memory-Based Papers:</strong> 10 actual Prelims papers faithfully digitized into 
          interactive online CBT format. Features pure English questions, full 45-minute composite timer with free 
          switching between Reasoning and Quantitative Aptitude, step-by-step mathematical solutions, and pause/resume support.
        </div>
        <div id="addaCardsGrid" class="adda-cards-grid"></div>
      `;
      origCards.parentNode.insertBefore(addaContainer, origCards.nextSibling);
    }

    // Bind switch buttons
    $('#tabOriginal').onclick = () => switchTab('original');
    $('#tabAdda').onclick = () => switchTab('adda');

    applyTabVisibility();
    renderAddaCards();
  }

  function switchTab(tab) {
    currentTab = tab;
    try {
      localStorage.setItem(PREF_KEY, tab);
    } catch {}

    const tabOrig = $('#tabOriginal');
    const tabAdda = $('#tabAdda');
    if (tabOrig && tabAdda) {
      if (tab === 'original') {
        tabOrig.classList.add('active');
        tabOrig.setAttribute('aria-selected', 'true');
        tabAdda.classList.remove('active');
        tabAdda.setAttribute('aria-selected', 'false');
      } else {
        tabAdda.classList.add('active');
        tabAdda.setAttribute('aria-selected', 'true');
        tabOrig.classList.remove('active');
        tabOrig.setAttribute('aria-selected', 'false');
      }
    }

    applyTabVisibility();

    if (tab === 'adda') {
      window.history.replaceState(null, '', '#adda-mocks');
      renderAddaCards();
    } else {
      window.history.replaceState(null, '', '#original-mocks');
    }
  }

  function applyTabVisibility() {
    const origCards = $('#mockCards');
    const addaContainer = $('#addaCardsContainer');
    const addaNotice = $('#addaOngoingNotice');

    if (origCards) origCards.style.display = currentTab === 'original' ? 'grid' : 'none';
    if (addaContainer) addaContainer.style.display = currentTab === 'adda' ? 'block' : 'none';
    if (addaNotice) addaNotice.style.display = currentTab === 'adda' ? 'block' : 'none';

    renderAddaOngoingNotice();
  }

  function renderAddaOngoingNotice() {
    const container = $('#addaOngoingNotice');
    if (!container) return;
    if (active && currentTab === 'adda') {
      const t = getAddaTest(active.testId);
      if (!t) return;
      const isP = active.isPaused;
      const remSec = active.timeRemainingSec || Math.max(0, Math.ceil(((active.testEndAt || Date.now()) - Date.now()) / 1000));

      container.innerHTML = `
        <div style="background: #fffbeb; border: 1px solid #fef3c7; border-left: 5px solid #f59e0b; border-radius: 10px; padding: 18px 24px; margin-bottom: 24px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px;">
          <div>
            <strong style="color: #92400e; font-size: 15px;">
              ${isP ? '☕ Paused Adda Mock in Progress:' : '⏱ Ongoing Adda Mock in Progress:'}
            </strong>
            <p style="color: #78350f; font-size: 13.5px; margin-top: 3px;">
              ${esc(t.title)} (${esc(t.paperLabel)}) — Time Remaining: <strong>${timeText(remSec)}</strong>.
            </p>
          </div>
          <div style="display:flex; gap:10px;">
            <button id="resumeAddaActiveBtn" class="btn btn-primary" style="padding:10px 20px; font-weight:750;">
              ${isP ? '▶ Resume Test Now' : 'Continue Test →'}
            </button>
            <button id="discardAddaActiveBtn" class="btn btn-ghost" style="color:#b45309; padding:10px 14px;">
              Discard
            </button>
          </div>
        </div>
      `;
      const btn = $('#resumeAddaActiveBtn');
      if (btn) btn.onclick = resumeTest;

      const discardBtn = $('#discardAddaActiveBtn');
      if (discardBtn) {
        discardBtn.onclick = () => {
          if (confirm('Are you sure you want to discard this unfinished mock attempt?')) {
            active = null;
            storeActive();
            renderAddaOngoingNotice();
            renderAddaCards();
          }
        };
      }
    } else {
      container.innerHTML = '';
    }
  }

  function renderAddaCards() {
    const grid = $('#addaCardsGrid');
    if (!grid) return;

    const attempts = history();
    const bestScores = {};
    const latestAttempts = {};
    for (const a of attempts) {
      if (bestScores[a.testId] === undefined || a.score > bestScores[a.testId]) {
        bestScores[a.testId] = a.score;
      }
      if (!latestAttempts[a.testId] || a.completedAt > latestAttempts[a.testId].completedAt) {
        latestAttempts[a.testId] = a;
      }
    }

    const papers = getCatalog();
    grid.innerHTML = papers.map(p => {
      const best = bestScores[p.id];
      const isOngoing = active && active.testId === p.id;
      const lastAtt = latestAttempts[p.id];
      const hasUnfinished = lastAtt && lastAtt.skippedCount > 0;

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
            <div>• 40 Reasoning Ability (Q1–Q40)</div>
            <div>• 40 Quantitative Aptitude (Q41–Q80)</div>
            <div>• 45:00 Composite Time · Free Switching</div>
            <div>• Step-by-Step Mathematical Solutions</div>
          </div>
          <div class="adda-card-actions">
            <div style="font-size: 12px; margin-bottom: 6px; display:flex; justify-content:space-between; align-items:center;">
              ${best !== undefined ? `
                <strong style="color: var(--c-answered);">Best: ${best.toFixed(2)} / 80</strong>
              ` : `
                <span style="color: var(--text-muted); font-size: 11px;">Not Attempted Yet</span>
              `}
              ${hasUnfinished && !isOngoing ? `
                <span style="font-size:11px; color:#d97706; font-weight:700;">${lastAtt.skippedCount} Skipped</span>
              ` : ''}
            </div>
            <div class="adda-btn-row" style="display:flex; gap:6px; flex-wrap:wrap;">
              <button class="btn btn-primary" style="flex:1;" data-adda-start="${esc(p.id)}">
                ${isOngoing ? (active.isPaused ? '▶ Resume Paused Test' : 'Continue Test →') : (best !== undefined ? 'Retake Test ↗' : 'Take Online Test (80 Qs) ↗')}
              </button>
              ${hasUnfinished && !isOngoing ? `
                <button class="btn btn-secondary" style="padding:8px 12px; font-size:11.5px; font-weight:750; background:#fef3c7; color:#92400e; border-color:#fde68a;" title="Complete Remaining Unattempted Questions" data-adda-continue-history="${esc(p.id)}">
                  ▶ Complete Quant
                </button>
              ` : ''}
              <button class="btn btn-ghost" style="padding: 8px 10px;" title="Timed Answer Sheet Companion" data-adda-companion="${esc(p.id)}">
                ⏱ Sheet
              </button>
            </div>
            <a href="${esc(p.pdfUrl)}" target="_blank" rel="noopener noreferrer" class="adda-pdf-link">
              <span>📄 View / Download Original PDF ↗</span>
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

    grid.querySelectorAll('[data-adda-continue-history]').forEach(btn => {
      btn.onclick = () => {
        const id = btn.dataset.addaContinueHistory;
        const lastAtt = latestAttempts[id];
        if (lastAtt) continueAttempt(lastAtt);
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
    if (!t) return enterHome();

    $('#app').innerHTML = `
      <div class="instructions-card" style="max-width: 860px; margin: 30px auto; background: #ffffff; border: 1px solid var(--border); border-radius: 12px; padding: 36px; box-shadow: 0 4px 16px rgba(0,0,0,0.06);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
          <span class="badge-official">Before you begin</span>
          <span class="adda-source-pill">Memory-based paper</span>
        </div>
        <h1 style="font-size: 26px; font-weight: 800; color: var(--primary); margin: 8px 0 6px;">${esc(t.title)}</h1>
        <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 20px;">${esc(t.paperLabel)} · Official Paper digitized in pure English</p>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 22px; margin-bottom: 24px; font-size: 13.5px; line-height: 1.8;">
          <h3 style="color: var(--primary); font-size: 15px; margin-bottom: 12px;">Exam Pattern & Operating Scheme:</h3>
          <ul style="padding-left: 20px;">
            <li><strong>Total Questions:</strong> 80 Objective Multiple Choice Questions in pure English.</li>
            <li><strong>Marking Scheme:</strong> +1.00 for Correct, −0.25 for Incorrect, 0 for Unattempted.</li>
            <li><strong>Composite 45:00 Minutes Timing:</strong> 
              Total composite duration of 45:00 minutes for the entire examination (standard IBPS RRB PO Prelims scheme).
            </li>
            <li><strong>Free Section Switching:</strong> 
              You can switch freely between <strong>Section 1 (Reasoning Ability, Q1–Q40)</strong> and <strong>Section 2 (Quantitative Aptitude, Q41–Q80)</strong> at any point during the mock test.
            </li>
            <li><strong>Pause & Take a Break:</strong> 
              Taking a short break? Click <strong>"⏸ Pause / Take Break"</strong> in the exam toolbar at any time to freeze the timer safely. Your answers and progress remain 100% saved.
            </li>
            <li><strong>Continue & Resume Incomplete Tests:</strong> 
              If you submit early or want to complete Quantitative Aptitude later, you can always click <strong>"▶ Continue Test / Complete Quant"</strong> on your analysis scorecard to finish the remaining questions!
            </li>
            <li><strong>Step-by-Step Mathematical Solutions:</strong> 
              Detailed logical and mathematical explanations are revealed immediately upon submission pointing out correct vs incorrect answers.
            </li>
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
    if (!t) return;
    const totalDurationSec = 45 * 60; // 45 Minutes composite time

    active = {
      testId: id,
      mode: mode,
      startedAt: now,
      testEndAt: now + totalDurationSec * 1000,
      timeRemainingSec: totalDurationSec,
      isPaused: false,
      sectionIndex: 0,
      currentIndex: 0,
      paletteSectionIndex: 0,
      answers: {},
      visited: [t.questions[0].id],
      marked: []
    };
    storeActive();
    page = 'exam';
    renderExam();
  }

  function continueAttempt(attempt) {
    if (!attempt) return;
    const t = getAddaTest(attempt.testId);
    if (!t) return;

    // Find first unattempted question
    let targetIdx = t.questions.findIndex(q => attempt.answers[q.id] === undefined);
    if (targetIdx === -1) targetIdx = 40; // Default to Quant (Q41) if all answered

    const now = Date.now();
    // Allow at least 25 minutes (1500s) to comfortably complete Quant / remaining questions
    const timeAllowedSec = Math.max(1500, attempt.timeRemainingSec || 1500);

    active = {
      testId: attempt.testId,
      mode: 'cbt',
      startedAt: attempt.startedAt || now,
      testEndAt: now + timeAllowedSec * 1000,
      timeRemainingSec: timeAllowedSec,
      isPaused: false,
      sectionIndex: targetIdx < 40 ? 0 : 1,
      currentIndex: targetIdx,
      paletteSectionIndex: targetIdx < 40 ? 0 : 1,
      answers: { ...(attempt.answers || {}) },
      visited: t.questions.filter(q => attempt.answers[q.id] !== undefined).map(q => q.id),
      marked: [],
      resumedFromAttemptId: attempt.attemptId
    };

    const targetQ = t.questions[targetIdx];
    if (targetQ && !active.visited.includes(targetQ.id)) {
      active.visited.push(targetQ.id);
    }

    storeActive();
    page = 'exam';
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
  }

  // --- EXAM INTERFACE ---

  function renderExam() {
    page = 'exam';
    if (!active) return enterHome();

    const t = getAddaTest(active.testId);
    if (!t) return enterHome();
    const q = getCurrentQuestion();
    const sec = getSection();
    const isAnswered = active.answers[q.id] !== undefined;
    const userChoice = active.answers[q.id];

    // Ensure visited
    if (!active.visited.includes(q.id)) {
      active.visited.push(q.id);
      storeActive();
    }

    const reasoningQuestions = t.questions.slice(0, 40);
    const quantQuestions = t.questions.slice(40, 80);

    const reasoningAnsCount = reasoningQuestions.filter(sq => active.answers[sq.id] !== undefined).length;
    const quantAnsCount = quantQuestions.filter(sq => active.answers[sq.id] !== undefined).length;

    // Palette section defaults to active section or user toggle
    const palSectionIndex = (active.paletteSectionIndex !== undefined) ? active.paletteSectionIndex : active.sectionIndex;
    const secQuestions = palSectionIndex === 0 ? reasoningQuestions : quantQuestions;

    const answeredCount = secQuestions.filter(sq => active.answers[sq.id] !== undefined).length;
    const markedCount = secQuestions.filter(sq => active.marked.includes(sq.id)).length;
    const notVisitedCount = secQuestions.filter(sq => !active.visited.includes(sq.id)).length;
    const notAnsweredCount = secQuestions.length - answeredCount - notVisitedCount;

    const remainingSec = active.isPaused 
      ? (active.timeRemainingSec || 0)
      : Math.max(0, Math.ceil(((active.testEndAt || Date.now()) - Date.now()) / 1000));

    $('#app').innerHTML = `
      <div class="exam-wrapper">
        <!-- Section Bar -->
        <div class="section-nav-bar" style="margin-bottom: 16px; background:#ffffff; border:1px solid var(--border); border-radius:12px; padding:12px 18px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
          <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
            <div style="font-weight:750; color:var(--primary); font-size:15px;">
              ${esc(t.title)}
            </div>
            <div style="display:flex; gap:8px;">
              <button type="button" class="section-nav-tab-btn ${active.sectionIndex === 0 ? 'active' : ''}" id="addaSecReasoning">
                1. Reasoning (Q1–Q40)
                <span class="sec-pill-badge">${reasoningAnsCount}/40</span>
              </button>
              <button type="button" class="section-nav-tab-btn ${active.sectionIndex === 1 ? 'active' : ''}" id="addaSecQuant">
                2. Quantitative (Q41–Q80)
                <span class="sec-pill-badge">${quantAnsCount}/40</span>
              </button>
            </div>
          </div>
          <div style="display:flex; align-items:center; gap:10px;">
            <button type="button" id="addaPauseBtn" class="btn btn-secondary" style="font-size:12px; padding:6px 14px; min-height:34px; display:inline-flex; align-items:center; gap:6px;">
              ⏸ Pause / Take Break
            </button>
            <a href="${esc(t.pdfUrl)}" target="_blank" rel="noopener noreferrer" class="btn btn-ghost" style="font-size:11.5px; padding:6px 12px; min-height:34px; text-decoration:none; display:inline-flex; align-items:center; gap:6px;">
              📄 PDF ↗
            </a>
            <div class="timer-box normal" style="font-family:monospace; font-size:18px; font-weight:800; padding:6px 14px; border-radius:8px; border:1px solid #cfdbc8; background:#edf3e9; color:var(--primary);">
              ⏱ <span id="addaTimerDisplay">${timeText(remainingSec)}</span>
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
                  Question ${q.number} of 80 · Section ${q.number <= 40 ? '1: Reasoning Ability' : '2: Quantitative Aptitude'}
                </h2>
              </div>
              <div style="font-size:12px; color:var(--text-muted); font-weight:600;">
                Marks: <strong style="color:var(--c-answered);">+1.00</strong> / <strong style="color:var(--c-not-answered);">-0.25</strong>
              </div>
            </div>

            <div class="question-body" style="padding:24px; flex:1; min-height:360px;">
              ${renderQuestionStemWithDiagrams(q)}

              <div class="options-list" style="display:flex; flex-direction:column; gap:10px;">
                ${q.options.map((opt, oIdx) => `
                  <button type="button" class="option-item ${userChoice === oIdx ? 'selected' : ''}" data-opt="${oIdx}" style="text-align:left; padding:12px 16px; border:1px solid ${userChoice === oIdx ? '#67905d' : 'var(--border)'}; background:${userChoice === oIdx ? '#edf3e8' : '#ffffff'}; border-radius:8px; cursor:pointer; font-size:13.5px; display:flex; align-items:center; gap:12px; font-family:inherit;">
                    <span style="font-weight:750; font-size:12px; color:var(--primary); width:20px;">(${'ABCDE'[oIdx]})</span>
                    <span style="flex:1;">${formatMathText(opt)}</span>
                  </button>
                `).join('')}
              </div>
            </div>

            <!-- Footer Controls -->
            <div class="exam-footer" style="padding:16px 20px; border-top:1px solid var(--border); background:#fcfdfb; border-bottom-left-radius:12px; border-bottom-right-radius:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
              <div style="display:flex; gap:8px;">
                <button type="button" id="addaMarkNext" class="btn btn-secondary" style="font-size:12px;">Mark for Review & Next</button>
                <button type="button" id="addaClear" class="btn btn-ghost" style="font-size:12px;">Clear Response</button>
              </div>
              <div style="display:flex; gap:8px;">
                <button type="button" id="addaPrev" class="btn btn-secondary" style="font-size:12px;" ${active.currentIndex === 0 ? 'disabled' : ''}>Previous</button>
                <button type="button" id="addaSaveNext" class="btn btn-primary" style="font-size:12px;">Save & Next →</button>
                <button type="button" id="addaSubmitBtn" class="btn btn-primary" style="background:#2e7d32; border-color:#2e7d32; font-size:12px;">Submit Test</button>
              </div>
            </div>
          </div>

          <!-- Right: Question Palette -->
          <div class="palette-sidebar" style="background:#ffffff; border:1px solid var(--border); border-radius:12px; display:flex; flex-direction:column;">
            <div style="padding:10px 14px; background:#edf2e8; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; gap:8px;">
              <div style="font-size:12px; font-weight:750; color:var(--primary);">
                Palette
              </div>
              <div style="display:flex; gap:4px;">
                <button type="button" id="palToggleReason" class="pal-tab-btn ${palSectionIndex === 0 ? 'active' : ''}">
                  Reasoning (1–40)
                </button>
                <button type="button" id="palToggleQuant" class="pal-tab-btn ${palSectionIndex === 1 ? 'active' : ''}">
                  Quant (41–80)
                </button>
              </div>
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
                    <button type="button" class="pal-btn ${st} ${isCurrent ? 'current' : ''}" data-adda-jump="${sq.number - 1}" style="width:100%; height:34px; font-size:11px; border-radius:6px; font-weight:700; cursor:pointer; ${isCurrent ? 'outline:2px solid var(--primary); outline-offset:1px;' : ''}">
                      ${sq.number}
                    </button>
                  `;
                }).join('')}
              </div>
            </div>
          </div>
        </div>

        <!-- Pause Break Modal Overlay -->
        ${active.isPaused ? `
          <div class="cbt-pause-overlay">
            <div class="cbt-pause-card">
              <div style="font-size:44px; margin-bottom:12px;">☕</div>
              <h2 style="font-size:22px; font-weight:800; color:var(--primary); margin:0 0 8px;">
                Test Paused — Take a Break!
              </h2>
              <p style="color:var(--text-muted); font-size:13.5px; margin:0 0 16px; line-height:1.6;">
                Your exam timer is safely paused and all your responses are saved.<br>
                Rest your eyes, take a breather, and click below when you're ready to jump back in.
              </p>
              <div class="cbt-pause-stats-grid">
                <div class="cbt-pause-stat-item">
                  <div style="font-size:10.5px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Time Remaining</div>
                  <div style="font-size:20px; font-weight:800; color:var(--primary); font-family:monospace; margin-top:4px;">
                    ${timeText(active.timeRemainingSec || remainingSec)}
                  </div>
                </div>
                <div class="cbt-pause-stat-item">
                  <div style="font-size:10.5px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Reasoning Done</div>
                  <div style="font-size:20px; font-weight:800; color:#2e7d32; margin-top:4px;">
                    ${reasoningAnsCount}/40
                  </div>
                </div>
                <div class="cbt-pause-stat-item">
                  <div style="font-size:10.5px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Quant Done</div>
                  <div style="font-size:20px; font-weight:800; color:#2e7d32; margin-top:4px;">
                    ${quantAnsCount}/40
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

    // Bind option click
    $('#app').querySelectorAll('[data-opt]').forEach(btn => {
      btn.onclick = () => {
        const optIdx = Number(btn.dataset.opt);
        active.answers[q.id] = optIdx;
        storeActive();
        renderExam();
      };
    });

    // Top Section Tabs Click
    const secRBtn = $('#addaSecReasoning');
    if (secRBtn) {
      secRBtn.onclick = () => {
        if (active.sectionIndex !== 0) {
          active.sectionIndex = 0;
          active.paletteSectionIndex = 0;
          const target = active.lastReasoningIndex !== undefined ? active.lastReasoningIndex : 0;
          goTo(target);
        }
      };
    }

    const secQBtn = $('#addaSecQuant');
    if (secQBtn) {
      secQBtn.onclick = () => {
        if (active.sectionIndex !== 1) {
          active.sectionIndex = 1;
          active.paletteSectionIndex = 1;
          const target = active.lastQuantIndex !== undefined ? active.lastQuantIndex : 40;
          goTo(target);
        }
      };
    }

    // Palette Section Toggles
    const palR = $('#palToggleReason');
    if (palR) {
      palR.onclick = () => {
        active.paletteSectionIndex = 0;
        storeActive();
        renderExam();
      };
    }

    const palQ = $('#palToggleQuant');
    if (palQ) {
      palQ.onclick = () => {
        active.paletteSectionIndex = 1;
        storeActive();
        renderExam();
      };
    }

    // Pause / Break buttons
    const pauseBtn = $('#addaPauseBtn');
    if (pauseBtn) pauseBtn.onclick = pauseTest;

    const resumePauseBtn = $('#resumeFromPauseBtn');
    if (resumePauseBtn) resumePauseBtn.onclick = unpauseTest;

    const exitPauseBtn = $('#exitToHomePauseBtn');
    if (exitPauseBtn) exitPauseBtn.onclick = enterHome;

    // Save & Next
    $('#addaSaveNext').onclick = () => {
      if (active.currentIndex === t.questions.length - 1) {
        if (confirm('You have reached the final question (Q80). Would you like to submit your exam now?')) {
          submitTest(false);
        }
      } else {
        goTo(active.currentIndex + 1);
      }
    };

    // Mark & Next
    $('#addaMarkNext').onclick = () => {
      if (!active.marked.includes(q.id)) active.marked.push(q.id);
      if (active.currentIndex === t.questions.length - 1) {
        if (confirm('You have reached the final question (Q80). Would you like to submit your exam now?')) {
          submitTest(false);
        }
      } else {
        goTo(active.currentIndex + 1);
      }
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
      if (active.currentIndex > 0) {
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
    const t = getAddaTest(active.testId);
    if (!t || idx < 0 || idx >= t.questions.length) return;

    if (active.currentIndex < 40) {
      active.lastReasoningIndex = active.currentIndex;
    } else {
      active.lastQuantIndex = active.currentIndex;
    }

    active.currentIndex = idx;
    // Automatically keep section and palette in sync with question number
    active.sectionIndex = idx < 40 ? 0 : 1;
    active.paletteSectionIndex = active.sectionIndex;

    const q = getCurrentQuestion();
    if (q && !active.visited.includes(q.id)) active.visited.push(q.id);
    storeActive();
    renderExam();
  }

  // --- SUBMIT & ANALYSIS ---

  function submitTest(auto = false) {
    if (!active) return;
    const t = getAddaTest(active.testId);
    if (!t) return;
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
      attemptId: active.resumedFromAttemptId || ('adda_att_' + Date.now()),
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
      startedAt: active.startedAt,
      answers: answers
    };

    const hist = history();
    // If updating resumed attempt, replace it; else unshift new
    const existingIdx = hist.findIndex(h => h.attemptId === attemptRecord.attemptId);
    if (existingIdx !== -1) {
      hist[existingIdx] = attemptRecord;
    } else {
      hist.unshift(attemptRecord);
    }
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
    if (!t) return enterHome();

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
              <p style="color: #cbd5e1; font-size: 13.5px;">${esc(attempt.paperLabel)} · Evaluated on ${esc(new Date(attempt.completedAt).toLocaleString())}</p>
              ${attempt.skippedCount > 0 ? `
                <div style="margin-top: 14px; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; padding: 10px 16px; display:inline-flex; align-items:center; gap:12px; flex-wrap:wrap;">
                  <span style="font-size: 13px; color: #f1f5f9;">
                    Took a break or skipped Quant? You have <strong>${attempt.skippedCount} unattempted questions</strong>.
                  </span>
                  <button type="button" id="heroContinueBtn" class="btn btn-primary" style="background:#cfe68c; color:#173c34; border:none; font-weight:800; font-size:12px; padding:6px 14px; cursor:pointer;">
                    ▶ Complete Remaining Questions →
                  </button>
                </div>
              ` : ''}
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
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
              ${attempt.skippedCount > 0 ? `
                <button type="button" id="addaContinueAttemptBtn" class="btn btn-primary" style="background:#2e7d32; border-color:#2e7d32; font-weight:750;">
                  ▶ Complete Quant & Remaining (${attempt.skippedCount} Unattempted)
                </button>
              ` : ''}
              <button type="button" id="addaRetakeBtn" class="btn btn-secondary">Retake Test</button>
              <button type="button" id="addaReturnHomeBtn" class="btn btn-primary">Mock Library ↗</button>
            </div>
          </div>

          <!-- Filter Buttons -->
          <div class="review-filter-bar">
            <button type="button" class="review-filter-btn ${reviewFilter === 'all' ? 'active' : ''}" data-rf="all">
              All Questions (80)
            </button>
            <button type="button" class="review-filter-btn ${reviewFilter === 'wrong' ? 'active' : ''}" data-rf="wrong">
              Incorrect Only (${attempt.wrongCount})
            </button>
            <button type="button" class="review-filter-btn ${reviewFilter === 'correct' ? 'active' : ''}" data-rf="correct">
              Correct Only (${attempt.correctCount})
            </button>
            <button type="button" class="review-filter-btn ${reviewFilter === 'skipped' ? 'active' : ''}" data-rf="skipped">
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

                  ${renderQuestionStemWithDiagrams(q)}

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
                          <span style="flex:1;">${formatMathText(opt)}</span>
                          ${tag}
                        </div>
                      `;
                    }).join('')}
                  </div>

                  <div class="expl-box" style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:16px; font-size:13.5px; line-height:1.8;">
                    <strong style="color:var(--primary); display:block; margin-bottom:6px;">Step-by-Step Analysis & Solution:</strong>
                    <div style="white-space:pre-wrap; color:#334155;">${formatMathText(q.explanation)}</div>
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

      const heroCont = $('#heroContinueBtn');
      if (heroCont) heroCont.onclick = () => continueAttempt(attempt);

      const actCont = $('#addaContinueAttemptBtn');
      if (actCont) actCont.onclick = () => continueAttempt(attempt);

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

    window.addEventListener('hashchange', () => {
      if (window.location.hash.includes('adda')) {
        switchTab('adda');
      } else if (window.location.hash.includes('original')) {
        switchTab('original');
      }
    });

    // Expose API for app.js or tests
    window.AddaPortal = {
      getCatalog,
      getAddaTests,
      getAddaTest,
      switchTab,
      showInstructions,
      startTest,
      continueAttempt,
      resumeTest,
      pauseTest,
      unpauseTest,
      history
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAdda);
  } else {
    initAdda();
  }
})();
'''

with open('adda.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully wrote updated adda.js ({len(content)} chars)!")
