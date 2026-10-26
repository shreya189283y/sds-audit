import html
import json
import math
import os
import re
import sys
from datetime import date
from string import Template

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.audit import audit_one

st.set_page_config(page_title="ToxiCheck: SDS Chemical Audit", page_icon="⬡", layout="wide")

THEME = {
    "green": "#1F8A5B",
    "green_border": "#D6EADD",
    "green_soft": "#EEF6F1",
    "bg": "#F6F9F7",
    "card": "#FFFFFF",
    "text": "#16241C",
    "text_faint": "#7B8A81",
}

LEVELS = ["HIGH", "MEDIUM", "UNDISCLOSED", "LOW", "UNREADABLE"]
RANK = {"HIGH": 5, "MEDIUM": 4, "UNDISCLOSED": 3, "LOW": 2, "UNREADABLE": 1}

LEVEL_COLORS = {
    "HIGH": ("#fde2e2", "#9b1c1c"),
    "MEDIUM": ("#fdf0d5", "#8a4b08"),
    "UNDISCLOSED": ("#ede9fe", "#5b21b6"),
    "LOW": ("#e0ecf8", "#1e4e79"),
    "UNREADABLE": ("#eeeeee", "#444444"),
}

LEVEL_MEANING = {
    "HIGH": "At least one ingredient is on Prop 65, the EU SVHC list, or EU Endocrine Disruptor List I.",
    "MEDIUM": "Matches only EU Endocrine Disruptor List II or III, or a listing that applies only under a condition, such as a particle size.",
    "UNDISCLOSED": "No list matches, but at least one ingredient's identity is hidden, so it cannot be checked.",
    "LOW": "No list matches and every ingredient is named. This is not proof that the product is safe.",
    "UNREADABLE": "Scanned or unusual PDF. The tool could not find the ingredient section.",
}

NEXT_STEP = {
    "HIGH": "Consider a replacement. Check whether the listed chemical is a main ingredient or a minor one.",
    "MEDIUM": "Review before reordering. Check the hazard and the concentration on the SDS.",
    "UNDISCLOSED": "Ask the manufacturer for the full composition, or choose a fully disclosed product.",
    "LOW": "No list matches. Chemicals not on these lists are not checked.",
    "UNREADABLE": "Ask the supplier for a text-based SDS, or review this one by hand.",
}

PLAIN_ENDPOINT = [
    (("cancer", "carcinogen", "57a"), "Linked to cancer"),
    (("mutagen", "57b"), "Can damage genes"),
    (("developmental",), "Can harm a developing baby"),
    (("female", "male", "reproduct", "57c"), "Can harm fertility or reproduction"),
    (("endocrine",), "Can disrupt hormones"),
    (("pbt", "vpvb", "57d", "57e"), "Persists and builds up in the environment"),
    (("57f",), "Of equivalent concern under EU REACH"),
]

PREFIX = r"^(Product\s*(Name|name|Description)|Trade\s*name)\s*:?\s*"

NAV = ["Home", "Summary", "Products", "Safer options", "Next steps", "Download"]
MODE_INST = "School or institution"
MODE_HOME = "Personal or home"

SAFER_PATH = "data/safer_choice.csv"
EPA_SEARCH = "https://www.epa.gov/saferchoice/products"
EPA_CSV = "https://data.epa.gov/efservice/t_safer_choice_and_design_for_the_environment/CSV"
NEEDS_SWAP = ("HIGH", "MEDIUM", "UNDISCLOSED")
DFE_OPTION = "Disinfectants and sanitizers"
PER_PAGE = 3

NAME_HINTS = [
    (("floor finish", "stripper", "wax", "sealer"), ("floor finish", "floor strip")),
    (("floor",), ("floor clean",)),
    (("glass", "window"), ("glass", "window")),
    (("disinfect", "sanitiz", "germicid", "bleach", "antibacterial", "antimicrobial"), (DFE_OPTION.lower(),)),
    (("toilet", "bowl", "urinal"), ("toilet",)),
    (("tub", "tile", "shower", "bathroom", "restroom"), ("tub", "tile", "bathroom")),
    (("carpet", "upholster"), ("carpet care products: clean", "carpet")),
    (("spot remov", "stain"), ("spot remov", "carpet")),
    (("degreas", "grease"), ("degreas",)),
    (("hand soap", "hand wash", "soap"), ("hand soap",)),
    (("odor", "deodor", "air fresh"), ("odor",)),
    (("laundry", "detergent"), ("laundry",)),
    (("dish",), ("dish",)),
    (("all purpose", "all-purpose", "multi-surface", "multi surface", "general purpose", "cleaner"), ("all-purpose", "all purpose")),
]

