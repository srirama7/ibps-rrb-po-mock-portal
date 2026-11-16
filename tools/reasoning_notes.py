"""Question-specific English deductions reviewed against the displayed source clues."""

def notes():
    result={}
    def put(paper,number,text,status='worked-deduction'):
        result[f'adda-{paper:02}-q{number:03}']={'text':text,'status':status}
    def shared(paper,numbers,text):
        for number in numbers:put(paper,number,text)

    # Coordinates use east as positive x and north as positive y.
    coordinate_sets=[
        (1,[23,24,25], 'Office (0,0), P (12,0), Q (12,−10), R (5,−10), S (5,−12), U (0,−12).',[
            'U has the same x-coordinate as the office and a smaller y-coordinate, so it is south.',
            'G is 31 m east of R, so G = (36,−10). From P the displacement is (24,−10). Distance = √(24² + 10²) = 26 m.',
            'The office is 10 m north of M, so M = (0,−10). From M to S the displacement is (5,−2), which is south-east.']),
        (4,[31,32,33,34], 'A (0,0), J (0,17), K (19,17), P (19,28), E (27,28), M (27,36).',[
            'P is east and north of A, so its direction is north-east.',
            'C is 8 km west of M, so C = (19,36). K = (19,17); C lies directly north of K.',
            'Follow the given route backwards from M via K to A: 8 + 8 + 11 + 19 + 17 = 63 km.',
            'K to E has horizontal separation 8 km and vertical separation 11 km. The straight-line distance is √(8² + 11²) = √185 km.']),
        (7,[13,14,15], 'A (0,0), B (0,8), C (−7,8), D (−7,13), E (−17,13), F (−17,0), G (−9,0).',[
            'G has the same north-south coordinate as A and is 9 m to its west.',
            'Along the stated route from G back to C: GF + FE + ED + DC = 8 + 13 + 10 + 5 = 36 m.',
            'M = (6,0), while B = (0,8). BM = √(6² + 8²) = 10 m.']),
        (8,[37,38,39], 'O (0,0), W (0,12), B (−8,12), A (−8,2), C (−17,2), M (−13,12), Q (−13,18), K (−13,7), E (−17,7).',[
            'M is west and north of O, so it is north-west of O.',
            'F is 5 m north of E, so F = (−17,12). M = (−13,12); F lies directly west of M.',
            'A and O differ by 8 m horizontally and 2 m vertically. AO = √(8² + 2²) = √68 m.']),
        (9,[32,33,34], 'P (0,0), Q (−8,0), R (−8,−10), S (−20,−10), T (−20,−4), Home (−28,−4).',[
            'Relative to Q, T is 12 m west and 4 m south: south-west.',
            'From S to home the displacement is (−8,6). Straight-line distance = √(8² + 6²) = 10 m.',
            'Add every walked segment: 8 + 10 + 12 + 6 + 8 = 44 m.']),
        (10,[33,34,35], 'A (0,0), B (0,10), C (15,10), D (15,−10), E (20,−10), F (20,15).',[
            'F is 20 m east and 5 m north of B, so it is north-east of B.',
            'B to D has horizontal separation 15 m and vertical separation 20 m. BD = √(15² + 20²) = 25 m.',
            'G is 5 m south of F, so G = (20,10). C = (15,10), directly west of G.']),
    ]
    for paper,numbers,coordinates,deductions in coordinate_sets:
        for number,deduction in zip(numbers,deductions):
            put(paper,number,'Take east as positive x and north as positive y. Apply each turn or positional clue to obtain:\n\n'+coordinates+'\n\n'+deduction)

    shared(1,[30,31,32],
        'S and W are sisters because S has no brother. W and P are the grandparents; '
        'their children are K (female) and R (male). R and J are the parents of U and Q. '
        'J is therefore P\'s daughter-in-law. If K marries M, R is M\'s brother-in-law. '
        'For Q32, equal male/female counts force Q to be male: S, W, K and J are the '
        'four females, while P, R, U and Q are the four males. Q is K\'s nephew.')
    shared(2,[15,16,17],
        'The family arrangement used by the source is: A and H are the parents of B and D; '
        'G is H\'s brother; D and F are the parents of C and E. B is unmarried, so '
        'her sister D is married to F, making B F\'s sister-in-law. C is female and '
        'E is male, so E is F\'s son. H, B, D and C are the four females. '
        'If S marries G, S is H\'s sister-in-law.')
    shared(3,[10,11,12],
        'S and R are the parents of sons V and W and daughter Q. V and U are the '
        'parents of Y and T; Y is male and T is not a daughter of V, so T is male. '
        'X is Y\'s wife, which makes her T\'s sister-in-law. P is R\'s sister '
        '(S has no siblings), so W is P\'s nephew. Q is Y\'s aunt. '
        'Among Y, T, P, W and S, P is the female member and the others are male.')
    shared(5,[16,17,18],
        'K and J are the parents of M and N. M is unmarried; N is male and is '
        'married to O. L and I are O\'s parents. N and O have children Q and P; '
        'P is female. J, M, O, I and P already account for five females, so the '
        'limit of at most five females forces Q to be male. Q is K\'s grandson. '
        'M, N and O are the three second-generation members. If A is P\'s husband, '
        'O is A\'s mother-in-law.')
    shared(6,[31,32,33],
        'P is Q\'s father. Q is married to V, whose mother is U; hence U is '
        'Q\'s mother-in-law. Q and V are W\'s parents, and W is married to R. '
        'T is U\'s son and S\'s father, so U is S\'s grandmother. The females '
        'are U, V and W; the males are P, Q, R, S and T. P is V\'s father-in-law. '
        'In Q33, statements I and II hold; R is not established as S\'s brother.')
    shared(7,[38,39,40],
        'Z and S are the parents of brothers W and U. X is Z\'s sister. '
        'W and Y are the parents of V and T. T is Y\'s only son, so V is '
        'female. The four females are S, X, Y and V. V is U\'s niece, '
        'and S is T\'s grandmother.')
    shared(8,[33,34,35],
        'P and S are the parents of Q. Q is the mother of R and T. R is '
        'married to V, and their daughter is U. W is V\'s father, so U is '
        'W\'s granddaughter. S is female and M has the opposite gender, so '
        'M is W\'s brother. The females are S, Q, R and U: four. Among '
        'P, W, V, T and S, S is the female member; the other four are male.')

    # Direct letter and digit manipulations: retain the intermediate sequence.
    direct={
        (1,33): 'DFI, MOR, SUX and EGJ have successive alphabet gaps +2, +3. HJL has gaps +2, +2, so HJL is different.',
        (1,34): 'Apply the changes by position: 478732359 → 387823268. Digits 3 and 2 occur twice, 8 occurs three times, and 6 and 7 occur once. The non-repeated digits are 6 and 7.',
        (1,40): 'The 3rd, 4th, 5th and 8th letters of HIERARCHY are E, R, A and H. HEAR and HARE are two valid words, so more than one word is possible. Select Z.',
        (2,18): 'Apply the succeeding-letter rule to consonants and to letters in even positions; apply the preceding-letter rule to the remaining vowels. ERUPTION becomes DSTQUJNO. No letter repeats.',
        (2,24): 'Ascending order gives 123456789. The second digit from the left is 2; the third from the right is 7. Their product is 14.',
        (2,25): 'The PDF keys ZUGN. However, the two examples do not specify a consistent unique transformation, and ZUGN is not a standard meaningful English word as required by the prompt. A reliable worked rule cannot be recovered from these clues alone; this source item needs publisher clarification.',
        (2,35): 'MPS, TWZ, RUX and GJM advance +3, +3. BDF advances +2, +2, so it is the odd group.',
        (3,18): 'The first, second, third and sixth letters of FELICITOUS are F, E, L and I. FILE and LIFE are distinct meaningful words. Since more than one is possible, select Z.',
        (3,32): 'In LRUK, TGJS, OKNN and BPSA the middle two letters differ by +3. In UDFT, D to F differs by +2. Thus UDFT is different.',
        (4,11): 'The selected letters of ALLEGATION are L, A, I and N. NAIL and LAIN are two meaningful arrangements. More than one word is possible, so select X.',
        (4,17): 'Even digits in descending order are 8642; remaining odd digits in ascending order are 3579. The combined sequence is 86423579. Digits in positions 2, 4, 6 and 8 sum to 6 + 2 + 5 + 9 = 22.',
        (4,40): 'FHI, ACD, PRS and UWX have gaps +2, +1. JKM has gaps +1, +2, so JKM is different.',
        (5,23): 'The second, fourth, sixth and eighth letters of SURPRISE are U, P, I and E. No standard four-letter English word is formed from precisely those letters under the source convention. Select Z.',
        (5,29): 'DCA, IHF, WVT and MLJ have gaps −1, −2. RQP has gaps −1, −1, so RQP is different.',
        (5,40): 'Change each odd digit down by one and each even digit up by one: 76294538 → 67385429. Descending order gives 98765432. The fourth digits from the left and right are 6 and 5; their sum is 11.',
        (6,15): 'The first, third, fifth and seventh letters of TECHNOLOGY are T, C, N and L. These cannot form a standard meaningful four-letter word under the source convention. Select Z.',
        (6,34): 'Change odd digits up by one and even digits down by one: 7854362 → 8763451. Ascending order is 1345678. The third digit is 4.',
        (6,40): 'Replacing vowels by preceding letters and consonants by succeeding letters changes RESOURCES to SDTN TSDDT (without spaces: SDTNTSDDT). S, D and T repeat, giving three repeated letter types.',
        (7,6): 'Apply even −2 and odd −1: 463278293 → 242066082. Digit 2 occurs three times; 0 and 6 occur twice each. Only 2 appears more than twice.',
        (7,29): 'The 3rd, 6th, 8th and 10th letters of FREELOADING are E, O, D and N. DONE and NODE are distinct meaningful words. Select X because more than one word is possible.',
        (8,11): 'The first, third, fifth and seventh letters of EXPLORE are E, P, O and E. No standard meaningful four-letter word is formed from these exact letters under the source convention. Select Z.',
        (8,36): 'DCB, KJI, XWV and UTS run backwards in consecutive alphabetical order. PQR runs forwards, so PQR is different.',
        (8,40): 'Replacing vowels by succeeding letters and consonants by preceding letters changes PROBLEMS to OQPAKFLR. Every resulting letter is different, so none repeats.',
        (9,21): 'Apply odd −1 and even −2 to obtain 268264442. Its 2nd, 4th and 6th digits are 6, 2 and 4; the required sum is 12.',
        (9,35): 'UPR, RMO, LGI and YTV have gaps −5, +2. GBE has gaps −5, +3, so GBE is different.',
        (10,1): 'MOQS, EGIK, TVXZ and PRTV advance by +2 at each step. HJLM advances +2, +2, +1, so HJLM is different.',
        (10,21): 'TURNOVER becomes SVQMPUFQ after the replacements. Alphabetical order is FMPQQSUV. Counting from the right, the fourth letter is Q.',
        (10,32): 'The first, third, fourth and sixth letters of FARMHOUSE are F, R, M and O. FORM and FROM are both meaningful words. Select P because more than one word can be made.',
    }
    for (paper,number),text in direct.items():put(paper,number,text,'source-interpretation-review' if (paper,number)==(2,25) else 'worked-deduction')

    # Venn deductions; "only a few" means some overlap and some non-overlap.
    venn={
        (1,27): 'Some digital are network, and every network is growth, so some digital are growth (I). "Only a few" also requires some digital outside network, excluding the possibility that all digital are network (II). Only I follows.',
        (1,28): 'Some houses are bricks, and no brick is cement; therefore some houses are not cement (II). No statement separates every hut from cement, so I is not established.',
        (1,29): 'The statements do not fix the glue–sharpener overlap. "No glue is sharpener" and "Some glue is sharpener" are exact complementary alternatives. Exactly one must hold, but neither is individually forced. Select either I or II.',
        (2,11): 'Nothing prevents all good objects from also being manual; manual objects need not all be memory. Thus I is possible. Gadget–manual overlap is not determined, so the universal separation in II does not follow.',
        (2,13): 'Some cities are markets and all markets are trade, so some cities are trade (I). Some trade being outside urban does not prevent every urban object from lying within trade. II is therefore possible as well.',
        (2,14): 'The floors–garden overlap is not fixed. "All floors are garden" and "Some floors are not garden" are complementary: either all floors lie in garden or at least one does not. The correct choice is either I or II.',
        (3,23): 'The orange–grapes overlap need not include an object outside apple, so I is not established. Apples may all be bananas if their orange overlap avoids grapes; no statement rules that arrangement out. Only possibility II follows.',
        (3,24): 'Cats can all be placed in the dog–lion overlap without contradicting the existence of other dogs outside lion, so I is possible. "Only a few tigers are lion" explicitly requires some tigers outside lion, making II impossible.',
        (3,26): 'Some magazines are newspapers does not mean every newspaper is a magazine, so I does not follow. Nothing prohibits newspapers from also being books; the non-magazine books can remain elsewhere. II is possible.',
        (5,7): 'Only a few dare are amaze establishes some dare–amaze overlap. Since all amaze are tall, some tall are dare (II). No exclusion prevents all monkeys from lying within amaze, so I is also possible.',
        (5,8): 'Some brothers are smart and no smart object is rare, so some brothers are not rare (II). All boys being brothers does not require them all to be smart, so I does not follow.',
        (5,10): 'Sales can all lie within motor without contradicting the existence of other draw objects outside motor, so I is possible. The given sales–draw overlap need not fall inside motor; consequently a sales–engine overlap is not certain and II does not follow.',
        (6,6): 'Some light objects are time and all time are right, giving some light objects that are right (II). No exclusion prevents all late objects from being time, so I is also possible.',
        (6,7): 'All early objects may be ugly: the statements contain no exclusion preventing that placement. Some travel objects are outside district, but those objects could still be ugly, so II is not forced.',
        (6,8): 'The marks–code relation is not fixed by the statements. "Some marks are code" and "No marks are code" are complementary. Either one must be true, although neither is forced separately.',
        (6,9): 'All good objects can be discount objects; this does not conflict with the partial good–search overlap. No mock–discount overlap is guaranteed. Only possibility I follows.',
        (7,21): '"Only a few blue are rain" requires some blue objects outside rain, proving I. The sky subset of water can lie inside rain while other water objects remain outside blue. Thus all sky being rain is possible (II).',
        (7,23): 'Wave objects belong to green, but the green–plant overlap need not include them, so I is not established. The plant objects in green need not be the wave objects excluded from tower. A plant outside tower is therefore not guaranteed either.',
        (8,29): 'Some flute objects are teacher and no flute object is burger, giving some teachers outside burger (I). Some Spain objects are burger, so those Spain objects cannot be flute. II is false.',
        (8,31): 'No relation forces or excludes all fire–cyber overlap. "No cyber is fire" and "Some cyber is fire" are exact complementary alternatives, so select either I or II.',
        (8,32): 'The common–plan overlap and plan–else overlap may involve different objects, so a common–else overlap is not guaranteed. Some plans are else and no else is mapping, proving some plans are not mapping (II).',
        (9,6): 'Some plants are fruits and no fruit is vegetable, proving some plants are not vegetables (II). Flowers lie within plants but need not intersect the fruit subset, so I does not follow.',
        (9,7): 'Mammals lie within birds, which lie within eggs. Under the exam convention that the named classes have members, some mammals are eggs (I). Birds cannot be reptiles because eggs and reptiles are disjoint, so II is impossible.',
        (10,2): 'The cats–animal overlap can avoid the dog subset of living, so no cats being dogs is possible (I). Nothing states that all animals avoid dogs; II is not a necessary conclusion.',
        (10,3): 'Some covers are white and no cover is a page, so some white objects are not pages (I). Books are pages, and no page is a cover; hence no book is a cover (II). Both follow.',
        (10,4): 'Some games are enjoy and all enjoy are dice, so games and dice do overlap: I is false. This overlap need not contain objects outside toys, and the statements do not otherwise guarantee such dice. II is not established.',
        (10,5): 'Access is a subset of tech and disjoint from request, but other tech objects may be request. Therefore I does not follow. All plan objects may lie in request while the access subset stays outside request; II is possible.',
    }
    for (paper,number),text in venn.items():put(paper,number,text)
    # The publisher's unqualified "only" wording is stronger than the ordinary
    # subset statement used in formal syllogisms. Do not invent missing premises.
    reviews={
        (1,26): '"Only project are completed" ordinarily gives completed ⊆ project. It does not by itself imply that any completed object is outside difficult. II is possible, but I needs an extra exclusion or existence premise. The PDF keys both conclusions without explaining that premise.',
        (2,12): '"Only stadium are arena" ordinarily gives arena ⊆ stadium. It does not force an arena outside match, and it permits arena and sport to be disjoint. Thus the PDF\'s choice of only II is not justified by ordinary subset logic. Additional intended meaning of "only" is needed.',
        (3,25): '"Only pencil are eraser" gives eraser ⊆ pencil. The pen–pencil overlap does not guarantee an eraser–pen overlap, so neither conclusion I nor II is individually established. They are complementary alternatives. The PDF keys only I, which needs an additional intended exclusivity premise.',
        (5,9): '"Only champion is start" ordinarily gives start ⊆ champion. It does not force start to intersect battery, so I is not established. All champions being power remains possible under ordinary subset logic, contrary to the source key of neither. The source\'s intended exclusivity convention needs clarification.',
        (7,22): '"Only leather is brown" gives brown ⊆ leather. It does not prohibit brown from overlapping black or chair. Under ordinary subset logic I remains possible and II is not forced; the source key of only II assumes an additional exclusivity convention.',
        (8,30): '"Only violin are drums" gives drums ⊆ violin. Neither salad nor pasta is explicitly excluded from drums. Thus some drums being salad is possible under ordinary subset logic, while no salad being drums is not forced. The PDF\'s key assumes an additional exclusivity convention.',
        (9,8): 'Some apples are oranges and all oranges are bananas, proving I. "Only bananas are grapes" gives grapes ⊆ bananas but does not guarantee a grape outside oranges. II needs an additional premise. The PDF keys both; the intended meaning of "only" needs clarification.',
    }
    for (paper,number),text in reviews.items():put(paper,number,text,'source-interpretation-review')
    return result
