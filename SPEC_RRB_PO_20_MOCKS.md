# PRODUCT & IMPLEMENTATION SPECIFICATION
## RRB PO Mock Lab — 20 original IBPS RRB Officer Scale I prelims simulations

**Specification version:** 1.0  
**Prepared:** 05 November 2026  
**Product type:** Responsive, browser-based, full-length mock-exam website  
**Primary users:** IBPS RRB Officer Scale I prelims aspirants practising independently  
**Delivery:** This specification plus 20 complete JSON papers, answer-key CSV, deterministic generator, QA script and a functional frontend prototype.

---

## 1. Vision and measurable definition of done

Build an exam-like practice website where a student can open the homepage, choose any of 20 independent papers, complete the full prelims examination, and view graded explanations **without entering an email address, mobile number, OTP or payment details**. The reference implementation in this ZIP is usable locally and can be deployed as a static site.

### Non-negotiable acceptance criteria

1. Exactly **20 separately numbered papers**, `MOCK-01` to `MOCK-20`.
2. Each mock includes **80 original multiple-choice questions**, of which **40 are Reasoning Ability** and **40 are Quantitative Aptitude**. Total is **1,600 distinct stems**.
3. Every question has **exactly five distinguishable options**, **one correct option**, a topic label, a unique ID and an explanation.
4. Reasoning has a **strict 25-minute timer**. When it ends, it locks and Quantitative Aptitude begins with a **strict 20-minute timer**. There is no manual switching backwards.
5. Scoring: **+1 correct, −0.25 wrong, 0 not attempted**. Display a raw score out of 80, including possible negative sectional scores. Round displayed totals to two decimals.
6. A one-question-at-a-time display with **Previous, Next/Save, Clear response, Mark for review, question palette, active timer and final Submit**.
7. Shared passages for puzzles, coding and DI, visible above each of their linked questions.
8. Final result with total score, section scores, counts, attempt rate, attempted-question accuracy, topic breakdown, and explanations for all 80 questions.
9. No sign-in or external backend required. Save unfinished attempts and completed attempts locally on the same browser; offer reset and retake.
10. Do not display answer keys during the live attempt. The demo client contains correct answers in downloaded JSON and is therefore **not cheat-proof**; a public high-stakes implementation must split questions from server-side answer keys.
11. The product is clearly described as an **independent practice simulation, not an official or leaked IBPS paper**.

## 2. Exam rules and source fidelity

The design uses the published Officer Scale I prelims structure from the IBPS 2025 notification: **Reasoning 40 questions/40 marks/25 minutes**, and **Quantitative Aptitude 40 questions/40 marks/20 minutes** (80 marks in 45 minutes). Candidates must qualify both sections. IBPS retains the right to alter the test structure, so the application must keep durations and markings configurable rather than hard-coded into many places.

| Parameter | Mock-engine setting | Source/fidelity note |
|---|---:|---|
| Stage | Preliminary exam, not Main | Officer Scale I |
| Reasoning | 40 × 1 mark | 25 minutes, separately timed |
| Quantitative Aptitude | 40 × 1 mark | 20 minutes, separately timed |
| Total | 80 questions / 80 marks | 45 minutes |
| Correct | +1 | Applicable to this simulation |
| Incorrect | −0.25 | Standard one-quarter negative marking |
| Unanswered | 0 | No penalty |
| Options | Five per question | A through E |
| Cut-off display | Do not claim an official predicted cut-off | Final cut-offs vary by year/state/category |

**Primary official references:**
- https://www.ibps.in/wp-content/uploads/CRP-RRBs-XIV_Final_AD_31.08.25.pdf
- https://www.ibps.in/wp-content/uploads/IBPS_CALENDAR_2026-27_final.pdf
- https://www.ibps.in/index.php/rural-bank-xv/

