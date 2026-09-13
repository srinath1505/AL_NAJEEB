/* =============================================================================
   AL NAJEEB — SITE CONFIGURATION
   -----------------------------------------------------------------------------
   ⚠️  EDIT THIS FILE to plug in the real business details.
   Everything the website shows for contact / branding comes from here.
   After editing, just refresh the page (no build step needed).
   ============================================================================= */
window.SITE_CONFIG = {
  // --- Company ----------------------------------------------------------------
  companyName: "AL NAJEEB",
  companyFull: "AL NAJEEB COSMETICS TRADING L.L.C",
  tagline: "Your Trusted Partner for Quality Personal Care, Healthcare & Beauty Products",
  shortTagline: "Quality Products. Trusted Supply.",

  // --- Logo -------------------------------------------------------------------
  // Drop your logo image into  assets/img/  and put its filename here.
  // Leave blank ("") to use the clean built-in text wordmark instead.
  logo: "assets/img/logo.png",   // TODO: replace with your real logo file (or set to "")

  // --- Contact  (⚠️ TODO: replace the placeholders with real values) ----------
  // WhatsApp number in FULL international format, digits only (no +, spaces or dashes).
  // Example for UAE: "9715XXXXXXXX"
  whatsapp: "97100000000",              // TODO
  phoneDisplay: "+971 00 000 0000",     // TODO  (shown to users)
  phoneDial: "+97100000000",            // TODO  (used by the "call" link)
  email: "info@alnajeeb.example",       // TODO
  address: "United Arab Emirates",      // TODO  (street, area, city)
  hours: "Sat – Thu: 9:00 AM – 9:00 PM", // TODO

  // --- Social links (optional — leave "" to hide) -----------------------------
  instagram: "",
  facebook: "",

  // --- Pricing display --------------------------------------------------------
  currency: "AED",
  showCredit: true,   // show Credit-1 prices alongside Cash

  // --- About carousel copy (drafted — edit freely) ----------------------------
  about: {
    slides: [
      {
        title: "About the Firm",
        body: "AL NAJEEB Cosmetics Trading L.L.C is a UAE-based wholesale supplier of quality personal care, healthcare and beauty products. We bring together trusted international and regional brands under one roof, serving retailers, salons and distributors with dependable supply and competitive pricing."
      },
      {
        title: "Our Product Range",
        body: "From skincare, hair care and cosmetics to baby care, oral care, healthcare and everyday personal hygiene — our catalogue spans hundreds of products across leading brands, available in multiple pack sizes to suit every order."
      },
      {
        title: "Wholesale & Bulk Supply",
        body: "Browse our full digital catalogue with transparent cash and credit pricing, box offers such as 12+1, and clear stock availability. Found what you need? Send an instant enquiry on WhatsApp and our team will confirm availability and order details."
      }
    ]
  }
};
