import glob

for p in glob.glob('*.*') + glob.glob('data/*.*'):
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
        if '__ADDA_MOCKS_CATALOG__' in text or '__ADDA_TESTS_DATA__' in text:
            print(f"File {p} has match:")
            for l in text.split('\n'):
                if '__ADDA_MOCKS_CATALOG__' in l or '__ADDA_TESTS_DATA__' in l:
                    print("  ", l[:120])