**Coverage reference, non-official:** Review of 2025 memory-based paper trends shows puzzles/seating arrangements, inequalities, syllogisms and coding in Reasoning, plus DI, number series, equations and arithmetic in Quant. See https://www.practicemock.com/blog/ibps-rrb-po-exam-analysis-2025/ and https://www.oliveboard.in/blog/ibps-rrb-po-topic-wise-weightage/ . These were used for topical inspiration only; none of their paper text is copied.

## 3. Scope, content and independence

### Fixed per-mock blueprint

| Numbered questions | Section | Topic | Count |
|---|---|---|---:|
| 1–20 | Reasoning | Four independent arrangement/puzzle passages, five linked questions each | 20 |
| 21–25 | Reasoning | Inequality inference, two proposed conclusions each | 5 |
| 26–30 | Reasoning | Syllogism, two proposed conclusions each | 5 |
| 31–34 | Reasoning | Chinese/word coding passage, four linked questions | 4 |
| 35–37 | Reasoning | Direction and distance | 3 |
| 38–40 | Reasoning | Blood relationships | 3 |
| 41–55 | Quant | Three independent data-interpretation passages, five linked questions each | 15 |
| 56–60 | Quant | Simplification/exact arithmetic | 5 |
| 61–65 | Quant | Missing-number series | 5 |
| 66–70 | Quant | Quadratic-root comparison | 5 |
| 71–80 | Quant | Ten mixed arithmetic word problems | 10 |
| **Total** | | | **80** |

**Puzzle types:** Linear rows, floor-based arrangements, vertical boxes, month sequences, seniority/designation rankings and race-position rankings. Generator uses ordered relations and an internal exhaustive-search solver to confirm exactly one valid final ordering for each of the 80 puzzle passages. One passage has five connected questions.

**DI styles:** Data tables, bar charts, line charts, text caselets and paired pie charts. Every DI passage has exact numeric data in structured rows and/or text as an accessible alternative to any chart.

**Arithmetic topics, rotated across tests:** Percentage, ratio and proportion, profit/loss, discounts, simple interest, compound interest, work, speed/distance/time, average, ages, mixtures, partnerships, pipes/cisterns, boats/streams and mensuration.

**Authenticity limitation:** These are freshly generated *practice* questions, not manually transcribed past papers or a professionally calibrated exam series. Some numerical and puzzle templates recur with different parameter values, even though all 1,600 question stems are textually unique. A publisher should conduct subject-expert checks of difficulty, grammar and distractor quality before claiming commercial-grade exam equivalence.

### Per-paper difficulty targets for an editorial upgrade

- 25% easy, 55% moderate and 20% harder.
- About half of Reasoning questions should be multi-step puzzles or arrangements.
- About 15 Quant questions should require data reading, roughly 10 arithmetic word problems, and 15 speedy computation/equation/series items.
- For every puzzle, ensure unique solution using search/backtracking; no unstated assumptions.
- At least two independent reviewers should solve a random 10% sample of questions and reconcile any disagreement.
- Reject vague or culturally ambiguous family relationships, missing units and mislabelled chart data.

## 4. Dataset/package architecture

```text
rrb_po_20_mock_suite/
  SPEC_RRB_PO_20_MOCKS.md       <-- THIS SPEC
  README.md
  START_WEBSITE_WINDOWS.bat
  index.html                    <-- working static web prototype
  styles.css
  app.js
  data/
    tests.json                  <-- full 20-mock bank
    mock_01.json ... mock_20.json
    answer_keys.csv
    qa_report.json
  tools/
    generate_questions.py       <-- reproducible content generator
    validate_questions.py       <-- paper and answer quality gates
    generation.log
```

### JSON schema

The root contains `format`, `version`, `exam`, `totalMocks`, `totalQuestions`, `tests`.

