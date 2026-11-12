import os, sys, json, urllib.request, ssl

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"
DATA_DIR = os.path.join(REPO_ROOT, "data")

def check_links():
    catalog_path = os.path.join(DATA_DIR, "adda_mocks_catalog.json")
    catalog = json.load(open(catalog_path, encoding='utf-8'))
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    all_ok = True
    print("Checking 10 Adda247 publisher PDF URLs...")
    for paper in catalog['papers']:
        pid = paper['id']
        url = paper['pdfUrl']
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                print(f"  {pid}: HTTP {resp.status} - OK ({resp.headers.get('Content-Length', 'unknown')} bytes)")
        except Exception as e:
            print(f"  {pid}: FAILED ({e})")
            all_ok = False
            
    if not all_ok:
        print("FAIL: One or more URLs failed.")
        sys.exit(1)
    else:
        print("PASS: All 10 Adda247 PDF URLs verified live and accessible.")

if __name__ == '__main__':
    check_links()
