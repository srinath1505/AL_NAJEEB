# Deploying the AL NAJEEB Catalogue

This is a **static website** — just HTML, CSS, JavaScript, a data file and images.
There is **no build step** and **no server code**. You can host it anywhere that serves
static files. Pick any one option below.

---

## ✅ Before you publish (2 minutes)

1. Open **`site-config.js`** and replace every value marked `// TODO`:
   - `whatsapp` — your WhatsApp number in full international format, **digits only**
     (e.g. UAE mobile `9715XXXXXXXX`). This powers every "Enquire on WhatsApp" button.
   - `phoneDisplay`, `phoneDial`, `email`, `address`, `hours`, and optional social links.
2. Drop your real logo image into **`assets/img/`** and set `logo:` in `site-config.js`
   to its filename (e.g. `"assets/img/logo.png"`). Leave `logo: ""` to use the text wordmark.
   - If your logo is a full "logo + name" lockup, also set `logoOnly: true` to hide the text.
3. Save. Refresh the page — done. (No rebuild needed.)

---

## Option A — Netlify Drop (easiest, free)

1. Go to <https://app.netlify.com/drop>.
2. Drag the **entire `al-najeeb-catalogue` folder** onto the page.
3. It publishes instantly and gives you a live URL (e.g. `your-site.netlify.app`).
4. To use your own domain: Site settings → Domain management.

## Option B — Vercel (free)

1. Install the CLI once: `npm i -g vercel`.
2. In this folder run: `vercel` and follow the prompts (accept defaults).
3. For production: `vercel --prod`.

## Option C — GitHub Pages (free)

1. Create a new GitHub repository and upload the contents of this folder.
2. Repo → **Settings → Pages** → Source: `Deploy from a branch` → branch `main`, folder `/root`.
3. Your site appears at `https://<username>.github.io/<repo>/`.

## Option D — Any web host / cPanel

Upload the whole folder to your `public_html` (or web root) via FTP/File Manager.
Make sure `index.html` sits at the root you want visitors to land on.

---

## Just want to view it locally?

- **Double-click `index.html`** — it opens in your browser and works fully offline.
- Or serve it (nicer for some browsers): from this folder run
  `python -m http.server 8080` and open <http://localhost:8080>.

---

## Notes

- All product images are already optimised WebP (~6 MB total for 341 products), so the
  site loads fast. Images lazy-load as you scroll.
- Nothing calls the internet except the WhatsApp links you click, so the catalogue works
  offline and behind firewalls.
- To update prices/products when the company issues a new PDF, see **README.md → Updating the catalogue**.