A test object contains:
- `id: "MOCK-01"`, `number: 1`, `title`, `durationSeconds: 2700`, `totalQuestions: 80`.
- `sectionOrder: ["reasoning", "quant"]` and section objects with `start`, `end`, `durationSeconds`.
- `marking: {"correct":1,"incorrect":-0.25,"unattempted":0}`.
- `stimuli[]`: shared passage records, referenced from linked questions.
- `questions[]`: 80 ordered MCQs; IDs `M01-Q01` to `M01-Q80`.

Illustrative record (format only; the actual 1,600 questions are in JSON):

```json
{
  "id": "M01-Q01",
  "number": 1,
  "section": "reasoning",
  "topic": "Puzzle & Seating Arrangement",
  "stem": "Based on arrangement T01-P1, who occupies rank 2?",
  "options": ["Option A", "Option B", "Option C", "Option D", "Option E"],
  "answerIndex": 3,
  "explanation": "Derive the unique rank order using the accompanying clues.",
  "stimulusId": "T01-P1"
}
```

`answerIndex` is zero-based, `options[answerIndex]` is the correct answer. **Never treat the illustrative record as a real question or answer key; consume the actual JSON.**

A shared stimulus has `id`, `type`, `title`, `body` and additional type-specific fields:
- `logic_puzzle`: `variant`, `solution`, `uniquenessVerified`.
- `coding`: word/code phrase list in `body`, mapping in `solution`.
- `data_interpretation`: `variant`, `visualization`, `columns`, `rows[{label,a,b}]`.

### Data validation rules

For every test, enforce:

```text
count(tests)                         == 20
count(test.questions)                == 80
count(reasoning)                     == 40
count(quant)                         == 40
count(test.stimuli)                  == 8
count(all question IDs)              == 1600 unique
count(all question stems)            == 1600 unique
count(question.options)              == 5 distinct strings
0 <= answerIndex < 5
question.stimulusId exists if present
Every explanation is nonempty
Every logic puzzle has one internally verified arrangement
```

Validator included: `python tools/validate_questions.py`. The supplied dataset passed this structural check. Structural QA does not replace subject-matter editorial review.

## 5. UX and visual specification

**Style:** Professional bank-exam CBT (computer-based testing) look. Desktop-first but accessible and responsive. Use a white/slate surface, a navy header, blue primary actions, green answered counters, pale red visited/unanswered, and violet review marks. Maintain high contrast and avoid relying on colour alone.

### Screen A — Home/dashboard

- Header: `RRB PO Mock Lab`, `No account needed`, `All mocks`.
- Four stats: 20 mock papers, 1,600 total questions, 45 minutes per test, user-completed attempts.
- Grid of 20 independent cards, showing mock number, 40/40 split, time, start/continue button and best prior score when available.
- Unfinished attempt banner with Resume. Timer continues while away from exam page.
- Attempts history with results/review links. Do not require sign-in or phone.

### Screen B — Instruction/confirmation screen

- Exact marks, section timing and negative marking.
- Prominent notice: Reasoning locks at 25 minutes; Quant starts automatically and runs 20 minutes.
- Mark for review and question navigation are section-limited.
- Show `Start timed mock` and `Back` actions.

### Screen C — Active exam

Desktop layout:

```text
+-------------------------------------------------------------------+
| Mock 03  | Reasoning: Q 19/40                 15:24 | Submit Test  |
+-------------------------------------------+-----------------------+
| Question 19    Puzzle & Seating            | QUESTION PALETTE      |
|                                           |  1  2  3  4  5        |
| [Common puzzle passage or DI graph]       |  6  7  8  9 10 ...   |
|                                           | Answered: green       |
| Question stem                             | Marked: violet        |
| (A) Option                                | Visited: pink         |
| (B) Option                                | Not visited: gray     |
| (C) Option                                |                       |
| (D) Option                                |                       |
| (E) Option                                |                       |
|                                           |                       |
| Previous | Clear | Mark Review | Save Next |                       |
+-------------------------------------------+-----------------------+
```

