"""Import the user's Prepp link pack as faithful, answer-hidden PDF practice pages.

Download the manifest PDFs into tools/prepp_cache before running. Scanned publisher key letters are compared against checked glyph templates;
question content is never rewritten.
"""
import csv
import argparse
import json
from pathlib import Path
import re
import shutil
from concurrent.futures import ProcessPoolExecutor

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'tools/prepp_cache'
OUT = ROOT / 'data/previous'


def scanned_key(path):
    # All eight publisher tables use the same raster font and cell geometry.
    # Compare glyphs against every manually checked letter in the first key;
    # this avoids OCR confusing the lowercase a/e letters with other symbols.
    import cv2
    import numpy as np

    def cells(file):
        doc = pymupdf.open(file)
        pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
        image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        h, w = image.shape[:2]
        output = []
        for col in range(5):
            for row in range(16):
                x = round((.203 + .1695*col)*w)
                y = round((.182 + .0451*row)*h)
                crop = cv2.cvtColor(image[y-15:y+15, x-16:x+16], cv2.COLOR_RGB2GRAY)
                mask = (crop < 100).astype(np.uint8)
                ys, xs = np.where(mask)
                assert len(ys), (file.name, col, row)
                output.append(cv2.resize(mask[ys.min():ys.max()+1, xs.min():xs.max()+1].astype(float), (24,32)))
        return output

    reference = cells(CACHE/'2025-11-22_Shift-1_RRB_PO_Prelims_Answer_Key.pdf')
    letters = ''.join([
        'd a c a b a e b a b a e a a a d',
        'a c a a c d a c c c e a a c a c',
        'e a a b d d a d e c d b c c a a',
        'd e c d c e d e e c e d c a c c',
        'e e b b d b c c d b d a a e b c',
    ]).replace(' ', '')
    assert len(letters) == 80
    answers = {}
    for number, glyph in enumerate(cells(path), 1):
        # The watermark crosses this e's middle stroke. Checked directly
        # against the 4 August 2024 Shift 2 and 23 November 2025 Shift 2
        # publisher tables, Q69.
        if path.name.startswith(('2024-08-04_Shift-2', '2025-11-23_Shift-2')) and number == 69:
            answers[number] = 4
            continue
        distances = sorted((min(float(np.mean((glyph-t)**2)) for t, label in zip(reference, letters) if label == letter), letter) for letter in 'abcde')
        assert distances[0][0] < .12 and distances[1][0]-distances[0][0] > .015, (path.name, number, distances)
        answers[number] = ord(distances[0][1])-ord('a')
    return answers


def render_page(task):
    pdf, number, target = task
    # PyMuPDF documents remain confined to their own process.
    temporary = str(Path(target).with_suffix('.temporary.jpg'))
    with pymupdf.open(pdf) as doc:
        doc[number].get_pixmap(matrix=pymupdf.Matrix(1.8, 1.8), alpha=False).save(temporary, jpg_quality=88)
    Path(temporary).replace(target)
    return target


