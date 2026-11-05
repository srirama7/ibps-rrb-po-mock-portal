# RRB PO Mock Lab — 20 full prelims papers

A **free, independent, no-login, browser-based mock-test suite** for IBPS RRB Officer Scale I prelims practice.

## What's included

- `SPEC_RRB_PO_20_MOCKS.md` — comprehensive build specification for an AI coding agent or developer.
- `data/tests.json` — all **20 × 80 = 1,600** original multiple-choice questions, answers, explanations and shared puzzle/DI passages.
- `data/mock_01.json` … `data/mock_20.json` — the same mocks in separate importable files.
- `data/answer_keys.csv` — 1,600 answer keys and explanations for review/import.
- `data/qa_report.json` — automated structural validation summary.
- `tools/generate_questions.py` — deterministic generator with internally solved reasoning arrangements.
- `tools/validate_questions.py` — content-structure validator and file splitter.
- `index.html`, `styles.css`, `app.js` — working responsive, timed mock-test website prototype.
- `START_WEBSITE_WINDOWS.bat` — local launch helper for Windows with Python installed.

## Run on Windows

Unzip the package, double-click `START_WEBSITE_WINDOWS.bat`, then open <http://localhost:8000>. If the Python launcher `py` isn't installed, open a terminal in this directory and run:

```sh
python -m http.server 8000
```

Then visit <http://localhost:8000>. **Opening `index.html` directly with `file://` will not work** because browsers block local JSON fetching.

You can deploy these static files directly on Vercel, Netlify, Firebase Hosting or another static host. There is no registration form, login, payment provider or server required for personal practice.

## Test parameters

| Item | Setting |
|---|---|
| Questions per mock | 80 |
| Reasoning | 40 questions / 25 minutes |
| Quantitative Aptitude | 40 questions / 20 minutes |
| Total | 45 minutes / 80 marks |
| Marking | +1 correct, −0.25 incorrect, 0 unanswered |
| Question choices | 5 per question |
| Result explanations | Accessible after final submission |
| Account requirement | None |

These mocks are **independently generated training material**, not official IBPS papers. They intentionally reuse broad reasoning and arithmetic *skills* while keeping the question stems unique. Question quality, difficulty calibration and linguistic phrasing need editorial review before using them for a paid/public exam product; uniqueness does **not** imply official difficulty parity.

The browser app stores incomplete and completed attempts in localStorage, which is local to that browser/device. Clearing site data deletes that progress. For a public platform with cheating resistance, do **not** deliver `answerIndex` and `explanation` in client-facing JSON before submission; move the answer keys to a protected server API.

## Verification

```sh
python tools/validate_questions.py
node --check app.js
```

## Disclaimer

Independent practice resource. Not affiliated with or endorsed by the Institute of Banking Personnel Selection. Official structure may change; verify the latest information at <https://www.ibps.in>.
