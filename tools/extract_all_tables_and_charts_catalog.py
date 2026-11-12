import re

with open(r"C:\Users\amogh\.gemini\antigravity-cli\brain\6f8eed6e-c0fe-4f44-984a-266d54d8f253\.system_generated\steps\633\output.txt", encoding='utf-8') as f:
    text = f.read()

sections = text.split("==================== CHECKING ")
for sec in sections[1:]:
    lines = sec.split("\n")
    pid = lines[0].replace(" ====================", "").strip()
    print(f"\n####################### {pid} #######################")
    
    # Find all Directions
    matches = re.finditer(r'(Directions?\s*[\(\[]?\d+\s*[-–to]+\s*\d+[\)\]]?.*?)(?=\n\s*\([a-e]\)|\n\s*Ans|\n\s*Q\d+|\Z)', sec, re.DOTALL)
    seen = set()
    for m in matches:
        dtext = m.group(1).strip()
        # Clean up snippet
        first_few = " ".join([l.strip() for l in dtext.split("\n")[:4] if l.strip()])
        if first_few not in seen:
            seen.add(first_few)
            print(f"  * {first_few}\n")
