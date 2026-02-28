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
    # Pattern: Number=Hero 68, Type=Desktop_result.webp
    m = re.search(r'Number=\S+\s+(\d+)', f)
    if m: return int(m.group(1))
    # Pattern: Blocks-4_result.webp
    m = re.search(r'Blocks?-(\d+)', f)
    if m: return int(m.group(1))
    # Pattern: Footer 12_result.webp or Dashboard 15_result.webp
    m = re.search(r'\s(\d+)_result', f)
    if m: return int(m.group(1))
    # Pattern: any number before _result
    m = re.search(r'(\d+)_result', f)
    if m: return int(m.group(1))
    # Last resort: any number
    m = re.search(r'(\d+)', f)
    if m: return int(m.group(1))
    return None

moves = []
skipped = []
for root, dirs, files in os.walk("."):
    if ".git" in root or "scripts" in root or ".github" in root: continue
    for f in files:
        if not f.lower().endswith(".webp"): continue
        old = os.path.join(root, f)
        parts = root.replace("\\", "/").split("/")
        # parts[0] is ".", parts[1] is top-level category
        if len(parts) < 2: continue
        old_cat = parts[1]
        new_cat = CATEGORY_MAP.get(old_cat)
        if not new_cat:
            # Skip already-renamed folders
            if old_cat.islower() or old_cat in CATEGORY_MAP.values():
                continue
            skipped.append(old)
            continue
        path_lower = old.lower()
        device = "mobile" if "mobile" in path_lower else "desktop"
        mode = detect_mode(path_lower)
        num = extract_number(f)
        if num is None:
            skipped.append(old)
            continue
        new_name = f"{new_cat}-{num}.webp"
        new_path = os.path.join(".", new_cat, device, mode, new_name)
        moves.append((old, new_path))

print(f"Found {len(moves)} files to rename")
if skipped:
    print(f"Skipped {len(skipped)} files (couldn't parse)")
    for s in skipped[:5]:
        print(f"  {s}")
print("\nExamples:")
for o, n in moves[:8]:
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
    except Exception as e:
        print(f"  Error: {e}")

print(f"\nCopied {ok} files")
confirm2 = input("Delete old folders? Type yes: ")
if confirm2.strip().lower() == "yes":
    for old_name in CATEGORY_MAP.keys():
        path = f"./{old_name}"
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"  Deleted {old_name}")
print("\nDone! Now run: git add -A && git commit -m 'fix rename' && git push")
