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

# --- 2. THE ULTIMATE WEAPON CSS (Design & Alignment) ---
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

    /* Table Alignment & Formatting (Fixes image_ebc855.jpg) */
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

    /* Dual Progress Bars */
    /* Bar 1: HP (Mako Green) */
    div[data-testid="stProgress"]:nth-of-type(1) > div > div > div > div {
        background-color: #00ffcc !important;
    }
    /* Bar 2: EXP (Materia Blue) */
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

# --- 4. CORE ENGINE FUNCTIONS ---
def get_stats(stats):
    # EXP & Leveling
    exp = stats["in"] + stats["out"] + stats["open"] + stats["close"]
    level = int(math.sqrt(exp / 50))
    rank = TITLES[min(max(level - 1, 0), len(TITLES) - 1)]
    
    # EXP Progress Calculation
    current_lvl_base = 50 * (level ** 2)
    next_lvl_base = 50 * ((level + 1) ** 2)
    exp_in_level = exp - current_lvl_base
    exp_needed_total = next_lvl_base - current_lvl_base
    exp_pct = min(1.0, max(0.0, exp_in_level / exp_needed_total)) if exp_needed_total > 0 else 0
    
    # HP Logic (Damage based on Ans Rate & AWOL)
    max_hp = 10 * (level ** 2) if level > 0 else 100
    damage = round(((1 - (stats["ans"] / 100)) * 800) + (stats["awol"] * 9))
    current_hp = max(0, max_hp - damage)
    hp_pct = current_hp / max_hp if max_hp > 0 else 0
    
    # GIL Wallet Logic
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

def load_data():
    if "staff_json" in st.secrets:
        return json.loads(st.secrets["staff_json"])
    # Default fallback if no secret found
    return {
        name: {
            "in": 0, "out": 0, "open": 0, "close": 0, 
            "ans": 100, "awol": 0, "weight": 1.0, 
            "spent": 0, "history": []
        } for name in AVATARS.keys()
    }

# Initialize State
if "master_data" not in st.session_state:
    st.session_state.master_data = load_data()

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
                
                # The Mini-Stat HUD Recap
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
                
                # HP & EXP Progress
                st.write(f"❤️ Vitality (HP): {res['HP_Display']}")
                st.progress(res["HP_Pct"])
                
                st.write(f"💠 Next Level: {res['Next_XP']} EXP needed")
                st.progress(res["EXP_Pct"])
                
                # Metrics
                m1, m2 = st.columns(2)
                m1.metric("Level", res["Level"])
                m2.metric("Wallet", f"💰 {res['GIL']}")

