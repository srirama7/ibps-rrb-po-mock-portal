# RRB Practice Room

20 independent full-length IBPS RRB Officer Scale I prelims practice papers: 1,600 original questions, five choices each, answer keys and explanations.

Live: https://srirama7.github.io/ibps-rrb-po-mock-portal/

## Practice format

- Reasoning: 40 questions in 25 minutes; Quantitative Aptitude: 40 questions in 20 minutes.
- +1 correct, -0.25 wrong, zero unanswered. Answered and marked questions are scored.
- Automatic section locking and final submission, browser-local resume and attempt history.
- Desktop passage/answer split, responsive mobile layout, keyboard answer controls, accessible focus indicators.
- Puzzle families: north-facing and south-facing rows, parallel rows, circular, box, floor-flat, month-date, month order, joining years and single-floor. All 20 papers have different four-puzzle combinations. Topic blocks and questions vary in order while passage questions stay together.
- Quant: indirect table DI, labelled bar charts, prose caselets, ten DI question formats, five series rules, approximation, quadratic comparisons, and alternate arithmetic families.

## November 9 variety update

Version 5 regenerates all 1,600 questions with a new seed and twenty different puzzle combinations. Cards show the actual puzzle types in each paper. A new browser storage version prevents old answers from being graded against the new bank; previous storage is retained. Shared topic families still recur for exam practice; these are original questions rather than claims of actual past-paper reproduction.

## Sources and limits

Topics reviewed on 8 November 2026 against the [current BankersAdda topic guide](https://www.bankersadda.com/ibps-rrb-po-syllabus/) and the publisher's [RRB prelims topic and past-paper guide, pages 5–6](https://www.adda247.com/jobs/wp-content/uploads/sites/8/2024/06/10162029/Copy-of-Decoding-IBPS-RRB-Prelims-2024-Final.pdf). The existing topics already fell within that guidance. Version 4 revises 400 puzzle tasks, 60 direction tasks and 10 pipes/cisterns tasks to address unclear clues, repetitive tasks and trivial rate cancellation; the complete bank was regenerated with updated explanations and keys. See [the review record](data/syllabus_review.json) for topic counts and sources.

This is a prelims bank: Reasoning and Quantitative Aptitude. General Awareness, Computer Knowledge and English/Hindi belong to mains. Preparation-provider topic lists are guidance, not an official topic-by-topic syllabus. The [current IBPS notification page](https://www.ibps.in/index.php/notification-for-common-recruitment-process-for-crp-rrb-xv/) is the authority for exam rules; its current PDF could not be retrieved during this review, so this update does not claim a new verification of the official 2026 rules. Timers retain the previously implemented 25/20-minute structure, also described by the current preparation guide; historical guide timings are not used.

Questions are original practice material, not copied exam papers. Topic/structure alignment is not official difficulty calibration. This independent resource is not affiliated with IBPS. Results deliberately do not invent state/category cutoffs or predict qualification.

Approximation choices also received a correctness fix: three regenerated items had a distractor closer to the exact value than the rounded key. All 100 approximation option sets now use wider spacing, and validation requires the keyed answer to be the uniquely closest choice.

## Adda Mocks (10 Memory-Based Papers)

Integrated 10-paper practice library based on Adda247 IBPS RRB Officer Scale I prelims memory-based question papers:

- **Original Mocks (20)** + **Adda Mocks (10)**: Switch between collections with the library tab selector.
- **English-Only Interactive CBT**: Every question extracted in pure English, with 5 options, sectional timers (Reasoning 25m, Quant 20m), palette, and automatic sectional lock.
- **Detailed Solution & Analysis**: After submission, clearly points out which questions are Correct (green +1.00), Incorrect (red -0.25), and Unattempted (0.00), with quick filter toggles and step-by-step mathematical/logical solutions.
- **Timed PDF Practice Mode**: Practice directly with the companion answer sheet alongside the original PDF.
- **Direct PDF Links**: View and download the original Adda247 memory-based PDFs in a new tab.
- **Independent Storage**: Uses `rrbpo_adda_active_v1` and `rrbpo_adda_history_v1` to ensure existing 20-mock attempts and progress remain completely untouched.

### Validate Adda Mocks

```sh
python tools/validate_adda_mocks.py
python tools/verify_adda_links.py
node --check adda.js
python tools/adda_browser_smoke_test.py
```

## Generate and validate

Run from the repository root with Python 3 and Node.js:

```sh
python tools/build_exam_bank.py
python tools/validate_questions.py
python tools/review_syllabus.py
python tools/check_answers.py
python tools/check_reasoning.py
python tools/check_puzzle_questions.py
node --check app.js
```

The generator exhaustively checks arrangement uniqueness and removes redundant clues. `data/solver_audit.json` records 80 uniquely solved sets. Independent checkers recompute all 800 quantitative keys and 400 standalone reasoning keys from displayed inputs, check 400 puzzle keys against solved layouts, and verify 1,600 distinct question contexts. Structural validation refreshes all per-paper JSON files and the CSV answer key. The syllabus check rejects topic labels outside the researched prelims scope. These checks do not substitute for human exam-difficulty calibration.

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
