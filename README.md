# RRB Practice Room

20 independent full-length IBPS RRB Officer Scale I prelims practice papers: 1,600 original questions, five choices each, answer keys and explanations.

Live: https://srirama7.github.io/ibps-rrb-po-mock-portal/

## Practice format

- Reasoning: 40 questions in 25 minutes; Quantitative Aptitude: 40 questions in 20 minutes.
- +1 correct, -0.25 wrong, zero unanswered. Answered and marked questions are scored.
- Automatic section locking and final submission, browser-local resume and attempt history.
- Desktop passage/answer split, responsive mobile layout, keyboard answer controls, accessible focus indicators.
- Puzzle families: linear, parallel rows, circular, box, floor-flat, month-date.
- Quant: indirect table DI, labelled bar charts, prose caselets, ten DI question formats, five series rules, approximation, quadratic comparisons, and alternate arithmetic families.

## Sources and limits

The exam structure was researched against [IBPS notification material](https://www.ibps.in/wp-content/uploads/CRP-RRBs-XIV_Final_AD-27.09.25.pdf). Check the [current IBPS notification hub](https://www.ibps.in/index.php/rural-bank-xv/) for changes. Topic selection was informed by [2025 shift analysis](https://www.bankersadda.com/ibps-rrb-po-exam-analysis-2025-shift-1-22-november/) and [cross-shift trends](https://www.practicemock.com/blog/ibps-rrb-po-exam-analysis-2025/). Candidate-reported analyses are indicative, not an official syllabus or a guarantee of future questions.

Questions are original practice material, not copied exam papers. Topic/structure alignment is not official difficulty calibration. This independent resource is not affiliated with IBPS. Results deliberately do not invent state/category cutoffs or predict qualification.

## Generate and validate

Run from the repository root with Python 3 and Node.js:

```sh
python tools/build_exam_bank.py
python tools/validate_questions.py
python tools/check_answers.py
python tools/check_reasoning.py
node --check app.js
```

The generator exhaustively checks arrangement uniqueness and removes redundant clues. `data/solver_audit.json` records 80 uniquely solved sets. Independent checkers recompute all 800 quantitative keys and 400 standalone reasoning keys from displayed inputs, and verify 1,600 distinct question contexts. Structural validation refreshes all per-paper JSON files and the CSV answer key. These checks do not substitute for human exam-difficulty calibration.

For UI regression checks (requires Playwright and its Chromium browser):

```sh
python tools/browser_smoke_test.py
```

This covers desktop/mobile overflow, keyboard selection, clearing, review marking, refresh/resume, timer transitions, DI layout, all 20 result reports, scoring/penalties and automatic submission. Screenshots are written to ignored `artifacts/`.

Older generator scripts and the original specification are retained as project history. `build_exam_bank.py` is the current bank generator; use the commands above for the published version.

## Run and deploy

```sh
python -m http.server 8000
```

Open http://localhost:8000. The app also bundles its bank in `data/tests_data.js` for offline loading. GitHub Pages publishes the repository root from `main`.

Progress is stored only in this browser. The new bank uses versioned storage so old responses are not graded against changed questions; prior storage is preserved. This is a personal practice app: answers ship with the static site and it is not a secure proctored assessment system.
