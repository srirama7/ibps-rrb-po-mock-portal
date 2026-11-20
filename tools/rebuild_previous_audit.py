"""Reproduce the checked audit from cached source OCR and explicit deductions."""
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
for script in ['ocr_previous_tesseract.py','audit_scanned_answers.py','audit_previous_old.py']:
    subprocess.run([sys.executable,str(ROOT/'tools'/script)],cwd=ROOT,check=True)
cache=ROOT/'tools/prepp_cache/audit'
assert json.loads((cache/'scan_failures.json').read_text(encoding='utf-8'))==[]
papers={**json.loads((cache/'derived_scan_answers.json').read_text(encoding='utf-8')),
        **json.loads((cache/'derived_old_answers.json').read_text(encoding='utf-8'))}
assert len(papers)==12 and all(len(rows)==80 for rows in papers.values())
summary={'reviewedQuestionSlots':960,
         'verifiedAnswers':sum(r['status']=='verified' for rows in papers.values() for r in rows.values()),
         'excludedQuestions':sum(r['status']=='excluded' for rows in papers.values() for r in rows.values()),
         'method':'Question calculations, direct deductions, and constraint models checked against the supplied PDF pages. Named sets are assumed to exist in the standard exam interpretation of syllogisms. Exclusions identify insufficient or defective source information.'}
assert summary['verifiedAnswers']==928 and summary['excludedQuestions']==32
audit={'version':'2026-11-20-reviewed-v1','summary':summary,'papers':papers}
(ROOT/'data/previous/answer_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
from apply_previous_audit import apply
apply()
