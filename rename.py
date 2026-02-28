#!/usr/bin/env python3
import os, re, shutil

CATEGORY_MAP = {
    "404": "404", "About Us": "about", "Announcement Bar": "announcement",
    "Benefits : Statistics": "stats", "Blog Articles": "blog",
    "Blog Category": "blog-category", "CTA : Banner": "cta",
    "Calendar": "calendar", "Case Studies": "case-studies",
    "Comparison Chart": "comparison", "Contact Us": "contact",
    "Courses": "courses", "Dashboard": "dashboard", "FAQ": "faq",
    "Features": "features", "Footer": "footer",
    "Form : Survey : Quiz": "form", "Forums : Discussion": "forums",
    "Gallery": "gallery", "Hero": "hero", "How It Works": "howitworks",
    "Integrations": "integrations", "Menu-Nav": "menu",
    "Miscellaneous": "misc", "Online Booking": "booking",
    "Password": "password", "Payment": "payment", "Popup": "popup",
    "Pricing Plan": "pricing", "Privacy Policy": "privacy",
    "Product Highlight Bar": "product-highlight",
    "Product Page": "product-page", "Product Specs": "product-specs",
    "Profile": "profile", "Registration : Progress Steps": "registration",
    "Reviews": "reviews", "Services": "services", "Sign In": "signin",
    "Sign Up": "signup", "Simple Text": "text", "Social Media": "social",
    "Tables": "tables", "Team": "team", "Testimonials": "testimonials",
    "Trusted Badges": "badges", "Upload : Download": "upload",
}

def detect_mode(p):
    p = p.lower()
    if "accent" in p: return "accent"
    elif "dark" in p: return "dark"
    else: return "light"

def extract_number(f):
    m = re.search(r'Number=\w+\s*(\d+)', f)
    if m: return int(m.group(1))
    m = re.search(r'Blocks?-(\d+)', f)
    if m: return int(m.group(1))
    m = re.search(r'(\d+)_result', f)
    if m: return int(m.group(1))
    m = re.search(r'(\d+)', f)
    if m: return int(m.group(1))
    return None

moves = []
for root, dirs, files in os.walk("."):
    if ".git" in root or "scripts" in root: continue
    for f in files:
        if not f.lower().endswith(".webp"): continue
        old = os.path.join(root, f)
        parts = old.split(os.sep)
        if len(parts) < 2: continue
        old_cat = parts[1]
        new_cat = CATEGORY_MAP.get(old_cat)
        if not new_cat: continue
        path_lower = old.lower()
        device = "mobile" if "mobile" in path_lower else "desktop"
        mode = detect_mode(path_lower)
        num = extract_number(f)
        if num is None: continue
        new_name = f"{new_cat}-{num}.webp"
        new_path = os.path.join(".", new_cat, device, mode, new_name)
        moves.append((old, new_path))

print(f"Found {len(moves)} files to rename")
print("Examples:")
for o, n in moves[:5]:
    print(f"  {o}")
    print(f"  -> {n}")
    print()

confirm = input("Type yes to rename: ")
if confirm.strip().lower() != "yes":
    print("Aborted"); exit()

used = set()
ok = 0
for old, new in moves:
    if new in used:
        base, ext = os.path.splitext(new)
        s = 1
        while f"{base}-{s}{ext}" in used: s += 1
        new = f"{base}-{s}{ext}"
    used.add(new)
    os.makedirs(os.path.dirname(new), exist_ok=True)
    try:
        shutil.copy2(old, new)
        ok += 1
    except: pass

print(f"Copied {ok} files")
confirm2 = input("Delete old folders? Type yes: ")
if confirm2.strip().lower() == "yes":
    for old_name in CATEGORY_MAP.keys():
        if os.path.exists(f"./{old_name}"):
            shutil.rmtree(f"./{old_name}")
            print(f"  Deleted {old_name}")
print("Done! Now run: git add -A && git commit -m 'clean rename' && git push")