CSS = Template("""
<style>
.stApp { background: $bg; }
.block-container { padding-top: 3.5rem; max-width: 1200px; }
h1, h2, h3 { color: $text; font-weight: 800 !important; letter-spacing: -0.5px; }

[data-testid="stSidebar"] { background: $card; border-right: 1px solid $green_border; }

.stButton > button, .stDownloadButton > button {
  border-radius: 12px; font-weight: 700; padding: 0.5rem 1rem;
  border: 1px solid $green_border; background: $card; color: $text;
}
.stButton > button:hover, .stDownloadButton > button:hover { border-color: $green; color: $green; }
.stButton > button[kind="primary"] { background: $green; border-color: $green; color: #fff; }
.stButton > button[kind="primary"]:hover { color: #fff; filter: brightness(0.94); }
.stButton > button:disabled { opacity: 0.35; }

.st-key-nav div[role="radiogroup"] {
  background: $card; border: 1px solid $green_border; border-radius: 14px;
  padding: 4px; gap: 4px; display: flex; flex-wrap: wrap;
}
.st-key-nav div[role="radiogroup"] label {
  margin: 0; padding: 8px 18px; border-radius: 10px; cursor: pointer;
}
.st-key-nav div[role="radiogroup"] label > div > div:first-child:not([data-testid]),
.st-key-nav div[role="radiogroup"] > label > div:first-child { display: none; }
.st-key-nav div[role="radiogroup"] label p { font-weight: 600; color: $text_faint; margin: 0; }
.st-key-nav div[role="radiogroup"] label:has(input:checked),
.st-key-nav div[role="radiogroup"] label[data-selected="true"] { background: $green_soft; }
.st-key-nav div[role="radiogroup"] label:has(input:checked) p,
.st-key-nav div[role="radiogroup"] label[data-selected="true"] p { color: $green; }

[data-testid="stExpander"] details { background: $card; border: 1px solid $green_border; border-radius: 14px; }
[data-testid="stFileUploaderDropzone"] { border-radius: 14px; border: 1.5px dashed $green_border; background: $green_soft; }

.tc-hero { background: $green; color: #fff; border-radius: 20px; padding: 28px 32px; margin-bottom: 16px; }
.tc-brand { display: flex; align-items: center; gap: 14px; }
.tc-logo {
  width: 52px; height: 52px; border-radius: 50%; background: rgba(255,255,255,0.16);
  display: flex; align-items: center; justify-content: center; font-size: 28px; line-height: 1;
}
.tc-name { font-size: 32px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.1; }
.tc-sub { font-size: 14px; font-weight: 500; color: rgba(255,255,255,0.7); margin-top: 2px; }
.tc-lede { font-size: 15px; color: rgba(255,255,255,0.85); margin: 16px 0 0; max-width: 680px; line-height: 1.5; }

.tc-card { background: $card; border: 1px solid $green_border; border-radius: 16px; padding: 18px 20px; margin-bottom: 12px; color: $text; }
.tc-faint { color: $text_faint; font-size: 13px; }
.tc-pill { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: 0.4px; }

.tc-steps, .tc-stats { display: grid; gap: 12px; margin-bottom: 12px; }
.tc-steps { grid-template-columns: repeat(3, 1fr); }
.tc-stats { grid-template-columns: repeat(5, 1fr); }
.tc-step-num {
  width: 30px; height: 30px; border-radius: 50%; background: $green_soft; color: $green;
  display: flex; align-items: center; justify-content: center; font-weight: 800; margin-bottom: 10px;
}
.tc-step-title { font-weight: 800; font-size: 17px; margin-bottom: 4px; }
.tc-num { font-size: 34px; font-weight: 800; letter-spacing: -1px; margin-top: 8px; line-height: 1; }

.tc-note { background: $green_soft; border: 1px solid $green_border; border-radius: 14px; padding: 14px 16px; color: $text; font-size: 14px; margin-bottom: 12px; }
.tc-note a { color: $green; font-weight: 600; }

.tc-row-name { font-weight: 800; font-size: 16px; line-height: 1.3; color: $text; }
.tc-row-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 6px; }
.tc-row-summary { color: $text_faint; font-size: 13.5px; margin-top: 6px; line-height: 1.45; }

.tc-detail-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.tc-detail-name { font-size: 22px; font-weight: 800; letter-spacing: -0.4px; }
.tc-next { background: $bg; border-radius: 12px; padding: 12px 14px; margin-top: 12px; font-size: 14px; }
.tc-flag-top { font-weight: 700; margin-bottom: 6px; }
.tc-chem { font-weight: 800; font-size: 17px; letter-spacing: -0.2px; }
.tc-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.tc-table th, .tc-table td { text-align: left; padding: 8px 10px; border-bottom: 1px solid $green_border; }
.tc-table th { color: $text_faint; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 0.4px; }
.tc-table tr.tc-hit td { background: #fdf2f2; font-weight: 600; }
.tc-cas { color: $green; }
.tc-flag ul { margin: 4px 0 8px 18px; padding: 0; font-size: 14px; }
.tc-flag a { color: $green; font-weight: 600; }

.tc-safer { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 8px; }
.tc-safer .tc-card { margin: 0; display: flex; flex-direction: column; gap: 4px; }
.tc-safer-card { margin-bottom: 8px; min-height: 120px; display: flex; flex-direction: column; gap: 4px; }
.tc-pick { color: $green; font-size: 13px; font-weight: 600; margin-top: 6px; }
.tc-safer-name { font-weight: 800; font-size: 15px; line-height: 1.3; }
.tc-safer-name a { color: $text; text-decoration: none; }
.tc-safer-name a:hover { color: $green; }
.tc-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }
.tc-badge { background: $green_soft; color: $green; border-radius: 999px; padding: 2px 9px; font-size: 11px; font-weight: 700; }
.tc-pager { text-align: center; color: $text_faint; font-size: 13px; font-weight: 600; padding-top: 10px; }

@media (max-width: 760px) {
  .tc-safer { grid-template-columns: 1fr; }
  .tc-stats { grid-template-columns: repeat(2, 1fr); }
  .tc-steps { grid-template-columns: 1fr; }
  .tc-hero { padding: 22px 20px; }
  .tc-name { font-size: 26px; }
}
</style>
""").substitute(THEME)


def e(text):
    return html.escape(str(text), quote=True)


def card(inner, extra_class=""):
    st.markdown(f'<div class="tc-card {extra_class}">{inner}</div>', unsafe_allow_html=True)


def pill(level):
    bg, fg = LEVEL_COLORS.get(level, ("#eeeeee", "#444444"))
    return f'<span class="tc-pill" style="background:{bg};color:{fg}">{e(level)}</span>'


def plural(n, word):
    return f"{n} {word}{'s' if n != 1 else ''}"


def clean_name(text):
    if pd.isna(text) or str(text).strip() == "":
        return "(no name)"
    name = re.sub(PREFIX, "", str(text)).strip()
    if name.lower().endswith(".pdf"):
        name = name[:-4].replace("_", " ").replace("-", " ").strip().title()
    return name


def endpoint_list(endpoint):
    low = str(endpoint).lower()
    found = [plain for keys, plain in PLAIN_ENDPOINT if any(k in low for k in keys)]
    return found or [str(endpoint)]


def plain_endpoint(endpoint):
    return ", ".join(dict.fromkeys(endpoint_list(endpoint)))


def parse_flags(row):
    text = row.get("flags_json", "")
    if pd.isna(text) or text in ("", "[]"):
        return []
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return []


def chem_name(f):
    return re.sub(r"\s+", " ", str(f.get("name") or "")).strip(" ,;:-")


def chem_label(f):
    name = chem_name(f)
    return f"{name} (CAS {f['cas']})" if name else f"CAS {f['cas']}"


def flagged_chems(row):
    seen = {}
    for f in parse_flags(row):
        if f["cas"] not in seen or (chem_name(f) and not chem_name(seen[f["cas"]])):
            seen[f["cas"]] = f
    return [chem_label(f) for f in seen.values()]


def parse_ingredient_rows(row):
    text = row.get("ingredients_json", "")
    if pd.isna(text) or text in ("", "[]"):
        return []
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return []


def fmt_num(x):
    return f"{float(x):g}"


