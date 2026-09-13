# -*- coding: utf-8 -*-
"""
AL NAJEEB catalogue extractor.

Turns the source price-list PDF into:
  data/products.json   -- canonical data
  data/products.js     -- window.CATALOGUE = {...}  (loaded via <script>, works on file://)
  images/pNN_qX.webp   -- one optimized product photo per product
  data/_review.log     -- anomalies to eyeball

Re-runnable: point PDF_PATH at a new price list and re-run to regenerate everything.

Usage:  python scripts/extract.py
"""
import os
import re
import io
import json
import sys

import fitz  # PyMuPDF
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy  # noqa: E402

# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                 # al-najeeb-catalogue/
PDF_PATH = os.path.join(os.path.dirname(ROOT), "AL_NAJEEB_PRODUCT_LIST_CASH_v5.1.26.pdf")
IMG_DIR = os.path.join(ROOT, "images")
DATA_DIR = os.path.join(ROOT, "data")

MAX_IMG_DIM = 700          # px, long edge
WEBP_QUALITY = 82

EXPECTED_PRODUCTS = 341
EXPECTED_OFFERS = 106   # verified against raw PDF: 106 products carry a (12+1) price offer
EXPECTED_OOS = 4

review = []


def log(msg):
    review.append(msg)


# ---------------------------------------------------------------------------
# Text parsing
# ---------------------------------------------------------------------------
SIZE_TOKEN = re.compile(r"^\d+(?:\.\d+)?(?:ML|GM|G|L|KG|MG)$", re.I)
OFFER_RE = re.compile(r"\(\s*(\d+)\s*\+\s*(\d+)\s*\)")
NUM_RE = re.compile(r"\d+(?:\.\d+)?")


def parse_page_blocks(page):
    """Return a list of raw product dicts in reading order for one page."""
    raw = page.get_text()
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    blocks = []
    i = 0
    n = len(lines)
    while i < n:
        if lines[i] == "NAME":
            # name -> until PACKAGE
            i += 1
            name_parts = []
            while i < n and lines[i] != "PACKAGE":
                name_parts.append(lines[i]); i += 1
            # package -> until PRICE(CASH)
            i += 1
            pkg_parts = []
            while i < n and lines[i] != "PRICE(CASH)":
                pkg_parts.append(lines[i]); i += 1
            # cash -> until CREDIT-1
            i += 1
            cash_parts = []
            while i < n and lines[i] != "CREDIT-1":
                cash_parts.append(lines[i]); i += 1
            # credit -> until next NAME
            i += 1
            credit_parts = []
            while i < n and lines[i] != "NAME":
                credit_parts.append(lines[i]); i += 1
            blocks.append({
                "name": taxonomy.clean_text(" ".join(name_parts)),
                "package": taxonomy.clean_text(" ".join(pkg_parts)),
                "cash_str": " ".join(cash_parts),
                "credit_str": " ".join(credit_parts),
            })
        else:
            i += 1
    return blocks


def extract_offer(s):
    m = OFFER_RE.search(s)
    if m:
        return f"{m.group(1)}+{m.group(2)}"
    return None


def strip_offers(s):
    return OFFER_RE.sub(" ", s)


def numbers(s):
    return [float(x) for x in NUM_RE.findall(strip_offers(s))]


def build_variants(block):
    """Turn a raw block into (variants, offer). Handles multi-size products."""
    pkg = block["package"]
    offer = extract_offer(block["cash_str"]) or extract_offer(block["credit_str"])
    cash_nums = numbers(block["cash_str"])
    credit_nums = numbers(block["credit_str"])

    tokens = pkg.split()
    is_multi = len(tokens) >= 2 and all(SIZE_TOKEN.match(t) for t in tokens)

    variants = []
    if is_multi and len(cash_nums) >= len(tokens) and len(credit_nums) >= len(tokens):
        for idx, size in enumerate(tokens):
            variants.append({
                "package": size.upper(),
                "cash": cash_nums[idx],
                "credit": credit_nums[idx],
                "cashRaw": f"AED {fmt(cash_nums[idx])}",
                "creditRaw": f"AED {fmt(credit_nums[idx])}",
            })
    else:
        cash = cash_nums[0] if cash_nums else None
        credit = credit_nums[0] if credit_nums else None
        variants.append({
            "package": pkg or "-",
            "cash": cash,
            "credit": credit,
            "cashRaw": f"AED {fmt(cash)}" if cash is not None else "-",
            "creditRaw": f"AED {fmt(credit)}" if credit is not None else "-",
        })
        if is_multi:
            log(f"[multi?] '{block['name']}' pkg='{pkg}' cash={cash_nums} credit={credit_nums} "
                f"-> counts didn't line up, kept single")
    return variants, offer


def fmt(x):
    if x is None:
        return "-"
    return str(int(x)) if float(x).is_integer() else f"{x:g}"


# ---------------------------------------------------------------------------
# Coordinates: quadrants, OOS, images
# ---------------------------------------------------------------------------
def quadrant_of(x, y, w, h):
    xmid, ymid = w / 2, h / 2
    if y < ymid:
        return 1 if x < xmid else 2
    return 3 if x < xmid else 4


def name_quadrants(page):
    """Quadrant for each NAME label, in reading order (matches parse_page_blocks order)."""
    w, h = page.rect.width, page.rect.height
    words = page.get_text("words")  # x0,y0,x1,y1,word,block,line,wordno
    qs = []
    for wd in words:
        if wd[4] == "NAME":
            qs.append((quadrant_of(wd[0], wd[1], w, h), wd[0], wd[1]))
    return qs