- Left: one question, any shared passage, A–E choices, actions. Right: 40-cell palette for active section only.
- On mobile the palette stacks above or below the question; A–E choices remain individually tappable and text wraps.
- Desktop keyboard shortcuts: keys `1`–`5` select options; `ArrowLeft`/`ArrowRight` move within current section.
- Persistent countdown `MM:SS`, warning styling during final 60 seconds.
- Avoid modal dialogs when changing ordinary questions. Confirmation only on early final Submit / navigation out / abandoning a paper.
- Never allow a user to edit or inspect the previous section once its time has passed.

### Screen D — Results and review

- Total raw score `/80`, correct/wrong/blank, total attempted, attempted-question accuracy.
- Reasoning and Quant independent score summaries.
- Topic table showing correct/wrong/blank for each topic.
- All questions reviewed in original order with user's selection, correct selection and explanation.
- `Show only wrong/unanswered`, `Retake test`, `All papers` buttons.
- No official pass/fail badge unless officially verified exam-year/state/category cut-offs are supplied.

## 6. Exam-engine state machine

States: `HOME -> INSTRUCTIONS -> REASONING_ACTIVE -> QUANT_ACTIVE -> SUBMITTED -> RESULTS`.

On START:

```ts
const state = {
  testId: "MOCK-01",
  startedAt: Date.now(),
  sectionIndex: 0,
  sectionEndAt: Date.now() + 25*60*1000,
  currentIndex: 0,
  answers: {} as Record<string, 0|1|2|3|4>,
  visited: ["M01-Q01"],
  marked: [] as string[]
};
```

The one and only source of truth for time is **the persisted timestamp deadline**, not `remainingSeconds--` counters. On each tick or page load:

```text
if now < deadline: stay in current section
else if reasoning_active:
    quant_deadline = original_reasoning_deadline + 20 minutes
    lock questions 1–40
    unlock 41–80
    if now >= quant_deadline: auto-submit immediately
else if quant_active: auto-submit immediately
```

This means refreshing the page cannot create more time, and a browser closed for more than 45 minutes completes the attempt when reopened. This remains a **client-only convenience**, not tamper-proof security, since local device time and storage can be manipulated.

**User actions**
- `selectOption(qid,index)`: replace prior selection, do not automatically advance.
- `clearResponse(qid)`: delete selection.
- `markForReview(qid)`: toggle a flag without changing selection.
- `navigateTo(n)`: permit only current-section indices.
- `submit()`: confirm and grade unanswered items as zero.
- `autoSubmit()`: grade without needing user click at end of Quant.
- `resume()`: reconstruct timestamp deadline and reload saved current section.
- `retake()`: create a new attempt, preserve historic completed attempts.

**Palette precedence:** If marked, display review decoration even if answered; show answered state in a secondary dot or `aria-label`. Do not misclassify answered-and-marked items as unanswered.

## 7. Grading and analytics formulas

For a section or whole test:

```ts
const right = items.filter(q => answers[q.id] === q.answerIndex).length;
const wrong = items.filter(q => answers[q.id] !== undefined && answers[q.id] !== q.answerIndex).length;
const blank = items.length - right - wrong;
const rawScore = Number((right - 0.25 * wrong).toFixed(2));
const accuracy = right + wrong ? 100 * right / (right + wrong) : 0;
const attemptRate = 100 * (right + wrong) / items.length;
```

**Numerical examples:** 55 correct + 15 incorrect + 10 blank ⇒ 55 − 3.75 = **51.25/80**. Zero attempts ⇒ **0**. Eight errors and no correct answers ⇒ **−2.00** (do not clamp to zero).

Compute topic stats by grouping `topic`. The pass prediction must remain `Not officially determined` unless an administrator enters a sourced cut-off; do not present user-specific results as final official qualification.

## 8. Persistence, privacy and hosting

### No registration mode (default and required)

