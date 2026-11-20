"""Cache OCR for development audits, preserving every original question image."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
EXE=Path(os.environ.get('TESSERACT_EXE',str(ROOT/'tools/prepp_cache/tesseract-portable/tesseract.exe')))
OUT=ROOT/'tools/prepp_cache/audit/tesseract'

def extract(image):
    path=Path(image);target=OUT/path.parent.name/(path.stem+'.txt')
    if target.exists():return
    target.parent.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,OMP_THREAD_LIMIT='1')
    r=subprocess.run([str(EXE),str(path),'stdout','--psm','6','-l','eng'],capture_output=True,check=True,env=env)
    target.write_bytes(r.stdout)

if __name__=='__main__':
    assert EXE.is_file(), 'Set TESSERACT_EXE to a local Tesseract executable with English data.'
    bank=json.loads((ROOT/'data/previous/catalog.json').read_text(encoding='utf-8'))
    for paper in bank['papers']:
        if paper['date'].startswith(('2022','2023')):continue
        dest=ROOT/'tools/prepp_cache/audit/native_images'/paper['id'];dest.mkdir(parents=True,exist_ok=True)
        for source in paper['pages']:
            target=dest/(Path(source).stem+'.png')
            if target.exists():continue
            image=Image.open(ROOT/source).convert('L').point(lambda x:255 if x>145 else 0)
            image.resize((int(image.width*1.7),int(image.height*1.7))).convert('RGB').save(target)
    paths=sorted((ROOT/'tools/prepp_cache/audit/native_images').glob('prepp-*/*.png'))
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,_ in enumerate(pool.map(extract,paths),1):
            if i%13==0:print(f'OCR: {i}/{len(paths)} pages',flush=True)