# --- TAB 2: MISSIONS & BOUNTIES ---
with tabs[1]:
    st.title("📜 Sector 7 Bounty Board")
    
    # 2.1 Team Mission: Outbound Target
    total_out = sum(s["out"] for s in st.session_state.master_data.values())
    goal_out = 500
    
    st.markdown('<div class="bounty-card">', unsafe_allow_html=True)
    st.subheader("⚔️ TEAM MISSION: Clear the Communications Jam")
    st.write(f"Objective: Reach **{goal_out}** collective Outbound calls this month.")
    prog_out = min(1.0, total_out / goal_out)
    st.progress(prog_out)
    st.write(f"Current Progress: **{total_out}** / {goal_out}")
    if prog_out >= 1.0:
        st.success("MISSION COMPLETE: The expressway is clear!")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2.2 Team Mission: Answer Rate Target
    avg_ans = sum(s["ans"] for s in st.session_state.master_data.values()) / len(st.session_state.master_data)
    goal_ans = 100
    
    st.markdown('<div class="bounty-card">', unsafe_allow_html=True)
    st.subheader("🛡️ TEAM MISSION: The Perfect Guard")
    st.write(f"Objective: Achieve a collective **{goal_ans}%** Answer Rate average.")
    prog_ans = min(1.0, avg_ans / goal_ans)
    st.progress(prog_ans)
    st.write(f"Current Team Average: **{avg_ans:.1f}%**")
    if avg_ans >= 100:
        st.success("MISSION COMPLETE: Flawless synchronization!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: TACTICAL OVERVIEW ---
with tabs[2]:
    st.title("📊 Tactical Command Overview")
    
    # Table Construction
    data_list = []
    for name, s in st.session_state.master_data.items():
        res = get_stats(s)
        data_list.append({
            "Operative": name,
            "Inbound": s["in"],
            "Outbound": s["out"],
            "Opened": s["open"],
            "Closed": s["close"],
            "Ans Rate": f"{s['ans']}%",
            "AWOL": f"{s['awol']}m",
            "Wallet": f"{res['GIL']} GIL"
        })
    
    df = pd.DataFrame(data_list)
    st.table(df)
    
    st.divider()
    
    # Top Performer Honors
    st.subheader("🏆 Sector 7 Honors (Top Performers)")
    
    def get_winners(metric, high_is_best=True):
        if high_is_best:
            target_val = max(s[metric] for s in st.session_state.master_data.values())
        else:
            target_val = min(s[metric] for s in st.session_state.master_data.values())
        
        winners = [n for n, s in st.session_state.master_data.items() if s[metric] == target_val]
        return ", ".join(winners)

    h1, h2, h3 = st.columns(3)
    h4, h5, h6 = st.columns(3)
    
    honors = [
        (h1, "📞 Inbound King/Queen", "in", True),
        (h2, "☎️ Outbound Ace", "out", True),
        (h3, "📂 Request Opener", "open", True),
        (h4, "✅ Ticket Crusher", "close", True),
        (h5, "💯 Comms Master", "ans", True),
        (h6, "🛡️ Always Ready (Least AWOL)", "awol", False)
    ]
    
    for col, title, key, best in honors:
        with col:
            st.markdown(f"""
                <div class="award-card">
                    <div style="color:#00ffcc; font-weight:bold; font-size:0.85rem; margin-bottom:5px;">{title}</div>
                    <div>{get_winners(key, best)}</div>
                </div>
            """, unsafe_allow_html=True)

# --- TAB 4: WALL MARKET (SHOP) ---
with tabs[3]:
    st.title("💰 Wall Market Item Shop")
    
    shop_col1, shop_col2 = st.columns([1, 2])
    
    with shop_col1:
        buyer = st.selectbox("Who is shopping?", list(st.session_state.master_data.keys()))
        item_choice = st.selectbox("Select Perk", [f"{k} ({v} GIL)" for k, v in SHOP_ITEMS.items()])
        
        # Extract item name and price
        item_name = item_choice.split(" (")[0]
        item_price = SHOP_ITEMS[item_name]
        
        current_bal = get_stats(st.session_state.master_data[buyer])["GIL"]
        st.write(f"Current Balance: **💰 {current_bal} GIL**")
        
        if st.button("Confirm Purchase"):
            if current_bal >= item_price:
                st.session_state.master_data[buyer]["spent"] += item_price
                timestamp = datetime.now().strftime("%d/%m %H:%M")
                st.session_state.master_data[buyer].setdefault("history", []).insert(0, f"{timestamp}: Bought {item_name}")
                st.success(f"Authorized! {item_name} added to history.")
                st.rerun()
            else:
                st.error("Insufficient GIL. Complete more missions!")
                
    with shop_col2:
        st.subheader("Purchase History")
        history_owner = st.selectbox("View Records For:", list(st.session_state.master_data.keys()))
        history_list = st.session_state.master_data[history_owner].get("history", [])
        
        if history_list:
            for entry in history_list:
                st.write(f"• {entry}")
        else:
            st.write("No transactions recorded yet.")

# --- TAB 5: ADMIN COMMAND CENTER ---
with tabs[4]:
    st.header("🔐 Admin Command Center")
    
    password = st.text_input("Enter Shinra Access Code", type="password")
    
    if password == "shinra2026":
        st.success("Access Granted, Commander.")
        
        target_op = st.selectbox("Select Operative to Update", list(st.session_state.master_data.keys()))
        current_vals = st.session_state.master_data[target_op]
        
        admin_col1, admin_col2 = st.columns(2)
        
        with admin_col1:
            new_in = st.number_input("Inbound Calls", value=current_vals["in"])
            new_out = st.number_input("Outbound Calls", value=current_vals["out"])
            new_ans = st.slider("Answer Rate %", 0, 100, int(current_vals["ans"]))
            
        with admin_col2:
            new_open = st.number_input("Tickets Opened", value=current_vals["open"])
            new_close = st.number_input("Tickets Closed", value=current_vals["close"])
            new_awol = st.number_input("AWOL Minutes", value=current_vals["awol"])
            
        if st.button("Commit Stats to Lifestream"):
            st.session_state.master_data[target_op].update({
                "in": new_in,
                "out": new_out,
                "ans": new_ans,
                "open": new_open,
                "close": new_close,
                "awol": new_awol
            })
            st.rerun()
            
        st.divider()
        
        # The Copy-Paste Secret Generator
        st.subheader("Save Data (Update Streamlit Secrets)")
        st.write("Copy the text below and paste it into your Streamlit Cloud Secrets:")
        json_output = json.dumps(st.session_state.master_data)
        st.code(f"staff_json = '{json_output}'", language="toml")
    
    elif password != "":
        st.error("Incorrect Access Code. Security Turrets engaged.")