def fmt_conc(lo, hi):
    lo = None if lo is None or (isinstance(lo, float) and math.isnan(lo)) else lo
    hi = None if hi is None or (isinstance(hi, float) and math.isnan(hi)) else hi
    if lo is not None and hi is not None:
        return f"{fmt_num(lo)}%" if float(lo) == float(hi) else f"{fmt_num(lo)} to {fmt_num(hi)}%"
    if hi is not None:
        return f"Up to {fmt_num(hi)}%"
    if lo is not None:
        return f"At least {fmt_num(lo)}%"
    return ""


def row_summary(row):
    level = row["level"]
    hidden = str(row.get("undisclosed", "")) == "True"
    flags = parse_flags(row)
    if level == "UNREADABLE":
        return "Could not read this SDS. Check it by hand."
    if flags:
        n = len({f["cas"] for f in flags})
        effects = list(dict.fromkeys(p for f in flags for p in endpoint_list(f["endpoint"])))
        effects = [effects[0]] + [x[0].lower() + x[1:] for x in effects[1:]]
        text = f"{plural(n, 'chemical')} on hazard lists: {', '.join(flagged_chems(row))}. {', '.join(effects)}."
        if hidden:
            text += " Also hides at least one ingredient."
        return text
    if hidden:
        return "No list matches, but at least one ingredient is hidden."
    return "No list matches."


@st.cache_data
def read_safer(path, mtime):
    sc = pd.read_csv(path, dtype=str).fillna("")
    sc.columns = [re.sub(r"[^a-z0-9]+", "_", c.strip().lower()).strip("_") for c in sc.columns]
    if "product_name" not in sc.columns:
        return None
    if "company_in_good_standing" in sc.columns:
        sc = sc[~sc["company_in_good_standing"].str.strip().str.lower().isin(["n", "no", "false"])]
    for c in ("category", "sector", "program", "company_name", "fragrance_free", "product_url"):
        if c not in sc.columns:
            sc[c] = ""
    type_col = max(("sector", "category"), key=lambda c: sc[c].nunique())
    sc["_type"] = sc[type_col].str.strip()
    labels = (sc["category"] + " " + sc["sector"]).str.lower()
    sc["_inst"] = labels.str.contains("industrial|institution|business|commercial", regex=True)
    sc["_dfe"] = (
        sc["program"].str.lower().str.contains("dfe|design for", regex=True)
        | sc["product_name"].str.lower().str.contains("disinfect|sanitiz", regex=True)
    )
    sc = sc.drop_duplicates(subset=["product_name", "company_name", "_type", "_dfe"])
    return sc.reset_index(drop=True)


def load_safer():
    if not os.path.exists(SAFER_PATH):
        return None
    return read_safer(SAFER_PATH, os.path.getmtime(SAFER_PATH))


def type_options(sc):
    if sc is None:
        return []
    opts = sorted(t for t in sc.loc[~sc["_dfe"], "_type"].unique() if t)
    if sc["_dfe"].any():
        opts.append(DFE_OPTION)
    return opts


def is_yes(value):
    return str(value).strip().lower() in ("y", "yes", "true", "1")


def guess_type(row, options):
    if not options:
        return None
    text = str(row.get("display_name", "")).lower()
    if "category" in row.index and not pd.isna(row["category"]):
        text += " " + str(row["category"]).lower()
    for name_keys, option_keys in NAME_HINTS:
        if any(k in text for k in name_keys):
            for key in option_keys:
                for opt in options:
                    if key in opt.lower():
                        return opt
    return None


def safer_matches(sc, option, fragrance_free=False, audience="all"):
    if sc is None or not option:
        return pd.DataFrame()
    if option == DFE_OPTION:
        m = sc[sc["_dfe"]]
    else:
        m = sc[(sc["_type"] == option) & ~sc["_dfe"]]
    if audience == "inst" and m["_inst"].any():
        m = m[m["_inst"]]
    elif audience == "home" and (~m["_inst"]).any():
        m = m[~m["_inst"]]
    if fragrance_free:
        m = m[m["fragrance_free"].apply(is_yes)]
    return m.drop_duplicates(subset=["product_name", "company_name"]).sort_values("product_name")


def safer_card_html(p):
    name = e(p["product_name"])
    url = str(p["product_url"]).strip()
    if url.startswith("http"):
        name = f'<a href="{e(url)}" target="_blank">{name}</a>'
    badges = []
    if p["program"]:
        badges.append(e(p["program"]))
    if is_yes(p["fragrance_free"]):
        badges.append("Fragrance-free")
    badges.append("Institutional" if p["_inst"] else "Consumer")
    return (
        f'<div class="tc-card tc-safer-card"><div class="tc-safer-name">{name}</div>'
        f'<div class="tc-faint">{e(p["company_name"])}</div>'
        f'<div class="tc-badges">{"".join(f"<span class=tc-badge>{b}</span>" for b in badges)}</div></div>'
    )


def shift_page(key, delta):
    st.session_state[key] = st.session_state.get(key, 0) + delta


def choose(pid, pick):
    st.session_state.setdefault("chosen", {})[pid] = pick


def carousel(m, key, pid):
    pages = max(1, math.ceil(len(m) / PER_PAGE))
    page = min(max(st.session_state.get(key, 0), 0), pages - 1)
    st.session_state[key] = page
    start = page * PER_PAGE
    end = min(start + PER_PAGE, len(m))
    current = st.session_state.get("chosen", {}).get(pid) or {}
    cols = st.columns(PER_PAGE)
    for col, (idx, p) in zip(cols, m.iloc[start:end].iterrows()):
        pick = {
            "product_name": p["product_name"], "company_name": p["company_name"],
            "product_url": p["product_url"], "program": p["program"],
        }
        is_chosen = (current.get("product_name"), current.get("company_name")) == (p["product_name"], p["company_name"])
        with col:
            st.markdown(safer_card_html(p), unsafe_allow_html=True)
            st.button(
                "Chosen ✓" if is_chosen else "Choose this", key=f"{key}_c_{idx}",
                type="primary" if is_chosen else "secondary",
                on_click=choose, args=(pid, pick), use_container_width=True,
            )
    if pages > 1:
        prev_col, mid_col, next_col = st.columns([1, 2, 1])
        prev_col.button("‹ Previous", key=f"{key}_prev", disabled=page == 0,
                        on_click=shift_page, args=(key, -1), use_container_width=True)
        mid_col.markdown(f'<div class="tc-pager">{start + 1} to {end} of {len(m)}</div>', unsafe_allow_html=True)
        next_col.button("Next ›", key=f"{key}_next", disabled=page >= pages - 1,
                        on_click=shift_page, args=(key, 1), use_container_width=True)


