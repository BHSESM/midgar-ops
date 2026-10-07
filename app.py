import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math
import json
import re
import html
import calendar
import unicodedata
import tomllib
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import plotly.express as px
import plotly.graph_objects as go

# --- 1. RPG CONFIGURATION & PAGE SETUP ---
st.set_page_config(
    page_title="Shinra Ops Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

UK_TZ = ZoneInfo("Europe/London")


def now_uk():
    """Streamlit Cloud runs on UTC, so always stamp times in UK time."""
    return datetime.now(UK_TZ)


# --- 2. THE ULTIMATE WEAPON CSS (FULL PRODUCTION VERSION) ---
# Note on the keyed containers (bounty cards / battle HUD): Streamlit gives a container created with
# st.container(key="x") a CSS class of "st-key-x". The attribute selector is repeated four times purely
# to out-rank the glass-morphism rule below so these boxes keep their own look.
st.markdown("""
    <style>
    /* Backdrop & Layout */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)),
                    url('https://github.com/BHSESM/midgar-ops/blob/main/BG.jpg?raw=true');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }

    /* Glass-Morphism HUD Containers */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        background: rgba(20, 20, 20, 0.75) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 255, 204, 0.3) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    /* Typography & Neon Colors */
    h1, h2, h3, h4, p, span, label, .stMarkdown {
        color: #f0f0f0 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }

    /* Table Alignment & Formatting */
    div[data-testid="stTable"] table {
        width: 100% !important;
    }
    div[data-testid="stTable"] th {
        text-align: center !important;
        color: #00ffcc !important;
        border-bottom: 1px solid rgba(0, 255, 204, 0.3) !important;
        padding: 12px !important;
        font-size: 0.9rem !important;
    }
    div[data-testid="stTable"] td {
        text-align: center !important;
        padding: 12px !important;
        color: #f0f0f0 !important;
        font-family: 'Courier New', monospace;
    }

    /* Mini-Stat Grid (Inside Party Cards) */
    .mini-stat-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 6px;
        margin: 15px 0;
        padding: 10px;
        background: rgba(0,0,0,0.4);
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .mini-stat-item {
        font-size: 0.7rem !important;
        color: #aaa !important;
        text-align: center;
        line-height: 1.2;
    }
    .mini-stat-value {
        display: block;
        color: #00ffcc !important;
        font-weight: bold;
        font-size: 0.8rem;
    }

    /* Bounty Board Styling (keyed containers) */
    div[class*="st-key-hud_bounty"][class*="st-key-hud_bounty"][class*="st-key-hud_bounty"][class*="st-key-hud_bounty"] {
        background: rgba(0, 255, 204, 0.05) !important;
        border: 1px dashed rgba(0, 255, 204, 0.4) !important;
        padding: 20px !important;
        border-radius: 15px !important;
        margin-bottom: 20px;
        backdrop-filter: none;
        box-shadow: none;
    }

    /* Quest Cards Styling */
    .quest-card {
        background: rgba(30, 20, 10, 0.45);
        border: 1px solid #ffcc00;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.6);
    }

    /* Dual Progress Bars */
    div[data-testid="stProgress"]:nth-of-type(1) > div > div > div > div {
        background-color: #00ffcc !important;
    }
    div[data-testid="stProgress"]:nth-of-type(2) > div > div > div > div {
        background-color: #0099ff !important;
    }

    /* Honors & Metrics */
    .award-card {
        background: rgba(0, 255, 204, 0.1);
        border: 1px solid rgba(0, 255, 204, 0.4);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        margin-bottom: 10px;
    }

    /* Flex Grid Container for Profile Badges */
    .profile-honors-flex-container {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        justify-content: center;
        margin: 12px 0;
        min-height: 52px;
        align-items: center;
    }

    /* Compact Profile Badge Design */
    .profile-honor-badge {
        background: rgba(0, 255, 204, 0.12);
        border: 1px solid rgba(0, 255, 204, 0.6);
        border-radius: 4px;
        color: #00ffcc !important;
        font-size: 0.68rem !important;
        font-weight: bold;
        text-align: center;
        padding: 3px 6px;
        box-shadow: 0 0 6px rgba(0, 255, 204, 0.15);
        white-space: nowrap;
    }

    /* Character Images */
    div[data-testid="stImage"] img {
        max-height: 135px !important;
        filter: drop-shadow(0px 0px 12px rgba(0, 255, 204, 0.5));
        transition: transform 0.4s ease;
    }
    div[data-testid="stImage"] img:hover {
        transform: scale(1.1) rotate(2deg);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(0, 0, 0, 0.6);
        border-radius: 15px;
        padding: 5px 20px;
    }
    .stTabs [aria-selected="true"] {
        color: #00ffcc !important;
        border-bottom: 2px solid #00ffcc !important;
    }

    [data-testid="stMetricValue"] { color: #00ffcc !important; font-family: 'Courier New', monospace; }

    /* Expander */
    div[data-testid="stExpander"] {
        background-color: rgba(30, 30, 30, 0.5) !important;
        border: 1px solid rgba(0, 255, 204, 0.2) !important;
        border-radius: 10px !important;
        margin-top: 15px !important;
    }

    /* Boss Battle CSS (keyed container) */
    div[class*="st-key-hud_battle"][class*="st-key-hud_battle"][class*="st-key-hud_battle"][class*="st-key-hud_battle"] {
        background: linear-gradient(180deg, rgba(0,0,120,0.85) 0%, rgba(0,0,40,0.95) 100%) !important;
        border: 3px solid #ffffff !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: inset 0 0 15px rgba(255,255,255,0.2), 0 10px 30px rgba(0,0,0,0.9) !important;
        font-family: 'Courier New', monospace;
    }
    .boss-profile-container {
        background: rgba(10, 10, 10, 0.85);
        border: 2px solid #ff4b4b;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 20px rgba(255,75,75,0.2);
    }
    .party-battle-row {
        border-bottom: 1px solid rgba(255,255,255,0.15);
        padding: 8px 0;
    }
    .party-battle-name {
        font-weight: bold;
        font-size: 1.1rem;
    }
    .party-battle-hp-text {
        font-weight: bold;
        font-size: 1.0rem;
        text-align: right;
    }

    /* Team Spirit Card */
    .spirit-card {
        background: rgba(0, 255, 204, 0.06);
        border: 1px solid rgba(0, 255, 204, 0.35);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 18px;
        text-align: center;
    }
    .spirit-stat-big {
        font-size: 2.4rem !important;
        font-weight: bold !important;
        color: #00ffcc !important;
        font-family: 'Courier New', monospace;
        display: block;
        line-height: 1.1;
    }
    .spirit-stat-label {
        font-size: 0.78rem !important;
        color: #888 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
        display: block;
    }
    .signal-card-ok {
        background: rgba(0, 255, 204, 0.07);
        border: 1px solid rgba(0, 255, 204, 0.4);
        border-left: 4px solid #00ffcc;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .signal-card-warn {
        background: rgba(255, 204, 0, 0.07);
        border: 1px solid rgba(255, 204, 0, 0.4);
        border-left: 4px solid #ffcc00;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .signal-card-crit {
        background: rgba(255, 75, 75, 0.07);
        border: 1px solid rgba(255, 75, 75, 0.4);
        border-left: 4px solid #ff4b4b;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .data-stamp {
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        color: #9adfd0 !important;
        margin-top: -10px;
        margin-bottom: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MASTER CONFIG, AVATARS & TIMEFRAMES ---
AVATARS = {
    "Sophie (Yuffie)": "https://raw.githubusercontent.com/BHSESM/midgar-ops/main/Yuffie_Kisaragi.png",
    "Bryan (Cloud)": "https://raw.githubusercontent.com/BHSESM/midgar-ops/main/Cloud_Strife.png",
    "Jo (Aerith)": "https://raw.githubusercontent.com/BHSESM/midgar-ops/main/Aerith_Gainsborough.png",
    "Amy (Jessie)": "https://raw.githubusercontent.com/BHSESM/midgar-ops/main/Jessie_from_Final_Fantasy_VII_Remake_render.webp",
    "Alisia (Tifa)": "https://raw.githubusercontent.com/BHSESM/midgar-ops/main/Tifa_Lockhart_from_FFVII_Remake_promo_render.webp",
    "Victor (Vincent)": "https://raw.githubusercontent.com/BHSESM/midgar-ops/main/Vincent_Valentine_from_FFVII_Rebirth_promo_render.webp"
}

# Direct raw link (not the github.com "?raw=true" redirect) so the screenshot button can capture it.
SEPHIROTH_IMG = "https://raw.githubusercontent.com/BHSESM/midgar-ops/c0fcf5cc9ab880e330b5d3314d3e10b6afdee8fe/Sephtransp.png"

TITLES = [
    "Sector 7 Recruit 🧰", "Midgar Mechanic 🔧", "Shinra Support Agent 🖥️",
    "Turk-in-Training 💼", "Materia Engineer 💠", "Junon Operative ⚙️",
    "Rocket Town Specialist 🚀", "Nibelheim Technician 🔩", "SOLDIER Tech 3rd Class ⚔️",
    "SOLDIER Tech 2nd Class ⚔️", "SOLDIER Tech 1st Class ⚔️", "Midgar Hero 🛡️",
    "Planet's Defender 🌿", "Lifestream Sage 💫", "Ancient of the LAN ✨"
]

TEAM_TITLES = [
    ("Sector 7 Survivors", "The party is just getting started. Keep pushing."),
    ("Midgar Resistance", "The team is finding its rhythm. Avalanche assembles."),
    ("Avalanche Operatives", "Solid output across the board. The Planet feels it."),
    ("Elite Strike Force", "The team is firing on all cylinders. Shinra is rattled."),
    ("Guardians of the Planet", "Legendary performance. The Lifestream flows strong. 🌿"),
]

SHOP_ITEMS = {
    "15m Extra Lunch": 600,
    "15m Early Leave": 600,
    "10m Extra Lunch": 400,
    "10m Early Leave": 400,
    "5m Extra Lunch": 200,
    "5m Early Leave": 200
}

SHIFT_WEIGHTS = {
    "Sophie (Yuffie)": 1.0,
    "Bryan (Cloud)": 1.0,
    "Jo (Aerith)": 0.75,
    "Amy (Jessie)": 1.0,
    "Alisia (Tifa)": 1.0,
    "Victor (Vincent)": 0.28
}

TIME_SLOTS = [
    "08:00:00", "08:30:00", "09:00:00", "09:30:00", "10:00:00", "10:30:00",
    "11:00:00", "11:30:00", "12:00:00", "12:30:00", "13:00:00", "13:30:00",
    "14:00:00", "14:30:00", "15:00:00", "15:30:00", "16:00:00", "16:30:00",
    "17:00:00", "17:30:00", "18:00:00", "18:30:00", "19:00:00"
]

OUTCOME_KEYS = [
    "COMP-FULL D2S", "COMP-FULL S2S", "COMP-FULL INV", "COMP-FULL NC",
    "I&L D2S", "I&L S2S", "I&L INV", "I&L NC",
    "Abort D2S", "Abort S2S", "Abort INV", "Abort NC"
]

# Team mission targets (used on the Bounty Board, Party Spirit and the Morning Brief)
GOAL_OUT = 500
GOAL_ANS = 98.0
MAX_AWOL = 5.0
GOAL_SLA = 92.5

# Boss settings
BOSS_MAX_HP = 95000
BOSS_DMG_PER_EXP = 10

# Working pattern for pacing: Mon-Fri full team, Saturday skeleton crew (counts as half a day), Sunday closed.
SATURDAY_WEIGHT = 0.5

# Non-operative keys stored alongside the operatives in the saved data
RESERVED_KEYS = {"team_stats", "volume_stats", "outcome_stats", "meta", "history_log"}
REMOVED_FIELDS = ("avg_ans_time", "avg_call_time")

# Daily history entries are stored compactly as lists in this order
HIST_FIELDS = ["in", "out", "open", "close", "ans", "awol", "lvl", "exp"]
HIST_MAX_ENTRIES = 45

LINE_COLORS = ["#00ffcc", "#0099ff", "#ff4b4b", "#ffcc00", "#c77dff", "#ff8c42"]


# --- 4. CORE ENGINE FUNCTIONS ---
def get_stats(stats):
    frontline_exp = stats["in"] + stats["out"] + stats["open"] + stats["close"]

    side_quest_exp = 0
    side_quest_gil = 0
    for quest in stats.get("side_quests", []):
        side_quest_exp += quest.get("simulated_exp", 0)
        side_quest_gil += quest.get("gil_reward", 0)

    exp = frontline_exp + side_quest_exp
    level = int(math.sqrt(exp / 50))
    rank = TITLES[min(max(level - 1, 0), len(TITLES) - 1)]

    current_lvl_base = 50 * (level ** 2)
    next_lvl_base = 50 * ((level + 1) ** 2)
    exp_in_level = exp - current_lvl_base
    exp_needed_total = next_lvl_base - current_lvl_base
    exp_pct = min(1.0, max(0.0, exp_in_level / exp_needed_total)) if exp_needed_total > 0 else 0

    # HP never drops below 100, so levelling up can never shrink the pool.
    max_hp = max(100, 10 * (level ** 2))
    damage = round(((1 - (stats["ans"] / 100)) * 800) + (stats["awol"] * 9))
    current_hp = max(0, max_hp - damage)
    hp_pct = current_hp / max_hp if max_hp > 0 else 0

    # Weight is synced from SHIFT_WEIGHTS on every load (see init below)
    weight = stats.get("weight", 1.0) or 1.0
    frontline_gil = round((frontline_exp / weight) ** 0.9) if frontline_exp > 0 else 0

    total_earned = frontline_gil + side_quest_gil
    current_gil = total_earned - stats.get("spent", 0)

    return {
        "Level": level,
        "Rank": rank,
        "HP_Pct": hp_pct,
        "EXP_Pct": exp_pct,
        "GIL": current_gil,
        "Next_XP": int(next_lvl_base - exp),
        "HP_Display": f"{current_hp}/{max_hp}",
        "Raw_EXP": exp,
        "Current_HP_Raw": current_hp,
        "Max_HP_Raw": max_hp
    }

def get_daily_averages(name, stats):
    days = stats.get("days_worked", 0)
    shift_weight = SHIFT_WEIGHTS.get(name, 1.0)
    effective_days = days * shift_weight

    if effective_days <= 0:
        return {"avg_in": None, "avg_out": None, "avg_open": None, "avg_close": None}

    return {
        "avg_in": math.floor(stats["in"] / effective_days),
        "avg_out": math.floor(stats["out"] / effective_days),
        "avg_open": math.floor(stats["open"] / effective_days),
        "avg_close": math.floor(stats["close"] / effective_days),
    }

def frontline_activity(name):
    s = st.session_state.master_data[name]
    return s["in"] + s["out"] + s["open"] + s["close"]

def calculate_winners(metric, staff_list, high_is_best=True):
    # Only operatives who have actually logged some work are in the running,
    # so nobody wins a badge on day 1 just because everyone is still on zero.
    active = [n for n in staff_list if frontline_activity(n) > 0]
    if not active:
        return []
    vals = {n: st.session_state.master_data[n][metric] for n in active}
    target = max(vals.values()) if high_is_best else min(vals.values())
    if high_is_best and target <= 0:
        return []
    return [n for n, v in vals.items() if v == target]

def hp_colour(pct, hi=0.75, lo=0.40):
    if pct > hi: return "#00ffcc"
    if pct > lo: return "#ffcc00"
    return "#ff4b4b"

def fresh_operative():
    return {
        "in": 0, "out": 0, "open": 0, "close": 0,
        "ans": 100, "awol": 0, "weight": 1.0,
        "spent": 0, "history": [], "days_worked": 0,
        "side_quests": [], "active_quest": {},
    }

def load_data():
    if "staff_json" in st.secrets:
        data = json.loads(st.secrets["staff_json"])
        data.setdefault("team_stats", {
            "success_pct": 0.0, "sla_pct": 0.0,
            "longest_wait": "00:00:00", "avg_queue": "00:00:00"
        })
        if "volume_stats" not in data:
            data["volume_stats"] = {slot: 0 for slot in TIME_SLOTS}
        if "outcome_stats" not in data:
            data["outcome_stats"] = {key: "0.0%" for key in OUTCOME_KEYS}
        return data

    base = {name: fresh_operative() for name in AVATARS.keys()}
    base["team_stats"] = {
        "success_pct": 0.0, "sla_pct": 0.0,
        "longest_wait": "00:00:00", "avg_queue": "00:00:00"
    }
    base["volume_stats"] = {slot: 0 for slot in TIME_SLOTS}
    base["outcome_stats"] = {key: "0.0%" for key in OUTCOME_KEYS}
    return base


# --- DATES, PACING & HISTORY HELPERS ---
def day_weight(d):
    wd = d.weekday()
    if wd < 5: return 1.0
    if wd == 5: return SATURDAY_WEIGHT
    return 0.0

def month_days(d):
    n = calendar.monthrange(d.year, d.month)[1]
    return [date(d.year, d.month, i) for i in range(1, n + 1)]

def month_progress(d):
    """(working days elapsed up to and including d, total working days in d's month)"""
    days = month_days(d)
    total = sum(day_weight(x) for x in days)
    elapsed = sum(day_weight(x) for x in days if x <= d)
    return elapsed, total

def previous_working_day(today):
    d = today - timedelta(days=1)
    while day_weight(d) == 0:
        d -= timedelta(days=1)
    return d

def get_data_date():
    s = st.session_state.master_data.get("meta", {}).get("data_date")
    try:
        return date.fromisoformat(s)
    except (TypeError, ValueError):
        return now_uk().date()

def fmt_day(d):
    return d.strftime("%a %d %b")

def data_stamp_text():
    meta = st.session_state.master_data.get("meta", {})
    if not meta.get("data_date"):
        return "No morning update committed yet"
    txt = f"📅 Data up to {fmt_day(get_data_date())}"
    if meta.get("last_updated"):
        txt += f"  ·  updated {meta['last_updated']}"
    return txt

def touch_last_updated():
    st.session_state.master_data.setdefault("meta", {})["last_updated"] = now_uk().strftime("%a %d %b %H:%M")

def record_history(for_date):
    md = st.session_state.master_data
    hist = md.setdefault("history_log", {})
    entry = {}
    for n in STAFF_NAMES:
        s = md[n]
        r = get_stats(s)
        entry[n] = [s["in"], s["out"], s["open"], s["close"], s["ans"], s["awol"], r["Level"], r["Raw_EXP"]]
    hist[for_date.isoformat()] = entry
    for old in sorted(hist)[:-HIST_MAX_ENTRIES]:
        del hist[old]

def get_level_ups():
    """Compare live levels against the last history entry before the current data date."""
    md = st.session_state.master_data
    hist = md.get("history_log", {})
    d = get_data_date().isoformat()
    prev_dates = [k for k in hist if k < d]
    if not prev_dates:
        return []
    prev = hist[max(prev_dates)]
    ups = []
    for n in STAFF_NAMES:
        if n not in prev:
            continue
        old_lvl = prev[n][HIST_FIELDS.index("lvl")]
        r = get_stats(md[n])
        if r["Level"] > old_lvl:
            old_rank = TITLES[min(max(old_lvl - 1, 0), len(TITLES) - 1)]
            ups.append({"name": n, "from": old_lvl, "to": r["Level"],
                        "rank": r["Rank"], "new_rank": r["Rank"] != old_rank})
    return ups

def boss_state(total_exp):
    damage = total_exp * BOSS_DMG_PER_EXP
    hp = max(0, BOSS_MAX_HP - damage)
    pct = hp / BOSS_MAX_HP
    if pct > 0.50:
        phase = "Form 1: Sephiroth (SOLDIER Legend)"
        flavour = "🔮 Sephiroth calmly prepares his blade... 'Is that all the strength the planet has left?'"
    elif pct > 0.15:
        phase = "Form 2: Bizarro Sephiroth (Core Mutation)"
        flavour = "⚡ The battlefield distorts! Bizarro Sephiroth emerges from the deep energetic Lifestream!"
    elif pct > 0.0:
        phase = "FINAL Form: Safer Sephiroth (One-Winged Angel Apex)"
        flavour = "🌌 CRITICAL! Sephiroth is calling down Supernova! Break his defenses immediately!"
    else:
        phase = "💥 SEPHIROTH DEFEATED 💥"
        flavour = "✨ VICTORY FANFARE! The planet is secure! Grid colors neutralized."
    return {"damage": damage, "hp": hp, "pct": pct, "phase": phase, "flavour": flavour}

def boss_projection(total_exp, d):
    """Plain-English forecast of when Sephiroth falls at the current pace."""
    needed = BOSS_MAX_HP / BOSS_DMG_PER_EXP
    if total_exp >= needed:
        return "💥 Already defeated this month!"
    elapsed, total = month_progress(d)
    if elapsed <= 0 or total_exp <= 0:
        return "⏳ Forecast appears once the month gets going."
    rate = total_exp / elapsed
    cum = 0.0
    for x in month_days(d):
        cum += day_weight(x)
        if cum * rate >= needed:
            return f"🎯 At this pace Sephiroth falls on {fmt_day(x)}."
    proj_pct = min(100, rate * total / needed * 100)
    return f"⚠️ At this pace we'll land {proj_pct:.0f}% of the damage needed – time to turn it up!"

def team_overview():
    md = st.session_state.master_data
    all_res = {n: get_stats(md[n]) for n in STAFF_NAMES}
    n_staff = len(STAFF_NAMES) or 1
    total_out = sum(md[n]["out"] for n in STAFF_NAMES)
    avg_ans = sum(md[n]["ans"] for n in STAFF_NAMES) / n_staff if STAFF_NAMES else 100.0
    total_awol = sum(md[n]["awol"] for n in STAFF_NAMES)
    sla = float(md["team_stats"]["sla_pct"])
    missions = [
        ("📞 Outbound", total_out >= GOAL_OUT, f"{total_out}/{GOAL_OUT}"),
        ("🛡️ Answer Rate", avg_ans >= GOAL_ANS, f"{avg_ans:.1f}%"),
        ("🐌 AWOL Pool", total_awol <= MAX_AWOL,
         f"{MAX_AWOL - total_awol:g}/{MAX_AWOL:g}m left" if total_awol <= MAX_AWOL
         else f"{total_awol - MAX_AWOL:g}m over"),
        ("📋 SLA", sla >= GOAL_SLA, f"{sla:.1f}%"),
    ]
    missions_hit = sum(1 for m in missions if m[1])
    avg_lvl = round(sum(r["Level"] for r in all_res.values()) / n_staff, 1) if STAFF_NAMES else 0
    combined = missions_hit + int(avg_lvl / 3)
    title, flavour = TEAM_TITLES[min(combined, len(TEAM_TITLES) - 1)]
    total_exp = sum(r["Raw_EXP"] for r in all_res.values())
    return {
        "all_res": all_res, "total_out": total_out, "avg_ans": avg_ans, "total_awol": total_awol,
        "sla": sla, "missions": missions, "missions_hit": missions_hit, "avg_lvl": avg_lvl,
        "title": title, "flavour": flavour, "total_exp": total_exp,
    }

def parse_quest_time(q, year):
    if q.get("ts"):
        try:
            return datetime.fromisoformat(q["ts"]).replace(tzinfo=None)
        except ValueError:
            pass
    try:
        return datetime.strptime(f"{q.get('timestamp', '')}/{year}", "%d/%m %H:%M/%Y")
    except ValueError:
        return datetime.min


# --- RUNNING INIT SEQUENCING ---
if "master_data" not in st.session_state:
    st.session_state.master_data = load_data()
if "editor_ver" not in st.session_state:
    st.session_state.editor_ver = 0

md = st.session_state.master_data
for _name, _val in list(md.items()):
    if _name in RESERVED_KEYS or not isinstance(_val, dict) or "in" not in _val:
        continue
    _val.setdefault("days_worked", 0)
    _val.setdefault("side_quests", [])
    _val.setdefault("active_quest", {})
    _val.setdefault("history", [])
    _val.setdefault("spent", 0)
    for _f in REMOVED_FIELDS:
        _val.pop(_f, None)
    # Keep GIL weighting in step with SHIFT_WEIGHTS everywhere
    _val["weight"] = SHIFT_WEIGHTS.get(_name, _val.get("weight", 1.0))

md.setdefault("volume_stats", {slot: 0 for slot in TIME_SLOTS})
md.setdefault("outcome_stats", {key: "0.0%" for key in OUTCOME_KEYS})
md.setdefault("meta", {})
md.setdefault("history_log", {})

STAFF_NAMES = [
    k for k in md.keys()
    if k not in RESERVED_KEYS
    and isinstance(md[k], dict)
    and "in" in md[k]
]

def blank_snapshot():
    return {"answered": 0, "pct": 100.0, "outbound": 0, "open": 0, "close": 0}

if "daily_snapshot_data" not in st.session_state:
    st.session_state.daily_snapshot_data = {name: blank_snapshot() for name in STAFF_NAMES}
for name in STAFF_NAMES:
    st.session_state.daily_snapshot_data.setdefault(name, blank_snapshot())

HONORS_MAP = [
    ("📞 Inbound King/Queen", "in", True),
    ("☎️ Outbound Ace", "out", True),
    ("📂 Request Opener", "open", True),
    ("✅ Ticket Crusher", "close", True),
    ("💯 Comms Master", "ans", True),
    ("🛡️ Always Ready", "awol", False)
]

OPERATIVE_HONORS = {name: [] for name in STAFF_NAMES}
for title, key, is_high in HONORS_MAP:
    for winner in calculate_winners(key, STAFF_NAMES, is_high):
        OPERATIVE_HONORS[winner].append(title)


# --- SCREENSHOT / CAPTURE COMPONENT ---
CAPTURE_BASE_CSS = """
* { box-sizing: border-box; }
body { margin: 0; background: transparent; font-family: 'Segoe UI', Arial, sans-serif; color: #f0f0f0; }
.toolbar { display: flex; gap: 10px; align-items: center; margin: 4px 0 12px; }
.toolbar button {
    background: rgba(0,255,204,0.12); color: #00ffcc; border: 1px solid #00ffcc; border-radius: 8px;
    padding: 8px 16px; font-weight: bold; font-size: 14px; cursor: pointer; font-family: 'Courier New', monospace;
}
.toolbar button:hover { background: rgba(0,255,204,0.25); }
#st { color: #ccc; font-size: 13px; }
.toolbar.sub { flex-wrap: wrap; margin-top: -4px; }
.toolbar.sub button { font-size: 13px; padding: 6px 12px; }
.hint { color: #9adfd0; font-size: 13px; }
.solo { padding: 24px !important; background: #0a0e13; border-radius: 14px; }
#cap { display: inline-block; background: #0a0e13; padding: 22px; border-radius: 14px; border: 1px solid rgba(0,255,204,0.35); }
.mono { font-family: 'Courier New', monospace; }
.bar { background: rgba(255,255,255,0.08); border-radius: 4px; height: 9px; overflow: hidden; }
.bar > div { height: 100%; }
"""

CAPTURE_JS = """
const statusEl = document.getElementById('st');
function setS(t) { statusEl.textContent = t; }
async function render(id) {
  const el = document.getElementById(id || 'cap');
  const solo = id && id !== 'cap';
  if (solo) el.classList.add('solo');
  try {
    return await html2canvas(el, { useCORS: true, backgroundColor: '#0a0e13', scale: 2, logging: false });
  } finally {
    if (solo) el.classList.remove('solo');
  }
}
function toBlob(c) { return new Promise(r => c.toBlob(r, 'image/png')); }
function ready() {
  if (typeof html2canvas === 'undefined') { setS('Screenshot tool still loading – try again in a second'); return false; }
  return true;
}
async function copyImg(id) {
  if (!ready()) return;
  setS('Capturing…');
  try {
    const item = new ClipboardItem({ 'image/png': render(id).then(toBlob) });
    await navigator.clipboard.write([item]);
    setS('✅ Copied – paste straight into Teams (Ctrl+V)');
  } catch (e) {
    console.error(e);
    setS('⚠️ Your browser blocked copying – use Download instead');
  }
}
// ---- Multi-section helpers (only used when SECTIONS is set) ----
let nextIdx = 0;
async function copyNext() {
  if (!SECTIONS.length) return;
  const [id, label] = SECTIONS[nextIdx];
  await copyImg(id);
  setS(`✅ Copied ${nextIdx + 1}/${SECTIONS.length}: ${label} – paste, then click again`);
  nextIdx = (nextIdx + 1) % SECTIONS.length;
  const btn = document.getElementById('nextbtn');
  if (btn) btn.textContent = `➡️ Copy next (${nextIdx + 1}/${SECTIONS.length}: ${SECTIONS[nextIdx][1]})`;
}
async function copyAllHtml() {
  // Experimental: puts every section on the clipboard as one rich-text block of images.
  if (!ready()) return;
  setS('Capturing all sections…');
  try {
    const build = (async () => {
      let h = '<div>';
      for (const [id] of SECTIONS) {
        const c = await render(id);
        h += `<img src="${c.toDataURL('image/png')}" width="${Math.round(c.width / 2)}"><br>`;
      }
      return new Blob([h + '</div>'], { type: 'text/html' });
    })();
    await navigator.clipboard.write([new ClipboardItem({ 'text/html': build })]);
    setS('🧪 Copied all sections – paste into Teams. If nothing appears, use "Copy next" or "Download all" instead.');
  } catch (e) {
    console.error(e);
    setS('⚠️ This browser cannot copy several images at once – use "Copy next" or "Download all" instead');
  }
}
async function dlAll() {
  if (!ready()) return;
  for (let i = 0; i < SECTIONS.length; i++) {
    setS(`Saving ${i + 1}/${SECTIONS.length}…`);
    await dlImg(SECTIONS[i][0]);
    await new Promise(r => setTimeout(r, 400));
  }
  setS('💾 All sections saved – select them in Downloads and drag them into Teams together');
}
async function dlImg(id) {
  if (!ready()) return;
  setS('Capturing…');
  try {
    const c = await render(id);
    const a = document.createElement('a');
    a.href = c.toDataURL('image/png');
    a.download = (id && id !== 'cap') ? FILENAME.replace('.png', '-' + id.replace('sec-', '') + '.png') : FILENAME;
    document.body.appendChild(a); a.click(); a.remove();
    setS('💾 Downloaded');
  } catch (e) {
    console.error(e);
    setS('⚠️ Download failed');
  }
}
"""

def capture_component(inner_html, extra_css, height, filename, sections=None):
    """sections: optional list of (element id, button label) that can be copied on their own.
    Smaller images display much larger when pasted into Teams."""
    sec_buttons = ""
    if sections:
        sec_buttons = ("<div class='toolbar sub'><span class='hint'>Copy one section (shows bigger in Teams):</span>"
                       + "".join(f"<button onclick=\"copyImg('{sid}')\">{lbl}</button>" for sid, lbl in sections)
                       + "</div>"
                       "<div class='toolbar sub'><span class='hint'>All sections:</span>"
                       f"<button id='nextbtn' onclick='copyNext()'>➡️ Copy next (1/{len(sections)}: {sections[0][1]})</button>"
                       "<button onclick='dlAll()'>💾 Download all</button>"
                       "<button onclick='copyAllHtml()'>🧪 Copy all at once (experimental)</button>"
                       "</div>")
    doc = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<script src='https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js'></script>"
        f"<style>{CAPTURE_BASE_CSS}{extra_css}</style></head><body>"
        "<div class='toolbar'>"
        f"<button onclick=\"copyImg('cap')\">📋 Copy {'whole brief' if sections else 'image'}</button>"
        "<button onclick=\"dlImg('cap')\">💾 Download PNG</button>"
        "<span id='st'></span></div>"
        f"{sec_buttons}"
        f"<div id='cap'>{inner_html}</div>"
        f"<script>const FILENAME = {json.dumps(filename)};const SECTIONS = {json.dumps(sections or [], ensure_ascii=False)};{CAPTURE_JS}</script>"
        "</body></html>"
    )
    if hasattr(st, "iframe"):
        # Newer Streamlit: auto-sizes the frame to fit the brief
        st.iframe(doc, height="content")
    else:
        components.html(doc, height=height, scrolling=True)


BRIEF_CSS = """
#cap { width: 1180px; }
.sec { margin-bottom: 20px; }
.sec:last-of-type { margin-bottom: 0; }
.hdr { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid rgba(0,255,204,0.35); padding-bottom: 12px; margin-bottom: 18px; }
.hdr .t { font-size: 32px; font-weight: bold; color: #00ffcc; font-family: 'Courier New', monospace; letter-spacing: 1px; }
.hdr .s { font-size: 16px; color: #9adfd0; font-family: 'Courier New', monospace; text-align: right; line-height: 1.5; }
.row { display: flex; gap: 16px; margin-bottom: 18px; }
.panel { flex: 1; background: rgba(255,255,255,0.03); border: 1px solid rgba(0,255,204,0.25); border-radius: 12px; padding: 16px 18px; }
.lbl { font-size: 14px; color: #8a9; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; }
.team { font-size: 28px; font-weight: bold; color: #00ffcc; font-family: 'Courier New', monospace; }
.flav { font-size: 15px; color: #bbb; font-style: italic; margin-top: 4px; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.chip { border-radius: 16px; padding: 4px 12px; font-size: 15px; }
.chip.ok { background: rgba(0,255,204,0.14); border: 1px solid rgba(0,255,204,0.6); color: #00ffcc; }
.chip.no { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.2); color: #999; }
.boss { display: flex; gap: 16px; align-items: center; }
.boss img { height: 110px; width: auto; border-radius: 8px; border: 2px solid #ff4b4b; }
.lvlups { background: rgba(255,204,0,0.08); border: 1px solid rgba(255,204,0,0.55); border-radius: 12px; padding: 12px 18px; }
.lvlups .h { color: #ffcc00; font-weight: bold; font-size: 18px; margin-bottom: 4px; }
.lvlups .i { font-size: 17px; color: #f0f0f0; margin: 4px 0; }
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.card { background: rgba(20,20,20,0.9); border: 2px solid; border-radius: 12px; padding: 16px; }
.card .top { display: flex; gap: 12px; align-items: center; }
.av { width: 84px; height: 84px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.av img { max-width: 84px; max-height: 84px; width: auto; height: auto; }
.card .nm { font-size: 21px; font-weight: bold; }
.card .rk { font-size: 15px; color: #bbb; }
.card .lv { font-size: 16px; color: #00ffcc; font-family: 'Courier New', monospace; margin-top: 3px; font-weight: bold; }
.g6 { display: grid; grid-template-columns: repeat(6, 1fr); gap: 2px; background: rgba(0,0,0,0.45); border-radius: 8px; padding: 10px 2px; margin: 12px 0 10px; }
.g6 div { text-align: center; font-size: 12px; color: #999; }
.g6 b { display: block; color: #00ffcc; font-size: 18px; font-family: 'Courier New', monospace; }
.badges { display: flex; flex-wrap: wrap; gap: 5px; min-height: 24px; margin-bottom: 8px; }
.badge { font-size: 12px; color: #00ffcc; border: 1px solid rgba(0,255,204,0.6); border-radius: 4px; padding: 2px 6px; }
.bl { display: flex; justify-content: space-between; font-size: 14px; color: #bbb; margin: 8px 0 4px; font-family: 'Courier New', monospace; }
.bar { height: 11px; }
.avgs { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.avg h4 { margin: 0 0 10px; font-size: 18px; font-family: 'Courier New', monospace; }
.ar { display: flex; align-items: center; gap: 10px; margin: 7px 0; font-size: 16px; }
.ar .n { width: 78px; color: #ddd; }
.ar .bar { flex: 1; height: 16px; }
.ar .v { width: 40px; text-align: right; font-family: 'Courier New', monospace; font-weight: bold; font-size: 18px; }
.foot { margin-top: 16px; font-size: 12px; color: #667; text-align: center; font-family: 'Courier New', monospace; }
"""

NOTES_CSS = """
.notes .greet { font-size: 24px; font-weight: bold; color: #f0f0f0; margin-bottom: 12px; }
.notes .para { font-size: 17px; color: #ddd; margin: 0 0 12px; line-height: 1.5; }
.nsecs { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 16px; margin-bottom: 12px; }
.nsec { background: rgba(255,255,255,0.03); border: 1px solid rgba(0,255,204,0.25); border-left: 5px solid #00ffcc; border-radius: 12px; padding: 14px 18px; }
.nsec h5 { margin: 0 0 10px; font-size: 20px; color: #00ffcc; }
.nsec ul { margin: 0; padding-left: 20px; }
.nsec li { font-size: 17px; color: #e6e6e6; line-height: 1.5; margin: 5px 0; }
.nsec li b, .notes .para b { color: #ffcc00; }
"""

BULLET_RE = re.compile(r"^\s*(?:[*•\-–·▪◦]|\d+[.)])(?:\s+|$)")


def ordinal_date(d):
    n = d.day
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{d.strftime('%A')} {n}{suffix} {d.strftime('%B %Y')}"


def inline_fmt(text):
    """Escape the text, then turn **bold** into bold."""
    t = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def format_bullet(text):
    # "Label: detail" -> bold label, as long as the label is short
    m = re.match(r"^(.{1,45}?):\s+(.+)$", text)
    if m and "**" not in m.group(1):
        return f"<b>{html.escape(m.group(1))}:</b> {inline_fmt(m.group(2))}"
    return inline_fmt(text)


def is_emoji_start(text):
    ch = text[:1]
    if not ch or ch.isalnum():
        return False
    cp = ord(ch)
    return unicodedata.category(ch) in ("So", "Sk") or cp >= 0x1F000 or 0x2600 <= cp <= 0x27BF


def notes_to_html(raw):
    """Turn pasted morning-brief notes into styled sections.
    Headings: a line starting with an emoji (e.g. '🌤️ Weather'), a short line ending in ':',
    or any line followed by '*'/'-'/'•' bullets. Lines under a heading become that section's points,
    with or without bullet symbols (Teams drops them when you copy). Text before the first heading
    is the greeting/intro; text after a blank line that follows a section is a closing paragraph.
    {date} becomes today's date and **text** is bold."""
    raw = (raw or "").replace("{date}", ordinal_date(now_uk().date())).replace("\r", "")
    lines = raw.split("\n")
    is_bullet = [bool(BULLET_RE.match(l)) for l in lines]
    nonempty = [i for i, l in enumerate(lines) if l.strip()]
    if not nonempty:
        return ""
    gaps = sum(1 for a, b in zip(nonempty, nonempty[1:]) if b - a > 1)
    # Some pastes put a blank line between every line; then blank lines carry no meaning.
    double_spaced = len(nonempty) > 3 and gaps >= 0.7 * (len(nonempty) - 1)

    def next_nonempty(i):
        return next((j for j in range(i + 1, len(lines)) if lines[j].strip()), None)

    def is_heading(i):
        text = lines[i].strip()
        if is_bullet[i] or len(text) > 90:
            return False
        if is_emoji_start(text):
            return True
        nxt = next_nonempty(i)
        if nxt is None:
            return False
        if is_bullet[nxt]:
            return True
        return text.endswith(":") and len(text) <= 60

    blocks, greet = [], None
    current = None        # open section
    ended = False         # blank line seen after the section had points
    for i, line in enumerate(lines):
        text = line.strip()
        if not text:
            if current is not None and current["items"] and not double_spaced:
                ended = True
            continue
        if is_heading(i):
            current = {"title": inline_fmt(text.rstrip(":") if text.endswith(":") else text), "items": []}
            blocks.append(current)
            ended = False
            continue
        if is_bullet[i]:
            item = BULLET_RE.sub("", line, count=1).strip()
            if not item:
                continue  # empty bullet
            if current is None or (ended and current["title"] is None):
                current = {"title": None, "items": []}
                blocks.append(current)
            ended = False
            current["items"].append(format_bullet(item))
            continue
        if current is not None and not ended:
            current["items"].append(format_bullet(text))
            continue
        # Plain paragraph: greeting/intro before sections, closing note after them
        current, ended = None, False
        if greet is None and not blocks:
            greet = inline_fmt(text)
        else:
            blocks.append({"para": inline_fmt(text)})

    out = ["<div class='notes'>"]
    if greet:
        out.append(f"<div class='greet'>{greet}</div>")
    secs = []
    for b in blocks:
        if "para" in b:
            if secs:
                out.append(f"<div class='nsecs'>{''.join(secs)}</div>")
                secs = []
            out.append(f"<div class='para'>{b['para']}</div>")
            continue
        if not b["items"]:
            if b["title"]:  # a "heading" with nothing under it is really just a line of text
                if secs:
                    out.append(f"<div class='nsecs'>{''.join(secs)}</div>")
                    secs = []
                out.append(f"<div class='para'>{b['title']}</div>")
            continue
        title = f"<h5>{b['title']}</h5>" if b["title"] else ""
        items = "".join(f"<li>{it}</li>" for it in b["items"])
        secs.append(f"<div class='nsec'>{title}<ul>{items}</ul></div>")
    if secs:
        out.append(f"<div class='nsecs'>{''.join(secs)}</div>")
    out.append("</div>")
    return "".join(out)


def build_brief_html(notes_text=""):
    md = st.session_state.master_data
    ov = team_overview()
    boss = boss_state(ov["total_exp"])
    d = get_data_date()
    elapsed, total = month_progress(d)
    ups = get_level_ups()
    meta = md.get("meta", {})

    chips = "".join(
        f"<span class='chip {'ok' if hit else 'no'}'>{'✅' if hit else '⬜'} {html.escape(lbl)} · {html.escape(val)}</span>"
        for lbl, hit, val in ov["missions"]
    )
    pace_out = round(GOAL_OUT * elapsed / total) if total else 0

    parts = []
    hdr_html = (
        "<div class='hdr'><div class='t'>⚔️ MIDGAR OPS · MORNING BRIEF</div>"
        f"<div class='s'>Data up to {fmt_day(d)}<br>"
        f"Day {elapsed:g} of {total:g} working days"
        + (f" · updated {html.escape(meta['last_updated'])}" if meta.get('last_updated') else "")
        + "</div></div>"
    )
    notes_html = notes_to_html(notes_text)
    if notes_html:
        parts.append(f"<div class='sec' id='sec-news'>{hdr_html}{notes_html}</div>")
        team_hdr = ""
    else:
        team_hdr = hdr_html
    boss_col = "#ff4b4b" if boss["hp"] > 0 else "#00ffcc"
    team_parts = [team_hdr]
    team_parts.append(
        "<div class='row'>"
        "<div class='panel'><div class='lbl'>Party designation</div>"
        f"<div class='team'>{html.escape(ov['title'])}</div><div class='flav'>{html.escape(ov['flavour'])}</div>"
        f"<div class='chips'>{chips}</div>"
        f"<div class='flav' style='margin-top:8px;'>Outbound pace check: target by now ≈ {pace_out}, actual {ov['total_out']}</div></div>"
        "<div class='panel'><div class='boss'>"
        f"<img src='{SEPHIROTH_IMG}' crossorigin='anonymous'>"
        "<div style='flex:1;'><div class='lbl'>Month-end boss</div>"
        f"<div style='color:{boss_col};font-weight:bold;font-size:19px;'>{html.escape(boss['phase'])}</div>"
        f"<div class='bl'><span>HP</span><span>{boss['hp']:,} / {BOSS_MAX_HP:,}</span></div>"
        f"<div class='bar' style='height:12px;'><div style='width:{boss['pct']*100:.1f}%;background:{boss_col};'></div></div>"
        f"<div class='flav' style='margin-top:6px;'>{html.escape(boss_projection(ov['total_exp'], d))}</div>"
        "</div></div></div></div>"
    )

    if ups:
        items = ""
        for u in ups:
            line = f"🌟 <b>{html.escape(u['name'])}</b> reached <b>Level {u['to']}</b>"
            if u["new_rank"]:
                line += f" – new title: <b>{html.escape(u['rank'])}</b>"
            items += f"<div class='i'>{line}</div>"
        team_parts.append(f"<div class='lvlups'><div class='h'>🎉 LEVEL UP!</div>{items}</div>")
    parts.append(f"<div class='sec' id='sec-team'>{''.join(team_parts)}</div>")

    cards = ""
    for name in STAFF_NAMES:
        s = md[name]
        r = ov["all_res"][name]
        col = hp_colour(r["HP_Pct"])
        badges = "".join(f"<span class='badge'>{html.escape(b)}</span>" for b in OPERATIVE_HONORS[name])
        cards += (
            f"<div class='card' style='border-color:{col};'>"
            f"<div class='top'><div class='av'><img src='{AVATARS.get(name, '')}' crossorigin='anonymous'></div>"
            f"<div><div class='nm'>{html.escape(name)}</div><div class='rk'>{html.escape(r['Rank'])}</div>"
            f"<div class='lv'>LVL {r['Level']} · 💰 {r['GIL']:,} GIL</div></div></div>"
            "<div class='g6'>"
            f"<div>IN<b>{s['in']}</b></div><div>OUT<b>{s['out']}</b></div>"
            f"<div>OPEN<b>{s['open']}</b></div><div>CLOSE<b>{s['close']}</b></div>"
            f"<div>ANS%<b>{s['ans']}%</b></div><div>AWOL<b>{s['awol']}m</b></div></div>"
            f"<div class='badges'>{badges}</div>"
            f"<div class='bl'><span>❤️ HP</span><span>{r['HP_Display']}</span></div>"
            f"<div class='bar'><div style='width:{r['HP_Pct']*100:.1f}%;background:{col};'></div></div>"
            f"<div class='bl'><span>💠 EXP</span><span>{r['Next_XP']} to next</span></div>"
            f"<div class='bar'><div style='width:{r['EXP_Pct']*100:.1f}%;background:#0099ff;'></div></div>"
            "</div>"
        )
    parts.append(f"<div class='sec' id='sec-party'><div class='lbl'>⚔️ The party · data up to {fmt_day(d)}</div><div class='cards'>{cards}</div></div>")

    avg_specs = [("Avg Inbound / day", "avg_in", "#00ffcc"), ("Avg Outbound / day", "avg_out", "#0099ff"),
                 ("Avg Tickets Opened / day", "avg_open", "#ff4b4b"), ("Avg Tickets Closed / day", "avg_close", "#ffcc00")]
    all_avgs = {n: get_daily_averages(n, md[n]) for n in STAFF_NAMES}
    panels = ""
    for label, key, colr in avg_specs:
        vals = {n: (all_avgs[n][key] or 0) for n in STAFF_NAMES}
        mx = max(vals.values()) if vals and max(vals.values()) > 0 else 1
        rows = "".join(
            f"<div class='ar'><span class='n'>{html.escape(n.split(' ')[0])}</span>"
            f"<div class='bar'><div style='width:{v / mx * 100:.1f}%;background:{colr};'></div></div>"
            f"<span class='v' style='color:{colr};'>{v}</span></div>"
            for n, v in vals.items()
        )
        panels += f"<div class='panel avg'><h4 style='color:{colr};'>{label} (weighted)</h4>{rows}</div>"
    parts.append(f"<div class='sec' id='sec-avgs'><div class='lbl'>📅 Weighted daily averages · data up to {fmt_day(d)}</div><div class='avgs'>{panels}</div></div>")
    parts.append("<div class='foot'>Shinra Ops Dashboard · Avalanche HQ</div>")

    card_rows = math.ceil(len(STAFF_NAMES) / 3)
    height = 330 + (40 + 28 * len(ups) if ups else 0) + (60 + 22 * notes_text.count(chr(10)) if notes_html else 0) + card_rows * 290 + 2 * (70 + 26 * len(STAFF_NAMES)) + 140
    return "".join(parts), height


SNAP_CSS = """
#cap { width: 1180px; }
.hdr { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid rgba(0,255,204,0.35); padding-bottom: 12px; margin-bottom: 16px; }
.hdr .t { font-size: 24px; font-weight: bold; color: #00ffcc; font-family: 'Courier New', monospace; }
.hdr .s { font-size: 13px; color: #9adfd0; font-family: 'Courier New', monospace; }
.tot { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
.tot div { background: rgba(0,255,204,0.06); border: 1px solid rgba(0,255,204,0.3); border-radius: 10px; text-align: center; padding: 10px; font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 1px; }
.tot b { display: block; font-size: 26px; color: #00ffcc; font-family: 'Courier New', monospace; letter-spacing: 0; }
.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.sc { background: rgba(20,20,20,0.9); border: 1px solid rgba(0,255,204,0.5); border-radius: 12px; padding: 14px; }
.sc .top { display: flex; align-items: center; gap: 14px; margin-bottom: 10px; }
.sav { width: 64px; height: 64px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border: 2px solid #00ffcc; border-radius: 8px; background: rgba(0,0,0,0.5); }
.sav img { max-width: 56px; max-height: 56px; width: auto; height: auto; }
.sc .nm { font-size: 19px; font-weight: bold; }
table { width: 100%; border-collapse: collapse; text-align: center; font-size: 12px; }
th { background: rgba(0,255,204,0.15); color: #00ffcc; padding: 6px; border: 1px solid rgba(255,255,255,0.1); }
td { padding: 8px; border: 1px solid rgba(255,255,255,0.1); font-family: 'Courier New', monospace; font-weight: bold; font-size: 16px; background: rgba(0,0,0,0.35); }
"""

def snapshot_gil(name, snap):
    daily_exp = snap["answered"] + snap["outbound"] + snap["open"] + snap["close"]
    weight = SHIFT_WEIGHTS.get(name, 1.0)
    return round((daily_exp / weight) ** 0.9) if daily_exp > 0 else 0

def fmt_pct(v):
    try:
        f = float(v)
        return f"{f:g}%"
    except (TypeError, ValueError):
        return str(v)

def build_snapshot_html():
    snaps = st.session_state.daily_snapshot_data
    stamp = st.session_state.get("snapshot_stamp", "not yet updated today")
    tot_ans = sum(snaps[n]["answered"] for n in STAFF_NAMES)
    tot_out = sum(snaps[n]["outbound"] for n in STAFF_NAMES)
    tot_open = sum(snaps[n]["open"] for n in STAFF_NAMES)
    tot_close = sum(snaps[n]["close"] for n in STAFF_NAMES)
    parts = [
        "<div class='hdr'><div class='t'>⚡ DAILY TACTICAL SNAPSHOT</div>"
        f"<div class='s'>{html.escape(stamp)}</div></div>",
        "<div class='tot'>"
        f"<div><b>{tot_ans}</b>Inbound</div><div><b>{tot_out}</b>Outbound</div>"
        f"<div><b>{tot_open}</b>SD opened</div><div><b>{tot_close}</b>SD closed</div></div>",
    ]
    cards = ""
    for name in STAFF_NAMES:
        s = snaps[name]
        cards += (
            "<div class='sc'>"
            f"<div class='top'><div class='sav'><img src='{AVATARS.get(name, '')}' crossorigin='anonymous'></div><div class='nm'>{html.escape(name)}</div></div>"
            "<table><tr><th>Inbound</th><th>Ans %</th><th>Outbound</th><th>SD Opened</th><th>SD Closed</th><th>Proj. GIL</th></tr>"
            f"<tr><td>{s['answered']}</td><td style='color:#00ffcc;'>{fmt_pct(s['pct'])}</td><td>{s['outbound']}</td>"
            f"<td style='color:#ff4b4b;'>{s['open']}</td><td style='color:#00ffcc;'>{s['close']}</td>"
            f"<td style='color:#ffcc00;'>💰 {snapshot_gil(name, s)}</td></tr></table></div>"
        )
    parts.append(f"<div class='grid'>{cards}</div>")
    height = 300 + math.ceil(len(STAFF_NAMES) / 2) * 175
    return "".join(parts), height


def style_fig(fig, height=300):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10), height=height,
        legend=dict(font=dict(color="#aaa", family="Courier New"), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(tickfont=dict(color="#00ffcc", family="Courier New"), gridcolor="rgba(0,255,204,0.06)", title=None),
        yaxis=dict(tickfont=dict(color="#aaa", family="Courier New"), gridcolor="rgba(0,255,204,0.08)", title=None),
    )
    return fig


# --- TABS ---
(tab_party, tab_brief, tab_boss, tab_missions, tab_quests, tab_snapshot, tab_overview,
 tab_charts, tab_trends, tab_spirit, tab_heat, tab_shop, tab_admin) = st.tabs([
    "⚔️ Active Party", "📣 Morning Brief", "🔥 Sephiroth Boss Battle", "📜 Team Missions", "🐉 Side Quests",
    "⚡ Daily Snapshot", "📊 Tactical Overview", "📈 Performance Charts", "📉 Trends",
    "🌟 Party Spirit", "🔥 Mako Heatmap", "💰 Wall Market", "🔐 Admin"
])

# =============================================================================
# TAB: ACTIVE PARTY VIEW
# =============================================================================
with tab_party:
    st.title("Midgar Operations: MTD Status")
    st.markdown(f"<div class='data-stamp'>{html.escape(data_stamp_text())}</div>", unsafe_allow_html=True)
    cols = st.columns(3)

    for i, name in enumerate(STAFF_NAMES):
        stats = md[name]
        res = get_stats(stats)
        with cols[i % 3]:
            with st.container(border=True):
                st.image(AVATARS.get(name))
                st.markdown(f"### <center>{name}</center>", unsafe_allow_html=True)

                st.markdown(f"""
                    <div class="mini-stat-grid">
                        <div class="mini-stat-item">IN<span class="mini-stat-value">{stats['in']}</span></div>
                        <div class="mini-stat-item">OUT<span class="mini-stat-value">{stats['out']}</span></div>
                        <div class="mini-stat-item">ANS%<span class="mini-stat-value">{stats['ans']}%</span></div>
                        <div class="mini-stat-item">OPEN<span class="mini-stat-value">{stats['open']}</span></div>
                        <div class="mini-stat-item">CLOSE<span class="mini-stat-value">{stats['close']}</span></div>
                        <div class="mini-stat-item">AWOL<span class="mini-stat-value">{stats['awol']}m</span></div>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown(f"<center><small style='color: #bbb;'>{res['Rank']}</small></center>", unsafe_allow_html=True)

                badge_html_buffer = "".join(f'<div class="profile-honor-badge">{badge}</div>' for badge in OPERATIVE_HONORS[name])
                st.markdown(f"""
                    <div class="profile-honors-flex-container">
                        {badge_html_buffer if badge_html_buffer else '<span style="color:#555; font-size:0.75rem; font-style:italic;">No Active Honors</span>'}
                    </div>
                """, unsafe_allow_html=True)

                st.write(f"❤️ Vitality (HP): {res['HP_Display']}")
                st.progress(res["HP_Pct"])
                st.write(f"💠 Next Level: {res['Next_XP']} EXP needed")
                st.progress(res["EXP_Pct"])

                mc1, mc2 = st.columns(2)
                mc1.metric("Level", res["Level"])
                mc2.metric("Wallet", f"💰 {res['GIL']}")


# =============================================================================
# TAB: MORNING BRIEF (screenshot-ready)
# =============================================================================
with tab_brief:
    st.title("📣 Morning Brief")
    st.caption("Everything for the morning post in one frame. Press **Copy image**, then paste straight into Teams.")
    with st.expander("📝 Today's news & notes (optional)", expanded=not st.session_state.get("brief_notes")):
        st.text_area(
            "Paste your notes – they appear at the top of the brief image",
            key="brief_notes", height=260,
            placeholder="Good Morning team - Here is your brief for {date}\n\n🌤️ Weather\n* Temperature: ...\n\n👥 Team Status\n* Sophie: On Annual Leave.",
        )
        st.caption("A line followed by bullets becomes a heading · bullets start with * - or • · "
                   "\"Label: detail\" bullets get a bold label · **text** is bold · {date} fills in today's date. "
                   "Notes are never saved – they clear when the page is refreshed. Press Ctrl+Enter to update the image.")
    brief_html, brief_height = build_brief_html(st.session_state.get("brief_notes", ""))
    brief_sections = ([("📰 News", "sec-news")] if "id='sec-news'" in brief_html else []) + [
        ("🎯 Missions & Boss", "sec-team"), ("⚔️ Party", "sec-party"), ("📅 Averages", "sec-avgs")]
    capture_component(brief_html, BRIEF_CSS + NOTES_CSS, brief_height,
                      f"midgar-brief-{get_data_date().isoformat()}.png",
                      sections=[(sid, lbl) for lbl, sid in brief_sections])


# =============================================================================
# TAB: SEPHIROTH BOSS BATTLE
# =============================================================================
with tab_boss:
    st.title("🔥 Destiny's Crossroads: The Final Month-End Showdown")
    st.write("Frontline operational volume is automatically channelled into physical damage outputs to bring down the legendary One-Winged Angel.")

    total_accumulated_exp = sum(get_stats(md[n])["Raw_EXP"] for n in STAFF_NAMES)
    boss = boss_state(total_accumulated_exp)
    damage_dealt = boss["damage"]
    sephiroth_current_hp = boss["hp"]
    sephiroth_hp_pct = boss["pct"]

    b_col1, b_col2 = st.columns([1.2, 1])

    with b_col1:
        st.subheader("⚔️ Frontline Party Formations")
        p_sub_cols = st.columns(3)
        for idx, name in enumerate(STAFF_NAMES):
            p_res = get_stats(md[name])
            avatar_link = AVATARS.get(name, "")
            with p_sub_cols[idx % 3]:
                border_color = hp_colour(p_res["HP_Pct"], 0.75, 0.35)
                st.markdown(f"""
                    <div style="background: rgba(15, 15, 15, 0.8); border: 2px solid {border_color}; border-radius: 10px; padding: 10px; text-align: center; margin-bottom: 15px;">
                        <img src="{avatar_link}" style="max-height: 80px; filter: drop-shadow(0 0 6px {border_color}); object-fit: contain;">
                        <div style="font-weight: bold; font-size: 0.9rem; margin-top: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: {border_color} !important;">{name.split(' ')[0]}</div>
                        <div style="font-size: 0.75rem; color: #aaa;">LVL {p_res['Level']}</div>
                        <div style="font-family: 'Courier New', monospace; font-size: 0.8rem; font-weight: bold; color: {border_color}; margin-top: 3px;">HP {p_res['HP_Display']}</div>
                    </div>
                """, unsafe_allow_html=True)

    with b_col2:
        st.subheader("🔮 The Arch-Nemesis Target")
        st.markdown(f"""
            <div class="boss-profile-container">
                <img src="{SEPHIROTH_IMG}" style="max-height: 180px; border-radius: 10px; margin-bottom: 15px; border: 2px solid #ff4b4b; box-shadow: 0 0 12px rgba(255,75,75,0.5);">
                <h3 style="margin:0; color:#ff4b4b !important;">{boss['phase']}</h3>
                <p style="font-size: 0.85rem; color: #888; margin: 4px 0;">Threat Status: Threat Level Omega</p>
                <div style="font-family: 'Courier New', monospace; font-size: 1.3rem; font-weight: bold; color: #ff4b4b; margin: 10px 0;">
                    HP: {sephiroth_current_hp:,} / {BOSS_MAX_HP:,}
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.progress(sephiroth_hp_pct)
        st.markdown(f"<p style='text-align: center; font-style: italic; color: #ffcc00 !important;'>{boss['flavour']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #9adfd0 !important;'>{boss_projection(total_accumulated_exp, get_data_date())}</p>", unsafe_allow_html=True)

    st.divider()

    st.subheader("🖥️ Shinra Command HUD Battlefield Log")
    with st.container(key="hud_battle"):
        h_r1, h_r2, h_r3 = st.columns([2, 1, 3])
        with h_r1: st.markdown("<span style='color: #00ffcc; font-weight: bold;'>PARTY MEMBERS IN POSITION</span>", unsafe_allow_html=True)
        with h_r2: st.markdown("<span style='color: #00ffcc; font-weight: bold; display: block; text-align: center;'>LEVEL STATUS</span>", unsafe_allow_html=True)
        with h_r3: st.markdown("<span style='color: #00ffcc; font-weight: bold; display: block; text-align: right;'>VITALITY CAPACITY SHIELD (HP)</span>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 8px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.3);'>", unsafe_allow_html=True)

        for name in STAFF_NAMES:
            p_res = get_stats(md[name])
            if p_res["Current_HP_Raw"] == 0: hp_color_hex = "#ff4b4b"
            elif p_res["HP_Pct"] > 0.35: hp_color_hex = "#00ffcc"
            else: hp_color_hex = "#ffcc00"

            r_c1, r_c2, r_c3 = st.columns([2, 1, 3])
            with r_c1:
                st.markdown(f"<span class='party-battle-name' style='color: {hp_color_hex} !important;'>🔹 {name}</span>", unsafe_allow_html=True)
            with r_c2:
                st.markdown(f"<span style='color: #ffffff; display: block; text-align: center;'>LVL {p_res['Level']}</span>", unsafe_allow_html=True)
            with r_c3:
                st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: flex-end; gap: 15px;">
                        <div style="width: 200px; background-color: rgba(0,0,0,0.5); border: 1px solid #fff; height: 12px; border-radius: 2px; overflow: hidden;">
                            <div style="background-color: {hp_color_hex}; width: {p_res['HP_Pct']*100}%; height: 100%;"></div>
                        </div>
                        <span class='party-battle-hp-text' style='color: {hp_color_hex} !important; width: 100px; display: inline-block; text-align: right;'>{p_res['Current_HP_Raw']} / {p_res['Max_HP_Raw']} HP</span>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<hr style='margin: 8px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
        st.markdown(f"<p style='margin:0; font-size:0.95rem; color:#aaa;'>💬 <strong>TACTICAL SENSORS REPORT:</strong> Total Month-To-Date collective damage output computed at <strong>{damage_dealt:,} points</strong>. Target Sephiroth has sustained <strong>{(1.0 - sephiroth_hp_pct)*100:.1f}%</strong> volume degradation from direct frontline encounters.</p>", unsafe_allow_html=True)


# =============================================================================
# TAB: TEAM MISSIONS & BOUNTIES
# =============================================================================
with tab_missions:
    st.title("📜 Sector 7 Bounty Board")
    elapsed_days, total_days = month_progress(get_data_date())
    st.caption(f"Month progress: day {elapsed_days:g} of {total_days:g} working days (Saturdays count as half a day).")

    total_out = sum(md[n]["out"] for n in STAFF_NAMES)
    with st.container(key="hud_bounty_out"):
        st.subheader("⚔️ TEAM MISSION: Clear the Communications Jam")
        st.write(f"Objective: Reach a collective **{GOAL_OUT}** Outbound calls this month.")
        st.progress(min(1.0, total_out / GOAL_OUT))
        if total_out >= GOAL_OUT: st.success(f"✅ MISSION COMPLETE! Total: {total_out}")
        elif total_out >= (GOAL_OUT * 0.5): st.info(f"🔵 ON TRACK: {total_out} / {GOAL_OUT} calls reached.")
        else: st.warning(f"⚠️ PUSH NEEDED: Only {total_out} calls logged so far.")
        if total_out < GOAL_OUT and total_days > 0:
            pace_target = round(GOAL_OUT * elapsed_days / total_days)
            diff = total_out - pace_target
            verdict = f"{diff} ahead of pace 🚀" if diff >= 0 else f"{-diff} behind pace 🐢"
            st.caption(f"Pace check: by now we'd want about **{pace_target}** – we're at **{total_out}** ({verdict}).")

    avg_ans = sum(md[n]["ans"] for n in STAFF_NAMES) / len(STAFF_NAMES) if STAFF_NAMES else 100.0
    with st.container(key="hud_bounty_ans"):
        st.subheader("🛡️ TEAM MISSION: The Perfect Guard")
        st.write(f"Objective: Maintain a collective **{GOAL_ANS}%** Answer Rate average.")
        st.progress(avg_ans / 100.0)
        if avg_ans >= GOAL_ANS: st.success(f"✅ MISSION SECURE: Current average is {avg_ans:.1f}%")
        elif avg_ans >= 95.0: st.warning(f"⚠️ WARNING: Average has dropped to {avg_ans:.1f}%")
        else: st.error(f"❌ CRITICAL: Average is below safety threshold at {avg_ans:.1f}%")

    total_awol = sum(md[n]["awol"] for n in STAFF_NAMES)
    with st.container(key="hud_bounty_awol"):
        st.subheader("🐌 TEAM MISSION: Stay in the Fight")
        st.write(f"Objective: The entire team shares a **{int(MAX_AWOL)} minute** total AWOL pool.")
        st.progress(min(1.0, total_awol / MAX_AWOL))
        if total_awol <= MAX_AWOL: st.success(f"✅ STAMINA REMAINING: {total_awol}m used. Pool has {MAX_AWOL - total_awol:.1f}m left.")
        else: st.error(f"❌ MISSION FAILED: Total AWOL is {total_awol}m ({total_awol - MAX_AWOL:.1f}m over limit).")

    sla_pct = float(md["team_stats"]["sla_pct"])
    with st.container(key="hud_bounty_sla"):
        st.subheader("📋 TEAM MISSION: Hold the Line on SLA")
        st.write(f"Objective: Keep SD Tickets Within SLA at **{GOAL_SLA}%** or above.")
        scaled_sla_progress = min(1.0, max(0.0, (sla_pct - 80.0) / 20.0)) if sla_pct > 80.0 else 0.0
        st.progress(scaled_sla_progress)
        if sla_pct >= GOAL_SLA: st.success(f"✅ SLA HOLDING: Currently at {sla_pct:.1f}% — target met.")
        elif sla_pct >= 88.0: st.warning(f"⚠️ SLIPPING: SLA is at {sla_pct:.1f}% — push to reach {GOAL_SLA}%.")
        else: st.error(f"❌ SLA BREACH: Currently at {sla_pct:.1f}% — immediate action needed.")

# =============================================================================
# TAB: SIDE QUEST CHRONICLES BOARD
# =============================================================================
with tab_quests:
    st.title("🐉 Tavern Side Quests Bulletin")
    st.write("Track active offline operations and view historical rewards logged by the team.")

    sq_col1, sq_col2 = st.columns(2)

    with sq_col1:
        st.subheader("📌 Currently Dispatched on Side Quests")
        active_found = False
        for name in STAFF_NAMES:
            aq = md[name].get("active_quest", {})
            if aq and aq.get("title"):
                active_found = True
                st.markdown(f"""
                    <div class="quest-card" style="border-left: 5px solid #00ffcc;">
                        <span style="float:right; color:#00ffcc; font-weight:bold;">⏳ ACTIVE</span>
                        <h4 style="margin:0; color:#fff;">{html.escape(aq['title'])}</h4>
                        <p style="margin:4px 0; font-size:0.9rem; color:#aaa;">Operative: <strong>{name}</strong></p>
                        <p style="margin:4px 0; font-size:0.85rem;">Allocated Duration: <strong>{aq['minutes']} mins</strong></p>
                        <small style="color:#666;">Commenced: {html.escape(str(aq.get('timestamp', '')))}</small>
                    </div>
                """, unsafe_allow_html=True)
        if not active_found:
            st.info("All operatives are currently deployed on the frontline desk.")

    with sq_col2:
        st.subheader("✅ Completed Quest Chronicles Log")
        quest_year = get_data_date().year
        completed_quests_list = []
        for name in STAFF_NAMES:
            for q in md[name].get("side_quests", []):
                completed_quests_list.append({
                    "time_sort": parse_quest_time(q, quest_year),
                    "html": f"""
                        <div class="quest-card" style="border-left: 5px solid #ffcc00;">
                            <span style="float:right; color:#ffcc00; font-weight:bold; text-align:right;">
                                💠 +{q['simulated_exp']} EXP<br>💰 +{q['gil_reward']} GIL
                            </span>
                            <h4 style="margin:0; color:#fff;">{html.escape(q['title'])}</h4>
                            <p style="margin:4px 0; font-size:0.9rem; color:#aaa;">Completed by: <strong>{name}</strong></p>
                            <p style="margin:4px 0; font-size:0.85rem;">Time spent compensating: <strong>{q['minutes']} mins</strong></p>
                            <small style="color:#666;">Logged: {html.escape(str(q.get('timestamp', '')))}</small>
                        </div>
                    """
                })
        if completed_quests_list:
            for q_card in sorted(completed_quests_list, key=lambda x: x["time_sort"], reverse=True):
                st.markdown(q_card["html"], unsafe_allow_html=True)
        else:
            st.write("No historical side quests recorded for this tactical frame.")

# =============================================================================
# TAB: DAILY SNAPSHOT HUD
# =============================================================================
with tab_snapshot:
    st.title("⚡ Daily Tactical Snapshot Node")
    st.caption("In-day numbers only – these are not saved and reset when the page is refreshed. Press **Copy image** to paste into Teams.")
    snap_html, snap_height = build_snapshot_html()
    capture_component(snap_html, SNAP_CSS, snap_height,
                      f"midgar-snapshot-{now_uk().strftime('%Y-%m-%d-%H%M')}.png")

    with st.expander("🛠️ Open Operational Data Entry Terminal", expanded=False):
        st.write("Edit any cell, then commit once.")
        snaps = st.session_state.daily_snapshot_data
        snap_df = pd.DataFrame(
            [{
                "Operative": n,
                "Inbound": int(snaps[n]["answered"]),
                "Ans %": float(str(snaps[n]["pct"]).rstrip("%") or 100),
                "Outbound": int(snaps[n]["outbound"]),
                "SD Opened": int(snaps[n]["open"]),
                "SD Closed": int(snaps[n]["close"]),
            } for n in STAFF_NAMES]
        ).set_index("Operative")
        edited_snap = st.data_editor(
            snap_df,
            key=f"snap_editor_{st.session_state.editor_ver}",
            width="stretch",
            num_rows="fixed",
            column_config={
                "Inbound": st.column_config.NumberColumn(min_value=0, step=1, format="%d"),
                "Ans %": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, step=0.1, format="%.1f%%"),
                "Outbound": st.column_config.NumberColumn(min_value=0, step=1, format="%d"),
                "SD Opened": st.column_config.NumberColumn(min_value=0, step=1, format="%d"),
                "SD Closed": st.column_config.NumberColumn(min_value=0, step=1, format="%d"),
            },
        )
        if st.button("🚀 Mass-Commit Daily Snapshots to Runtime Memory"):
            for n, row in edited_snap.iterrows():
                st.session_state.daily_snapshot_data[n].update({
                    "answered": int(row["Inbound"] or 0),
                    "pct": float(row["Ans %"]) if pd.notna(row["Ans %"]) else 100.0,
                    "outbound": int(row["Outbound"] or 0),
                    "open": int(row["SD Opened"] or 0),
                    "close": int(row["SD Closed"] or 0),
                })
            st.session_state.snapshot_stamp = f"As of {now_uk().strftime('%a %d %b · %H:%M')}"
            st.session_state.editor_ver += 1
            st.rerun()

    st.divider()
    st.subheader("📋 Collective Daily Snapshot Overview")
    daily_rows_matrix = []
    for name in STAFF_NAMES:
        snap_item = st.session_state.daily_snapshot_data[name]
        daily_rows_matrix.append({
            "Operative": name, "Inbound": snap_item["answered"], "Answer Rate": fmt_pct(snap_item["pct"]),
            "Outbound Calls": snap_item["outbound"], "SD Opened": snap_item["open"], "SD Closed": snap_item["close"],
            "Projected Daily GIL": f"💰 {snapshot_gil(name, snap_item)}"
        })
    st.table(pd.DataFrame(daily_rows_matrix))

# =============================================================================
# TAB: TACTICAL OVERVIEW
# =============================================================================
with tab_overview:
    st.title("📊 Tactical Command Overview")
    st.markdown(f"<div class='data-stamp'>{html.escape(data_stamp_text())}</div>", unsafe_allow_html=True)
    st.subheader("📋 MTD Raw Stats")
    data_rows = []
    for name in STAFF_NAMES:
        s = md[name]
        res = get_stats(s)
        data_rows.append({
            "Operative": name, "Inbound": s["in"], "Outbound": s["out"],
            "SD Opened": s["open"], "SD Closed": s["close"], "Ans Rate": f"{s['ans']}%",
            "AWOL": f"{s['awol']}m", "Wallet": f"{res['GIL']} GIL"
        })
    st.table(pd.DataFrame(data_rows))

    st.divider()
    st.subheader("➕ MTD Team Totals")
    totals_row = {
        "Total Inbound": sum(md[n]["in"] for n in STAFF_NAMES),
        "Total Outbound": sum(md[n]["out"] for n in STAFF_NAMES),
        "Total SD Opened": sum(md[n]["open"] for n in STAFF_NAMES),
        "Total SD Closed": sum(md[n]["close"] for n in STAFF_NAMES),
    }
    st.table(pd.DataFrame([totals_row]))

    st.divider()
    ts = md["team_stats"]
    st.subheader("🌐 Team Performance Metrics")
    team_metrics_row = {
        "Overall Success %": f"{ts['success_pct']}%", "SD Tickets Within SLA %": f"{ts['sla_pct']}%",
        "Longest Wait Avg": ts["longest_wait"], "Avg Queue Time": ts["avg_queue"],
    }
    st.table(pd.DataFrame([team_metrics_row]))

    st.divider()
    st.subheader("📅 Weighted Daily Averages")
    avg_rows = []
    for name in STAFF_NAMES:
        s = md[name]
        avgs = get_daily_averages(name, s)
        days = s.get("days_worked", 0)
        shift_weight = SHIFT_WEIGHTS.get(name, 1.0)
        eff_days = round(days * shift_weight, 2)
        def fmt(val): return str(val) if val is not None else "—"
        avg_rows.append({
            "Operative": name, "Days Worked": days, "Weighted Days": eff_days if days > 0 else "—",
            "Avg Inbound": fmt(avgs["avg_in"]), "Avg Outbound": fmt(avgs["avg_out"]),
            "Avg SD Opened": fmt(avgs["avg_open"]), "Avg SD Closed": fmt(avgs["avg_close"]),
        })
    st.table(pd.DataFrame(avg_rows))

    st.divider()
    st.subheader("🏆 Sector 7 Honors (Top Performers)")
    h_col1, h_col2, h_col3 = st.columns(3)
    h_col4, h_col5, h_col6 = st.columns(3)
    honors_columns = [h_col1, h_col2, h_col3, h_col4, h_col5, h_col6]
    for idx, (title, key, is_high) in enumerate(HONORS_MAP):
        winners_list = calculate_winners(key, STAFF_NAMES, is_high)
        winners_str = ", ".join(winners_list) if winners_list else "Up for grabs"
        with honors_columns[idx]:
            st.markdown(f'<div class="award-card"><div style="color:#00ffcc; font-weight:bold; font-size:0.85rem; margin-bottom:5px;">{title}</div><div>{winners_str}</div></div>', unsafe_allow_html=True)

# =============================================================================
# TAB: PERFORMANCE CHARTS
# =============================================================================
with tab_charts:
    st.title("📈 Operative Performance Charts")
    st.write("Visual breakdown of MTD totals and weighted daily averages across all operatives.")

    agent_names = [n.split(" ")[0] for n in STAFF_NAMES]

    def make_bar(title, values, color, y_label):
        fig = go.Figure(go.Bar(
            x=agent_names,
            y=values,
            marker_color=color,
            text=values,
            textposition="outside",
            textfont=dict(color="#f0f0f0", family="Courier New", size=13)
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(color="#00ffcc", size=16, family="Courier New"), x=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=50, b=10),
            height=270,
            showlegend=False,
            xaxis=dict(
                tickfont=dict(color="#00ffcc", family="Courier New"),
                gridcolor="rgba(0, 255, 204, 0.06)",
                title=None
            ),
            yaxis=dict(
                tickfont=dict(color="#aaa", family="Courier New"),
                gridcolor="rgba(0, 255, 204, 0.08)",
                title=dict(text=y_label, font=dict(color="#aaa", size=11)),
                rangemode="tozero"
            )
        )
        return fig

    st.subheader("📊 Month-To-Date Totals")
    mtd_in    = [md[n]["in"]    for n in STAFF_NAMES]
    mtd_out   = [md[n]["out"]   for n in STAFF_NAMES]
    mtd_open  = [md[n]["open"]  for n in STAFF_NAMES]
    mtd_close = [md[n]["close"] for n in STAFF_NAMES]

    st.plotly_chart(make_bar("Inbound Calls — MTD", mtd_in, "#00ffcc", "Calls"), width="stretch", config={"displayModeBar": False})
    st.plotly_chart(make_bar("Outbound Calls — MTD", mtd_out, "#0099ff", "Calls"), width="stretch", config={"displayModeBar": False})
    st.plotly_chart(make_bar("Tickets Opened — MTD", mtd_open, "#ff4b4b", "Tickets"), width="stretch", config={"displayModeBar": False})
    st.plotly_chart(make_bar("Tickets Closed — MTD", mtd_close, "#ffcc00", "Tickets"), width="stretch", config={"displayModeBar": False})

    st.divider()
    st.subheader("📅 Weighted Daily Averages")

    avg_in_vals, avg_out_vals, avg_open_vals, avg_close_vals = [], [], [], []
    for name in STAFF_NAMES:
        avgs = get_daily_averages(name, md[name])
        avg_in_vals.append(avgs["avg_in"]    if avgs["avg_in"]    is not None else 0)
        avg_out_vals.append(avgs["avg_out"]  if avgs["avg_out"]   is not None else 0)
        avg_open_vals.append(avgs["avg_open"]  if avgs["avg_open"]  is not None else 0)
        avg_close_vals.append(avgs["avg_close"] if avgs["avg_close"] is not None else 0)

    st.plotly_chart(make_bar("Avg Inbound Calls — Daily (Weighted)", avg_in_vals, "#00ffcc", "Calls/day"), width="stretch", config={"displayModeBar": False})
    st.plotly_chart(make_bar("Avg Outbound Calls — Daily (Weighted)", avg_out_vals, "#0099ff", "Calls/day"), width="stretch", config={"displayModeBar": False})
    st.plotly_chart(make_bar("Avg Tickets Opened — Daily (Weighted)", avg_open_vals, "#ff4b4b", "Tickets/day"), width="stretch", config={"displayModeBar": False})
    st.plotly_chart(make_bar("Avg Tickets Closed — Daily (Weighted)", avg_close_vals, "#ffcc00", "Tickets/day"), width="stretch", config={"displayModeBar": False})


# =============================================================================
# TAB: TRENDS (built from the daily history saved with each morning update)
# =============================================================================
with tab_trends:
    st.title("📉 Month Trends")
    st.write("Built from each morning update you commit in Admin. One point per update.")
    hist = md.get("history_log", {})
    hist_dates = sorted(hist)

    if len(hist_dates) < 2:
        st.info("Trends appear after your second morning update this month – check back tomorrow! 🌱")
    else:
        rows = []
        for i in range(1, len(hist_dates)):
            prev, cur = hist[hist_dates[i - 1]], hist[hist_dates[i]]
            label = fmt_day(date.fromisoformat(hist_dates[i]))
            for n in STAFF_NAMES:
                if n not in cur:
                    continue
                c = cur[n]
                p = prev.get(n, [0] * len(HIST_FIELDS))
                d_in, d_out, d_open, d_close = (max(0, c[j] - p[j]) for j in range(4))
                rows.append({"Date": label, "sort": hist_dates[i], "Operative": n.split(" ")[0],
                             "Inbound": d_in, "Outbound": d_out, "Opened": d_open, "Closed": d_close,
                             "Total": d_in + d_out + d_open + d_close})
        tdf = pd.DataFrame(rows)

        st.subheader("📊 Team output per update")
        team_daily = tdf.groupby(["sort", "Date"], as_index=False)[["Inbound", "Outbound", "Opened", "Closed"]].sum().sort_values("sort")
        fig_td = go.Figure()
        for cat, colr in zip(["Inbound", "Outbound", "Opened", "Closed"], ["#00ffcc", "#0099ff", "#ff4b4b", "#ffcc00"]):
            fig_td.add_trace(go.Bar(name=cat, x=team_daily["Date"], y=team_daily[cat], marker_color=colr, opacity=0.88))
        fig_td.update_layout(barmode="stack")
        st.plotly_chart(style_fig(fig_td, 320), width="stretch", config={"displayModeBar": False})
        st.caption("Gaps such as weekends roll into the next update's bar.")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🏁 EXP Race")
            fig_race = go.Figure()
            for idx, n in enumerate(STAFF_NAMES):
                xs, ys = [], []
                for dkey in hist_dates:
                    if n in hist[dkey]:
                        xs.append(fmt_day(date.fromisoformat(dkey)))
                        ys.append(hist[dkey][n][HIST_FIELDS.index("exp")])
                fig_race.add_trace(go.Scatter(x=xs, y=ys, mode="lines+markers", name=n.split(" ")[0],
                                              line=dict(color=LINE_COLORS[idx % len(LINE_COLORS)], width=3)))
            st.plotly_chart(style_fig(fig_race, 340), width="stretch", config={"displayModeBar": False})
        with c2:
            st.subheader("🛡️ Answer Rate Trend")
            fig_ans = go.Figure()
            for idx, n in enumerate(STAFF_NAMES):
                xs, ys = [], []
                for dkey in hist_dates:
                    if n in hist[dkey]:
                        xs.append(fmt_day(date.fromisoformat(dkey)))
                        ys.append(hist[dkey][n][HIST_FIELDS.index("ans")])
                fig_ans.add_trace(go.Scatter(x=xs, y=ys, mode="lines+markers", name=n.split(" ")[0],
                                             line=dict(color=LINE_COLORS[idx % len(LINE_COLORS)], width=3)))
            fig_ans.add_hline(y=GOAL_ANS, line_dash="dot", line_color="#ffcc00")
            style_fig(fig_ans, 340)
            lowest_ans = min((hist[dk][n][HIST_FIELDS.index("ans")] for dk in hist_dates for n in hist[dk]), default=90)
            fig_ans.update_yaxes(range=[min(90, lowest_ans - 1), 100.5])
            st.plotly_chart(fig_ans, width="stretch", config={"displayModeBar": False})

        st.subheader("🏆 Best Update This Month")
        best_rows = []
        for n in STAFF_NAMES:
            short = n.split(" ")[0]
            sub = tdf[tdf["Operative"] == short]
            if sub.empty or sub["Total"].max() <= 0:
                continue
            top = sub.loc[sub["Total"].idxmax()]
            best_rows.append({"Operative": n, "Best Update": top["Date"], "Calls + Tickets": int(top["Total"])})
        if best_rows:
            st.table(pd.DataFrame(best_rows))
        team_best = tdf.groupby("Date")["Total"].sum()
        if not team_best.empty and team_best.max() > 0:
            st.success(f"🌟 Team best so far: **{int(team_best.max())}** calls + tickets on **{team_best.idxmax()}**")


# =============================================================================
# TAB: PARTY SPIRIT — COLLECTIVE TEAM VIEW
# =============================================================================
with tab_spirit:
    st.title("🌟 Party Spirit — Avalanche Collective Status")
    st.write("One view. One team. How are we doing together this month?")

    ov = team_overview()
    all_res = ov["all_res"]

    total_team_exp   = ov["total_exp"]
    total_team_gil   = sum(r["GIL"] for r in all_res.values())
    avg_team_lvl     = ov["avg_lvl"]

    total_in    = sum(md[n]["in"]    for n in STAFF_NAMES)
    total_out   = ov["total_out"]
    total_open  = sum(md[n]["open"]  for n in STAFF_NAMES)
    total_close = sum(md[n]["close"] for n in STAFF_NAMES)
    total_awol  = ov["total_awol"]
    sla_val     = ov["sla"]
    missions_hit = ov["missions_hit"]
    team_title, team_flavour = ov["title"], ov["flavour"]

    avg_hp_pct = sum(r["HP_Pct"] for r in all_res.values()) / len(all_res) if all_res else 0
    party_hp_color = hp_colour(avg_hp_pct)

    mako_level = min(100, round((total_team_exp / 3000) * 100))

    # ── SECTION 1: Team identity banner ──────────────────────────────────────
    mission_chips = "".join(
        f'<span style="background:rgba(0,255,204,0.15);border:1px solid rgba(0,255,204,0.5);border-radius:20px;padding:4px 14px;font-size:0.78rem;color:#00ffcc;">✅ {lbl}</span>'
        if hit else
        f'<span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.15);border-radius:20px;padding:4px 14px;font-size:0.78rem;color:#555;">⬜ {lbl}</span>'
        for lbl, hit, _ in ov["missions"]
    )
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(0,255,204,0.08) 0%, rgba(0,100,80,0.15) 100%);
                    border: 1px solid rgba(0,255,204,0.45); border-radius: 18px;
                    padding: 28px 32px; text-align: center; margin-bottom: 28px;">
            <div style="font-size: 0.8rem; letter-spacing: 3px; color: #888; text-transform: uppercase; margin-bottom: 6px;">Current Party Designation</div>
            <div style="font-size: 2rem; font-weight: bold; color: #00ffcc; font-family: 'Courier New', monospace; text-shadow: 0 0 18px rgba(0,255,204,0.4);">
                {team_title}
            </div>
            <div style="font-size: 0.9rem; color: #bbb; margin-top: 10px; font-style: italic;">{team_flavour}</div>
            <div style="margin-top: 18px; display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">
                {mission_chips}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── SECTION 2: Big stat row ───────────────────────────────────────────────
    s1, s2, s3, s4 = st.columns(4)
    for col, big, lbl in [(s1, f"{total_team_exp:,}", "💠 Total Party EXP"), (s2, f"{total_team_gil:,}", "💰 Total Party GIL"),
                          (s3, f"{avg_team_lvl}", "⚔️ Avg Operative Level"), (s4, f"{missions_hit}/4", "🎯 Missions Achieved")]:
        with col:
            st.markdown(f"""
                <div class="spirit-card">
                    <span class="spirit-stat-big">{big}</span>
                    <span class="spirit-stat-label">{lbl}</span>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── SECTION 3: Mako Level gauge + Party HP side by side ──────────────────
    g1, g2 = st.columns(2)

    with g1:
        st.markdown("#### ⚡ Collective Mako Level")
        st.markdown(f"""
            <div style="background: rgba(0,0,0,0.4); border: 1px solid rgba(0,255,204,0.25);
                        border-radius: 12px; padding: 20px; margin-bottom: 6px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color:#aaa; font-size:0.85rem;">Combined team output fuelling the reactor</span>
                    <span style="color:#00ffcc; font-family:'Courier New'; font-weight:bold; font-size:1.1rem;">{mako_level}%</span>
                </div>
                <div style="background: rgba(0,0,0,0.5); border-radius: 6px; height: 22px; overflow: hidden; border: 1px solid rgba(0,255,204,0.2);">
                    <div style="background: linear-gradient(90deg, #005544, #00ffcc); width: {mako_level}%; height: 100%; transition: width 0.4s ease;"></div>
                </div>
                <div style="margin-top: 12px; font-size: 0.8rem; color: #666;">
                    Total Calls: {total_in + total_out:,} &nbsp;|&nbsp; Total Tickets: {total_open + total_close:,} &nbsp;|&nbsp; Total EXP: {total_team_exp:,}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with g2:
        st.markdown("#### ❤️ Party Vitality Reading")
        pill_html = ""
        for name in STAFF_NAMES:
            r = all_res[name]
            pc = hp_colour(r["HP_Pct"])
            short = name.split(" ")[0]
            pill_html += f'<span style="background:rgba(0,0,0,0.5);border:1px solid {pc};border-radius:20px;padding:3px 10px;font-size:0.72rem;color:{pc};margin:2px;display:inline-block;">{short} {round(r["HP_Pct"]*100)}%</span>'
        st.markdown(f"""
            <div style="background: rgba(0,0,0,0.4); border: 1px solid rgba(0,255,204,0.25);
                        border-radius: 12px; padding: 20px; margin-bottom: 6px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color:#aaa; font-size:0.85rem;">Average HP across all operatives</span>
                    <span style="color:{party_hp_color}; font-family:'Courier New'; font-weight:bold; font-size:1.1rem;">{round(avg_hp_pct*100)}%</span>
                </div>
                <div style="background: rgba(0,0,0,0.5); border-radius: 6px; height: 22px; overflow: hidden; border: 1px solid rgba(0,255,204,0.2);">
                    <div style="background-color: {party_hp_color}; width: {round(avg_hp_pct*100)}%; height: 100%;"></div>
                </div>
                <div style="margin-top: 12px;">{pill_html}</div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── SECTION 4: Collective volume chart (stacked bar per person) ───────────
    st.subheader("📊 Party Contribution Breakdown")
    st.write("How each operative is contributing to the team's total output this month.")

    categories = ["Inbound", "Outbound", "Opened", "Closed"]
    chart_colors = ["#00ffcc", "#0099ff", "#ff4b4b", "#ffcc00"]
    keys = ["in", "out", "open", "close"]

    fig_stack = go.Figure()
    for ki, (cat, col) in enumerate(zip(categories, chart_colors)):
        fig_stack.add_trace(go.Bar(
            name=cat,
            x=[n.split(" ")[0] for n in STAFF_NAMES],
            y=[md[n][keys[ki]] for n in STAFF_NAMES],
            marker_color=col,
            opacity=0.88
        ))
    fig_stack.update_layout(barmode="stack")
    st.plotly_chart(style_fig(fig_stack, 320), width="stretch", config={"displayModeBar": False})

    st.divider()

    # ── SECTION 5: Support signals ────────────────────────────────────────────
    st.subheader("🔍 Party Support Signals")
    st.write("Areas where the team might need a helping hand — framed for the group, not the individual.")

    signals_found = False

    for name in STAFF_NAMES:
        ans = md[name]["ans"]
        short = name.split(" ")[0]
        if ans < 95:
            signals_found = True
            st.markdown(f"""
                <div class="signal-card-crit">
                    <strong style="color:#ff4b4b;">📞 Comms Under Pressure</strong>
                    <p style="margin:6px 0 0; color:#ccc; font-size:0.88rem;">
                        {short}'s answer rate has dipped to <strong style="color:#ff4b4b;">{ans}%</strong>.
                        The team may be able to help cover volume or check in.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        elif ans < 98:
            signals_found = True
            st.markdown(f"""
                <div class="signal-card-warn">
                    <strong style="color:#ffcc00;">📞 Comms Slightly Stretched</strong>
                    <p style="margin:6px 0 0; color:#ccc; font-size:0.88rem;">
                        {short}'s answer rate is at <strong style="color:#ffcc00;">{ans}%</strong>.
                        Worth keeping an eye on as the month progresses.
                    </p>
                </div>
            """, unsafe_allow_html=True)

    for name in STAFF_NAMES:
        r = all_res[name]
        short = name.split(" ")[0]
        if r["HP_Pct"] < 0.35 and r["Max_HP_Raw"] > 0:
            signals_found = True
            st.markdown(f"""
                <div class="signal-card-crit">
                    <strong style="color:#ff4b4b;">❤️ Vitality Critical</strong>
                    <p style="margin:6px 0 0; color:#ccc; font-size:0.88rem;">
                        {short} is running low on HP ({r['HP_Display']}). AWOL time or answer rate may need attention — the party can rally around this.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        elif r["HP_Pct"] < 0.60 and r["Max_HP_Raw"] > 0:
            signals_found = True
            st.markdown(f"""
                <div class="signal-card-warn">
                    <strong style="color:#ffcc00;">❤️ Vitality Moderate</strong>
                    <p style="margin:6px 0 0; color:#ccc; font-size:0.88rem;">
                        {short} is at {round(r['HP_Pct']*100)}% HP. Not critical yet, but worth a check-in.
                    </p>
                </div>
            """, unsafe_allow_html=True)

    if total_awol > MAX_AWOL:
        signals_found = True
        st.markdown(f"""
            <div class="signal-card-crit">
                <strong style="color:#ff4b4b;">⏱️ AWOL Pool Exceeded</strong>
                <p style="margin:6px 0 0; color:#ccc; font-size:0.88rem;">
                    The team has used <strong style="color:#ff4b4b;">{total_awol} minutes</strong> of AWOL time against a {MAX_AWOL:g}-minute pool.
                    Collective focus will help bring this back on track.
                </p>
            </div>
        """, unsafe_allow_html=True)
    elif total_awol > 3:
        signals_found = True
        st.markdown(f"""
            <div class="signal-card-warn">
                <strong style="color:#ffcc00;">⏱️ AWOL Pool Thinning</strong>
                <p style="margin:6px 0 0; color:#ccc; font-size:0.88rem;">
                    {total_awol} of {MAX_AWOL:g} AWOL minutes used. Only {MAX_AWOL - total_awol:.1f} minutes remaining in the shared pool.
                </p>
            </div>
        """, unsafe_allow_html=True)

    if 0 < sla_val < 88:
        signals_found = True
        st.markdown(f"""
            <div class="signal-card-crit">
                <strong style="color:#ff4b4b;">📋 SLA Needs Urgent Attention</strong>
                <p style="margin:6px 0 0; color:#ccc; font-size:0.88rem;">
                    SLA is currently at <strong style="color:#ff4b4b;">{sla_val:.1f}%</strong> against a {GOAL_SLA}% target.
                    Ticket prioritisation across the team will make the biggest difference.
                </p>
            </div>
        """, unsafe_allow_html=True)
    elif 0 < sla_val < GOAL_SLA:
        signals_found = True
        st.markdown(f"""
            <div class="signal-card-warn">
                <strong style="color:#ffcc00;">📋 SLA Approaching Threshold</strong>
                <p style="margin:6px 0 0; color:#ccc; font-size:0.88rem;">
                    SLA is at <strong style="color:#ffcc00;">{sla_val:.1f}%</strong>. The team is close — a coordinated push on tickets will secure the mission.
                </p>
            </div>
        """, unsafe_allow_html=True)

    if not signals_found:
        st.markdown("""
            <div class="signal-card-ok">
                <strong style="color:#00ffcc;">✅ All Systems Green</strong>
                <p style="margin:6px 0 0; color:#ccc; font-size:0.88rem;">
                    No support signals detected. The party is healthy, the Mako flows strong, and the Planet is breathing easy. Keep it up, Avalanche.
                </p>
            </div>
        """, unsafe_allow_html=True)


# =============================================================================
# TAB: MAKO VOLUME HEATMAP
# =============================================================================
with tab_heat:
    st.title("🔥 Mako Reactor Traffic Flow")
    st.subheader("📈 MTD Half-Hour Traffic Volumes")
    v_stats = md["volume_stats"]
    st.table(pd.DataFrame([v_stats], columns=TIME_SLOTS))

    st.subheader("📊 Mako core Traffic Surge graph")
    df_vol = pd.DataFrame(list(v_stats.items()), columns=["Time Slot", "Call Volume"])
    fig = px.area(df_vol, x="Time Slot", y="Call Volume", color_discrete_sequence=["rgba(0, 255, 204, 0.45)"])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=15, b=10), height=280, showlegend=False,
        xaxis=dict(showgrid=True, gridcolor="rgba(0, 255, 204, 0.08)", tickfont=dict(color="#00ffcc", family="Courier New"), title=None),
        yaxis=dict(showgrid=True, gridcolor="rgba(0, 255, 204, 0.08)", tickfont=dict(color="#00ffcc", family="Courier New"), title=None)
    )
    fig.update_traces(line=dict(color="rgba(0, 255, 204, 1)", width=3), hovertemplate="<b>Time:</b> %{x}<br><b>Calls:</b> %{y}<extra></extra>")
    st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

    st.divider()
    st.subheader("📊 Global Outcome Percentages")
    o_stats = md["outcome_stats"]
    st.table(pd.DataFrame([o_stats], columns=OUTCOME_KEYS))

# =============================================================================
# TAB: WALL MARKET (SHOP)
# =============================================================================
with tab_shop:
    st.title("💰 Wall Market Item Shop")
    shop_ui_col1, shop_ui_col2 = st.columns([1, 2])

    with shop_ui_col1:
        current_buyer = st.selectbox("Who is shopping?", STAFF_NAMES)
        selected_perk = st.selectbox("Select Perk", [f"{k} ({v} GIL)" for k, v in SHOP_ITEMS.items()])
        perk_name = selected_perk.split(" (")[0]
        perk_price = SHOP_ITEMS[perk_name]
        buyer_stats = get_stats(md[current_buyer])
        st.write(f"Your Balance: **💰 {buyer_stats['GIL']} GIL**")

        if st.button("Confirm Purchase"):
            if buyer_stats["GIL"] >= perk_price:
                md[current_buyer]["spent"] += perk_price
                now_str = now_uk().strftime("%d/%m %H:%M")
                md[current_buyer]["history"].insert(0, f"{now_str}: Bought {perk_name} cost_{perk_price}")
                st.success(f"Authorized! {perk_name} acquired.")
                st.rerun()
            else: st.error("Insufficient GIL.")

    with shop_ui_col2:
        st.subheader("Item Logs")
        log_view_name = st.selectbox("View History For:", STAFF_NAMES)
        logs = md[log_view_name].get("history", [])
        if logs:
            for entry in logs:
                st.write(f"• {entry.split(' cost_')[0]}")
        else: st.write("No items purchased yet.")

# =============================================================================
# TAB: ADMIN COMMAND CENTER
# =============================================================================
@st.dialog("🌙 Start a new month?")
def new_month_dialog():
    st.write("This will **reset every operative to zero**, clear all Wall Market purchases, side quests and "
             "this month's trend history, and reset the team metrics, heatmap and outcomes.")
    st.warning("Copy this month's save string first if you want to keep a record of it.")
    confirm = st.text_input("Type NEW MONTH to confirm")
    if st.button("Reset for the new month", type="primary", disabled=confirm.strip().upper() != "NEW MONTH"):
        for n in STAFF_NAMES:
            md[n].update({"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0,
                          "days_worked": 0, "spent": 0, "history": [], "side_quests": [], "active_quest": {}})
        md["team_stats"] = {"success_pct": 0.0, "sla_pct": 0.0, "longest_wait": "00:00:00", "avg_queue": "00:00:00"}
        md["volume_stats"] = {slot: 0 for slot in TIME_SLOTS}
        md["outcome_stats"] = {key: "0.0%" for key in OUTCOME_KEYS}
        # Zero baseline dated the day before this month starts, so day 1's trends and level-ups work.
        baseline = now_uk().date().replace(day=1) - timedelta(days=1)
        md["history_log"] = {}
        record_history(baseline)
        md["meta"]["data_date"] = baseline.isoformat()
        touch_last_updated()
        st.session_state.daily_snapshot_data = {n: blank_snapshot() for n in STAFF_NAMES}
        st.session_state.editor_ver += 1
        st.session_state.flash_msg = "🌙 New month started! Everyone is back to zero. Remember to copy the save string into Secrets."
        st.rerun()


with tab_admin:
    st.header("🔐 Admin Command Center")
    admin_access = st.text_input("Enter Shinra Access Code", type="password")
    vault_password = st.secrets.get("admin_password", "shinra2026")

    if admin_access == vault_password:
        st.success("Access Granted. Systems online.")

        if st.session_state.get("flash_levelups"):
            st.balloons()
            for u in st.session_state.flash_levelups:
                msg = f"🌟 **{u['name']}** reached **Level {u['to']}**!"
                if u["new_rank"]:
                    msg += f" New title: **{u['rank']}**"
                st.success(msg)
            st.session_state.flash_levelups = []
        if st.session_state.get("flash_msg"):
            st.success(st.session_state.flash_msg)
            st.session_state.flash_msg = ""

        # --- MODULE 1: ALL OPERATIVES IN ONE GRID ---
        st.subheader("👤 Module 1: Morning Update – All Operatives")
        st.caption("Edit any cell in the grid, set the date the numbers run up to, then commit once.")
        mtd_df = pd.DataFrame(
            [{
                "Operative": n,
                "Inbound": int(md[n]["in"]),
                "Outbound": int(md[n]["out"]),
                "SD Opened": int(md[n]["open"]),
                "SD Closed": int(md[n]["close"]),
                "Answer %": int(md[n]["ans"]),
                "AWOL (mins)": md[n]["awol"],
                "Days Worked": int(md[n].get("days_worked", 0)),
            } for n in STAFF_NAMES]
        ).set_index("Operative")
        edited_mtd = st.data_editor(
            mtd_df,
            key=f"mtd_editor_{st.session_state.editor_ver}",
            width="stretch",
            num_rows="fixed",
            column_config={
                "Inbound": st.column_config.NumberColumn(min_value=0, step=1, format="%d"),
                "Outbound": st.column_config.NumberColumn(min_value=0, step=1, format="%d"),
                "SD Opened": st.column_config.NumberColumn(min_value=0, step=1, format="%d"),
                "SD Closed": st.column_config.NumberColumn(min_value=0, step=1, format="%d"),
                "Answer %": st.column_config.NumberColumn(min_value=0, max_value=100, step=1, format="%d%%"),
                "AWOL (mins)": st.column_config.NumberColumn(min_value=0),
                "Days Worked": st.column_config.NumberColumn(min_value=0, step=1, format="%d"),
            },
        )
        part_timers = [f"{n} x{w}" for n, w in SHIFT_WEIGHTS.items() if w < 1.0 and n in STAFF_NAMES]
        if part_timers:
            st.caption("Shift weights applied to averages and GIL: " + ", ".join(part_timers))
        d_col, b_col = st.columns([1, 2])
        with d_col:
            data_for = st.date_input("Numbers are up to and including",
                                     value=previous_working_day(now_uk().date()), format="DD/MM/YYYY")
        with b_col:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            commit_mtd = st.button("Commit Morning Update to Lifestream", type="primary")
        if commit_mtd:
            before = {n: get_stats(md[n])["Level"] for n in STAFF_NAMES}
            for n, row in edited_mtd.iterrows():
                awol_val = row["AWOL (mins)"] if pd.notna(row["AWOL (mins)"]) else 0
                md[n].update({
                    "in": int(row["Inbound"] or 0),
                    "out": int(row["Outbound"] or 0),
                    "open": int(row["SD Opened"] or 0),
                    "close": int(row["SD Closed"] or 0),
                    "ans": int(row["Answer %"]) if pd.notna(row["Answer %"]) else 100,
                    "awol": int(awol_val) if float(awol_val).is_integer() else float(awol_val),
                    "days_worked": int(row["Days Worked"] or 0),
                })
            md["meta"]["data_date"] = data_for.isoformat()
            touch_last_updated()
            record_history(data_for)
            ups = []
            for n in STAFF_NAMES:
                r = get_stats(md[n])
                if r["Level"] > before[n]:
                    old_rank = TITLES[min(max(before[n] - 1, 0), len(TITLES) - 1)]
                    ups.append({"name": n, "to": r["Level"], "rank": r["Rank"], "new_rank": r["Rank"] != old_rank})
            st.session_state.flash_levelups = ups
            st.session_state.flash_msg = f"✅ Morning update saved for {fmt_day(data_for)}. Copy the save string at the bottom into Secrets."
            st.session_state.editor_ver += 1
            st.rerun()

        st.divider()

        # --- MODULE 0: SIDE QUEST CONSOLE ---
        st.subheader("🐉 Module 2: Tavern Dispatch Side Quest Control Board")
        sq_adm_col1, sq_adm_col2 = st.columns(2)

        with sq_adm_col1:
            st.markdown("##### **Deploy / Cancel Active Quests**")
            q_target = st.selectbox("Target Operative", STAFF_NAMES, key="q_tgt")
            q_title = st.text_input("Quest Objective Title (Free Text)", placeholder="e.g., Auditing Archive Logs / Writing SOP Guide")
            q_mins = st.number_input("Quest Duration (Minutes spent off-line)", min_value=1, value=60, step=1)
            tgt_avgs = get_daily_averages(q_target, md[q_target])
            if tgt_avgs["avg_in"] is not None:
                st.caption(f"ℹ️ Run Rate Preview for {q_target}: Extrapolating from calculated baseline metrics...")
            else:
                st.caption("⚠️ Note: Operative has 0 days logged. Payouts fallback to safety baselines.")
            adm_btn_c1, adm_btn_c2 = st.columns(2)
            with adm_btn_c1:
                if st.button("🚀 Deploy to Active Quest Board"):
                    if q_title:
                        md[q_target]["active_quest"] = {
                            "title": q_title, "minutes": int(q_mins), "inflation": 1.0,
                            "timestamp": now_uk().strftime("%d/%m %H:%M")
                        }
                        touch_last_updated()
                        st.success(f"{q_target} dispatched out to: '{q_title}'")
                        st.rerun()
                    else: st.error("Please provide a quest title description.")
            with adm_btn_c2:
                if st.button("❌ Terminate Active Quest"):
                    md[q_target]["active_quest"] = {}
                    st.toast(f"Active project for {q_target} purged.")
                    st.rerun()

        with sq_adm_col2:
            st.markdown("##### **Complete and Pay Out Quest**")
            q_complete_target = st.selectbox("Select Operative to Complete Active Quest For", STAFF_NAMES, key="q_comp_tgt")
            active_q_obj = md[q_complete_target].get("active_quest", {})
            if active_q_obj and active_q_obj.get("title"):
                st.info(f"**Quest:** {active_q_obj['title']}\n\n**Logged:** {active_q_obj['minutes']} mins (1:1 Frontline Match)")
                if st.button("🏆 Mark Completed & Inject Rewards"):
                    m_stats = md[q_complete_target]
                    avgs = get_daily_averages(q_complete_target, m_stats)
                    base_in = avgs["avg_in"] if avgs["avg_in"] is not None else 15
                    base_out = avgs["avg_out"] if avgs["avg_out"] is not None else 10
                    base_open = avgs["avg_open"] if avgs["avg_open"] is not None else 5
                    base_close = avgs["avg_close"] if avgs["avg_close"] is not None else 5
                    m_duration = active_q_obj["minutes"]
                    boost = 1.0
                    sim_in    = (base_in    / 480.0) * m_duration * boost
                    sim_out   = (base_out   / 480.0) * m_duration * boost
                    sim_open  = (base_open  / 480.0) * m_duration * boost
                    sim_close = (base_close / 480.0) * m_duration * boost
                    simulated_exp_sum = round(sim_in + sim_out + sim_open + sim_close)
                    if simulated_exp_sum < 1: simulated_exp_sum = max(1, round(m_duration * 0.4 * boost))
                    calculated_gil_bonus = round((simulated_exp_sum) ** 0.9)
                    if calculated_gil_bonus < 1: calculated_gil_bonus = max(1, round(simulated_exp_sum * 0.8))
                    stamp_now = now_uk()
                    completed_quest_payload = {
                        "title": active_q_obj["title"], "minutes": m_duration, "inflation": boost,
                        "simulated_exp": int(simulated_exp_sum), "gil_reward": int(calculated_gil_bonus),
                        "timestamp": stamp_now.strftime("%d/%m %H:%M"),
                        "ts": stamp_now.replace(tzinfo=None).isoformat(timespec="minutes"),
                    }
                    md[q_complete_target]["side_quests"].append(completed_quest_payload)
                    md[q_complete_target]["active_quest"] = {}
                    touch_last_updated()
                    st.success(f"Quest Complete! Paid out +{simulated_exp_sum} EXP and +💰 {calculated_gil_bonus} GIL to {q_complete_target}.")
                    st.rerun()
            else:
                st.write("This operative does not currently have an unresolved active side quest assignment.")

        st.divider()

        # --- MODULE 2: GLOBALS & TEAM METRICS ---
        st.subheader("🌐 Module 3: Update Team Global Metrics")
        ts = md["team_stats"]
        tm_col1, tm_col2 = st.columns(2)
        with tm_col1:
            val_success = st.number_input("Overall Success %", value=float(ts["success_pct"]), min_value=0.0, max_value=100.0, step=0.1, format="%.1f")
            val_sla     = st.number_input("SD Tickets Within SLA %", value=float(ts["sla_pct"]), min_value=0.0, max_value=100.0, step=0.1, format="%.1f")
        with tm_col2:
            val_longest_wait = st.text_input("Longest Wait Time Average (HH:MM:SS)", value=ts.get("longest_wait", "00:00:00"))
            val_avg_queue    = st.text_input("Average Queue Time (HH:MM:SS)", value=ts.get("avg_queue", "00:00:00"))
            time_pattern = re.compile(r"^\d{2}:\d{2}:\d{2}$")
            lw_valid = bool(time_pattern.match(val_longest_wait))
            aq_valid = bool(time_pattern.match(val_avg_queue))
            if not lw_valid: st.error("Longest Wait format error. Use HH:MM:SS format.")
            if not aq_valid: st.error("Avg Queue Time format error. Use HH:MM:SS format.")
        if st.button("Commit Team Metrics to Lifestream"):
            if lw_valid and aq_valid:
                md["team_stats"].update({
                    "success_pct": val_success, "sla_pct": val_sla,
                    "longest_wait": val_longest_wait, "avg_queue": val_avg_queue
                })
                touch_last_updated()
                st.rerun()
            else: st.error("Cannot preserve configuration.")

        st.divider()

        # --- MODULE 3: HEATMAP DATA ---
        st.subheader("🔥 Module 4: Update Mako Traffic Flows & Global Outcomes")
        st.markdown("##### **Part A: Half-Hour Volume Parameters Input Grid**")
        st.caption("Tab moves left to right through the times in order.")
        # Built row by row (not column by column) so the Tab key runs 08:00 → 08:30 → 09:00 …
        v_inputs = {}
        for row_start in range(0, len(TIME_SLOTS), 4):
            row_cols = st.columns(4)
            for col, slot in zip(row_cols, TIME_SLOTS[row_start:row_start + 4]):
                with col:
                    v_inputs[slot] = st.number_input(f"Vol: {slot[:5]}", value=int(md["volume_stats"].get(slot, 0)),
                                                     min_value=0, step=1, key=f"vol_{slot}_{st.session_state.editor_ver}")
        st.markdown("##### **Part B: Standalone Percentage Metrics Input Grid**")
        st.caption("One row per outcome type – Tab runs D2S → S2S → INV → NC.")

        def pct_to_float(v):
            try:
                return float(str(v).strip().rstrip("%") or 0)
            except ValueError:
                return 0.0

        o_inputs = {}
        for row_start in range(0, len(OUTCOME_KEYS), 4):
            row_cols = st.columns(4)
            for col, key in zip(row_cols, OUTCOME_KEYS[row_start:row_start + 4]):
                with col:
                    o_inputs[key] = st.number_input(f"{key} %", value=pct_to_float(md["outcome_stats"].get(key, "0.0%")),
                                                    min_value=0.0, max_value=100.0, step=0.1, format="%.1f",
                                                    key=f"outcome_{key}_{st.session_state.editor_ver}")
        if st.button("🚀 Mass-Commit Heatmap Metrics to Lifestream"):
            for slot in TIME_SLOTS: md["volume_stats"][slot] = int(v_inputs[slot])
            # Stored as "12.3%" text, same as before, so older saves and the Heatmap tab keep working
            for key in OUTCOME_KEYS: md["outcome_stats"][key] = f"{o_inputs[key]:.1f}%"
            touch_last_updated()
            st.success("All traffic flows saved!")
            st.rerun()

        st.divider()

        # --- MODULE 4: LEDGER CORRECTIONS ---
        st.subheader("🚨 Module 5: Shinra Financial Audit & Ledger Deletions Panel")
        aud_col1, aud_col2 = st.columns(2)

        with aud_col1:
            st.markdown("##### **🐉 Roll Back Completed Side Quests**")
            sq_del_user  = st.selectbox("Select Operative to Audit Quests", STAFF_NAMES, key="sq_del_usr")
            user_quests  = md[sq_del_user].get("side_quests", [])
            if user_quests:
                quest_options = [f"{idx} | {q['title']} (+{q['simulated_exp']} XP, +{q['gil_reward']} GIL)" for idx, q in enumerate(user_quests)]
                selected_quest_str = st.selectbox("Select Target Quest to Erase", quest_options)
                target_quest_idx   = int(selected_quest_str.split(" | ")[0])
                if st.button("💥 Purge Quest & Deduct Rewards", type="primary"):
                    removed_quest = md[sq_del_user]["side_quests"].pop(target_quest_idx)
                    touch_last_updated()
                    st.success(f"Successfully voided '{removed_quest['title']}'! Deducted {removed_quest['simulated_exp']} EXP and {removed_quest['gil_reward']} GIL from {sq_del_user}.")
                    st.rerun()
            else:
                st.write("This operative has no completed side quests registered in this frame ledger.")

        with aud_col2:
            st.markdown("##### **💰 Void Wall Market Purchases & Issue Refunds**")
            shop_del_user  = st.selectbox("Select Shopper to Audit Invoices", STAFF_NAMES, key="shop_del_usr")
            user_history   = md[shop_del_user].get("history", [])
            purchase_entries = [item for item in user_history if " cost_" in item]
            if purchase_entries:
                purchase_options = [f"{idx} | {item.split(' cost_')[0]} (Refund Value: {item.split(' cost_')[1]} GIL)" for idx, item in enumerate(purchase_entries)]
                selected_item_str = st.selectbox("Select Target Order to Void", purchase_options)
                target_item_idx_in_filtered = int(selected_item_str.split(" | ")[0])
                raw_string_to_remove = purchase_entries[target_item_idx_in_filtered]
                if st.button("💸 Void Purchase & Refund GIL", type="primary"):
                    extracted_cost = int(raw_string_to_remove.split(" cost_")[1])
                    md[shop_del_user]["history"].remove(raw_string_to_remove)
                    md[shop_del_user]["spent"] -= extracted_cost
                    touch_last_updated()
                    st.success(f"Order Voided! Refunded +💰 {extracted_cost} GIL back into {shop_del_user}'s wallet.")
                    st.rerun()
            else:
                st.write("This operative has no refundable Wall Market ledger interactions logged.")

        st.divider()

        # --- MODULE 6: NEW MONTH ---
        st.subheader("🌙 Module 6: New Month Reset")
        st.write("Zero everything ready for the new month (asks you to confirm first).")
        if st.button("🌙 Reset to New Month…"):
            new_month_dialog()

        st.divider()

        # --- EXPORT ---
        st.subheader("💾 Manual Data Save String")
        st.markdown(f"<div class='data-stamp' style='margin-top:0;'>{html.escape(data_stamp_text())}</div>", unsafe_allow_html=True)
        st.warning("Copy the line below and replace the existing **staff_json** line in your Streamlit Secrets (leave admin_password as it is).")
        export_string = json.dumps(md, separators=(",", ":"))
        # json.dumps of the string produces a safely escaped TOML basic string, so apostrophes,
        # quotes and emoji in quest titles can never break the Secrets file.
        toml_line = "staff_json = " + json.dumps(export_string)
        try:
            check_ok = json.loads(tomllib.loads(toml_line)["staff_json"]) == json.loads(export_string)
        except Exception:
            check_ok = False
        if check_ok:
            st.caption(f"✅ Save string checked and safe to paste ({len(toml_line) / 1024:.1f} KB).")
        else:
            st.error("⚠️ The save string failed its safety check – don't paste it; let me know what changed.")
        st.code(toml_line, language="toml")

    elif admin_access != "":
        st.error("Access Denied. Security measures initialized.")
