import streamlit as st
import pandas as pd
import math
import json
import re
from datetime import datetime
import plotly.express as px # Added for high-fidelity styled charting mechanics

# --- 1. RPG CONFIGURATION & PAGE SETUP ---
st.set_page_config(
    page_title="Shinra Ops Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. THE ULTIMATE WEAPON CSS (FULL PRODUCTION VERSION) ---
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
    h1, h2, h3, p, span, label, .stMarkdown {
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
        grid-template-columns: 1fr 1fr 1fr;
        gap: 8px;
        margin: 15px 0;
        padding: 10px;
        background: rgba(0,0,0,0.4);
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .mini-stat-item {
        font-size: 0.75rem !important;
        color: #aaa !important;
        text-align: center;
        line-height: 1.3;
    }
    .mini-stat-value {
        display: block;
        color: #00ffcc !important;
        font-weight: bold;
        font-size: 0.85rem;
    }

    /* Bounty Board Styling */
    .bounty-card {
        background: rgba(0, 255, 204, 0.05);
        border: 1px dashed rgba(0, 255, 204, 0.4);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
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
    
    /* Flex Grid Container for Profile Badges (Keeps heights uniform) */
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
    
    /* Character Images (Default MTD Tab Views) */
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
    
    /* Collapsible Dropdown Accordion Panel Override Styling */
    div[data-testid="stExpander"] {
        background-color: rgba(30, 30, 30, 0.5) !important;
        border: 1px solid rgba(0, 255, 204, 0.2) !important;
        border-radius: 10px !important;
        margin-top: 15px !important;
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

TITLES = [
    "Sector 7 Recruit 🧰", "Midgar Mechanic 🔧", "Shinra Support Agent 🖥️", 
    "Turk-in-Training 💼", "Materia Engineer 💠", "Junon Operative ⚙️", 
    "Rocket Town Specialist 🚀", "Nibelheim Technician 🔩", "SOLDIER Tech 3rd Class ⚔️", 
    "SOLDIER Tech 2nd Class ⚔️", "SOLDIER Tech 1st Class ⚔️", "Midgar Hero 🛡️", 
    "Planet’s Defender 🌿", "Lifestream Sage 💫", "Ancient of the LAN ✨"
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

# --- 4. CORE ENGINE FUNCTIONS ---
def get_stats(stats):
    # Frontline Volume EXP
    frontline_exp = stats["in"] + stats["out"] + stats["open"] + stats["close"]
    
    # Calculate Side Quest Injectors
    side_quest_exp = 0
    side_quest_gil = 0
    for quest in stats.get("side_quests", []):
        side_quest_exp += quest.get("simulated_exp", 0)
        side_quest_gil += quest.get("gil_reward", 0)
        
    # Total combined systems logic values
    exp = frontline_exp + side_quest_exp
    level = int(math.sqrt(exp / 50))
    rank = TITLES[min(max(level - 1, 0), len(TITLES) - 1)]
    
    current_lvl_base = 50 * (level ** 2)
    next_lvl_base = 50 * ((level + 1) ** 2)
    exp_in_level = exp - current_lvl_base
    exp_needed_total = next_lvl_base - current_lvl_base
    exp_pct = min(1.0, max(0.0, exp_in_level / exp_needed_total)) if exp_needed_total > 0 else 0
    
    max_hp = 10 * (level ** 2) if level > 0 else 100
    damage = round(((1 - (stats["ans"] / 100)) * 800) + (stats["awol"] * 9))
    current_hp = max(0, max_hp - damage)
    hp_pct = current_hp / max_hp if max_hp > 0 else 0
    
    # Wallet Economy Formula (Frontline base + Side Quest cash injection)
    weight = stats.get("weight", 1.0)
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
        "HP_Display": f"{current_hp}/{max_hp}"
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

def calculate_winners(metric, staff_list, high_is_best=True):
    if not staff_list: return []
    vals = {n: st.session_state.master_data[n][metric] for n in staff_list}
    target = max(vals.values()) if high_is_best else min(vals.values())
    return [n for n, v in vals.items() if v == target]

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

    base = {
        name: {
            "in": 0, "out": 0, "open": 0, "close": 0,
            "ans": 100, "awol": 0, "weight": 1.0,
            "spent": 0, "history": [], "days_worked": 0,
            "side_quests": [], "active_quest": {}
        } for name in AVATARS.keys()
    }
    base["team_stats"] = {
        "success_pct": 0.0, "sla_pct": 0.0,
        "longest_wait": "00:00:00", "avg_queue": "00:00:00"
    }
    base["volume_stats"] = {slot: 0 for slot in TIME_SLOTS}
    base["outcome_stats"] = {key: "0.0%" for key in OUTCOME_KEYS}
    return base

# --- RUNNING INIT SEQUENCING ---
if "master_data" not in st.session_state:
    st.session_state.master_data = load_data()

# Verification loop for verification of structural dictionaries
for _name in list(st.session_state.master_data.keys()):
    if _name not in ["team_stats", "volume_stats", "outcome_stats"]:
        st.session_state.master_data[_name].setdefault("days_worked", 0)
        st.session_state.master_data[_name].setdefault("side_quests", [])
        st.session_state.master_data[_name].setdefault("active_quest", {})
        st.session_state.master_data[_name].setdefault("history", [])
        st.session_state.master_data[_name].setdefault("spent", 0)

st.session_state.master_data.setdefault("volume_stats", {slot: 0 for slot in TIME_SLOTS})
st.session_state.master_data.setdefault("outcome_stats", {key: "0.0%" for key in OUTCOME_KEYS})

STAFF_NAMES = [
    k for k in st.session_state.master_data.keys() 
    if k not in ["team_stats", "volume_stats", "outcome_stats"] 
    and isinstance(st.session_state.master_data[k], dict) 
    and "in" in st.session_state.master_data[k]
]

if "daily_snapshot_data" not in st.session_state:
    st.session_state.daily_snapshot_data = {
        name: {"answered": 0, "pct": "100%", "outbound": 0, "open": 0, "close": 0}
        for name in STAFF_NAMES
    }

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
    winners = calculate_winners(key, STAFF_NAMES, is_high)
    for winner in winners:
        OPERATIVE_HONORS[winner].append(title)

# --- TABS DESCRIPTOR HUD ---
tabs = st.tabs([
    "⚔️ Active Party", "📜 Team Missions", "🐉 Side Quests", "⚡ Daily Snapshot", 
    "📊 Tactical Overview", "🔥 Mako Heatmap", "💰 Wall Market", "🔐 Admin"
])

# =============================================================================
# TAB 1: ACTIVE PARTY VIEW
# =============================================================================
with tabs[0]:
    st.title("Midgar Operations: MTD Status")
    cols = st.columns(3)
    
    for i, name in enumerate(STAFF_NAMES):
        stats = st.session_state.master_data[name]
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
                
                badge_html_buffer = ""
                for badge in OPERATIVE_HONORS[name]:
                    badge_html_buffer += f'<div class="profile-honor-badge">{badge}</div>'
                
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
# TAB 2: TEAM MISSIONS & BOUNTIES
# =============================================================================
with tabs[1]:
    st.title("📜 Sector 7 Bounty Board")
    
    # Mission 1
    total_out = sum(st.session_state.master_data[n]["out"] for n in STAFF_NAMES)
    goal_out = 500
    st.markdown('<div class="bounty-card">', unsafe_allow_html=True)
    st.subheader("⚔️ TEAM MISSION: Clear the Communications Jam")
    st.write(f"Objective: Reach a collective **{goal_out}** Outbound calls this month.")
    st.progress(min(1.0, total_out / goal_out))
    if total_out >= goal_out: st.success(f"✅ MISSION COMPLETE! Total: {total_out}")
    elif total_out >= (goal_out * 0.5): st.info(f"🔵 ON TRACK: {total_out} / {goal_out} calls reached.")
    else: st.warning(f"⚠️ PUSH NEEDED: Only {total_out} calls logged so far.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Mission 2
    avg_ans = sum(st.session_state.master_data[n]["ans"] for n in STAFF_NAMES) / len(STAFF_NAMES) if STAFF_NAMES else 100.0
    goal_ans = 98.0
    st.markdown('<div class="bounty-card">', unsafe_allow_html=True)
    st.subheader("🛡️ TEAM MISSION: The Perfect Guard")
    st.write(f"Objective: Maintain a collective **{goal_ans}%** Answer Rate average.")
    st.progress(avg_ans / 100.0)
    if avg_ans >= goal_ans: st.success(f"✅ MISSION SECURE: Current average is {avg_ans:.1f}%")
    elif avg_ans >= 95.0: st.warning(f"⚠️ WARNING: Average has dropped to {avg_ans:.1f}%")
    else: st.error(f"❌ CRITICAL: Average is below safety threshold at {avg_ans:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

    # Mission 3
    total_awol = sum(st.session_state.master_data[n]["awol"] for n in STAFF_NAMES)
    max_awol = 5.0
    st.markdown('<div class="bounty-card">', unsafe_allow_html=True)
    st.subheader("🐌 TEAM MISSION: Stay in the Fight")
    st.write(f"Objective: The entire team shares a **{int(max_awol)} minute** total AWOL pool.")
    st.progress(min(1.0, total_awol / max_awol))
    if total_awol <= max_awol: st.success(f"✅ STAMINA REMAINING: {total_awol}m used. Pool has {max_awol - total_awol:.1f}m left.")
    else: st.error(f"❌ MISSION FAILED: Total AWOL is {total_awol}m ({total_awol - max_awol:.1f}m over limit).")
    st.markdown('</div>', unsafe_allow_html=True)

    # Mission 4
    sla_pct = float(st.session_state.master_data["team_stats"]["sla_pct"])
    goal_sla = 92.5
    st.markdown('<div class="bounty-card">', unsafe_allow_html=True)
    st.subheader("📋 TEAM MISSION: Hold the Line on SLA")
    st.write(f"Objective: Keep SD Tickets Within SLA at **{goal_sla}%** or above.")
    scaled_sla_progress = min(1.0, max(0.0, (sla_pct - 80.0) / 20.0)) if sla_pct > 80.0 else 0.0
    st.progress(scaled_sla_progress)
    if sla_pct >= goal_sla: st.success(f"✅ SLA HOLDING: Currently at {sla_pct:.1f}% — target met.")
    elif sla_pct >= 88.0: st.warning(f"⚠️ SLIPPING: SLA is at {sla_pct:.1f}% — push to reach {goal_sla}%.")
    else: st.error(f"❌ SLA BREACH: Currently at {sla_pct:.1f}% — immediate action needed.")
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# TAB 3: SIDE QUEST CHRONICLES BOARD
# =============================================================================
with tabs[2]:
    st.title("🐉 Tavern Side Quests Bulletin")
    st.write("Track active offline operations and view historical rewards logged by the team.")
    
    sq_col1, sq_col2 = st.columns(2)
    
    with sq_col1:
        st.subheader("📌 Currently Dispatched on Side Quests")
        active_found = False
        for name in STAFF_NAMES:
            aq = st.session_state.master_data[name].get("active_quest", {})
            if aq and aq.get("title"):
                active_found = True
                st.markdown(f"""
                    <div class="quest-card" style="border-left: 5px solid #00ffcc;">
                        <span style="float:right; color:#00ffcc; font-weight:bold;">⏳ ACTIVE</span>
                        <h4 style="margin:0; color:#fff;">{aq['title']}</h4>
                        <p style="margin:4px 0; font-size:0.9rem; color:#aaa;">Operative: <strong>{name}</strong></p>
                        <p style="margin:4px 0; font-size:0.85rem;">Allocated Duration: <strong>{aq['minutes']} mins</strong></p>
                        <small style="color:#666;">Commenced: {aq['timestamp']}</small>
                    </div>
                """, unsafe_allow_html=True)
        if not active_found:
            st.info("All operatives are currently deployed on the frontline desk.")
            
    with sq_col2:
        st.subheader("✅ Completed Quest Chronicles Log")
        completed_quests_list = []
        for name in STAFF_NAMES:
            for q in st.session_state.master_data[name].get("side_quests", []):
                completed_quests_list.append({
                    "time_sort": q.get("timestamp", ""),
                    "html": f"""
                        <div class="quest-card" style="border-left: 5px solid #ffcc00;">
                            <span style="float:right; color:#ffcc00; font-weight:bold; text-align:right;">
                                💠 +{q['simulated_exp']} EXP<br>💰 +{q['gil_reward']} GIL
                            </span>
                            <h4 style="margin:0; color:#fff;">{q['title']}</h4>
                            <p style="margin:4px 0; font-size:0.9rem; color:#aaa;">Completed by: <strong>{name}</strong></p>
                            <p style="margin:4px 0; font-size:0.85rem;">Time spent compensating: <strong>{q['minutes']} mins</strong></p>
                            <small style="color:#666;">Logged: {q['timestamp']}</small>
                        </div>
                    """
                })
        if completed_quests_list:
            for q_card in reversed(completed_quests_list):
                st.markdown(q_card["html"], unsafe_allow_html=True)
        else:
            st.write("No historical side quests recorded for this tactical frame.")

# =============================================================================
# TAB 4: DAILY SNAPSHOT HUD OPERATIONAL HUB
# =============================================================================
with tabs[3]:
    st.title("⚡ Daily Tactical Snapshot Node")
    st.subheader("📸 Teams Live Output Panel Feed")
    
    stack_cols = st.columns(2)
    for idx, name in enumerate(STAFF_NAMES):
        active_snap = st.session_state.daily_snapshot_data[name]
        avatar_url = AVATARS.get(name, "")
        
        with stack_cols[idx % 2]:
            st.markdown(f"""
                <div style="background: rgba(20, 20, 20, 0.88); border: 1px solid rgba(0, 255, 204, 0.55); border-radius: 16px; padding: 35px; box-shadow: 0 10px 25px rgba(0,0,0,0.95); margin-bottom: 25px; min-height: 230px;">
                    <div style="display: flex; align-items: center; margin-bottom: 22px;">
                        <img src="{avatar_url}" style="width: 85px; height: 85px; border-radius: 8px; border: 2px solid #00ffcc; box-shadow: 0 0 12px rgba(0,255,204,0.5); object-fit: contain; background-color: rgba(0,0,0,0.5); margin-right: 22px;">
                        <div>
                            <h2 style="color: #ffffff; margin: 0; padding: 0; font-size: 1.75rem; font-weight: bold; text-shadow: 2px 2px 4px #000; letter-spacing: 0.5px;">{name}</h2>
                        </div>
                    </div>
                    <table style="width: 100%; border-collapse: collapse; text-align: center; color: #ffffff; font-size: 1.0rem;">
                        <thead>
                            <tr style="background: rgba(0, 255, 204, 0.18); color: #00ffcc; border-bottom: 3px solid rgba(0, 255, 204, 0.4); font-weight: bold;">
                                <th style="padding: 12px; border: 1px solid rgba(255,255,255,0.12);">Calls Ans</th>
                                <th style="padding: 12px; border: 1px solid rgba(255,255,255,0.12);">Answer Rate</th>
                                <th style="padding: 12px; border: 1px solid rgba(255,255,255,0.12);">Outbound</th>
                                <th style="padding: 12px; border: 1px solid rgba(255,255,255,0.12);">SD Opened</th>
                                <th style="padding: 12px; border: 1px solid rgba(255,255,255,0.12);">SD Closed</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="font-weight: bold; font-family: 'Courier New', monospace; background: rgba(0,0,0,0.4); font-size: 1.35rem;">
                                <td style="padding: 16px; border: 1px solid rgba(255,255,255,0.12);">{active_snap['answered']}</td>
                                <td style="padding: 16px; border: 1px solid rgba(255,255,255,0.12); color: #00ffcc;">{active_snap['pct']}</td>
                                <td style="padding: 16px; border: 1px solid rgba(255,255,255,0.12);">{active_snap['outbound']}</td>
                                <td style="padding: 16px; border: 1px solid rgba(255,255,255,0.12); color: #ff4b4b;">{active_snap['open']}</td>
                                <td style="padding: 16px; border: 1px solid rgba(255,255,255,0.12); color: #00ffcc;">{active_snap['close']}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            """, unsafe_allow_html=True)
            
    st.divider()

    with st.expander("🛠️ Open Operational Data Entry Terminal", expanded=False):
        st.write("Mass multi-row entry console system.")
        new_answered, new_pct, new_outbound, new_open, new_close = {}, {}, {}, {}, {}
        
        for name in STAFF_NAMES:
            current_vals = st.session_state.daily_snapshot_data[name]
            r_col0, r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns([1.5, 1, 1, 1, 1, 1])
            with r_col0: st.markdown(f"<div style='padding-top:25px;'><strong>👤 {name}</strong></div>", unsafe_allow_html=True)
            with r_col1: new_answered[name] = st.number_input("Calls Ans", min_value=0, value=int(current_vals["answered"]), step=1, key=f"ans_{name}")
            with r_col2: new_pct[name] = st.text_input("Answer %", value=str(current_vals["pct"]), key=f"pct_{name}")
            with r_col3: new_outbound[name] = st.number_input("Outbound", min_value=0, value=int(current_vals["outbound"]), step=1, key=f"out_{name}")
            with r_col4: new_open[name] = st.number_input("SD Opened", min_value=0, value=int(current_vals["open"]), step=1, key=f"open_{name}")
            with r_col5: new_close[name] = st.number_input("SD Closed", min_value=0, value=int(current_vals["close"]), step=1, key=f"close_{name}")
                
        if st.button("🚀 Mass-Commit Daily Snapshots to Runtime Memory"):
            for name in STAFF_NAMES:
                st.session_state.daily_snapshot_data[name].update({
                    "answered": new_answered[name], "pct": new_pct[name] if new_pct[name] else "100%",
                    "outbound": new_outbound[name], "open": new_open[name], "close": new_close[name]
                })
            st.success("All snapshots preserved!")
            st.rerun()
        
    st.divider()
    st.subheader("📋 Collective Daily Snapshot Overview")
    daily_rows_matrix = []
    for name in STAFF_NAMES:
        snap_item = st.session_state.daily_snapshot_data[name]
        daily_exp = snap_item["answered"] + snap_item["outbound"] + snap_item["open"] + snap_item["close"]
        weight = SHIFT_WEIGHTS.get(name, 1.0)
        projected_gil = round((daily_exp / weight) ** 0.9) if daily_exp > 0 else 0
        
        daily_rows_matrix.append({
            "Operative": name, "Calls Answered": snap_item["answered"], "Answer Rate": snap_item["pct"],
            "Outbound Calls": snap_item["outbound"], "SD Opened": snap_item["open"], "SD Closed": snap_item["close"],
            "Projected Daily GIL": f"💰 {projected_gil}"
        })
    st.table(pd.DataFrame(daily_rows_matrix))

# =============================================================================
# TAB 5: TACTICAL OVERVIEW
# =============================================================================
with tabs[4]:
    st.title("📊 Tactical Command Overview")
    st.subheader("📋 MTD Raw Stats")
    data_rows = []
    for name in STAFF_NAMES:
        s = st.session_state.master_data[name]
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
        "Total Inbound": sum(st.session_state.master_data[n]["in"] for n in STAFF_NAMES),
        "Total Outbound": sum(st.session_state.master_data[n]["out"] for n in STAFF_NAMES),
        "Total SD Opened": sum(st.session_state.master_data[n]["open"] for n in STAFF_NAMES),
        "Total SD Closed": sum(st.session_state.master_data[n]["close"] for n in STAFF_NAMES),
    }
    st.table(pd.DataFrame([totals_row]))

    st.divider()
    ts = st.session_state.master_data["team_stats"]
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
        s = st.session_state.master_data[name]
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
        target_col = honors_columns[idx]
        winners_list = calculate_winners(key, STAFF_NAMES, is_high)
        winners_str = ", ".join(winners_list) if winners_list else "None"
        with target_col:
            st.markdown(f'<div class="award-card"><div style="color:#00ffcc; font-weight:bold; font-size:0.85rem; margin-bottom:5px;">{title}</div><div>{winners_str}</div></div>', unsafe_allow_html=True)

# =============================================================================
# TAB 6: MAKO VOLUME HEATMAP
# =============================================================================
with tabs[5]:
    st.title("🔥 Mako Reactor Traffic Flow")
    st.subheader("📈 MTD Half-Hour Traffic Volumes")
    v_stats = st.session_state.master_data["volume_stats"]
    st.table(pd.DataFrame([v_stats], columns=TIME_SLOTS))
    
    # --- TRANSMUTED TRANSPARENT MAKO SURGE GRAPH ---
    st.subheader("📊 Live Mako Core Traffic Surge Graph")
    
    # Process dictionary directly into a chronological layout
    df_vol = pd.DataFrame(list(v_stats.items()), columns=["Time Slot", "Call Volume"])
    
    # Generate interactive area wave through Plotly Express engine
    fig = px.area(
        df_vol, 
        x="Time Slot", 
        y="Call Volume",
        color_discrete_sequence=["rgba(0, 255, 204, 0.45)"] # Neon Mako Green filling
    )
    
    # Apply intense deep-space styling & full alpha transparency overlays
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",  # Purges canvas box background completely
        plot_bgcolor="rgba(0,0,0,0)",   # Purges interior tracking graph fill
        margin=dict(l=10, r=10, t=15, b=10),
        height=280,
        showlegend=False,
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(0, 255, 204, 0.08)", # Faded cyber-grid markers
            tickfont=dict(color="#00ffcc", family="Courier New"), # Flat configuration layout for Python 3.14 compatibility
            title=None
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0, 255, 204, 0.08)",
            tickfont=dict(color="#00ffcc", family="Courier New"), # Flat configuration layout for Python 3.14 compatibility
            title=None
        )
    )
    
    # Polish line aesthetic bounds
    fig.update_traces(
        line=dict(color="rgba(0, 255, 204, 1)", width=3), # Striking solid neon perimeter
        hovertemplate="<b>Time:</b> %{x}<br><b>Calls:</b> %{y}<extra></extra>"
    )
    
    # Commit chart safely back inside container constraints
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.divider()
    st.subheader("📊 Global Outcome Percentages")
    o_stats = st.session_state.master_data["outcome_stats"]
    st.table(pd.DataFrame([o_stats], columns=OUTCOME_KEYS))

# =============================================================================
# TAB 7: WALL MARKET (SHOP)
# =============================================================================
with tabs[6]:
    st.title("💰 Wall Market Item Shop")
    shop_ui_col1, shop_ui_col2 = st.columns([1, 2])
    
    with shop_ui_col1:
        current_buyer = st.selectbox("Who is shopping?", STAFF_NAMES)
        selected_perk = st.selectbox("Select Perk", [f"{k} ({v} GIL)" for k, v in SHOP_ITEMS.items()])
        perk_name = selected_perk.split(" (")[0]
        perk_price = SHOP_ITEMS[perk_name]
        buyer_stats = get_stats(st.session_state.master_data[current_buyer])
        st.write(f"Your Balance: **💰 {buyer_stats['GIL']} GIL**")

        if st.button("Confirm Purchase"):
            if buyer_stats["GIL"] >= perk_price:
                st.session_state.master_data[current_buyer]["spent"] += perk_price
                now_str = datetime.now().strftime("%d/%m %H:%M")
                # Structure purchase log metadata clearly
                st.session_state.master_data[current_buyer]["history"].insert(0, f"{now_str}: Bought {perk_name} cost_{perk_price}")
                st.success(f"Authorized! {perk_name} acquired.")
                st.rerun()
            else: st.error("Insufficient GIL.")

    with shop_ui_col2:
        st.subheader("Item Logs")
        log_view_name = st.selectbox("View History For:", STAFF_NAMES)
        logs = st.session_state.master_data[log_view_name].get("history", [])
        if logs:
            for entry in logs:
                clean_entry = entry.split(" cost_")[0]
                st.write(f"• {clean_entry}")
        else: st.write("No items purchased yet.")

# =============================================================================
# TAB 8: ADMIN COMMAND CENTER
# =============================================================================
with tabs[7]:
    st.header("🔐 Admin Command Center")
    admin_access = st.text_input("Enter Shinra Access Code", type="password")
    vault_password = st.secrets.get("admin_password", "shinra2026")

    if admin_access == vault_password:
        st.success("Access Granted. Systems online.")

        # --- PANEL MODULE 0: SIDE QUEST CONSOLE ---
        st.subheader("🐉 Module 0: Tavern Dispatch Side Quest Control Board")
        
        sq_adm_col1, sq_adm_col2 = st.columns(2)
        
        with sq_adm_col1:
            st.markdown("##### **Deploy / Cancel Active Quests**")
            q_target = st.selectbox("Target Operative", STAFF_NAMES, key="q_tgt")
            q_title = st.text_input("Quest Objective Title (Free Text)", placeholder="e.g., Auditing Archive Logs / Writing SOP Guide")
            q_mins = st.number_input("Quest Duration (Minutes spent off-line)", min_value=1, value=60, step=1)
            
            tgt_stats = st.session_state.master_data[q_target]
            tgt_avgs = get_daily_averages(q_target, tgt_stats)
            
            if tgt_avgs["avg_in"] is not None:
                st.caption(f"ℹ️ Run Rate Preview for {q_target}: Extrapolating from calculated baseline metrics...")
            else:
                st.caption("⚠️ Note: Operative has 0 days logged. Payouts fallback to safety baselines.")
                
            adm_btn_c1, adm_btn_c2 = st.columns(2)
            with adm_btn_c1:
                if st.button("🚀 Deploy to Active Quest Board"):
                    if q_title:
                        st.session_state.master_data[q_target]["active_quest"] = {
                            "title": q_title, "minutes": int(q_mins), "inflation": 1.0,
                            "timestamp": datetime.now().strftime("%d/%m %H:%M")
                        }
                        st.success(f"{q_target} dispatched out to: '{q_title}'")
                        st.rerun()
                    else: st.error("Please provide a quest title description.")
                    
            with adm_btn_c2:
                if st.button("❌ Terminate Active Quest"):
                    st.session_state.master_data[q_target]["active_quest"] = {}
                    st.toast(f"Active project for {q_target} purged.")
                    st.rerun()

        with sq_adm_col2:
            st.markdown("##### **Complete and Pay Out Quest**")
            q_complete_target = st.selectbox("Select Operative to Complete Active Quest For", STAFF_NAMES, key="q_comp_tgt")
            active_q_obj = st.session_state.master_data[q_complete_target].get("active_quest", {})
            
            if active_q_obj and active_q_obj.get("title"):
                st.info(f"**Quest:** {active_q_obj['title']}\n\n**Logged:** {active_q_obj['minutes']} mins (1:1 Frontline Match)")
                
                if st.button("🏆 Mark Completed & Inject Rewards"):
                    m_stats = st.session_state.master_data[q_complete_target]
                    avgs = get_daily_averages(q_complete_target, m_stats)
                    
                    base_in = avgs["avg_in"] if avgs["avg_in"] is not None else 15
                    base_out = avgs["avg_out"] if avgs["avg_out"] is not None else 10
                    base_open = avgs["avg_open"] if avgs["avg_open"] is not None else 5
                    base_close = avgs["avg_close"] if avgs["avg_close"] is not None else 5
                    
                    m_duration = active_q_obj["minutes"]
                    boost = 1.0
                    
                    sim_in = (base_in / 480.0) * m_duration * boost
                    sim_out = (base_out / 480.0) * m_duration * boost
                    sim_open = (base_open / 480.0) * m_duration * boost
                    sim_close = (base_close / 480.0) * m_duration * boost
                    
                    simulated_exp_sum = round(sim_in + sim_out + sim_open + sim_close)
                    if simulated_exp_sum < 1: simulated_exp_sum = max(1, round(m_duration * 0.4 * boost))
                    
                    calculated_gil_bonus = round((simulated_exp_sum) ** 0.9)
                    if calculated_gil_bonus < 1: calculated_gil_bonus = max(1, round(simulated_exp_sum * 0.8))
                    
                    completed_quest_payload = {
                        "title": active_q_obj["title"],
                        "minutes": m_duration,
                        "inflation": boost,
                        "simulated_exp": int(simulated_exp_sum),
                        "gil_reward": int(calculated_gil_bonus),
                        "timestamp": datetime.now().strftime("%d/%m %H:%M")
                    }
                    
                    st.session_state.master_data[q_complete_target]["side_quests"].append(completed_quest_payload)
                    st.session_state.master_data[q_complete_target]["active_quest"] = {}
                    
                    st.success(f"Quest Complete! Paid out +{simulated_exp_sum} EXP and +💰 {calculated_gil_bonus} GIL to {q_complete_target}.")
                    st.rerun()
            else:
                st.write("This operative does not currently have an unresolved active side quest assignment.")
                
        st.divider()

        # --- PANEL MODULE 1: INDIVIDUAL OPERATIVES ---
        st.subheader("👤 Module 1: Update Individual Operative Metrics")
        target_name = st.selectbox("Select Operative to Update", STAFF_NAMES)
        operative_vals = st.session_state.master_data[target_name]

        form_col1, form_col2 = st.columns(2)
        with form_col1:
            val_in = st.number_input("Inbound Calls", value=operative_vals["in"])
            val_out = st.number_input("Outbound Calls", value=operative_vals["out"])
            val_ans = st.slider("Answer Rate %", 0, 100, int(operative_vals["ans"]))
            val_days = st.number_input("Days Worked (MTD)", value=operative_vals.get("days_worked", 0), min_value=0, step=1)
        with form_col2:
            val_open = st.number_input("SD Tickets Opened", value=operative_vals["open"])
            val_close = st.number_input("SD Tickets Closed", value=operative_vals["close"])
            val_awol = st.number_input("AWOL Minutes", value=operative_vals["awol"])

        shift_weight = SHIFT_WEIGHTS.get(target_name, 1.0)
        if shift_weight < 1.0:
            st.info(f"Shift weight for **{target_name}** is x{shift_weight}. {int(val_days)} days worked -> **{round(val_days * shift_weight, 2)} weighted days**.")

        if st.button("Commit Operative Stats to Lifestream"):
            st.session_state.master_data[target_name].update({
                "in": val_in, "out": val_out, "ans": val_ans,
                "open": val_open, "close": val_close, "awol": val_awol,
                "days_worked": int(val_days)
            })
            st.rerun()

        st.divider()

        # --- PANEL MODULE 2: GLOBALS & TEAM METRICS ---
        st.subheader("🌐 Module 2: Update Team Global Metrics")
        ts = st.session_state.master_data["team_stats"]
        tm_col1, tm_col2 = st.columns(2)
        with tm_col1:
            val_success = st.number_input("Overall Success %", value=float(ts["success_pct"]), min_value=0.0, max_value=100.0, step=0.1, format="%.1f")
            val_sla = st.number_input("SD Tickets Within SLA %", value=float(ts["sla_pct"]), min_value=0.0, max_value=100.0, step=0.1, format="%.1f")
        with tm_col2:
            val_longest_wait = st.text_input("Longest Wait Time Average (HH:MM:SS)", value=ts.get("longest_wait", "00:00:00"))
            val_avg_queue = st.text_input("Average Queue Time (HH:MM:SS)", value=ts.get("avg_queue", "00:00:00"))

            time_pattern = re.compile(r"^\d{2}:\d{2}:\d{2}$")
            lw_valid = bool(time_pattern.match(val_longest_wait))
            aq_valid = bool(time_pattern.match(val_avg_queue))
            if not lw_valid: st.error("Longest Wait format error. Use HH:MM:SS format.")
            if not aq_valid: st.error("Avg Queue Time format error. Use HH:MM:SS format.")

        if st.button("Commit Team Metrics to Lifestream"):
            if lw_valid and aq_valid:
                st.session_state.master_data["team_stats"].update({
                    "success_pct": val_success, "sla_pct": val_sla,
                    "longest_wait": val_longest_wait, "avg_queue": val_avg_queue
                })
                st.rerun()
            else: st.error("Cannot preserve configuration.")

        st.divider()

        # --- PANEL MODULE 3: HEATMAP DATA ENTRIES ---
        st.subheader("🔥 Module 3: Update Mako Traffic Flows & Global Outcomes")
        
        st.markdown("##### **Part A: Half-Hour Volume Parameters Input Grid**")
        v_inputs = {}
        v_cols = st.columns(4)
        for idx, slot in enumerate(TIME_SLOTS):
            col_target = v_cols[idx % 4]
            with col_target: v_inputs[slot] = st.number_input(f"Vol: {slot}", value=int(st.session_state.master_data["volume_stats"].get(slot, 0)), min_value=0, step=1)
                
        st.markdown("##### **Part B: Standalone Percentage Metrics Input Grid**")
        o_inputs = {}
        o_cols = st.columns(4)
        for idx, key in enumerate(OUTCOME_KEYS):
            col_target = o_cols[idx % 4]
            with col_target: o_inputs[key] = st.text_input(f"{key}", value=str(st.session_state.master_data["outcome_stats"].get(key, "0.0%")))
                
        if st.button("🚀 Mass-Commit Heatmap Metrics to Lifestream"):
            for slot in TIME_SLOTS: st.session_state.master_data["volume_stats"][slot] = v_inputs[slot]
            for key in OUTCOME_KEYS: st.session_state.master_data["outcome_stats"][key] = o_inputs[key]
            st.success("All traffic flows saved!")
            st.rerun()

        st.divider()

        # --- PANEL MODULE 4: LEDGER CORRECTIONS MODERATOR BLOCK ---
        st.subheader("🚨 Module 4: Shinra Financial Audit & Ledger Deletions Panel")
        aud_col1, aud_col2 = st.columns(2)
        
        with aud_col1:
            st.markdown("##### **🐉 Roll Back Completed Side Quests**")
            sq_del_user = st.selectbox("Select Operative to Audit Quests", STAFF_NAMES, key="sq_del_usr")
            user_quests = st.session_state.master_data[sq_del_user].get("side_quests", [])
            
            if user_quests:
                quest_options = []
                for idx, q_obj in enumerate(user_quests):
                    quest_options.append(f"{idx} | {q_obj['title']} (+{q_obj['simulated_exp']} XP, +{q_obj['gil_reward']} GIL)")
                
                selected_quest_str = st.selectbox("Select Target Quest to Erase", quest_options)
                target_quest_idx = int(selected_quest_str.split(" | ")[0])
                
                if st.button("💥 Purge Quest & Deduct Rewards", type="primary"):
                    removed_quest = st.session_state.master_data[sq_del_user]["side_quests"].pop(target_quest_idx)
                    st.success(f"Successfully voided '{removed_quest['title']}'! Deducted {removed_quest['simulated_exp']} EXP and {removed_quest['gil_reward']} GIL from {sq_del_user}.")
                    st.rerun()
            else:
                st.write("This operative has no completed side quests registered in this frame ledger.")
                
        with aud_col2:
            st.markdown("##### **💰 Void Wall Market Purchases & Issue Refunds**")
            shop_del_user = st.selectbox("Select Shopper to Audit Invoices", STAFF_NAMES, key="shop_del_usr")
            user_history = st.session_state.master_data[shop_del_user].get("history", [])
            
            # Filter history entries that explicitly contain cost flags
            purchase_entries = [item for item in user_history if " cost_" in item]
            
            if purchase_entries:
                purchase_options = []
                for idx, item in enumerate(purchase_entries):
                    clean_title = item.split(" cost_")[0]
                    cost_val = item.split(" cost_")[1]
                    purchase_options.append(f"{idx} | {clean_title} (Refund Value: {cost_val} GIL)")
                
                selected_item_str = st.selectbox("Select Target Order to Void", purchase_options)
                target_item_idx_in_filtered = int(selected_item_str.split(" | ")[0])
                raw_string_to_remove = purchase_entries[target_item_idx_in_filtered]
                
                if st.button("💸 Void Purchase & Refund GIL", type="primary"):
                    # Find exact cost value match
                    extracted_cost = int(raw_string_to_remove.split(" cost_")[1])
                    
                    # Remove it directly from their primary list string log array
                    st.session_state.master_data[shop_del_user]["history"].remove(raw_string_to_remove)
                    # Refund the ledger currency points wallet variables
                    st.session_state.master_data[shop_del_user]["spent"] -= extracted_cost
                    
                    st.success(f"Order Voided! Refunded +💰 {extracted_cost} GIL back into {shop_del_user}'s wallet.")
                    st.rerun()
            else:
                st.write("This operative has no refundable Wall Market ledger interactions logged.")

        st.divider()

        # --- EXPORT INTERFACE BLOCK MATRIX ---
        st.subheader("Manual Data Save String")
        st.warning("Ensure this text block code snippet is extracted and pasted into your active Streamlit Cloud Vault configuration properties framework setup.")
        export_string = json.dumps(st.session_state.master_data)
        st.code(f"staff_json = '{export_string}'", language="toml")

    elif admin_access != "":
        st.error("Access Denied. Security measures initialized.")
