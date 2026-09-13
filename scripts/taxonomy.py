# -*- coding: utf-8 -*-
"""
Taxonomy + text-cleaning helpers for the AL NAJEEB catalogue extractor.

Kept separate from extract.py so brand/category corrections don't touch the
extraction logic. Everything here is deterministic and re-runnable.
"""
import re

# The source PDF uses three "smart" glyphs that render as boxes in some terminals:
#   U+2013 EN DASH  (–)  -> used as a separator: "WELLS – CASTOR", "PADS –ALOE"
#   U+2019 APOSTROPHE(’) -> "JOHNSON’S" (apostrophe) AND "LA’FRESH" (word separator)
#   U+201D QUOTE     (”) -> rare, treated as an inch/quote mark


def clean_text(s: str) -> str:
    """Normalise the source PDF's smart glyphs and whitespace. Names are kept
    UPPERCASE to preserve source fidelity. Real hyphens (AXIS-Y, ANTI-AGING,
    DMT-4333) are left untouched."""
    if not s:
        return ""
    # 1) apostrophe-S: letter + ’ + S at a word boundary  ->  'S  (JOHNSON’S)
    s = re.sub(r"(?<=[A-Za-z])’(?=[Ss]\b)", "'", s)
    # 2) any other ’ acts as a separator/space  (LA’FRESH -> LA FRESH)
    s = s.replace("’", " ")
    # 3) closing double quote -> straight quote (inches etc.)
    s = s.replace("”", '"')
    # 4) en/em dash (with or without surrounding spaces) -> " - " separator
    s = re.sub(r"\s*[–—]\s*", " - ", s)
    # collapse whitespace only (do NOT touch real hyphens)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ---------------------------------------------------------------------------