def main(reuse_images=False):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader((CACHE / 'links.csv').read_text(encoding='utf-8-sig').splitlines()))
    keys = {r['Date_and_shift']: r for r in rows if r['Type'] == 'Answer_Keys'}
    papers = []
    render_tasks = []
    for row in rows:
        if row['Type'] != 'Question_Papers':
            continue
        stamp = row['Date_and_shift']
        paper_id = 'prepp-' + stamp.lower().replace('_', '-')
        dest = OUT / paper_id
        dest.mkdir(exist_ok=True)
        source = CACHE / row['Local_PDF_filename_after_download']
        doc = pymupdf.open(source)
        full_text = ''.join(p.get_text() for p in doc)
        answers = {}
        excluded = {}
        question_pages = {}
        # Older PDFs contain searchable answers. Remove those labels from all
        # practice images and the practice PDF before exporting either asset.
        for page_no, page in enumerate(doc):
            if not full_text:
                break
            text = page.get_text()
            for match in re.finditer(r'Que\.\s*(\d+)\b(.*?)(?=Que\.\s*\d+\b|\Z)', text, re.S):
                number = int(match[1])
                question_pages[number] = page_no
            for line in page.get_text('dict', flags=pymupdf.TEXTFLAGS_DICT & ~pymupdf.TEXT_PRESERVE_IMAGES)['blocks']:
                for item in line.get('lines', []):
                    value = ''.join(span['text'] for span in item['spans'])
                    if re.search(r'Correct\s+Option\s*-', value):
                        page.add_redact_annot(pymupdf.Rect(item['bbox']), fill=(1, 1, 1))
            page.apply_redactions(images=0)
        if full_text:
            matches = re.findall(r'Que\.\s*(\d+)\b(?:(?!Que\.\s*\d+\b).)*?Correct\s+Option\s*-\s*([1-5])', full_text, re.S)
            answers = {int(q): int(a)-1 for q, a in matches}
            if stamp == '2022-08-20_Shift-1':
                # Page 3 contains Q9's five options and key (4), but the
                # supplied PDF omits the question heading and prompt entirely.
                # Preserve that source key while excluding Q9 from scoring.
                answers[9] = 3
                question_pages[9] = 2
                excluded['9'] = 'The supplied PDF omits Q9’s heading and question prompt. Only its options and source key appear on page 3. This question is excluded from scoring.'
            assert len(answers) == 80, (stamp, len(answers))
        key_row = keys.get(stamp)
        key_url = None
        if key_row:
            answers = scanned_key(CACHE / key_row['Local_PDF_filename_after_download'])
            shutil.copy2(CACHE / key_row['Local_PDF_filename_after_download'], dest / 'answer-key.pdf')
            key_url = f'data/previous/{paper_id}/answer-key.pdf'
        pages = []
        if full_text:
            doc.save(dest / 'practice.pdf', garbage=1, deflate=True)
        else:
            # The scanned question-only sources need no redaction. Preserve
            # their original PDF instead of recompressing every scan.
            shutil.copy2(source, dest / 'practice.pdf')
        for i in range(len(doc)):
            name = f'page-{i+1:02}.jpg'
            if not reuse_images or not (dest/name).is_file():
                render_tasks.append((str(dest/'practice.pdf'), i, str(dest/name)))
            pages.append(f'data/previous/{paper_id}/{name}')
        papers.append(dict(id=paper_id, title='RRB PO Prelims - ' + stamp.replace('_', ' - ').replace('Shift-', 'Shift '),
                           date=stamp[:10], count=80, durationMinutes=45,
                           pdf=f'data/previous/{paper_id}/practice.pdf', sourceUrl=row['Direct_PDF_URL'],
                           keyPdf=key_url, pages=pages, questionPages=question_pages,
                           excludedQuestions=excluded,
                           answers={str(k): v for k,v in sorted(answers.items())}))
        print(stamp, len(pages), 'pages;', len(answers), 'source answers', flush=True)
    with ProcessPoolExecutor(max_workers=4) as pool:
        for i, target in enumerate(pool.map(render_page, render_tasks), 1):
            if i % 12 == 0 or i == len(render_tasks):
                print(f'Exported {i}/{len(render_tasks)} remaining page images', flush=True)
    bank = dict(papers=papers, sourceNote='Memory-based papers from the supplied Prepp download pack. Independent practice; not official IBPS paper releases.')
    (OUT/'catalog.json').write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT/'catalog.js').write_text('window.PREVIOUS_PAPERS = '+json.dumps(bank, ensure_ascii=False)+';\n', encoding='utf-8')
    if (OUT/'answer_audit.json').is_file():
        from apply_previous_audit import apply
        apply()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reuse-images', action='store_true', help='Resume an interrupted import with unchanged source PDFs.')
    main(parser.parse_args().reuse_images)