def safer_caveat():
    st.markdown(
        '<div class="tc-note">These products are certified under EPA Safer Choice, or Design for the '
        'Environment for disinfectants. EPA reviews every ingredient before certifying, but certification '
        'is not a guarantee. Run a product\'s SDS through ToxiCheck before switching. '
        f'<a href="{EPA_SEARCH}" target="_blank">Search EPA\'s full list</a>.</div>',
        unsafe_allow_html=True,
    )


def safer_missing():
    st.markdown(
        '<div class="tc-note"><b>Safer product list not loaded.</b> Download EPA\'s certified product list '
        f'(<a href="{EPA_CSV}" target="_blank">CSV</a>), rename it <code>safer_choice.csv</code>, and put it '
        f'in the <code>data</code> folder. Until then, <a href="{EPA_SEARCH}" target="_blank">search EPA\'s list</a>.</div>',
        unsafe_allow_html=True,
    )


REPORT_CSS = Template("""
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; color: $text;
  background: #fff; margin: 0; padding: 32px; line-height: 1.55; font-size: 15px; }
.wrap { max-width: 820px; margin: 0 auto; }
.hero { background: $green; color: #fff; border-radius: 16px; padding: 24px 28px; margin-bottom: 24px; }
.hero h1 { margin: 0; font-size: 28px; letter-spacing: -0.5px; }
.hero p { margin: 6px 0 0; color: rgba(255,255,255,0.8); font-size: 14px; }
h2 { font-size: 19px; margin: 28px 0 8px; letter-spacing: -0.3px; border-bottom: 2px solid $green_border; padding-bottom: 6px; }
h3 { font-size: 16px; margin: 0 0 4px; }
.stats { display: flex; gap: 10px; flex-wrap: wrap; margin: 10px 0; }
.stat { border: 1px solid $green_border; border-radius: 12px; padding: 10px 14px; min-width: 110px; }
.stat b { display: block; font-size: 24px; }
.pill { display: inline-block; padding: 2px 9px; border-radius: 999px; font-size: 11px; font-weight: 700; }
table { border-collapse: collapse; width: 100%; font-size: 14px; margin-top: 8px; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid $green_border; vertical-align: top; }
th { background: $green_soft; }
.item { border: 1px solid $green_border; border-radius: 12px; padding: 14px 16px; margin: 10px 0; break-inside: avoid; }
.why { color: $text_faint; font-size: 14px; margin: 2px 0 8px; }
.swap { background: $green_soft; border-radius: 10px; padding: 8px 12px; font-size: 14px; margin-top: 8px; }
.note { background: $green_soft; border-radius: 12px; padding: 12px 16px; }
.faint { color: $text_faint; font-size: 13px; }
ul, ol { padding-left: 22px; margin: 6px 0; }
li { margin: 3px 0; }
a { color: $green; }
@media print { body { padding: 0; } .hero { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
""").substitute(THEME)


def report_page(title, subtitle, body):
    return (
        f"<!doctype html><html><head><meta charset='utf-8'><title>{e(title)}</title>"
        f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<style>{REPORT_CSS}</style></head><body><div class='wrap'>"
        f"<div class='hero'><h1>{e(title)}</h1><p>{subtitle}</p></div>{body}"
        f"<p class='faint' style='margin-top:32px'>Generated with ToxiCheck. Lists checked: California Prop 65, "
        f"the EU SVHC Candidate List, and the EU endocrine disruptor lists I to III.</p></div></body></html>"
    )


def report_pill(level):
    bg, fg = LEVEL_COLORS.get(level, ("#eeeeee", "#444444"))
    return f"<span class='pill' style='background:{bg};color:{fg}'>{e(level)}</span>"


def row_effects(row):
    return list(dict.fromkeys(p for f in parse_flags(row) for p in endpoint_list(f["endpoint"])))


def swap_text(pid):
    pick = st.session_state.get("chosen", {}).get(pid)
    if not pick:
        return None
    text = f"{e(pick['product_name'])}, {e(pick['company_name'])}"
    if str(pick.get("product_url", "")).startswith("http"):
        text = f"<a href='{e(pick['product_url'])}'>{text}</a>"
    if pick.get("program"):
        text += f" ({e(pick['program'])} certified)"
    return text


def effect_summary(rows):
    chems, prods = {}, {}
    for _, r in rows.iterrows():
        for f in parse_flags(r):
            for p in endpoint_list(f["endpoint"]):
                chems.setdefault(p, set()).add(f["cas"])
                prods.setdefault(p, set()).add(r["product_id"])
    return [(p, len(chems[p]), len(prods[p])) for p in sorted(chems, key=lambda k: -len(prods[k]))]