- Save `rrbpo_active_v1` and `rrbpo_history_v1` in browser localStorage.
- No data leaves the device during standalone static practice other than ordinary requests to fetch static assets from the host.
- No Google, WhatsApp, email, OTP or telephone authentication.
- State clearly that clearing cookies/site storage or changing browsers removes local scores.
- Provide optional Export/Import progress JSON in a later enhancement; require user action.

### Optional future cloud sync

Add anonymous Firebase Authentication or a custom pseudonymous token only if the user chooses cross-device sync, and provide a clear privacy explanation. Avoid personal-info collection entirely if it is not required. **No Firebase secrets or external credentials are needed for the supplied local prototype.**

### Answer protection for public deployment

The included JSON has complete answer keys because it is convenient for self-hosted personal study. This is not a secure model for a public timed assessment. For cheating resistance:

1. A server endpoint returns question stems, public passages and options, **without** `answerIndex`, `explanation`, or `solution`.
2. Server securely stores answer key by immutable `questionId`, and grades submitted answers.
3. An API computes authoritative section deadlines from server time and uses a signed attempt token.
4. Return correct answers and explanations only after submission or timeout.
5. Enforce rate limits and authentication on the grading API if later adding public multi-user features; user registration is not required for the present personal website.

### Static deployment

- No bundler required in the included prototype.
- Run from `python -m http.server 8000`, then open `http://localhost:8000`.
- Static host options: Vercel, Netlify, Firebase Hosting, Cloudflare Pages, GitHub Pages (update asset paths if deploying under a subfolder).
- Cache `tests.json` by version in production; apply atomic releases so old in-progress attempts don't mix with changed questions.

## 9. Technical architecture for a rebuilt production-quality version

Suggested stack when converting to a larger application in Codex:

- **Frontend:** React + TypeScript + Vite + Tailwind CSS (or keep vanilla JS for smallest footprint).
- **State:** `useReducer`/Zustand, typed `ExamState` and `Attempt` interfaces.
- **Persistence:** IndexedDB for large attempt history, localStorage for last active attempt; no account needed.
- **Charts:** Simple accessible SVG for line/bar charts and optional pie SVG/Canvas. Always retain exact accessible data table.
- **Security:** Static practice -> client graded. Public secure assessment -> server API grade + server deadline.
- **Content:** Import `data/mock_XX.json` via a typed parser and schema validator (Zod or JSON Schema).
- **Testing:** Vitest/Jest for scoring and timers; Playwright for real browser flows.
- **Deployment:** Static hosting with HTTPS, cache-control, error boundaries and app build checks.

Recommended modular structure:

```text
src/
  app/App.tsx
  data/loadMock.ts
  types/exam.ts
  engine/examReducer.ts
  engine/timer.ts
  engine/score.ts
  components/QuestionPane.tsx
  components/PassagePane.tsx
  components/GraphPane.tsx
  components/QuestionPalette.tsx
  components/ExamTimer.tsx
  screens/Dashboard.tsx
  screens/Instructions.tsx
  screens/Exam.tsx
  screens/Results.tsx
  storage/localAttempts.ts
  test/score.test.ts
  test/timer.test.ts
  test/browser.spec.ts
```

## 10. Testing plan and edge cases

### Static content checks (already implemented)

- 20 mock objects and 1,600 unique questions.
- 80-question 40/40 section partition in each paper.
- Five different nonblank options; valid correct index.
- Shared passages are defined and referenced correctly.
- Correct topic counts and valid section start/end ranges.
- Every question has an explanation.
- Eight passages per paper: four puzzles + one coding + three DI.

### Functional browser tests (developer must verify)

