#!/usr/bin/env python3
import os, re, json

CATEGORY_SIMPLIFY = {
    "404": "404",
    "about us": "about",
    "announcement bar": "announcement",
    "benefits : statistics": "stats",
    "blog articles": "blog",
    "blog category": "blog-category",
    "cta : banner": "cta",
    "calendar": "calendar",
    "case studies": "case-studies",
    "comparison chart": "comparison",
    "contact us": "contact",
    "courses": "courses",
    "dashboard": "dashboard",
    "faq": "faq",
    "features": "features",
    "footer": "footer",
    "form : survey : quiz": "form",
    "forums : discussion": "forums",
    "gallery": "gallery",
    "hero": "hero",
    "how it works": "howitworks",
    "integrations": "integrations",
    "menu-nav": "menu",
    "miscellaneous": "misc",
    "online booking": "booking",
    "password": "password",
    "payment": "payment",
    "popup": "popup",
    "pricing plan": "pricing",
    "privacy policy": "privacy",
    "product highlight bar": "product-highlight",
    "product page": "product-page",
    "product specs": "product-specs",
    "profile": "profile",
    "registration : progress steps": "registration",
    "reviews": "reviews",
    "services": "services",
    "sign in": "signin",
    "sign up": "signup",
    "simple text": "text",
    "social media": "social",
    "tables": "tables",
    "team": "team",
    "testimonials": "testimonials",
    "trusted badges": "badges",
    "upload : download": "upload",
}

blocks = []
skipped = []

for root, dirs, files in os.walk("."):
    if ".git" in root or "scripts" in root or ".github" in root:
        continue
    for f in files:
        if not f.lower().endswith(".webp"):
            continue
        
        filepath = os.path.join(root, f)
        parts = filepath.split(os.sep)
        if len(parts) < 3:
            continue
        
        original_cat = parts[1]
        simple_cat = CATEGORY_SIMPLIFY.get(original_cat.lower())
        if not simple_cat:
            skipped.append(filepath)
            continue
        
        path_lower = filepath.lower()
        device = "mobile" if "/mobile/" in path_lower or "/mobile\\" in path_lower else "desktop"
        
        if "accent" in path_lower:
            mode = "accent"
        elif "dark" in path_lower:
            mode = "dark"
        else:
            mode = "light"
        
        num = None
        m = re.search(r'Number=\S+\s+(\d+)', f)
        if m:
            num = int(m.group(1))
        if not num:
            m = re.search(r'Blocks?-(\d+)', f)
            if m:
                num = int(m.group(1))
        if not num:
            m = re.search(r'[a-zA-Z]\s+(\d+)_result', f)
            if m:
                num = int(m.group(1))
        if not num:
            m = re.search(r'[a-zA-Z]-(\d+)_result', f)
            if m:
                num = int(m.group(1))
        if not num:
            m = re.search(r'(\d+)_result', f)
            if m:
                val = int(m.group(1))
                if val < 1000:
                    num = val
        if not num:
            skipped.append(filepath)
            continue
        
        rel_path = filepath[2:] if filepath.startswith("./") else filepath
        
        blocks.append({
            "c": simple_cat,
            "d": device,
            "m": mode,
            "n": num,
            "p": rel_path
        })

blocks.sort(key=lambda x: (x["c"], x["d"], x["m"], x["n"]))

cats = {}
for b in blocks:
    k = b["c"]
    if k not in cats:
        cats[k] = {"desktop": {"light": 0, "dark": 0, "accent": 0}, "mobile": {"light": 0, "dark": 0, "accent": 0}}
    cats[k][b["d"]][b["m"]] += 1

print(f"Total blocks mapped: {len(blocks)}")
print(f"Skipped: {len(skipped)}")
if skipped:
    print("Skipped examples:")
    for s in skipped[:10]:
        print(f"  {s}")
print(f"\nCategories ({len(cats)}):")
for k in sorted(cats.keys()):
    total = sum(cats[k]["desktop"].values()) + sum(cats[k]["mobile"].values())
    dl = cats[k]["desktop"]["light"]
    dd = cats[k]["desktop"]["dark"]
    da = cats[k]["desktop"]["accent"]
    print(f"  {k:20s}: {total:4d} total  (desktop: {dl}L {dd}D {da}A)")

with open("blocks.json", "w") as out:
    json.dump(blocks, out, separators=(",", ":"))

size = os.path.getsize("blocks.json")
print(f"\nSaved blocks.json ({size:,} bytes)")
print("Done!")