def institution_report(df, scope, org, author):
    needs = scope[scope["level"].isin(NEEDS_SWAP)]
    counts = df["level"].value_counts()
    hidden = scope[scope["undisclosed"].astype(str) == "True"]
    unreadable = scope[scope["level"] == "UNREADABLE"]
    effects = effect_summary(scope)
    persistent = next((c for p, c, _ in effects if p.startswith("Persists")), 0)
    org_name = org or "Our School District"
    sub = f"Prepared {date.today().strftime('%B %-d, %Y')}"
    if author:
        sub += f" by {e(author)}"

    b = ["<h2>Summary</h2>",
         f"<p>We audited {plural(len(df), 'product')} used at {e(org_name)} by reading each product's "
         f"Safety Data Sheet. Every named ingredient was checked against major regulatory hazard lists."
         + (f" This report covers {len(scope)} of them." if len(scope) < len(df) else "") + "</p>",
         "<div class='stats'>" + "".join(
             f"<div class='stat'>{report_pill(lv)}<b>{int(counts.get(lv, 0))}</b></div>" for lv in LEVELS
         ) + "</div>",
         f"<p><b>{plural(len(needs), 'product')} in this report should be reviewed for replacement.</b></p>"]

    if len(scope):
        b.append("<h2>Products in this report</h2><table><tr><th>Product</th><th>Level</th><th>Why</th><th>Recommended replacement</th></tr>")
        for _, r in scope.iterrows():
            why = row_summary(r)
            if r["level"] in NEEDS_SWAP:
                swap = swap_text(r["product_id"]) or "<span class='faint'>Not chosen yet. See EPA Safer Choice.</span>"
            else:
                swap = "<span class='faint'>No replacement needed.</span>"
            b.append(f"<tr><td>{e(r['display_name'])}</td><td>{report_pill(r['level'])}</td><td>{e(why)}</td><td>{swap}</td></tr>")
        b.append("</table>")

    b.append("<h2>Health and environmental concerns</h2>")
    if effects:
        b.append("<ul>" + "".join(
            f"<li><b>{e(p)}:</b> {plural(c, 'chemical')} found in {plural(n, 'product')}</li>" for p, c, n in effects
        ) + "</ul>")
    else:
        b.append("<p>No ingredients matched the hazard lists.</p>")
    b.append(
        "<p>Cleaning and maintenance products are rinsed down drains after use. Wastewater treatment removes "
        "some chemicals, but not all of them. Hormone-disrupting and persistent chemicals that pass through can "
        "reach local creeks and waterways, where they can affect fish and wildlife.</p>"
    )
    if persistent:
        b.append(f"<p>{plural(persistent, 'chemical')} in this audit {'is' if persistent == 1 else 'are'} listed "
                 "as persistent. These break down slowly and can build up in the environment over time.</p>")

    if len(hidden):
        b.append(f"<h2>Hidden ingredients</h2><p>{plural(len(hidden), 'product')} withhold at least one "
                 "ingredient's identity, usually as a trade secret. Hidden ingredients cannot be checked.</p>")

    b.append("<h2>Recommended actions for the district</h2><ol>")
    if len(needs):
        b.append("<li>Replace HIGH products first, at the next reorder, with a certified alternative.</li>")
    if len(hidden):
        b.append("<li>Ask suppliers of products with hidden ingredients for the full composition. "
                 "If they won't share it, choose a fully disclosed product.</li>")
    b.append("<li>Adopt a purchasing rule that prefers EPA Safer Choice products, and Design for the "
             "Environment products for disinfecting.</li>")
    b.append("<li>Until products are replaced, train custodial staff on safe use: follow label dilutions, "
             "ventilate, wear the listed protective equipment, and never mix products.</li>")
    if len(unreadable):
        b.append(f"<li>Review the {plural(len(unreadable), 'Safety Data Sheet')} this tool could not read by hand.</li>")
    b.append("<li>Re-audit every year and whenever a new product is purchased.</li>")
    b.append("<li>Share these results with staff and families, and report progress publicly.</li></ol>")

    b.append("<h2>What community members can do</h2><ul>"
             "<li><b>Families:</b> Ask the district which cleaning products are used in classrooms, and whether "
             "it has a safer purchasing policy.</li>"
             "<li><b>Anyone:</b> Speak during public comment at a school board meeting and share this report.</li>"
             "<li><b>Staff:</b> Use products only as the label directs, and report any product that is not on "
             "the approved list.</li>"
             "<li><b>Students:</b> Start or join a green team to track replacements and keep this audit current.</li>"
             "</ul>")

    b.append("<h2>Limits of this audit</h2><ul>"
             "<li>LOW means no list match. It does not prove a product is safe.</li>"
             "<li>The audit checks hazard, not exposure. It does not measure how much of a chemical people "
             "actually contact.</li>"
             "<li>Only chemicals on the checked lists are flagged. Others, including some preservatives, are not.</li>"
             "<li>Safety Data Sheets do not always list every ingredient, especially below disclosure thresholds.</li>"
             "</ul>")
    return report_page(f"Chemical Safety Audit: {org_name}", sub, "".join(b))


TYPE_TIPS = [
    (("toilet",), "Never mix it with bleach or another cleaner. Many toilet bowl cleaners are acidic, and acid plus bleach makes chlorine gas."),
    (("tub", "tile", "bathroom"), "Run the fan and keep the door open. Small bathrooms trap fumes."),
    (("glass", "window"), "Spray it onto the cloth, not into the air, so you breathe in less."),
    (("floor finish", "floor strip"), "Keep kids and pets off the floor until it is dry and the room has aired out."),
    (("floor clean",), "Dilute it exactly as the label says. Extra product leaves residue that kids and pets touch."),
    (("disinfect", "sanitiz"), "Clean first, then disinfect only where needed, like after someone is sick. Leave it on for the label's contact time, and rinse food-contact surfaces if the label says to."),
    (("carpet", "spot remov"), "Use as little as possible and let the spot dry with a window open. Carpet holds residue where kids play."),
    (("degreas",), "Wear gloves. Degreasers are hard on skin."),
    (("hand soap",), "Plain soap and water work. Antibacterial soap is not needed at home."),
    (("all-purpose", "all purpose"), "If it's a concentrate, dilute it exactly as directed. Stronger is not cleaner."),
    (("odor",), "Fix the source and open windows instead of covering the smell. Odor products add chemicals to the air."),
    (("laundry",), "Use the dose line on the cap. Extra detergent stays in fabric."),
    (("dish",), "Rinse dishes well with water after washing."),
]

PRIORITY = {"HIGH": "Replace first", "MEDIUM": "Replace soon", "UNDISCLOSED": "Ask for ingredients"}


def type_tip(ptype):
    low = str(ptype or "").lower()
    for keys, tip in TYPE_TIPS:
        if any(k in low for k in keys):
            return tip
    return None


def home_steps(row, ptype):
    joined = " ".join(row_effects(row)).lower()
    steps = []
    if "developing baby" in joined or "fertility" in joined:
        steps.append("If anyone in your home is pregnant or planning to be, stop using it now.")
    if "hormones" in joined:
        steps.append("Keep it off surfaces children touch and food prep areas. Wipe with water after use.")
    if "persists" in joined:
        steps.append("Never pour it down the drain. Take leftovers to household hazardous waste.")
    if str(row.get("undisclosed", "")) == "True":
        steps.append("Check the company's website for a full ingredient list. If you can't find one, "
                     "choose a product that lists everything.")
    tip = type_tip(ptype)
    if tip:
        steps.append(tip)
    if not steps:
        steps.append("Switch when you run out.")
    return steps