1. Start mock 1: exactly 40 Reasoning palette cells and 25:00 initial timer.
2. Choose Q1 option C; navigate to Q5 and back; choice C persists.
3. Mark Q5 for review, then answer it; both statuses remain represented.
4. Clear an answer: answer count decreases and score is affected appropriately.
5. Simulate Reasoning deadline; Quant auto-starts with Q41 and 20-minute deadline. Q1 cannot be accessed.
6. Simulate Quant deadline; all answers submitted with 0 for blanks.
7. Use 3 right, 2 wrong, 75 blank; total score is `2.50`.
8. Reload browser mid-test; current answers remain and countdown reflects elapsed real time.
9. Reload after 45 minutes; the exam is auto-graded rather than restarted.
10. Submit early; confirmation appears; solutions only then become visible.
11. Finish mock 1, then mock 2; test 1 history remains, and question stems are not repeated.
12. Retake mock 1; previous historic score remains visible.
13. On 360px phone width, choices, passage and palette remain usable without sideways scrolling.
14. On network load failure show a visible error; do not silently present a blank screen.
15. Edge cases: zero attempted, all correct, all wrong, negative scores, missing or invalid localStorage, duplicated IDs rejected by validation.
16. Browser accessibility: keyboard navigation, focus outlines, accessible timer, semantic questions/options and chart table alternatives.

### Editorial QA before commercial/public release

- Expert review of all 1,600 answers and explanations; structural validation alone does not guarantee subject accuracy.
- Check all 80 puzzle passages against the full set of clues and question wording.
- Evaluate category-balanced answer positions, typo corrections, data charts and pairwise distractors.
- Calibrate easy/medium/hard based on real aspirant completion times and feedback, not arbitrary confidence tags.
- Conduct copyright review and keep an independent branding identity instead of implying affiliation with IBPS.

## 11. Implementation sequence for one coding session

**Phase A — Load and validate content:** import all 20 mock JSONs, build strict types, render dashboard; execute `tools/validate_questions.py` before UI changes.

**Phase B — Exam engine:** implement `ExamState`, local persistence, strict separate section deadlines, section navigation restrictions, automatic transitions and early submission.

**Phase C — Question UI:** render all five choices; linked reasoning passages; rich DI tables, bars, lines and pies; palette statuses; mobile responsiveness.

**Phase D — Results:** correct score formula, section and topic analytics, all explanations, wrong-only review and retake/history.

**Phase E — Quality checks:** unit tests for score/timer, interactive browser tests for 40-to-41 auto transition and refresh, ensure no email/phone/login.

**Phase F — Deploy:** create a production build, test on desktop/mobile, release to static host, verify all 20 mocks load.

### Copy-paste Codex build instruction

> Read `SPEC_RRB_PO_20_MOCKS.md` and all files under `data/`. Build a polished responsive IBPS RRB Officer Scale I prelims mock website from the included original question bank. Implement every requirement and acceptance criterion. Preserve exactly 20 independent mocks with 80 questions each and five options per question. Timers must be separately enforced (Reasoning 25 min, Quant 20 min), with no backward section navigation, +1/−0.25/0 scoring, autosave/resume, palette, mark-for-review, final solutions and analytics. The user must be able to practise with no phone, email, OTP, login or payment. Run and fix automated tests and produce an actually runnable build rather than a static design. Use the supplied JSON as the source of truth; do not replace it with placeholder questions. Do not misrepresent this website as official IBPS content. For public anti-cheating protection, separate private answer keys from client-delivered prompts. Complete the implementation and report test results.

## 12. Handover checklist

- [x] 20 original mock objects.
- [x] 1,600 structurally validated unique question stems.
- [x] Five choices and an answer/explanation per question.
- [x] 160 linked puzzle/coding/DI passages.
- [x] Independent file per mock and combined question-bank JSON.
- [x] CSV answer key.
- [x] Functional static website files; responsive UI, navigation, timers, scoring and review.
- [x] QA script and README.
- [ ] Full human subject-expert review and real-user difficulty calibration (recommended before publication).
- [ ] Production server-side protection of answers (needed only if deploying as a secure, competitive exam platform).

---

**Ownership and permitted use:** These questions are newly generated as an independent training resource, not copied from official question papers. You may customise this package and deploy it as your own practice project. Do not label it “official IBPS” or guarantee that its difficulty or topics will exactly match any 2026 examination shift.
