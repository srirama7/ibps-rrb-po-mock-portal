"""Apply source-PDF-verified quant repairs and synchronize all published copies.

Run from any directory. Repairs are idempotent. Keep question IDs and answer order
stable so saved attempts continue to refer to the same questions.
"""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
APPROX = 'What approximate value should come in place of the question mark (?)?'


def repair(tests):
    original = json.dumps(tests, ensure_ascii=False)
    def q(paper, number):
        return tests[paper - 1]['questions'][number - 1]

    def replace(paper, number, old, new):
        question = q(paper, number)
        if new not in question['stem']:
            pattern = re.compile(r'\s+'.join(re.escape(part) for part in old.split()))
            assert pattern.search(question['stem']), (paper, number, old)
            question['stem'] = pattern.sub(lambda _: new, question['stem'])

    def note(paper, numbers, text):
        for number in numbers:
            question = q(paper, number)
            if text not in question['stem']:
                question['stem'] = text + '\n\n' + question['stem']

    def diagrams(paper, number, paths, caption=None):
        question = q(paper, number)
        question['diagrams'] = paths
        if paths and caption:
            question['diagramCaption'] = caption
        else:
            question.pop('diagramCaption', None)

    def image(paper, number, page, image_number, caption):
        diagrams(paper, number,
                 [f'data/diagrams/adda-{paper:02}_page{page}_Image{image_number}.png'], caption)

    # Restore fractions that were embedded images in the PDFs.
    replace(2, 75, 'A spends of his income on food and of remaining in transport.',
            'A spends 33 1/3% of his income on food and 14 2/7% of the remaining income on transport.')
    replace(2, 76, 'decreased by kg.', 'decreased by y/16 kg.')
    replace(2, 77, 'age of C is of the present age of A.',
            'age of C is 100/9% of the present age of A.')
    replace(3, 78, 'in seconds.', 'in 60/11 seconds.')
    replace(7, 78, 'sold at the profit', 'sold at a profit of 33 1/3%')
    replace(7, 79, 'sphere is of the hypotenuse', 'sphere is 12 1/2% of the hypotenuse')
    replace(9, 66, 'visited in F are of total', 'visited in F are 7/5 of total')
    replace(9, 73, 'woman\nis more than', 'woman\nis 100/3% more than')

    # Q60 has a text formula; all subsequent formula images were off by one.
    diagrams(3, 60, [])
    for number, page, image_number in [(61, 32, 160), (62, 33, 165),
                                        (63, 33, 166), (64, 33, 167)]:
        image(3, number, page, image_number, 'Approximation equation')

    # The ten image-only equations belong to Q65–Q74, not Q56–Q65.
    for number in range(56, 75):
        diagrams(7, number, [])
    for number, page, image_number in [(65, 34, 164), (66, 34, 165),
            (67, 35, 170), (68, 35, 171), (69, 35, 172), (70, 36, 177),
            (71, 36, 178), (72, 36, 179), (73, 37, 184), (74, 37, 185)]:
        image(7, number, page, image_number,
              'Quadratic equations' if number < 70 else 'Approximation equation')
    # Use the English text version of this bilingual image-only formula.
    q(7, 70)['stem'] = ('14.98% of 240 − 20.01% of 60 = √?\n' + APPROX)
    diagrams(7, 70, [])

    diagrams(8, 60, [])  # Image175 belongs to Q62, where it is already present.

    # Remove residual translated formula fragments; retain one English expression.
    for paper, number, formula in [
        (4, 62, '14.99² + 24 − (1/4) of 99 = ?'),
        (4, 65, '√780 − √443 = ? − 39% of 499'),
        (5, 54, '349 + (5/9) of 35 = ? − 19.98% of 240'),
        (5, 58, '89.99% of 240 + (3/5) of 79 = ? − 79.98'),
        (5, 59, '√140 + 5.01² + 40% of 199 = ? × 12.99'),
        (6, 49, '11.02³ + 199.09 = ? − 29.98% of 401'),
        (6, 51, '35 × (4/9) + 79 × (3/5) = √? × 4'),
    ]:
        q(paper, number)['stem'] = formula + '\n' + APPROX
    # The correct equation is already in the source image; remove garbled text.
    q(10, 48)['stem'] = APPROX

    # Shared directions must accompany every question that needs them.
    note(8, range(41, 46), 'Note: Each student likes either physics or chemistry.')
    note(8, range(46, 51), 'Note: The total number of females in each village is 80.')
    note(10, range(64, 69), 'Note: The total number of females in company D is 500.')
    q(8, 80)['options'] = [
        'Neither statement I nor statement II alone is sufficient.',
        'Statement II alone is sufficient, but statement I alone is not sufficient.',
        'Either statement I or statement II alone is sufficient.',
        'Both statements together are necessary; neither statement alone is sufficient.',
        'Statement I alone is sufficient, but statement II alone is not sufficient.',
    ]

    # The second image in these sets is just a translated duplicate.
    for paper, numbers, english_image in [
        (3, range(47, 53), 'data/diagrams/adda-03_page27_Image135.jpeg'),
        (3, range(53, 59), 'data/diagrams/adda-03_page30_Image149.png'),
        (6, range(52, 58), 'data/diagrams/adda-06_page28_Image142.jpeg'),
        (7, range(41, 47), 'data/diagrams/adda-07_page25_Image124.png'),
    ]:
        for number in numbers:
            question = q(paper, number)
            question['diagrams'] = [english_image]

    # Separate prose, Markdown headers, and final rows before rendering tables.
    for test in tests:
        for question in test['questions'][40:]:
            if '|---|' not in question['stem']:
                continue
            normalized = []
            for line in question['stem'].splitlines():
                if '|' in line:
                    start, end = line.index('|'), line.rindex('|')
                    if start:
                        normalized.extend([line[:start].strip(), ''])
                    normalized.append(line[start:end + 1].strip())
                    if line[end + 1:].strip():
                        normalized.extend(['', line[end + 1:].strip()])
                else:
                    normalized.append(line)
            question['stem'] = '\n'.join(normalized)

    # Explicitly assign the question types that the keyword guesser mislabels.
    for paper, ranges, topic in [
        (1, [(41, 46), (68, 70), (76, 80)], 'Data Interpretation'),
        (2, [(46, 51), (57, 62)], 'Data Interpretation'),
        (3, [(47, 58), (65, 66)], 'Data Interpretation'),
        (4, [(41, 55)], 'Data Interpretation'),
        (5, [(41, 53)], 'Data Interpretation'),
        (6, [(41, 46), (52, 57)], 'Data Interpretation'),
        (7, [(41, 46), (51, 55)], 'Data Interpretation'),
        (8, [(41, 50)], 'Data Interpretation'),
        (9, [(51, 55), (66, 70)], 'Data Interpretation'),
        (10, [(64, 68), (71, 75)], 'Data Interpretation'),
        (1, [(63, 67)], 'Quadratic Equations'),
        (2, [(67, 71)], 'Quadratic Equations'),
        (6, [(76, 80)], 'Quadratic Equations'),
        (7, [(65, 69)], 'Quadratic Equations'),
        (8, [(51, 56)], 'Quadratic Equations'),
        (9, [(76, 80)], 'Quadratic Equations'),
        (10, [(76, 80)], 'Quadratic Equations'),
        (7, [(60, 64)], 'Number Series'),
        (7, [(70, 74)], 'Simplification & Approximation'),
        (8, [(80, 80)], 'Data Sufficiency'),
    ]:
        for lo, hi in ranges:
            for number in range(lo, hi + 1):
                q(paper, number)['topic'] = topic
    for paper, number, topic in [(1, 61, 'Mensuration'),
            (7, 56, 'Problems on Ages'), (7, 57, 'Mixture & Alligation'),
            (7, 58, 'Partnership'), (7, 59, 'Average')]:
        q(paper, number)['topic'] = topic

    # Replace stale placeholder answers in explanations with actual option text.
    # Remove template assertions of a calculation when no worked solution exists.
    worked = {
        (7, 63): 'Subtract consecutive cubes: 1708 − 8³ = 1196; '
            '1196 − 7³ = 853; 853 − 6³ = 637; 637 − 5³ = 512; '
            '512 − 4³ = 448; 448 − 3³ = 421. The last term should be 421, so 444 is wrong.',
        (8, 80): 'Let A, B and C denote the positive fill/fill/drain rates. '
            'The given relation is A − C = 0.3(B − C). Statement I gives B = 1/5 '
            'but leaves A and C undetermined. Statement II gives A = 2.5C but no '
            'absolute rate. Together: 1.5C = 0.3(1/5 − C), so C = 1/30 and '
            'A = 1/12. A fills the tank in 12 minutes. Both statements are needed.',
        (2, 75): 'Food uses 1/3 of income. Transport uses 1/7 of the remaining '
            '2/3, or 2/21 of income. Total spending is 3/7 of income. '
            'Income = 9000 × 7/3 = Rs. 21000.',
        (2, 76): 'The new average is 15y/16. Thus (12y + 72)/14 = 15y/16, '
            'giving y = 64. The heavier new student weighs 40 kg and the other '
            'weighs 32 kg; the difference is 8 kg.',
        (2, 77): 'C = (100/9)% of A = A/9. Put A = 9k and B = 7k, so C = k. '
            'The total age is 3 × (22 + 8/12) = 68 years. Hence 17k = 68 '
            'and C is 4 years old.',
        (3, 78): 'Combined length = 300 m. Opposite-direction speed sum = '
            '300 ÷ (60/11) = 55 m/s. With speed ratio 6:5, the speed difference '
            'is 5 m/s. Same-direction crossing time = 300/5 = 60 seconds.',
        (7, 78): 'Let B cost b. Its selling price, and thus A\'s cost, is 1.5b. '
            'A sells at 33 1/3% profit, so its selling price is 2b. '
            'b + 2b = 672 gives b = 224; A\'s cost is Rs. 336.',
        (7, 79): 'Triangle area = 128 × 16 = 2048 m². If its equal legs are a, '
            'then a²/2 = 2048, so a = 64 m and the hypotenuse is 64√2 m. '
            'Sphere radius = (1/8) × 64√2 = 8√2 m. Surface area = '
            '4π × (8√2)² = 512π m².',
        (9, 66): 'The graph gives non-vegetarians in A = 150, vegetarians in '
            'B = 100 and non-vegetarians in D = 120. F has (7/5) × 150 = 210 '
            'vegetarians and 1.5 × 100 = 150 non-vegetarians. '
            'The required difference is 210 + 150 − 120 = 240.',
        (9, 73): 'A woman works at 4/3 of a man\'s rate. Required men = '
            '30 × (1500/1000) × (9/5) × (10/10) × (4/3) = 108.',
    }
    for test in tests:
        paper = test['number']
        for question in test['questions'][40:]:
            idx = question['answerIndex']
            answer = f'Answer: ({chr(97 + idx)}) {question["options"][idx]}'
            solution = worked.get((paper, question['number']))
            question['explanation'] = answer + '\n\n' + (
                solution or 'This answer follows the source PDF answer key. '
                'A worked solution is not available for this question.')
    return original != json.dumps(tests, ensure_ascii=False)


def publish_copies(tests):
    data = ROOT / 'data'
    (data / 'adda_tests.json').write_text(
        json.dumps({'tests': tests}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (data / 'adda_tests_data.js').write_text(
        'window.__ADDA_TESTS_DATA__ = ' + json.dumps({'tests': tests}, ensure_ascii=False)
        + ';\n', encoding='utf-8')
    for test in tests:
        (data / 'licensed_adda' / (test['id'] + '.json')).write_text(
            json.dumps(test, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    tests = json.loads((ROOT / 'data/adda_tests.json').read_text(encoding='utf-8'))['tests']
    changed = repair(tests)
    if changed:
        publish_copies(tests)
    print('Applied quant repairs.' if changed else 'Quant repairs already applied.')