def home_plan(df, type_of):
    needs = df[df["level"].isin(NEEDS_SWAP)]
    sub = f"Made {date.today().strftime('%B %-d, %Y')}"
    effects_all = " ".join(" ".join(row_effects(r)) for _, r in needs.iterrows()).lower()
    b = ["<h2>Start here</h2>"]
    if needs.empty:
        b.append("<p>None of your products matched the hazard lists or hid ingredients. That is not proof "
                 "they are safe, but nothing here needs urgent action.</p>")
    else:
        first = needs.iloc[0]
        b.append(f"<p>{plural(len(needs), 'product')} in your home should be replaced or used with care. "
                 f"They are listed below in order, most urgent first. Start with <b>{e(first['display_name'])}</b>.</p>")
        if "developing baby" in effects_all or "fertility" in effects_all:
            b.append("<div class='note'>Some of your products contain chemicals that can harm fertility or a "
                     "developing baby. If anyone at home is pregnant or planning to be, replace those first.</div>")

    b.append("<h2>Until you switch, for every product</h2><ul>"
             "<li>Use the smallest amount the label allows.</li>"
             "<li>Open a window or run a fan while you clean.</li>"
             "<li>Wear gloves if the label says to.</li>"
             "<li>Never mix products. Bleach mixed with ammonia or with acids makes toxic gas.</li>"
             "<li>Keep products in their original containers, up high or locked, away from children and pets.</li>"
             "</ul>")

    if not needs.empty:
        b.append("<h2>Your products</h2>")
        for i, (_, r) in enumerate(needs.iterrows(), start=1):
            ptype = type_of(r)
            swap = swap_text(r["product_id"])
            type_line = f"<p class='faint' style='margin:0'>Type: {e(ptype)}</p>" if ptype else ""
            b.append(
                f"<div class='item'><h3>{i}. {e(r['display_name'])} {report_pill(r['level'])} "
                f"<span class='faint'>{PRIORITY.get(r['level'], '')}</span></h3>{type_line}"
                f"<p class='why'>{e(row_summary(r))}</p>"
                "<ul>" + "".join(f"<li>{e(x)}</li>" for x in home_steps(r, ptype)) + "</ul>"
                + (f"<div class='swap'><b>Swap for:</b> {swap}</div>" if swap
                   else "<div class='swap'><b>Swap for:</b> pick a replacement in ToxiCheck's Safer options.</div>")
                + "</div>"
            )

    b.append("<h2>Getting rid of old products</h2><ul>"
             "<li>Don't pour leftover hazardous products down the drain or toss them in the trash.</li>"
             "<li>Take them to a household hazardous waste drop-off. Search for your county's program.</li>"
             "<li>Empty containers can usually be recycled. Check your city's rules.</li></ul>")
    b.append("<h2>Shopping tips</h2><ul>"
             "<li>Look for the EPA Safer Choice label on cleaners, and Design for the Environment on disinfectants.</li>"
             "<li>Choose fragrance-free when you can. \"Fragrance\" can stand for many unlisted ingredients.</li>"
             "<li>Buy fewer products. One all-purpose cleaner covers most jobs.</li>"
             "<li>Run any new product's Safety Data Sheet through ToxiCheck before you buy more.</li></ul>")
    b.append("<h2>Keep in mind</h2><p class='faint'>LOW means no list match, not proven safe. This plan "
             "checks hazard, not how much you are exposed to, and only chemicals on the checked lists.</p>")
    return report_page("Your Home Action Plan", sub, "".join(b))


HOW_TO = [
    ("Choose who it's for",
     "In the sidebar, pick <b>School or institution</b> or <b>Personal or home</b>. This sets which safer "
     "products you see and what your Next steps page gives you."),
    ("Upload your Safety Data Sheets",
     "Add one PDF per product in the sidebar, then click <b>Run audit</b>. No files yet? Click "
     "<b>Try a sample district</b> to see an example."),
    ("Read the Summary",
     "See how many products fall into each level, from HIGH to UNREADABLE."),
    ("Check your Products",
     "Every product with a plain-English reason. Click <b>Details</b> to see each flagged chemical and the list it's on."),
    ("Pick Safer options",
     "For each product that needs a swap, confirm its type, browse EPA-certified alternatives, and click "
     "<b>Choose this</b> on the one you want."),
    ("Get your Next steps",
     "A community report for schools, or a home action plan for personal use. Download it to print or share."),
]


