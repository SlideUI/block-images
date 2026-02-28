import fs from "fs";
import path from "path";

const OUT = path.join(process.cwd(), "manifest.json");

const exts = new Set([".webp", ".png", ".jpg", ".jpeg", ".svg"]);

function walk(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const out = [];
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...walk(full));
    else out.push(full);
  }
  return out;
}

// repo root contains your category folders (404, About Us, Features, etc)
// ignore hidden folders + github config folders + manifest itself
const root = process.cwd();
const ignore = new Set([".git", ".github", "node_modules"]);

const top = fs.readdirSync(root, { withFileTypes: true })
  .filter(d => d.isDirectory() && !ignore.has(d.name))
  .map(d => d.name);

const files = top.flatMap(folder => walk(path.join(root, folder)))
  .filter(f => exts.has(path.extname(f).toLowerCase()));

const items = files.map(abs => {
  const rel = abs.replace(root + path.sep, "").split(path.sep).join("/"); // "About Us/Desktop/Accent Mode/file.webp"
  const parts = rel.split("/");
  const [category, device, mode, ...rest] = parts;
  const filename = rest.join("/");

  const url = `https://raw.githubusercontent.com/SlideUI/block-images/main/${encodeURI(rel)}`;

  // create stable id
  const id = rel
    .replace(/\.[^.]+$/, "")
    .replace(/\s+/g, "-")
    .replace(/[^a-zA-Z0-9-_\/]/g, "")
    .toLowerCase();

  return { id, category, device, mode, filename: path.basename(filename), url };
});

items.sort((a, b) => a.id.localeCompare(b.id));

fs.writeFileSync(OUT, JSON.stringify({ count: items.length, items }, null, 2));
console.log(`✅ Wrote ${items.length} items to ${OUT}`);