def oos_quadrants(page):
    """Quadrants that contain an (OUT OF STOCK) marker."""
    w, h = page.rect.width, page.rect.height
    txt = page.get_text().upper()
    if "OUT OF STOCK" not in txt:
        return set()
    rects = page.search_for("OUT OF STOCK")
    quads = set()
    for r in rects:
        cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        quads.add(quadrant_of(cx, cy, w, h))
    return quads


def image_by_quadrant(doc, page):
    """Return {quadrant: xref} choosing the largest-area image in each quadrant."""
    w, h = page.rect.width, page.rect.height
    best = {}  # quad -> (area, xref)
    for img in page.get_images(full=True):
        xref = img[0]
        try:
            rects = page.get_image_rects(xref)
        except Exception:
            rects = []
        for r in rects:
            cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
            q = quadrant_of(cx, cy, w, h)
            area = r.width * r.height
            if q not in best or area > best[q][0]:
                best[q] = (area, xref)
    return {q: xref for q, (area, xref) in best.items()}


def export_image(doc, xref, out_path):
    """Export an embedded image (by xref) to an optimized WebP on white background."""
    pix = fitz.Pixmap(doc, xref)
    if pix.n - pix.alpha >= 4:  # CMYK -> RGB
        pix = fitz.Pixmap(fitz.csRGB, pix)
    mode = "RGBA" if pix.alpha else "RGB"
    img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    img.thumbnail((MAX_IMG_DIM, MAX_IMG_DIM), Image.LANCZOS)
    img.save(out_path, "WEBP", quality=WEBP_QUALITY, method=6)


# ---------------------------------------------------------------------------
def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:60] or "item"


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    # clean old images
    for f in os.listdir(IMG_DIR):
        if f.lower().endswith(".webp"):
            os.remove(os.path.join(IMG_DIR, f))

    doc = fitz.open(PDF_PATH)
    products = []
    seen_ids = {}
    offer_count = 0
    oos_count = 0

    for pi in range(1, len(doc)):  # skip page 1 (cover)
        page = doc[pi]
        page_no = pi + 1
        blocks = parse_page_blocks(page)
        quads = name_quadrants(page)
        oos = oos_quadrants(page)
        imgs = image_by_quadrant(doc, page)

        if len(blocks) != len(quads):
            log(f"[warn] page {page_no}: {len(blocks)} blocks but {len(quads)} NAME labels")

        for bi, block in enumerate(blocks):
            if not block["name"]:
                continue
            q = quads[bi][0] if bi < len(quads) else (bi + 1)
            variants, offer = build_variants(block)
            brand, category = taxonomy.classify(block["name"])
            in_stock = q not in oos

            # image
            image_rel = ""
            if q in imgs:
                fname = f"p{page_no:02d}_q{q}.webp"
                try:
                    export_image(doc, imgs[q], os.path.join(IMG_DIR, fname))
                    image_rel = f"images/{fname}"
                except Exception as e:
                    log(f"[img-fail] page {page_no} q{q} '{block['name']}': {e}")
            else:
                log(f"[no-img] page {page_no} q{q} '{block['name']}'")

            # unique id
            base = slugify(block["name"])
            seen_ids[base] = seen_ids.get(base, 0) + 1
            pid = base if seen_ids[base] == 1 else f"{base}-{seen_ids[base]}"

            if offer:
                offer_count += 1
            if not in_stock:
                oos_count += 1

            # price sanity
            if any(v["cash"] is None for v in variants):
                log(f"[no-price] page {page_no} q{q} '{block['name']}' cash='{block['cash_str']}'")

            products.append({
                "id": pid,
                "name": block["name"],
                "brand": brand,
                "category": category,
                "image": image_rel,
                "variants": variants,
                "offer": offer,
                "inStock": in_stock,
                "sourcePage": page_no,
            })

    # facets
    brands = sorted({p["brand"] for p in products}, key=str.lower)
    categories = sorted({p["category"] for p in products}, key=str.lower)
    counts = {
        "products": len(products),
        "offers": offer_count,
        "outOfStock": oos_count,
        "brands": len(brands),
        "categories": len(categories),
    }

    payload = {
        "products": products,
        "brands": brands,
        "categories": categories,
        "counts": counts,
    }

    with open(os.path.join(DATA_DIR, "products.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA_DIR, "products.js"), "w", encoding="utf-8") as f:
        f.write("window.CATALOGUE = ")
        json.dump(payload, f, ensure_ascii=False)
        f.write(";\n")
    with open(os.path.join(DATA_DIR, "_review.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(review) if review else "No anomalies logged.\n")

    # report
    print("=== EXTRACTION SUMMARY ===")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print(f"  anomalies logged: {len(review)}")
    print("=== VALIDATION ===")
    ok = True
    for label, got, exp in [("products", counts["products"], EXPECTED_PRODUCTS),
                            ("offers", offer_count, EXPECTED_OFFERS),
                            ("out-of-stock", oos_count, EXPECTED_OOS)]:
        status = "OK" if got == exp else "MISMATCH"
        if got != exp:
            ok = False
        print(f"  {label}: {got} (expected {exp}) -> {status}")
    imgs_written = len([f for f in os.listdir(IMG_DIR) if f.endswith('.webp')])
    print(f"  images written: {imgs_written}")
    print("RESULT:", "PASS" if ok else "CHECK _review.log")


if __name__ == "__main__":
    main()
