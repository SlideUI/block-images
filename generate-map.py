#!/usr/bin/env python3
import os, re, json

blocks = []
for root, dirs, files in os.walk("."):
    if ".git" in root or "scripts" in root or ".github" in root: continue
    for f in files:
        if not f.lower().endswith(".webp"): continue
        filepath = os.path.join(root, f)[2:]  # remove ./
        path_lower = filepath.lower()
        
        # Get category from top folder
        cat = filepath.split("/")[0].lower()
        cat = re.sub(r'\s*:\s*', '-', cat)
        cat = cat.replace(" ", "-")
        
        # Device
        device = "mobile" if "mobile" in path_lower else "desktop"
        
        # Mode
        if "accent" in path_lower: mode = "accent"
        elif "dark" in path_lower: mode = "dark"
        else: mode = "light"
        
        # Number
        num = None
        m = re.search(r'Number=\S+\s+(\d+)', f)
        if m: num = int(m.group(1))
        if not num:
            m = re.search(r'Blocks?-(\d+)', f)
            if m: num = int(m.group(1))
        if not num:
            m = re.search(r'\s(\d+)_result', f)
            if m: num = int(m.group(1))
        if not num:
            m = re.search(r'(\d+)_result', f)
            if m: num = int(m.group(1))
        if not num:
            m = re.search(r'(\d+)', f)
            if m: num = int(m.group(1))
        if not num: continue
        
        blocks.append({
            "cat": cat,
            "device": device,
            "mode": mode,
            "num": num,
            "path": filepath
        })

blocks.sort(key=lambda x: (x["cat"], x["device"], x["mode"], x["num"]))
print(f"Total blocks: {len(blocks)}")

cats = {}
for b in blocks:
    k = b["cat"]
    if k not in cats: cats[k] = 0
    cats[k] += 1
print("Categories:")
for k in sorted(cats.keys()):
    print(f"  {k}: {cats[k]}")

with open("blocks.json", "w") as f:
    json.dump(blocks, f)
print("\nSaved blocks.json")