# BRANDS  --  ordered, most-specific (multi-word) first; matched as a prefix
# or substring of the cleaned UPPERCASE name. First hit wins.
# ---------------------------------------------------------------------------
BRANDS = [
    ("BEAUTY OF JOSEON", "Beauty of Joseon"),
    ("LADY SPEED STICK", "Lady Speed Stick"),
    ("ONE MAN SHOW", "One Man Show"),
    ("HEAD&SHOULDERS", "Head & Shoulders"),
    ("HEAD & SHOULDERS", "Head & Shoulders"),
    ("FAIR&LOVELY", "Fair & Lovely"),
    ("SKIN DOCTOR", "Skin Doctor"),
    ("LADY DIANA", "Lady Diana"),
    ("LASER WHITE", "Laser White"),
    ("ACTIVE SHOTS", "Active Shots"),
    ("ALMALAKY", "Almalaky Royal"),
    ("KWICK RELEEF", "Kwick Releef"),
    ("HENNA SPEEDY", "Henna Speedy"),
    ("CANSIN BANT", "Cansin Bant"),
    ("MADAM RANEE", "Madam Ranee"),
    ("DERMA ROLLER", "Derma Roller"),
    ("PEDICURE FILE", "Pedicure File"),
    ("NAIL CLIPPER", "Nail Clipper"),
    ("PALM CARE", "Palm Care"),
    ("GOLD MEDAL", "Gold Medal"),
    ("TIGER BALM", "Tiger Balm"),
    ("DEEP HEAT", "Deep Heat"),
    ("AXE BRAND", "Axe Brand"),
    ("LOVE JOJO", "Love Jojo"),
    ("TOUCH ME", "Touch Me"),
    ("KAS MARK", "Kas Mark"),
    ("CREME 21", "Creme 21"),
    ("ST. IVES", "St. Ives"),
    ("ST IVES", "St. Ives"),
    ("DR.RASHEL", "Dr. Rashel"),
    ("DR RASHEL", "Dr. Rashel"),
    ("DR.ALTHEA", "Dr. Althea"),
    ("DR.CARE", "Dr. Care"),
    ("AXIS-Y", "Axis-Y"),
    ("LA FRESH", "La Fresh"),
    ("ITCH GUARD", "Itch Guard"),
    ("SKINLIFE", "Skinlife"),
    ("SKIN LIFE", "Skinlife"),
    ("SUDO", "Sudocrem"),
    ("OLIVE OIL", "Olive Oil"),
    ("GOVIL", "Govil's"),
    ("JENNIFER", "Jennifer's"),
    ("JOHNSON", "Johnson's"),
    ("PEPSODENT", "Pepsodent"),
    ("NEUTROGENA", "Neutrogena"),
    ("ENCHANTEUR", "Enchanteur"),
    ("AMRUTANJAN", "Amrutanjan"),
    ("PARACHUTE", "Parachute"),
    ("BRYLCREEM", "Brylcreem"),
    ("SANTAVIK", "Santavik"),
    ("GREENCROSS", "Greencross"),
    ("LISTERINE", "Listerine"),
    ("SENSODYNE", "Sensodyne"),
    ("NAVRATNA", "Navratna"),
    ("FOOTGUARD", "Footguard"),
    ("GLYSOLID", "Glysolid"),
    ("DEKASAN", "Dekasan"),
    ("MEDICAM", "Medicam"),
    ("CLOSEUP", "Closeup"),
    ("PANTENE", "Pantene"),
    ("KOLESTON", "Koleston"),
    ("HIMALAYA", "Himalaya"),
    ("GILLETTE", "Gillette"),
    ("VASELINE", "Vaseline"),
    ("COLGATE", "Colgate"),
    ("SALONPAS", "Salonpas"),
    ("SENORITA", "Senorita"),
    ("LABELLO", "Labello"),
    ("CONCORD", "Concord"),
    ("VATIKA", "Vatika"),
    ("SUNSILK", "Sunsilk"),
    ("MEDIZ", "Mediz"),
    ("HOTPACK", "Hotpack"),
    ("LYFCARE", "Lyfcare"),
    ("RASASI", "Rasasi"),
    ("DETTOL", "Dettol"),
    ("CASINO", "Casino"),
    ("MOKERU", "Mokeru"),
    ("KOTEX", "Kotex"),
    ("ALWAYS", "Always"),
    ("SIGNAL", "Signal"),
    ("DABUR", "Dabur"),
    ("PANTENE", "Pantene"),
    ("COSRX", "COSRX"),
    ("DISAAR", "Disaar"),
    ("BIGEN", "Bigen"),
    ("VICKS", "Vicks"),
    ("IODEX", "Iodex"),
    ("ZANDU", "Zandu"),
    ("RELAX", "Relax"),
    ("RADIAN", "Radian"),
    ("OMEGA", "Omega"),
    ("CAREX", "Carex"),
    ("JAGUAR", "Jaguar"),
    ("MOODS", "Moods"),
    ("PEARL", "Pearl"),
    ("NAILS", "Nails"),
    ("WELLS", "Wells"),
    ("NIVEA", "Nivea"),
    ("FOGG", "Fogg"),
    ("DOVE", "Dove"),
    ("PEARS", "Pears"),
    ("CREST", "Crest"),
    ("CLEAR", "Clear"),
    ("OLAY", "Olay"),
    ("JUNSUI", "Junsui"),
    ("ABAAN", "Abaan"),
    ("BABE", "Babe"),
    ("DEXE", "Dexe"),
    ("NITRO", "Nitro"),
    ("KOJIE", "Kojie San"),
    ("KOJIC", "Kojic"),
    ("VEET", "Veet"),
    ("NAIR", "Nair"),
    ("MOOV", "Moov"),
    ("ENO", "Eno"),
    ("DADA", "Dada"),
    ("APPLE", "Apple"),
    ("SUDOCREM", "Sudocrem"),
    ("YC", "YC"),
]


# Brand names always appear at the START of the product name in this catalogue,
# so match by prefix (longest key first) to avoid mid-name false hits
# (e.g. "CONCORD NAIL CLIPPER" must be Concord, not "Nail Clipper").
_BRANDS_SORTED = sorted(BRANDS, key=lambda kv: len(kv[0]), reverse=True)


