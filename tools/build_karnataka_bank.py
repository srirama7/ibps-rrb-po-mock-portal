"""Import the supplied original campus-style PDFs without rewriting their content."""
import csv
import io
import json
from pathlib import Path
import re
import sys
import zipfile
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = [('verbal', 'Verbal Ability', 12), ('quant', 'Quantitative Aptitude', 15),
            ('reasoning', 'Logical Reasoning', 15), ('gk', 'General Knowledge / Banking', 11),
            ('computer', 'Computer Awareness', 11), ('sales', 'Sales Aptitude', 11)]


def build(archive):
    out = ROOT / 'data/karnataka'
    (out / 'pdfs').mkdir(parents=True, exist_ok=True)
    tests = []
    with zipfile.ZipFile(archive) as z:
        for number in range(1, 11):
            filename = f'Karnataka_Bank_CSA_Mock_{number:02d}.pdf'
            raw = z.read('Mock_Tests/' + filename)
            (out / 'pdfs' / filename).write_bytes(raw)
            doc = pymupdf.open(stream=raw, filetype='pdf')
            pages = [p.get_text() for p in doc]
            cleaned = []
            for page in pages:
                page = re.sub(r'^Karnataka Bank CSA \| independent practice material\s*\n', '', page)
                page = re.sub(r'^Mock \d+ .*?Page \d+\s*\n', '', page)
                cleaned.append(page)
            text = '\n'.join(cleaned)
            body, back = text.split('Answer key', 1)
            key_text, explanation_text = back.split('Short explanations', 1)
            keys = {int(n): ord(a) - 65 for n, a in re.findall(r'(?m)^(\d+)\. ([A-E])\s*$', key_text)}
            explanations = {int(n): (ord(a) - 65, ' '.join(e.split())) for n, a, e in
                            re.findall(r'(?ms)^Q(\d+) - ([A-E])\. (.*?)(?=^Q\d+ - |\Z)', explanation_text)}
            assert set(keys) == set(range(1, 76)) == set(explanations), filename
            passage = re.search(r'Read the following passage for questions 1-3:\s*(.*?)\s*Q1\.', body, re.S).group(1)
            body = re.sub(r'(?m)^Section \d+: .*\n', '', body)
            blocks = list(re.finditer(r'(?ms)^Q(\d+)\. (.*?)(?=^Q\d+\. |\Z)', body))
            assert len(blocks) == 75, filename
            questions = []
            for match in blocks:
                n = int(match[1])
                option_start = re.search(r'(?m)^A\. ', match[2]).start()
                parts = [match[2][:option_start]] + re.split(r'(?m)^([A-E])\. ', match[2][option_start:])[1:]
                assert parts[1::2] == list('ABCDE'), (filename, n, parts)
                options = [' '.join(x.split()) for x in parts[2::2]]
                assert all(options) and len(set(options)) == 5, (filename, n)
                assert keys[n] == explanations[n][0], (filename, n)
                end = 0
                for section, name, count in SECTIONS:
                    end += count
                    if n <= end:
                        break
                source_page = next(i + 1 for i, p in enumerate(pages) if re.search(rf'(?m)^Q{n}\. ', p))
                questions.append(dict(id=f'KBL-{number:02d}-Q{n}', number=n, section=section,
                                      stem=' '.join(parts[0].split()), options=options, answerIndex=keys[n],
                                      explanation=explanations[n][1], passage=' '.join(passage.split()) if n <= 3 else '',
                                      sourcePage=source_page))
            tests.append(dict(id=f'KBL-{number:02d}', title=f'Karnataka Bank CSA Mock {number:02d}',
                              durationMinutes=60, pdf=f'data/karnataka/pdfs/{filename}',
                              sections=[dict(id=s, name=n, count=c) for s, n, c in SECTIONS], questions=questions))
        links = list(csv.DictReader(io.StringIO(z.read('Previous_Year_Papers_Links/SOURCE_LINKS.csv').decode())))
        (out / 'START_HERE.txt').write_bytes(z.read('START_HERE.txt'))
        (out / 'SOURCE_LINKS.csv').write_bytes(z.read('Previous_Year_Papers_Links/SOURCE_LINKS.csv'))
    bank = dict(patternSource='https://karnatakabank.lntedutech.com/e/CNJDMT8X/login',
                patternChecked='2026-11-17', tests=tests,
                paperLinks=[dict(title=r['Exam'], url=r['URL']) for r in links])
    (out / 'tests.json').write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding='utf-8')
    (out / 'tests.js').write_text('window.KARNATAKA_BANK = ' + json.dumps(bank, ensure_ascii=False) + ';\n', encoding='utf-8')
    print(f'Imported {len(tests)} mocks, {sum(len(t["questions"]) for t in tests)} questions with matching keys and explanations, {len(links)} external paper links.')


if __name__ == '__main__':
    build(sys.argv[1])
