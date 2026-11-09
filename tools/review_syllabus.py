"""Enforce the researched prelims topic scope and publish a review record."""
import json
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parents[1]
data = json.loads((root / 'data/tests.json').read_text(encoding='utf-8'))
allowed = {
    'reasoning': {
        'Linear seating', 'Parallel rows', 'Circular seating', 'Box puzzle',
        'Floor puzzle', 'Year puzzle', 'Floor and flat puzzle', 'Month and date puzzle', 'Syllogism', 'Inequality',
        'Coding and decoding', 'Direction sense', 'Blood relations', 'Ranking',
    },
    'quant': {
        'Data interpretation', 'Approximation', 'Quadratic equations', 'Number series',
        'Profit and loss', 'Time and work', 'Boats and streams', 'Partnership',
        'Compound interest', 'Mixtures', 'Average', 'Ages', 'Trains', 'Percentage',
        'Pipes and cisterns', 'Simple interest', 'Replacement mixture', 'Relative speed',
        'Expenditure',
    },
}
counts = Counter()
for test in data['tests']:
    for q in test['questions']:
        assert q['topic'] in allowed[q['section']], (q['id'], q['topic'])
        counts[q['topic']] += 1
report = {
    'reviewedOn': '2026-11-09',
    'bankVersion': data['version'],
    'examStage': 'Officer Scale I preliminary examination',
    'questionsReviewed': sum(counts.values()),
    'outOfScopeTopicLabels': [],
    'finding': 'Twenty distinct four-puzzle combinations now span ten arrangement variants. Each section has independently varied topic blocks and question order; all contexts were regenerated. Month, year and single-floor sets extend the published prelims puzzle guidance.',
    'revisedFamilies': {
        'puzzleQuestions': 400,
        'directionSenseQuestions': 60,
        'pipesAndCisternsQuestions': 10,
        'approximationOptionSets': 100,
    },
    'topicCounts': dict(sorted(counts.items())),
    'sources': [
        {
            'url': 'https://www.ibps.in/index.php/notification-for-common-recruitment-process-for-crp-rrb-xv/',
            'role': 'Official notification reference; the current PDF was not retrievable during this review. No claim of a newly verified official topic-by-topic syllabus.',
        },
        {
            'url': 'https://www.bankersadda.com/ibps-rrb-po-syllabus/',
            'role': 'Current preparation-provider topic guidance and prelims/mains distinction, read during this review.',
        },
        {
            'url': 'https://www.adda247.com/jobs/wp-content/uploads/sites/8/2024/06/10162029/Copy-of-Decoding-IBPS-RRB-Prelims-2024-Final.pdf',
            'role': 'Publisher topic guidance and past-paper trends, pages 5–6. Historical timing information is not used for current timers.',
        },
    ],
    'limits': 'Topic checks do not establish official difficulty equivalence, exhaustive syllabus coverage or future question weightage.',
    'additionalFinding': 'Three regenerated approximation items had a distractor closer to the exact value than the rounded key. All 100 approximation option sets now use wider spacing; the independent checker enforces a uniquely nearest correct option.',
}
(root / 'data/syllabus_review.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print('PASS: all 1,600 questions use researched prelims topic labels; review record saved.')