def home_page(has_results):
    st.markdown(
        '<div class="tc-note"><b>Tip: name each SDS file after its product before you upload.</b> '
        'For example, <code>Glass Cleaner.pdf</code> or <code>Brand X Floor Finish.pdf</code>, not '
        '<code>SDS_00417.pdf</code>. ToxiCheck uses names to label your results and to guess each product\'s '
        'type, so clear names mean fewer fixes later.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### How to use ToxiCheck")
    st.markdown(
        '<div class="tc-steps">' + "".join(
            f'<div class="tc-card"><div class="tc-step-num">{i}</div>'
            f'<div class="tc-step-title">{title}</div><div class="tc-faint">{body}</div></div>'
            for i, (title, body) in enumerate(HOW_TO, start=1)
        ) + "</div>",
        unsafe_allow_html=True,
    )
    with st.expander("What the levels mean"):
        st.markdown("\n".join(f"- **{lv}:** {LEVEL_MEANING[lv]}" for lv in LEVELS))
    if not has_results:
        st.caption("Start in the sidebar. Upload SDS PDFs, or click Try a sample district.")


def open_product(pid):
    st.session_state["selected"] = pid


def close_product():
    st.session_state["selected"] = None


def go_safer(pid):
    st.session_state["focus"] = pid
    st.session_state["nav"] = "Safer options"


def reset_view():
    st.session_state["types"] = {}
    st.session_state["chosen"] = {}
    st.session_state["selected"] = None
    st.session_state["focus"] = None
    st.session_state["nav"] = "Summary"


st.markdown(CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("**Who is this for?**")
    mode = st.radio("Who is this for?", [MODE_INST, MODE_HOME], key="mode",
                    horizontal=True, label_visibility="collapsed")
    st.divider()
    st.header("Run an audit")
    files = st.file_uploader("Upload SDS PDFs", type="pdf", accept_multiple_files=True)

    if st.button("Run audit", type="primary", use_container_width=True):
        if not files:
            st.warning("Upload at least one PDF first.")
        else:
            bar = st.progress(0, text="Reading SDS files...")
            rows = []
            for i, f in enumerate(files, start=1):
                rows.append(audit_one(f, f"U{i:03d}", f.name))
                bar.progress(i / len(files), text=f"Audited {i} of {len(files)}")
            st.session_state["results"] = pd.DataFrame(rows)
            st.session_state["source"] = f"your upload of {len(files)} files"
            reset_view()
            st.success(f"Audited {len(files)} files.")

    if st.button("Try a sample district", use_container_width=True):
        sample = pd.read_csv("data/results.csv")
        st.session_state["results"] = sample
        st.session_state["source"] = f"a sample district of {len(sample)} products"
        reset_view()

    st.divider()
    st.markdown(
        "**How it works**\n\n"
        "1. Upload a district's SDS PDFs.\n"
        "2. The tool reads Section 3 and finds each ingredient's CAS number.\n"
        "3. It checks each one against Prop 65, the EU SVHC list, and the EU "
        "endocrine disruptor lists."
    )

st.markdown(
    '<div class="tc-hero">'
    '<div class="tc-brand"><div class="tc-logo">⬡</div>'
    '<div><div class="tc-name">ToxiCheck</div><div class="tc-sub">SDS Chemical Audit</div></div></div>'
    '<p class="tc-lede">Find which products in a school district\'s inventory contain chemicals on '
    'major regulatory hazard lists, and which ones hide their ingredients.</p>'
    '</div>',
    unsafe_allow_html=True,
)

if "results" not in st.session_state:
    home_page(False)
    st.stop()

df = st.session_state["results"].copy()
df["display_name"] = df["product_name"].map(clean_name)
df["rank"] = df["level"].map(RANK)
df = df.sort_values(["rank", "product_id"], ascending=[False, True]).reset_index(drop=True)

sc = load_safer()
options = type_options(sc)
types = st.session_state.setdefault("types", {})
chosen = st.session_state.setdefault("chosen", {})


def product_type(r):
    pid = r["product_id"]
    if pid in types and (types[pid] is None or types[pid] in options):
        return types[pid]
    return guess_type(r, options)


st.caption(f"Showing results for {st.session_state.get('source', 'your audit')}.")
st.session_state.setdefault("nav", "Home")
page = st.radio("Section", NAV, horizontal=True, key="nav", label_visibility="collapsed")

if page == "Home":
    home_page(True)

elif page == "Summary":
    counts = df["level"].value_counts()
    st.markdown(
        '<div class="tc-stats">' + "".join(
            f'<div class="tc-card" title="{e(LEVEL_MEANING[lv])}">{pill(lv)}'
            f'<div class="tc-num">{int(counts.get(lv, 0))}</div></div>'
            for lv in LEVELS
        ) + "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="tc-note">Ingredients are checked against Prop 65, the EU SVHC list, and the EU '
        'endocrine disruptor lists. <b>LOW means no list match, not proven safe.</b> Chemicals not on '
        'these lists, such as some preservatives and plasticizers, are not flagged.</div>',
        unsafe_allow_html=True,
    )
    with st.expander("What the levels mean"):
        st.markdown("\n".join(f"- **{lv}:** {LEVEL_MEANING[lv]}" for lv in LEVELS))

elif page == "Products":
    selected = st.session_state.get("selected")
    if selected in df["product_id"].values:
        row = df[df["product_id"] == selected].iloc[0]
        level = row["level"]
        st.button("‹ All products", on_click=close_product)

        parts = [
            f'<div class="tc-detail-head"><div class="tc-detail-name">{e(row["display_name"])}</div>{pill(level)}</div>',
            f'<p style="margin:10px 0 0">{e(LEVEL_MEANING.get(level, ""))}</p>',
            f'<div class="tc-next"><b>What to do next</b><br>{e(NEXT_STEP.get(level, ""))}</div>',
        ]
        if "rule" in row.index and not pd.isna(row["rule"]):
            parts.append(f'<p class="tc-faint" style="margin:10px 0 0">Rule applied: {e(row["rule"])}</p>')
        if str(row["undisclosed"]) == "True":
            parts.append('<p style="margin:10px 0 0">At least one ingredient\'s identity is withheld by the manufacturer.</p>')
            if "evidence" in row.index and not pd.isna(row["evidence"]) and row["evidence"]:
                parts.append(f'<p class="tc-faint" style="margin:4px 0 0">Evidence: {e(row["evidence"])}</p>')
        card("".join(parts))

        if level in NEEDS_SWAP:
            st.button("See safer options", type="primary", on_click=go_safer, args=(selected,))

        flags = parse_flags(row)
        if flags:
            grouped = {}
            for flag in flags:
                grouped.setdefault(flag["cas"], []).append(flag)
            st.markdown(f"**Flagged chemicals ({len(grouped)})**")
            for cas, fl in grouped.items():
                meanings = ", ".join(dict.fromkeys(plain_endpoint(f["endpoint"]) for f in fl))
                name = next((chem_name(f) for f in fl if chem_name(f)), "")
                items = []
                for f in fl:
                    line = f'<a href="{e(f["source_url"])}" target="_blank">{e(f["list_name"])}</a>'
                    if f.get("via_group"):
                        line += f", listed as <i>{e(f['via_group'])}</i>"
                    if f.get("condition"):
                        line += f". Applies only: {e(f['condition'])}"
                    items.append(f"<li>{line}</li>")
                wording = "; ".join(dict.fromkeys(str(f["endpoint"]) for f in fl))
                card(
                    f'<div class="tc-chem">{e(name) if name else "Name not recorded"}</div>'
                    f'<div class="tc-faint">CAS {e(cas)}</div>'
                    f'<div class="tc-flag-top" style="margin-top:8px">{e(meanings)}</div>'
                    f'<ul>{"".join(items)}</ul>'
                    f'<div class="tc-faint">Official wording: {e(wording)}</div>',
                    extra_class="tc-flag",
                )
        elif level != "UNREADABLE":
            st.write("No list matches.")

        ingredients = parse_ingredient_rows(row)
        if ingredients:
            flagged_cas = {f["cas"] for f in flags}
            body = "".join(
                f'<tr{" class=tc-hit" if i.get("cas") in flagged_cas else ""}>'
                f'<td>{e(chem_name(i) or "(no name)")}</td>'
                f'<td>{e(i.get("cas") or "Not listed")}</td>'
                f'<td>{e(fmt_conc(i.get("conc_min"), i.get("conc_max")))}</td>'
                f'<td>{"On a hazard list" if i.get("cas") in flagged_cas else ""}</td></tr>'
                for i in ingredients
            )
            with st.expander(f"All ingredients on the SDS ({len(ingredients)})"):
                st.markdown(
                    '<table class="tc-table"><tr><th>Ingredient</th><th>CAS</th><th>Amount</th><th></th></tr>'
                    f"{body}</table>",
                    unsafe_allow_html=True,
                )
        elif "ingredients_json" not in row.index and level != "UNREADABLE":
            st.caption("Re-run the audit to see this product's full ingredient list.")
    else:
        c1, c2 = st.columns([1, 1])
        query = c1.text_input("Search products", placeholder="Type a product name")
        picked = c2.multiselect("Show levels", LEVELS, default=LEVELS)
        shown = df[df["level"].isin(picked)]
        if query.strip():
            shown = shown[shown["display_name"].str.contains(query.strip(), case=False, regex=False)]
        st.caption(f"{plural(len(shown), 'product')}, most concerning first. Click Details to see why.")
        for _, r in shown.iterrows():
            with st.container(border=True):
                left, right = st.columns([5, 1])
                left.markdown(
                    f'<div class="tc-row-name">{e(r["display_name"])}</div>'
                    f'<div class="tc-row-meta">{pill(r["level"])}</div>'
                    f'<div class="tc-row-summary">{e(row_summary(r))}</div>',
                    unsafe_allow_html=True,
                )
                right.button("Details", key=f"open_{r['product_id']}", on_click=open_product,
                             args=(r["product_id"],), use_container_width=True)

elif page == "Safer options":
    if sc is None:
        safer_missing()
    else:
        needs = df[df["level"].isin(NEEDS_SWAP)]
        focus = st.session_state.get("focus")
        if focus in needs["product_id"].values:
            needs = pd.concat([needs[needs["product_id"] == focus], needs[needs["product_id"] != focus]])

        if needs.empty:
            st.write("No products in this audit need a replacement.")
        else:
            home = mode == MODE_HOME
            c1, c2 = st.columns([1, 1])
            query = c1.text_input("Search products", placeholder="Search your audited products", key="safer_search")
            c3, c4 = c2.columns([1, 1])
            ff = c3.checkbox("Fragrance-free only", key="swap_ff")
            widen = c4.checkbox("Show institutional too" if home else "Show consumer too", key=f"widen_{home}")
            audience = "all" if widen else ("home" if home else "inst")

            shown = needs
            if query.strip():
                shown = needs[needs["display_name"].str.contains(query.strip(), case=False, regex=False)]
            st.caption(
                f"{plural(len(needs), 'product')} in this audit need a replacement. Showing "
                f"{'consumer' if audience == 'home' else 'institutional' if audience == 'inst' else 'all'} products. "
                f"Each type is detected from the product name. To change it, click the type box and pick from "
                f"all {len(options)} EPA categories, or type to search them. Click Choose this to pick a replacement."
            )
            if shown.empty:
                st.write("No audited products match that search.")

            for _, r in shown.iterrows():
                pid = r["product_id"]
                current = product_type(r)
                pick = chosen.get(pid)
                with st.container(border=True):
                    left, right = st.columns([3, 2])
                    pick_line = (
                        f'<div class="tc-pick">Your pick: {e(pick["product_name"])}, {e(pick["company_name"])}</div>'
                        if pick else ""
                    )
                    left.markdown(
                        f'<div class="tc-row-name">{e(r["display_name"])}</div>'
                        f'<div class="tc-row-meta">{pill(r["level"])}</div>{pick_line}',
                        unsafe_allow_html=True,
                    )
                    picked_type = right.selectbox(
                        "Product type", options,
                        index=options.index(current) if current in options else None,
                        placeholder="Choose or type a product type", label_visibility="collapsed",
                        key=f"swap_type_{pid}_{current}",
                    )
                    if picked_type != current:
                        types[pid] = picked_type
                        current = picked_type
                    if not current:
                        st.caption("Choose a type to see safer options.")
                        continue
                    m = safer_matches(sc, current, fragrance_free=ff, audience=audience)
                    if m.empty:
                        st.caption("No certified products for this type with these filters.")
                        continue
                    with st.expander(f"See {plural(len(m), 'safer option')}", expanded=pid == focus):
                        q = st.text_input(
                            "Search safer options", key=f"q_{pid}",
                            placeholder="Search by product or company name",
                            label_visibility="collapsed",
                        ).strip()
                        hits = m
                        if q:
                            hay = m["product_name"] + " " + m["company_name"]
                            hits = m[hay.str.contains(q, case=False, regex=False)]
                            st.caption(f"{len(hits)} match{'es' if len(hits) != 1 else ''} for \"{q}\".")
                        if hits.empty:
                            st.write("No safer options match that search.")
                        else:
                            carousel(hits, f"pg_{pid}_{current}_{ff}_{audience}_{q.lower()}", pid)
        safer_caveat()

elif page == "Next steps":
    if mode == MODE_INST:
        st.markdown(
            '<div class="tc-note">A report to share with your school board, staff, and families. '
            'It uses your audit results and the replacements you chose in Safer options. '
            'Switch to <b>Personal or home</b> in the sidebar for a home action plan instead.</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns([1, 1])
        org = c1.text_input("School or district name", key="rep_org", placeholder="Example: Dublin Unified School District")
        author = c2.text_input("Prepared by", key="rep_author", placeholder="Your name or group")
        st.markdown("**Choose what goes in the report**")
        g1, g2 = st.columns([1, 1])
        by_level = g1.multiselect("Include by risk level", LEVELS, default=list(NEEDS_SWAP), key="rep_levels")
        names = dict(zip(df["product_id"], df["display_name"] + " (" + df["level"] + ")"))
        extra = g2.multiselect("Add individual products", list(names), format_func=names.get,
                               key="rep_products", placeholder="Search or pick products")
        scope = df[df["level"].isin(by_level) | df["product_id"].isin(extra)]
        st.caption(f"The report covers {plural(len(scope), 'product')}: everything in the levels you picked, "
                   f"plus any products you added one by one.")
        if scope.empty:
            st.warning("Pick at least one risk level or product to build the report.")
            st.stop()
        doc = institution_report(df, scope, org.strip(), author.strip())
        fname = "toxicheck_community_report.html"
        label = "Download report"
    else:
        st.markdown(
            '<div class="tc-note">A plan for the products you use at home, built from your audit and the '
            'replacements you chose in Safer options. Switch to <b>School or institution</b> in the sidebar '
            'for a community report instead.</div>',
            unsafe_allow_html=True,
        )
        doc = home_plan(df, product_type)
        fname = "toxicheck_home_plan.html"
        label = "Download plan"
    picks = sum(1 for p in df.loc[df["level"].isin(NEEDS_SWAP), "product_id"] if p in chosen)
    needed = int(df["level"].isin(NEEDS_SWAP).sum())
    if needed and picks < needed:
        b1, b2 = st.columns([3, 1])
        b1.caption(f"You've chosen replacements for {picks} of {needed} products. Pick more to fill in the rest.")
        b2.button("Choose replacements", on_click=lambda: st.session_state.update(nav="Safer options"),
                  use_container_width=True)
    st.download_button(label, data=doc, file_name=fname, mime="text/html", type="primary")
    st.caption("Open the file in a browser and print it, or save it as a PDF to share.")
    components.html(doc, height=1100, scrolling=True)

elif page == "Download":
    card(
        '<div class="tc-step-title">Download the full audit</div>'
        '<div class="tc-faint">One row per product, with its level, list matches, flagged chemicals, and product type.</div>'
    )
    st.download_button(
        "Download audit (CSV)",
        data=df.assign(product_type=[product_type(r) or "" for _, r in df.iterrows()])
        .drop(columns=["display_name", "rank"]).to_csv(index=False),
        file_name="sds_audit.csv",
        mime="text/csv",
    )