def detect_brand(name: str) -> str:
    up = name.upper()
    for key, canon in _BRANDS_SORTED:
        if up.startswith(key):
            return canon
    # fallback: first alphabetic token, Title-cased
    tok = re.split(r"[\s\-]+", name.strip())
    return tok[0].title() if tok and tok[0] else "Other"


# ---------------------------------------------------------------------------
# CATEGORIES  --  ordered list of (keywords, category). First keyword that is
# found (as a substring, case-insensitive) wins, so order = priority.
# ---------------------------------------------------------------------------
CATEGORIES = [
    # --- Sexual wellness (check before generic) ---
    (["CONDOM", "MOODS", "LUBRICATING", "CAREX"], "Sexual Wellness"),
    # --- Baby care ---
    (["BABY", "DIAPER RASH"], "Baby Care"),
    # --- Oral / dental ---
    (["TOOTHPASTE", "TOOTHBRUSH", "MOUTHWASH", "MOUTH FRESHENER", "DENTAL FLOSS",
      "TOOTH POWDER", "FLOSS", "MISWAK"], "Oral / Dental Care"),
    # --- Women's care (sanitary) --- (brand-anchored so "cotton pads" don't match) ---
    (["ALWAYS", "KOTEX", "MAXI PROTECT", "SANITARY", "NIGHT HEAVY", "PANTYLINER"], "Women's Care"),
    # --- Lip / nail cosmetics (before "BALM" -> Healthcare) ---
    (["LIP BALM", "LIP CARE", "LIP GLOSS", "LIPSTICK", "NAIL BALM", "CUTICLE"], "Beauty & Cosmetics"),
    (["HEEL BALM"], "Skin Care"),
    # --- Men's grooming (beard) ---
    (["BEARD"], "Men's Grooming"),
    # --- Shaving & hair removal ---
    (["RAZOR", "SHAVING", "SHAVE", "BLADE", "HAIR REMOVER", "EYEBROW",
      "VENUS", "MACH3", "FUSION5"], "Shaving & Hair Removal"),
    # --- Hair care ---
    (["SHAMPOO", "HAIR OIL", "HAIR COLOR", "HAIR COLOUR", "HAIR DYE", "HAIR RELAXER",
      "HAIR TONIC", "HAIRDRESSING", "HAIR BUILDING", "HAIR LOSS", "CONDITIONER",
      "HENNA", "KERATIN", "COCUNUT OIL", "COCONUT OIL", "AMLA", "HERBAL OIL"], "Hair Care"),
    # --- First aid & medical supplies ---
    (["GLOVES", "FACE MASK", "ISOPROPYL", "ETHYL ALCOHOL", "ALCOHOL 70",
      "THERMOMETER", "HOT WATER BAG", "CORN PLASTER", "FIRST AID", "BANT PLASTER",
      "SANTAVIK", "GAUZE", "SYRINGE"], "First Aid & Medical"),
    # --- Healthcare & pain relief ---
    (["BALM", "VAPORUB", "VICKS", "PAIN", "LINIMENT", "MASSAGE", "INHALER",
      "ENO", "SALONPAS", "ITCH GUARD", "ITCH", "SNORING", "SLIMMING", "ACTIVE SHOTS",
      "CLOVE OIL", "SUDO", "PULL UP PANTS", "MEDICATED", "UNIVERSAL OIL",
      "DEEP HEAT", "PATCH", "FOOT POWDER", "PRICKLY HEAT"], "Healthcare & Pain Relief"),
    # --- Perfumes & fragrances ---
    (["PERFUME", "BODY SPRAY", "FRAGRANCE", "EAU DE", "ATTAR", "DEODORANT"], "Perfumes & Fragrances"),
    # --- Beauty & cosmetics / grooming tools ---
    (["NAIL POLISH", "NAIL CLIPPER", "SCISSOR", "PEDICURE", "DERMA ROLLER",
      "MAGNETIC BRACELET", "LIP BALM", "LIP CARE", "MASCARA", "KAJAL", "LIPSTICK",
      "MAKEUP", "COTTON BUDS", "COTTON BALLS", "COTTON PADS", "CUTICLE"], "Beauty & Cosmetics"),
    # --- Skin care (treatment soaps + face/skin) ---
    (["SULFUR SOAP", "SULPHUR SOAP", "FUNGAL SOAP", "ACNE SOAP", "PAPAYA SOAP",
      "KOJIC ACID SOAP", "ACID SOAP", "WHITENING SOAP", "BEAUTY SOAP",
      "SERUM", "TONER", "SUNSCREEN", "SUNBLOCK", "SPF", "FACE WASH", "FACIAL",
      "FACE CREAM", "FACE SERUM", "FACE OIL", "EYE CREAM", "EYE SERUM", "ESSENCE",
      "NIACINAMIDE", "HYALURONIC", "SNAIL", "MUCIN", "COLLAGEN", "RETINOL",
      "DARK SPOT", "FADE SPOT", "SPOT REMOVER", "SPOT CORRECT", "WHITENING",
      "ANTI-AGING", "ANTI AGING", "ANTI-ACNE", "PEEL OFF", "NOSE STRIPS",
      "CLEANSING PADS", "CLEANSER", "MOISTURIS", "MOISTURIZ", "MOSTURIS",
      "GLYCERIN", "BEAUTY CREAM", "AURA CREAM", "MULTIVITAMIN", "VITAMIN C",
      "VITAMIN E", "ALOE VERA", "HYDRO BOOST", "WATER GEL", "RELIEF CREAM",
      "HEEL", "FOOT CREAM", "JELLY", "BLACK MASK", "EXTRA WHITE"], "Skin Care"),
    # --- Personal hygiene / bath & body ---
    (["HAND WASH", "HAND SANITIZER", "SHOWER GEL", "BODY LOTION", "BODY CREAM",
      "ROLL ON", "SPEED STICK", "SOAP", "BODY WASH", "TALC", "POWDER", "CREAM",
      "LOTION"], "Personal Hygiene / Bath & Body"),
]


