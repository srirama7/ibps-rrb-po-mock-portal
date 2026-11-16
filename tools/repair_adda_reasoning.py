"""Restore reasoning question content from the linked Adda source PDFs.

Edits preserve IDs, answer indexes and quant records. Explanation records are
curated separately from publisher keys; source references are not worked solutions.
"""
import json
import re
from pathlib import Path

from repair_adda_quant import publish_copies

ROOT = Path(__file__).resolve().parents[1]
INSTRUCTIONS = ('Study the statements and decide which conclusions necessarily follow. '
                'Use only the stated relationships.')

RESTORED_INEQUALITIES = {
    (3,6): ('P > Q = R ≥ S < T; U ≤ S > W', 'P > T', 'W < P'),
    (3,7): ('M = N ≤ O > G < Q ≤ R; S < R = T', 'G < T', 'G ≥ R'),
    (3,8): ('B ≥ C ≥ D = E > F ≤ G < Y ≤ H', 'C < E', 'G ≤ D'),
    (9,14): ('J < Q ≤ L = M; K = Q > P', 'J < P', 'M > P'),
    (9,15): ('A < K < T = C > Y; T = N > P', 'N > A', 'C > P'),
    (9,16): ('G ≥ H > I = L < M; V ≤ K < O', 'O ≥ I', 'L > O'),
    (10,22): ('G ≤ H = I; I > J = K < L', 'G ≤ L', 'H > K'),
    (10,23): ('U < S = T; U < V = W ≤ X', 'S > V', 'T > W'),
    (10,24): ('M < N = P; S ≤ Q = R > P', 'Q > M', 'S ≤ N'),
    (10,25): ('A > B ≥ C; C > D = E > F', 'A > F', 'B > E'),
    (10,26): ('E = F > G ≤ H < I; G ≥ U = R', 'I > R', 'H ≥ U'),
}

CODING_10 = '''Study the following information carefully and answer the question.
In a certain code language:
“Rain plain sky cloud” is coded as “sf gi yt cn”
“Cloud cricket ball Pencil” is coded as “te ku fa cn”
“Lawn cricket plain home” is coded as “fa je gi ho”
“Sky lawn park” is coded as “yt ho dw”'''


def repair_content(tests):
    for (paper, number), (statements, first, second) in RESTORED_INEQUALITIES.items():
        q = tests[paper-1]['questions'][number-1]
        q['stem'] = (f'Statements: {statements}\n\nConclusions:\n'
                     f'I. {first}\nII. {second}\n\n{INSTRUCTIONS}')
        q['topic'] = 'Inequalities'
        q['diagrams'] = []
        q.pop('diagramCaption', None)
    for number in range(11,15):
        q = tests[9]['questions'][number-1]
        lead = q['stem'].split('\n')[0].strip()
        q['stem'] = lead + '\n\n' + CODING_10
        q['topic'] = 'Coding-Decoding'
    for number, prompt in [
        (9, 'Which of the following is correct?\nI. H sits just right of B\n'
            'II. N and F face in the same direction\nIII. K faces north'),
        (30, 'Which of the following is not true?\nI. A lives just above O\n'
             'II. One floor gap between W and Q\nIII. M lives above E')]:
        q = tests[9]['questions'][number-1]
        marker = '8 persons sit' if number == 9 else 'Ten persons live'
        q['stem'] = prompt + '\n\n' + q['stem'][q['stem'].index(marker):].strip()
    for paper, number, index, text in [
        (4,9,3,'Both (a) and (b)'), (4,9,4,'Both (b) and (c)'),
        (4,22,4,'Both (a) and (c)'), (9,27,4,'Both (a) and (c)')]:
        tests[paper-1]['questions'][number-1]['options'][index] = text
    tests[8]['questions'][39]['options'] = ['K and F','L and D','G and K','I and H','D and G']

    # Translated copies of conclusions were previously left behind as extra I/II
    # lines. Retain the first complete pair, then the original instructions.
    for test in tests:
        for q in test['questions'][:40]:
            if 'Statements:' not in q['stem'] or not re.search(r'[A-Z]\s*[<>=≥≤]',q['stem']):
                continue
            match = re.search(r'Conclusions?:\s*(.*)',q['stem'],re.S|re.I)
            if not match:
                continue
            conditions = re.findall(r'\b(II|I)\.\s*([A-Z]\s*[<>=≥≤]\s*[A-Z])',match[1])
            unique = {}
            for label, condition in conditions:
                unique.setdefault(label,condition)
            if set(unique) == {'I','II'}:
                q['stem'] = (q['stem'][:match.start()].strip() + '\n\nConclusions:\n'
                    + 'I. ' + unique['I'] + '\nII. ' + unique['II'] + '\n\n' + INSTRUCTIONS)
                q['topic'] = 'Inequalities'


def add_source_pages(tests, pdf_dir):
    import pymupdf
    for test in tests:
        pages={}
        with pymupdf.open(pdf_dir/(test['id']+'.pdf')) as doc:
            for i,page in enumerate(doc):
                for match in re.finditer(r'(?m)^Q\s*\.?\s*(\d+)\.', page.get_text()):
                    pages.setdefault(int(match[1]),i+1)
        for q in test['questions'][:40]:
            q['sourcePdfPage'] = pages[q['number']]


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--pdf-dir',type=Path,default=ROOT/'tools/pdf_cache')
    args=parser.parse_args()
    tests=json.loads((ROOT/'data/adda_tests.json').read_text(encoding='utf-8'))['tests']
    repair_content(tests)
    add_source_pages(tests,args.pdf_dir)
    publish_copies(tests)
    print('Restored reasoning source content and PDF page references.')
