import streamlit as st
import pandas as pd
import math
import json
from datetime import datetime

# --- 1. RPG CONFIGURATION & PAGE SETUP ---
st.set_page_config(
    page_title="Shinra Ops Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. THE ULTIMATE WEAPON CSS ---
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
        font-size: 1rem !important;
    }
    div[data-testid="stTable"] td {
        text-align: center !important;
        padding: 12px !important;
        color: #f0f0f0 !important;
    }

    /* Mini-Stat Grid */
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
    </style>
    """, unsafe_allow_html=True)

# --- 3. MASTER DATA & RPG CONFIG ---
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
    "Planet's Defender 🌿", "Lifestream Sage 💫", "Ancient of the LAN ✨"
]

SHOP_ITEMS = {
    "15m Extra Lunch": 600,
    "15m Early Leave": 600,
    "10m Extra Lunch": 400,
    "10m Early Leave": 400,
    "5m Extra Lunch": 200,
    "5m Early Leave": 200
}

# Shift weighting factors — hardcoded as these reflect shift structure, not performance
# Full-time standard shifts = 1.0; reduced hours/evenings/weekends = lower factor
SHIFT_WEIGHTS = {
    "Sophie (Yuffie)": 1.0,
    "Bryan (Cloud)":   1.0,
    "Jo (Aerith)":     0.75,
    "Amy (Jessie)":    1.0,
    "Alisia (Tifa)":   1.0,
    "Victor (Vincent)": 0.28
}

# --- 4. CORE ENGINE FUNCTIONS ---
def get_stats(stats):
    exp = stats["in"] + stats["out"] + stats["open"] + stats["close"]
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
    
    weight = stats.get("weight", 1.0)
    total_earned = round((exp / weight) ** 0.9) if exp > 0 else 0
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
    """
    Returns weighted daily averages for the four accumulating stats.
    Formula: stat / (days_worked * shift_weight)
    Shift weight normalises for operatives on reduced hours / lower-volume shifts.
    Returns None for each stat if days_worked is 0 or not set.
    """
    days = stats.get("days_worked", 0)
    shift_weight = SHIFT_WEIGHTS.get(name, 1.0)
    effective_days = days * shift_weight

    if effective_days <= 0:
        return {"avg_in": None, "avg_out": None, "avg_open": None, "avg_close": None}

    return {
        "avg_in":    round(stats["in"]    / effective_days, 1),
        "avg_out":   round(stats["out"]   / effective_days, 1),
        "avg_open":  round(stats["open"]  / effective_days, 1),
        "avg_close": round(stats["close"] / effective_days, 1),
    }

def load_data():
    if "staff_json" in st.secrets:
        return json.loads(st.secrets["staff_json"])
    return {
        name: {
            "in": 0, "out": 0, "open": 0, "close": 0,
            "ans": 100, "awol": 0, "weight": 1.0,
            "spent": 0, "history": [], "days_worked": 0
        } for name in AVATARS.keys()
    }

# Ensure session state is initialised
if "master_data" not in st.session_state:
    st.session_state.master_data = load_data()

# Backfill days_worked for any records loaded from older secrets snapshots
for name in st.session_state.master_data:
    st.session_state.master_data[name].setdefault("days_worked", 0)

# --- 5. TABS INTERFACE ---
tabs = st.tabs(["⚔️ Active Party", "📜 Missions", "📊 Tactical Overview", "💰 Wall Market", "🔐 Admin"])

# --- TAB 1: ACTIVE PARTY VIEW ---
with tabs[0]:
    st.title("Midgar Operations: MTD Status")
    cols = st.columns(3)
    
    for i, (name, stats) in enumerate(st.session_state.master_data.items()):
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
                
                st.write(f"❤️ Vitality (HP): {res['HP_Display']}")
                st.progress(res["HP_Pct"])
                
                st.write(f"💠 Next Level: {res['Next_XP']} EXP needed")
                st.progress(res["EXP_Pct"])
                
                metric_col1, metric_col2 = st.columns(2)
                metric_col1.metric("Level", res["Level"])
                metric_col2.metric("Wallet", f"💰 {res['GIL']}")

# --- TAB 2: MISSIONS & BOUNTIES ---
with tabs[1]:
    st.title("📜 Sector 7 Bounty Board")
    
    total_out = sum(s["out"] for s in st.session_state.master_data.values())
    goal_out = 500
    
    st.markdown('<div class="bounty-card">', unsafe_allow_html=True)
    st.subheader("⚔️ TEAM MISSION: Clear the Communications Jam")
    st.write(f"Objective: Reach a collective **{goal_out}** Outbound calls this month.")
    st.progress(min(1.0, total_out / goal_out))
    if total_out >= goal_out:
        st.success(f"✅ MISSION COMPLETE! The expressway is clear. Total: {total_out}")
    elif total_out >= (goal_out * 0.5):
        st.info(f"🔵 ON TRACK: {total_out} / {goal_out} calls reached.")
    else:
        st.warning(f"⚠️ PUSH NEEDED: Only {total_out} calls logged so far.")
    st.markdown('</div>', unsafe_allow_html=True)

    avg_ans = sum(s["ans"] for s in st.session_state.master_data.values()) / len(st.session_state.master_data)
    goal_ans = 98.0
    
    st.markdown('<div class="bounty-card">', unsafe_allow_html=True)
    st.subheader("🛡️ TEAM MISSION: The Perfect Guard")
    st.write(f"Objective: Maintain a collective **{goal_ans}%** Answer Rate average.")
    st.progress(avg_ans / 100.0)
    if avg_ans >= goal_ans:
        st.success(f"✅ MISSION SECURE: Current average is {avg_ans:.1f}%")
    elif avg_ans >= 95.0:
        st.warning(f"⚠️ WARNING: Average has dropped to {avg_ans:.1f}%")
    else:
        st.error(f"❌ CRITICAL: Average is below safety threshold at {avg_ans:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

    total_awol = sum(s["awol"] for s in st.session_state.master_data.values())
    max_awol = 5.0
    
    st.markdown('<div class="bounty-card">', unsafe_allow_html=True)
    st.subheader("🐌 TEAM MISSION: Stay in the Fight")
    st.write(f"Objective: The entire team shares a **{int(max_awol)} minute** total AWOL pool.")
    st.progress(min(1.0, total_awol / max_awol))
    if total_awol <= max_awol:
        st.success(f"✅ STAMINA REMAINING: {total_awol}m used. Pool has {max_awol - total_awol:.1f}m left.")
    else:
        st.error(f"❌ MISSION FAILED: Total AWOL is {total_awol}m ({total_awol - max_awol:.1f}m over limit).")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: TACTICAL OVERVIEW ---
with tabs[2]:
    st.title("📊 Tactical Command Overview")
    
    # --- RAW STATS TABLE ---
    st.subheader("📋 MTD Raw Stats")
    data_rows = []
    for name, s in st.session_state.master_data.items():
        res = get_stats(s)
        data_rows.append({
            "Operative": name,
            "Inbound": s["in"],
            "Outbound": s["out"],
            "SD Opened": s["open"],
            "SD Closed": s["close"],
            "Ans Rate": f"{s['ans']}%",
            "AWOL": f"{s['awol']}m",
            "Wallet": f"{res['GIL']} GIL"
        })
    st.table(pd.DataFrame(data_rows))

    st.divider()

    # --- WEIGHTED DAILY AVERAGES TABLE ---
    st.subheader("📅 Weighted Daily Averages")
    st.caption(
        "Averages are calculated against weighted working days to ensure fairness "
        "across different shift patterns. Jo (×0.75) and Victor (×0.28) are adjusted "
        "to reflect lower-volume evening/weekend hours."
    )

    avg_rows = []
    for name, s in st.session_state.master_data.items():
        avgs = get_daily_averages(name, s)
        days = s.get("days_worked", 0)
        shift_weight = SHIFT_WEIGHTS.get(name, 1.0)
        effective_days = round(days * shift_weight, 2)

        def fmt(val):
            return f"{val:.1f}" if val is not None else "—"

        avg_rows.append({
            "Operative":       name,
            "Days Worked":     days,
            "Weighted Days":   effective_days if days > 0 else "—",
            "Avg Inbound":     fmt(avgs["avg_in"]),
            "Avg Outbound":    fmt(avgs["avg_out"]),
            "Avg SD Opened":   fmt(avgs["avg_open"]),
            "Avg SD Closed":   fmt(avgs["avg_close"]),
        })

    st.table(pd.DataFrame(avg_rows))

    st.divider()

    # --- TOP PERFORMER HONORS ---
    st.subheader("🏆 Sector 7 Honors (Top Performers)")
    
    def calculate_winners(metric, high_is_best=True):
        if high_is_best:
            target_value = max(s[metric] for s in st.session_state.master_data.values())
        else:
            target_value = min(s[metric] for s in st.session_state.master_data.values())
        winners = [n for n, s in st.session_state.master_data.items() if s[metric] == target_value]
        return ", ".join(winners)

    h_col1, h_col2, h_col3 = st.columns(3)
    h_col4, h_col5, h_col6 = st.columns(3)
    
    honors_list = [
        (h_col1, "📞 Inbound King/Queen", "in", True),
        (h_col2, "☎️ Outbound Ace", "out", True),
        (h_col3, "📂 Request Opener", "open", True),
        (h_col4, "✅ Ticket Crusher", "close", True),
        (h_col5, "💯 Comms Master", "ans", True),
        (h_col6, "🛡️ Always Ready", "awol", False)
    ]
    
    for col, title, key, is_high in honors_list:
        with col:
            st.markdown(f"""
                <div class="award-card">
                    <div style="color:#00ffcc; font-weight:bold; font-size:0.85rem; margin-bottom:5px;">{title}</div>
                    <div>{calculate_winners(key, is_high)}</div>
                </div>
            """, unsafe_allow_html=True)

# --- TAB 4: WALL MARKET (SHOP) ---
with tabs[3]:
    st.title("💰 Wall Market Item Shop")
    
    shop_ui_col1, shop_ui_col2 = st.columns([1, 2])
    
    with shop_ui_col1:
        current_buyer = st.selectbox("Who is shopping?", list(st.session_state.master_data.keys()))
        selected_perk = st.selectbox("Select Perk", [f"{k} ({v} GIL)" for k, v in SHOP_ITEMS.items()])
        
        perk_name = selected_perk.split(" (")[0]
        perk_price = SHOP_ITEMS[perk_name]
        
        buyer_stats = get_stats(st.session_state.master_data[current_buyer])
        st.write(f"Your Balance: **💰 {buyer_stats['GIL']} GIL**")
        
        if st.button("Confirm Purchase"):
            if buyer_stats["GIL"] >= perk_price:
                st.session_state.master_data[current_buyer]["spent"] += perk_price
                now_str = datetime.now().strftime("%d/%m %H:%M")
                st.session_state.master_data[current_buyer].setdefault("history", []).insert(0, f"{now_str}: Bought {perk_name}")
                st.success(f"Authorized! {perk_name} acquired.")
                st.rerun()
            else:
                st.error("Insufficient GIL. Return to missions.")
                
    with shop_ui_col2:
        st.subheader("Item Logs")
        log_view_name = st.selectbox("View History For:", list(st.session_state.master_data.keys()))
        logs = st.session_state.master_data[log_view_name].get("history", [])
        
        if logs:
            for entry in logs:
                st.write(f"• {entry}")
        else:
            st.write("No items purchased yet.")

# --- TAB 5: ADMIN COMMAND CENTER ---
with tabs[4]:
    st.header("🔐 Admin Command Center")
    
    admin_access = st.text_input("Enter Shinra Access Code", type="password")
    
    if admin_access == "shinra2026":
        st.success("Access Granted. Update the stats, Operative.")
        
        target_name = st.selectbox("Select Operative to Update", list(st.session_state.master_data.keys()))
        operative_vals = st.session_state.master_data[target_name]
        
        form_col1, form_col2 = st.columns(2)
        
        with form_col1:
            val_in   = st.number_input("Inbound Calls",   value=operative_vals["in"])
            val_out  = st.number_input("Outbound Calls",  value=operative_vals["out"])
            val_ans  = st.slider("Answer Rate %", 0, 100,  int(operative_vals["ans"]))
            val_days = st.number_input(
                "Days Worked (MTD)",
                value=operative_vals.get("days_worked", 0),
                min_value=0,
                step=1,
                help="Raw calendar days worked this month. Weighted adjustment for Jo and Victor is applied automatically."
            )
            
        with form_col2:
            val_open  = st.number_input("SD Tickets Opened", value=operative_vals["open"])
            val_close = st.number_input("SD Tickets Closed", value=operative_vals["close"])
            val_awol  = st.number_input("AWOL Minutes",      value=operative_vals["awol"])

        # Show a live preview of what the weighted days will be after saving
        shift_weight = SHIFT_WEIGHTS.get(target_name, 1.0)
        effective_preview = round(val_days * shift_weight, 2)
        if shift_weight < 1.0:
            st.info(
                f"ℹ️ Shift weight for **{target_name}** is ×{shift_weight}. "
                f"{int(val_days)} days worked → **{effective_preview} weighted days** used in averages."
            )
            
        if st.button("Commit Stats to Lifestream"):
            st.session_state.master_data[target_name].update({
                "in":          val_in,
                "out":         val_out,
                "ans":         val_ans,
                "open":        val_open,
                "close":       val_close,
                "awol":        val_awol,
                "days_worked": int(val_days)
            })
            st.rerun()
            
        st.divider()
        
        st.subheader("Manual Data Save")
        st.warning("⚠️ Don't forget to copy this and update your Streamlit Secrets, then redeploy — otherwise changes will be lost on next reload!")
        export_string = json.dumps(st.session_state.master_data)
        st.code(f"staff_json = '{export_string}'", language="toml")
    
    elif admin_access != "":
        st.error("Access Denied. Shinra Security is en route.")
