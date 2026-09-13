# AL NAJEEB — Wholesale Product Catalogue Website

A fast, single-page, searchable digital catalogue for **AL NAJEEB COSMETICS TRADING L.L.C**,
generated from the company price-list PDF. Browse 341 products across 116 brands and 13
categories, filter by brand / availability / offers / price, view multi-size variants, and
send an instant enquiry on WhatsApp.

- **Zero build. Zero dependencies to view.** Double-click `index.html`.
- **Real product photos** extracted from the source PDF.
- **Cash + Credit-1 pricing**, `12+1` offers and live stock status, straight from the PDF.

---

## Quick start

- **View:** double-click `index.html` (or run `python -m http.server 8080` and open
  <http://localhost:8080>).
- **Configure:** edit `site-config.js` (contact details, WhatsApp number, logo, about text).
- **Deploy:** see `DEPLOY.md`.

---

## Folder structure

```
al-najeeb-catalogue/
├─ index.html            Single-page site
├─ site-config.js        ⚙️  EDIT ME — contact info, WhatsApp #, logo, about copy
├─ assets/
│  ├─ css/styles.css     Styling (modern wholesale / clean)
│  ├─ js/app.js          Search, filters, rendering, modal, WhatsApp
│  └─ img/logo.png       Logo (placeholder badge — replace with the real logo)
├─ data/
│  ├─ products.js        window.CATALOGUE — loaded by the page (works offline / file://)
│  ├─ products.json      Same data as canonical JSON (for reuse / re-import)
│  └─ _review.log        Extraction anomaly log (empty = clean)
├─ images/               341 optimised WebP product photos (~6 MB total)
├─ scripts/              Data pipeline (only needed to regenerate data)
│  ├─ extract.py         PDF → products.json + products.js + images
│  └─ taxonomy.py        Brand normalisation + category rules + text cleanup
├─ DEPLOY.md
└─ README.md
```

## Features

- **Search** across product name, brand, category and pack size (all terms must match), e.g.
  `vaseline`, `100ml`, `vitamin c`.
- **Filters:** category chips, brand multi-select (searchable), availability
  (all / in stock / out of stock), `12+1` offers only, and cash-price bands. Sort by name or price.
- **Product modal** with a per-size variants table (Package / Cash / Credit) and a
  variant-aware **Enquire on WhatsApp** button that pre-fills the message.
- **Responsive** (2–5 column grid), lazy-loaded images, keyboard-accessible modal,
  mobile bottom-sheet filters.

---

## Updating the catalogue (new PDF)

The website reads `data/products.js`. Regenerate it whenever the company issues a new price list.

1. Install the one-time Python dependencies:
   ```
   pip install pymupdf pillow
   ```
2. Put the new PDF next to the project folder and update `PDF_PATH` at the top of
   `scripts/extract.py` if the filename changed.
3. Run:
   ```
   python scripts/extract.py
   ```
   It rewrites `data/products.json`, `data/products.js` and all images, then prints a
   validation summary (product / offer / out-of-stock counts). Anything unusual is written
   to `data/_review.log`.
4. Refresh the website. Done.

### Tuning brands & categories

Product names are the source of truth for prices and packages. Brand names and category
assignments are derived automatically in `scripts/taxonomy.py`:

- **Brands** — add or correct entries in the `BRANDS` list (matched as a name prefix).
- **Categories** — adjust the ordered `CATEGORIES` keyword rules (first match wins).
- **One-off fixes** — add an entry to the `OVERRIDES` map (keyed by the exact cleaned,
  uppercase product name) to force a specific brand and/or category.

Re-run `python scripts/extract.py` after any change.

---

## How the data was extracted

The source PDF lays out 4 products per page in a 2×2 grid, each with a photo and a
`NAME / PACKAGE / PRICE(CASH) / CREDIT-1` table. The pipeline:

- parses each page by quadrant coordinates,
- detects **multi-size products** (e.g. Vaseline Jelly Original: 50/100/250/450 ML) and maps
  each size to its cash & credit price,
- reads inline `(12+1)` offers and `(OUT OF STOCK)` markers,
- normalises the PDF's smart punctuation, and
- exports one optimised WebP photo per product.

Validated counts: **341 products · 106 with a 12+1 offer · 4 out of stock · 341 images**.
