/* =============================================================================
   AL NAJEEB — Catalogue app  (vanilla JS, zero-build)
   Data comes from window.CATALOGUE (data/products.js) and window.SITE_CONFIG.
   ============================================================================= */
(function () {
  "use strict";

  var CFG = window.SITE_CONFIG || {};
  var DATA = window.CATALOGUE || { products: [], brands: [], categories: [], counts: {} };
  var PRODUCTS = DATA.products || [];
  var CUR = CFG.currency || "AED";
  var SHOW_CREDIT = CFG.showCredit !== false;
  var BATCH = 48;

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  // ---------- helpers ----------
  function money(n) {
    if (n === null || n === undefined || isNaN(n)) return "—";
    return Number.isInteger(n) ? String(n) : Number(n).toFixed(2);
  }
  function minCash(p) {
    var vals = p.variants.map(function (v) { return v.cash; }).filter(function (v) { return v != null; });
    return vals.length ? Math.min.apply(null, vals) : null;
  }
  function minCredit(p) {
    var vals = p.variants.map(function (v) { return v.credit; }).filter(function (v) { return v != null; });
    return vals.length ? Math.min.apply(null, vals) : null;
  }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function debounce(fn, ms) {
    var t; return function () { var a = arguments, c = this; clearTimeout(t); t = setTimeout(function () { fn.apply(c, a); }, ms); };
  }

  // ---------- WhatsApp ----------
  function waNumber() { return (CFG.whatsapp || "").replace(/[^0-9]/g, ""); }
  function waLink(text) {
    return "https://wa.me/" + waNumber() + "?text=" + encodeURIComponent(text);
  }
  function productMessage(p, variant) {
    var v = variant || p.variants[0];
    var lines = [];
    lines.push("Hello " + (CFG.companyName || "AL NAJEEB") + ", I'd like to enquire about:");
    lines.push("");
    lines.push("*" + p.name + "*" + (v && v.package && v.package !== "-" ? " (" + v.package + ")" : ""));
    if (v && v.cash != null) {
      var priceLine = "Cash: " + CUR + " " + money(v.cash);
      if (SHOW_CREDIT && v.credit != null) priceLine += "  |  Credit-1: " + CUR + " " + money(v.credit);
      lines.push(priceLine);
    }
    if (p.offer) lines.push("Offer: " + p.offer);
    lines.push("");
    lines.push("Please share availability and order details.");
    return lines.join("\n");
  }
  function generalMessage() {
    return "Hello " + (CFG.companyName || "AL NAJEEB") + ", I'd like to enquire about your wholesale catalogue and pricing.";
  }

  // ---------- state ----------
  var state = {
    search: "",
    category: "All",
    brands: {},        // brand -> true
    avail: "all",      // all | in | out
    offersOnly: false,
    priceMin: 0,
    priceMax: 100000,
    sort: "featured"
  };
  var filtered = [];
  var rendered = 0;

  // ---------- config-driven chrome ----------
  function applyConfig() {
    // logo: shown as a badge beside the wordmark; falls back to wordmark-only if missing.
    // Set CFG.logoOnly = true if your logo is a full lockup and you want to hide the text wordmark.
    var logo = $("#brandLogo");
    if (CFG.logo) {
      logo.src = CFG.logo;
      logo.alt = CFG.companyFull || CFG.companyName || "Logo";
      logo.hidden = false;
      logo.onload = function () { if (CFG.logoOnly) $(".brand-wordmark").style.display = "none"; };
      logo.onerror = function () { logo.hidden = true; }; // fall back to wordmark
    }
    if (CFG.companyName) { $("#brandName").textContent = CFG.companyName; $("#footerName").textContent = CFG.companyName; }
    if (CFG.companyFull) { $("#heroTitle").textContent = CFG.companyFull; $("#footerFull").textContent = CFG.companyFull; document.title = CFG.companyFull + " — Wholesale Product Catalogue"; }
    if (CFG.tagline) { $("#heroTag").innerHTML = escapeHtml(CFG.tagline); $("#footerTag").textContent = CFG.tagline; }

    // hero stats
    var c = DATA.counts || {};
    var stats = [
      { n: c.products || PRODUCTS.length, l: "Products" },
      { n: (c.brands || DATA.brands.length) + "+", l: "Brands" },
      { n: (c.categories || DATA.categories.length), l: "Categories" },
      { n: "Cash + Credit", l: "Pricing", small: true }
    ];
    $("#heroStats").innerHTML = stats.map(function (s) {
      return "<li><b" + (s.small ? " style='font-size:1.05rem'" : "") + ">" + s.n + "</b><span>" + s.l + "</span></li>";
    }).join("");

    // carousel
    buildCarousel((CFG.about && CFG.about.slides) || []);

    // contact links
    var wl = waLink(generalMessage());
    ["#headerWa", "#contactWa", "#footWa"].forEach(function (sel) { var el = $(sel); if (el) el.href = wl; });
    if (CFG.phoneDial) { $("#footPhone").href = "tel:" + CFG.phoneDial; $("#footPhone").textContent = CFG.phoneDisplay || CFG.phoneDial; }
    if (CFG.email) { $("#footEmail").href = "mailto:" + CFG.email; $("#footEmail").textContent = CFG.email; }
    $("#footAddress").textContent = CFG.address || "";
    $("#footHours").textContent = CFG.hours || "";
    var social = $("#footSocial"), sHtml = "";
    if (CFG.instagram) sHtml += "<a href='" + CFG.instagram + "' target='_blank' rel='noopener'>Instagram</a>";
    if (CFG.facebook) sHtml += "<a href='" + CFG.facebook + "' target='_blank' rel='noopener'>Facebook</a>";
    social.innerHTML = sHtml;
    $("#copyright").textContent = "© " + new Date().getFullYear() + " " + (CFG.companyFull || CFG.companyName || "AL NAJEEB") + ". All Rights Reserved.";
  }

  // ---------- carousel ----------
  function buildCarousel(slides) {
    if (!slides.length) { $("#about").style.display = "none"; return; }
    var track = $("#carouselTrack"), dots = $("#carouselDots");
    track.innerHTML = slides.map(function (s, i) {
      return "<div class='slide'><span class='slide-num'>0" + (i + 1) + " / 0" + slides.length + "</span>" +
        "<h3>" + escapeHtml(s.title) + "</h3><p>" + escapeHtml(s.body) + "</p></div>";
    }).join("");
    dots.innerHTML = slides.map(function (_, i) { return "<button role='tab' aria-label='Slide " + (i + 1) + "'></button>"; }).join("");
    var idx = 0, dotBtns = $$("button", dots), timer;
    function go(i) {
      idx = (i + slides.length) % slides.length;
      track.style.transform = "translateX(-" + (idx * 100) + "%)";
      dotBtns.forEach(function (d, di) { d.classList.toggle("active", di === idx); });
    }
    function auto() { clearInterval(timer); timer = setInterval(function () { go(idx + 1); }, 6000); }
    dotBtns.forEach(function (d, di) { d.addEventListener("click", function () { go(di); auto(); }); });
    $("#carNext").addEventListener("click", function () { go(idx + 1); auto(); });
    $("#carPrev").addEventListener("click", function () { go(idx - 1); auto(); });
    go(0); auto();
  }

  // ---------- facets ----------
  function categoryCounts() {
    var m = {}; PRODUCTS.forEach(function (p) { m[p.category] = (m[p.category] || 0) + 1; }); return m;
  }
  function brandCounts() {
    var m = {}; PRODUCTS.forEach(function (p) { m[p.brand] = (m[p.brand] || 0) + 1; }); return m;
  }
  function buildChips() {
    var counts = categoryCounts(), cats = ["All"].concat(DATA.categories);
    $("#categoryChips").innerHTML = cats.map(function (c) {
      var n = c === "All" ? PRODUCTS.length : (counts[c] || 0);
      return "<button class='chip" + (c === state.category ? " active" : "") + "' data-cat='" + escapeHtml(c) + "'>" +
        escapeHtml(c) + "<span class='c-count'>" + n + "</span></button>";
    }).join("");
  }
  function buildBrandList(filter) {
    var counts = brandCounts(), f = (filter || "").toLowerCase();
    var list = DATA.brands.filter(function (b) { return !f || b.toLowerCase().indexOf(f) >= 0; });
    $("#brandList").innerHTML = list.map(function (b) {
      return "<label class='brand-item'><input type='checkbox' value='" + escapeHtml(b) + "'" +
        (state.brands[b] ? " checked" : "") + "><span>" + escapeHtml(b) + "</span>" +
        "<span class='b-count'>" + (counts[b] || 0) + "</span></label>";
    }).join("") || "<p style='color:var(--muted);font-size:.85rem;padding:6px'>No brands found.</p>";
  }

  // ---------- filtering ----------
  function matches(p) {
    if (state.category !== "All" && p.category !== state.category) return false;
    if (state.avail === "in" && !p.inStock) return false;
    if (state.avail === "out" && p.inStock) return false;
    if (state.offersOnly && !p.offer) return false;
    var brandKeys = Object.keys(state.brands);
    if (brandKeys.length && !state.brands[p.brand]) return false;
    var priceActive = !(state.priceMin === 0 && state.priceMax === 100000);
    if (priceActive) {
      var mc = minCash(p);
      if (mc == null || mc < state.priceMin || mc > state.priceMax) return false;
    }
    if (state.search) {
      var q = state.search.toLowerCase();
      var hay = (p.name + " " + p.brand + " " + p.category + " " +
        p.variants.map(function (v) { return v.package; }).join(" ")).toLowerCase();
      // all whitespace-separated tokens must be present
      var toks = q.split(/\s+/).filter(Boolean);
      for (var i = 0; i < toks.length; i++) { if (hay.indexOf(toks[i]) < 0) return false; }
    }
    return true;
  }
  function sortList(arr) {
    var s = state.sort;
    if (s === "name-asc") arr.sort(function (a, b) { return a.name.localeCompare(b.name); });
    else if (s === "price-asc") arr.sort(function (a, b) { return (minCash(a) || 1e9) - (minCash(b) || 1e9); });
    else if (s === "price-desc") arr.sort(function (a, b) { return (minCash(b) || -1) - (minCash(a) || -1); });
    else {
      // featured: in-stock first, then offers, then name
      arr.sort(function (a, b) {
        if (a.inStock !== b.inStock) return a.inStock ? -1 : 1;
        if (!!a.offer !== !!b.offer) return a.offer ? -1 : 1;
        return a.name.localeCompare(b.name);
      });
    }
    return arr;
  }
  function applyFilters() {
    filtered = sortList(PRODUCTS.filter(matches));
    rendered = 0;
    $("#productGrid").innerHTML = "";
    $("#emptyState").hidden = filtered.length !== 0;
    renderNextBatch();
    updateMeta();
    updateFilterCount();
  }

  // ---------- rendering ----------
  function cardHtml(p) {
    var multi = p.variants.length > 1;
    var mc = minCash(p), mcr = minCredit(p);
    var badges = "";
    if (p.offer) badges += "<span class='badge badge-offer'>" + escapeHtml(p.offer) + "</span>";
    else badges += "<span></span>";
    if (!p.inStock) badges += "<span class='badge badge-oos'>Out of stock</span>";
    var pkgLine = multi ? (p.variants.length + " sizes available") : escapeHtml(p.variants[0].package || "");
    var priceHtml = "<div class='card-price'>";
    if (multi) priceHtml += "<span class='price-from'>From</span>";
    priceHtml += "<span class='price-cash'><span class='cur'>" + CUR + "</span>" + money(mc) + "</span>";
    if (SHOW_CREDIT && mcr != null) priceHtml += "<span class='price-credit'>Credit " + CUR + " " + money(mcr) + "</span>";
    priceHtml += "</div>";
    var img = p.image
      ? "<img loading='lazy' decoding='async' src='" + escapeHtml(p.image) + "' alt='" + escapeHtml(p.name) + "' onerror=\"this.style.visibility='hidden'\">"
      : "<div style='color:var(--muted);font-size:.8rem'>No image</div>";
    return "<button class='card" + (p.inStock ? "" : " oos") + "' data-id='" + escapeHtml(p.id) + "'>" +
      "<div class='card-media'>" + img + "<div class='card-badges'>" + badges + "</div></div>" +
      "<div class='card-body'>" +
      "<span class='card-brand'>" + escapeHtml(p.brand) + "</span>" +
      "<span class='card-name'>" + escapeHtml(p.name) + "</span>" +
      "<span class='card-pkg'>" + pkgLine + "</span>" +
      priceHtml +
      "<span class='card-cta'>View details &rarr;</span>" +
      "</div></button>";
  }
  function renderNextBatch() {
    var slice = filtered.slice(rendered, rendered + BATCH);
    if (!slice.length) return;
    var html = slice.map(cardHtml).join("");
    $("#productGrid").insertAdjacentHTML("beforeend", html);
    rendered += slice.length;
  }
  function updateMeta() {
    var el = $("#resultsCount");
    el.textContent = filtered.length === PRODUCTS.length
      ? "Showing all " + PRODUCTS.length + " products"
      : "Showing " + filtered.length + " of " + PRODUCTS.length + " products";
    renderActiveFilters();
  }
  function renderActiveFilters() {
    var chips = [];
    if (state.category !== "All") chips.push({ k: "cat", label: state.category });
    Object.keys(state.brands).forEach(function (b) { chips.push({ k: "brand", label: b, val: b }); });
    if (state.avail !== "all") chips.push({ k: "avail", label: state.avail === "in" ? "In stock" : "Out of stock" });
    if (state.offersOnly) chips.push({ k: "offers", label: "12+1 offers" });
    if (!(state.priceMin === 0 && state.priceMax === 100000)) chips.push({ k: "price", label: CUR + " " + state.priceMin + "–" + (state.priceMax === 100000 ? "50+" : state.priceMax) });
    if (state.search) chips.push({ k: "search", label: '"' + state.search + '"' });
    $("#activeFilters").innerHTML = chips.map(function (c) {
      return "<span class='af-chip'>" + escapeHtml(c.label) + "<button data-k='" + c.k + "' data-v='" + escapeHtml(c.val || "") + "' aria-label='Remove'>&times;</button></span>";
    }).join("");
  }
  function updateFilterCount() {
    var n = 0;
    if (state.category !== "All") n++;
    n += Object.keys(state.brands).length;
    if (state.avail !== "all") n++;
    if (state.offersOnly) n++;
    if (!(state.priceMin === 0 && state.priceMax === 100000)) n++;
    var badge = $("#filterCount");
    badge.textContent = n; badge.hidden = n === 0;
  }

  // ---------- modal ----------
  var lastFocus = null, currentModalVariant = 0, currentModalProduct = null;
  function openModal(p) {
    currentModalProduct = p; currentModalVariant = 0;
    lastFocus = document.activeElement;
    $("#modalBrand").textContent = p.brand;
    $("#modalTitle").textContent = p.name;
    $("#modalCat").textContent = p.category + "  ·  Ref. page " + p.sourcePage;
    var img = $("#modalImg");
    if (p.image) { img.src = p.image; img.alt = p.name; img.style.visibility = "visible"; }
    else { img.removeAttribute("src"); img.alt = ""; }
    var badges = "";
    if (p.offer) badges += "<span class='badge badge-offer'>" + escapeHtml(p.offer) + " offer</span>";
    $("#modalBadges").innerHTML = badges;
    $("#modalAvail").innerHTML = p.inStock
      ? "<span class='avail-pill avail-in'>● In stock</span>"
      : "<span class='avail-pill avail-out'>● Out of stock</span>";

    var multi = p.variants.length > 1;
    var rows = p.variants.map(function (v, i) {
      var sel = i === 0 ? " selected" : "";
      return "<tr class='" + (multi ? "selectable" : "") + sel + "' data-vi='" + i + "'>" +
        (multi ? "<td class='v-radio'><input type='radio' name='variant' " + (i === 0 ? "checked" : "") + "></td>" : "") +
        "<td class='v-pkg'>" + escapeHtml(v.package || "-") + "</td>" +
        "<td class='v-cash'>" + CUR + " " + money(v.cash) + "</td>" +
        (SHOW_CREDIT ? "<td class='v-credit'>" + CUR + " " + money(v.credit) + "</td>" : "") +
        "</tr>";
    }).join("");
    var head = "<tr>" + (multi ? "<th></th>" : "") + "<th>Package</th><th>Cash</th>" + (SHOW_CREDIT ? "<th>Credit-1</th>" : "") + "</tr>";
    $("#modalVariants").innerHTML = "<table><thead>" + head + "</thead><tbody>" + rows + "</tbody></table>" +
      (multi ? "<p class='variant-hint'>Select a size for your WhatsApp enquiry.</p>" : "");

    if (multi) {
      $$("#modalVariants tr.selectable").forEach(function (tr) {
        tr.addEventListener("click", function () {
          currentModalVariant = parseInt(tr.getAttribute("data-vi"), 10);
          $$("#modalVariants tr").forEach(function (t) { t.classList.remove("selected"); });
          tr.classList.add("selected");
          var radio = tr.querySelector("input[type=radio]"); if (radio) radio.checked = true;
          refreshModalWa();
        });
      });
    }
    refreshModalWa();
    if (CFG.phoneDial) { $("#modalCall").href = "tel:" + CFG.phoneDial; } else { $("#modalCall").style.display = "none"; }

    var modal = $("#productModal");
    modal.hidden = false;
    document.body.style.overflow = "hidden";
    $(".modal-close").focus();
  }
  function refreshModalWa() {
    var p = currentModalProduct; if (!p) return;
    $("#modalWa").href = waLink(productMessage(p, p.variants[currentModalVariant]));
  }
  function closeModal() {
    $("#productModal").hidden = true;
    document.body.style.overflow = "";
    if (lastFocus && lastFocus.focus) lastFocus.focus();
    currentModalProduct = null;
  }

  // ---------- mobile filter sheet ----------
  function openSheet() { $("#filters").classList.add("open"); $("#sheetBackdrop").hidden = false; document.body.style.overflow = "hidden"; $("#filterToggle").setAttribute("aria-expanded", "true"); }
  function closeSheet() { $("#filters").classList.remove("open"); $("#sheetBackdrop").hidden = true; document.body.style.overflow = ""; $("#filterToggle").setAttribute("aria-expanded", "false"); }

  // ---------- events ----------
  function bind() {
    // search
    var si = $("#searchInput");
    si.addEventListener("input", debounce(function () {
      state.search = si.value.trim();
      $("#searchClear").hidden = !si.value;
      applyFilters();
    }, 180));
    $("#searchClear").addEventListener("click", function () { si.value = ""; state.search = ""; $("#searchClear").hidden = true; applyFilters(); si.focus(); });

    // sort
    $("#sortSelect").addEventListener("change", function () { state.sort = this.value; applyFilters(); });

    // category chips
    $("#categoryChips").addEventListener("click", function (e) {
      var b = e.target.closest(".chip"); if (!b) return;
      state.category = b.getAttribute("data-cat");
      $$(".chip", this).forEach(function (c) { c.classList.remove("active"); });
      b.classList.add("active");
      applyFilters();
    });

    // availability
    $("#availSeg").addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      state.avail = b.getAttribute("data-avail");
      $$("button", this).forEach(function (x) { x.classList.remove("active"); });
      b.classList.add("active"); applyFilters();
    });
    // price
    $("#priceSeg").addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      state.priceMin = parseFloat(b.getAttribute("data-min"));
      state.priceMax = parseFloat(b.getAttribute("data-max"));
      $$("button", this).forEach(function (x) { x.classList.remove("active"); });
      b.classList.add("active"); applyFilters();
    });
    // offers
    $("#offersOnly").addEventListener("change", function () { state.offersOnly = this.checked; applyFilters(); });

    // brands
    $("#brandSearch").addEventListener("input", debounce(function () { buildBrandList(this.value); }.bind($("#brandSearch")), 120));
    $("#brandList").addEventListener("change", function (e) {
      var cb = e.target; if (cb.type !== "checkbox") return;
      if (cb.checked) state.brands[cb.value] = true; else delete state.brands[cb.value];
      applyFilters();
    });

    // clear
    function clearAll() {
      state = { search: "", category: "All", brands: {}, avail: "all", offersOnly: false, priceMin: 0, priceMax: 100000, sort: state.sort };
      si.value = ""; $("#searchClear").hidden = true; $("#offersOnly").checked = false;
      $$("#availSeg button").forEach(function (x, i) { x.classList.toggle("active", i === 0); });
      $$("#priceSeg button").forEach(function (x, i) { x.classList.toggle("active", i === 0); });
      buildChips(); buildBrandList("");
      $$(".chip").forEach(function (c) { c.classList.toggle("active", c.getAttribute("data-cat") === "All"); });
      applyFilters();
    }
    $("#clearFilters").addEventListener("click", clearAll);
    $("#emptyClear").addEventListener("click", clearAll);

    // active filter chip removal
    $("#activeFilters").addEventListener("click", function (e) {
      var btn = e.target.closest("button"); if (!btn) return;
      var k = btn.getAttribute("data-k"), v = btn.getAttribute("data-v");
      if (k === "cat") { state.category = "All"; buildChips(); }
      else if (k === "brand") { delete state.brands[v]; buildBrandList($("#brandSearch").value); }
      else if (k === "avail") { state.avail = "all"; $$("#availSeg button").forEach(function (x, i) { x.classList.toggle("active", i === 0); }); }
      else if (k === "offers") { state.offersOnly = false; $("#offersOnly").checked = false; }
      else if (k === "price") { state.priceMin = 0; state.priceMax = 100000; $$("#priceSeg button").forEach(function (x, i) { x.classList.toggle("active", i === 0); }); }
      else if (k === "search") { state.search = ""; si.value = ""; $("#searchClear").hidden = true; }
      applyFilters();
    });

    // product cards -> modal
    $("#productGrid").addEventListener("click", function (e) {
      var card = e.target.closest(".card"); if (!card) return;
      var p = PRODUCTS.find(function (x) { return x.id === card.getAttribute("data-id"); });
      if (p) openModal(p);
    });

    // modal close
    $$("[data-close]").forEach(function (el) { el.addEventListener("click", closeModal); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { if (!$("#productModal").hidden) closeModal(); else closeSheet(); }
    });

    // mobile filters
    $("#filterToggle").addEventListener("click", openSheet);
    $("#filtersClose").addEventListener("click", closeSheet);
    $("#applyFilters").addEventListener("click", closeSheet);
    $("#sheetBackdrop").addEventListener("click", closeSheet);

    // infinite scroll
    var sentinel = $("#loadMoreSentinel");
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) renderNextBatch();
      }, { rootMargin: "600px" });
      io.observe(sentinel);
    } else {
      window.addEventListener("scroll", function () {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 800) renderNextBatch();
      });
    }
  }

  // ---------- init ----------
  function init() {
    if (!PRODUCTS.length) {
      $("#resultsCount").textContent = "Could not load product data. Make sure data/products.js is present.";
      return;
    }
    applyConfig();
    buildChips();
    buildBrandList("");
    bind();
    applyFilters();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