def detect_category(name: str) -> str:
    up = name.upper()
    for keywords, cat in CATEGORIES:
        for kw in keywords:
            if kw in up:
                return cat
    return "Other / General"


# Exact-name overrides (cleaned UPPERCASE name -> (brand or None, category or None)).
# Use for the handful of items the generic rules get wrong.
OVERRIDES = {
    "P CREAM": (None, "First Aid & Medical"),
    "CONCORD MAGNETIC BRACELET SUPER (GREEN) / REGULAR (BLUE)": (None, "Healthcare & Pain Relief"),
    "MEDIZ - DIGITAL THERMOMETER DMT-4333": (None, "First Aid & Medical"),
    "DADA - EASY BREATHE ANTI- SNORING DEVICES": (None, "Healthcare & Pain Relief"),
    "LYFCARE - ADULT PULL UP PANTS(DIAPER) (10 PCS PACK)": (None, "Healthcare & Pain Relief"),
    "DR.RASHEL HAIR BUILDING FIBRE": (None, "Hair Care"),
    "DR.RASHEL ARGAN OIL WITH KERATIN": (None, "Hair Care"),
    "WELLS - CASTOR OIL B.P.": (None, "Hair Care"),
    "DETTOL LIQUID - ARABIC": (None, "First Aid & Medical"),
    "DEXE - ARGAN OIL FROM MOROCCO - NOURISHING OIL": (None, "Hair Care"),
    "DISAAR EXTRA WHITE SUPER C+": (None, "Skin Care"),
    "LOVE JOJO MOROCCO ARGAN OIL": (None, "Hair Care"),
}


def classify(name: str):
    """Return (brand, category) for a cleaned name, applying overrides."""
    brand = detect_brand(name)
    category = detect_category(name)
    up = name.upper()
    if up in OVERRIDES:
        ob, oc = OVERRIDES[up]
        if ob:
            brand = ob
        if oc:
            category = oc
    return brand, category
