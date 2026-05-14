import streamlit as st
import pandas as pd
import math
import json
from datetime import datetime

# --- RPG CONFIGURATION ---
st.set_page_config(page_title="Shinra Ops Dashboard", layout="wide")

# --- THE "ULTIMATE WEAPON" CSS INJECTION ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)), 
                    url('https://github.com/BHSESM/midgar-ops/blob/main/images.jpg?raw=true');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }

    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        background: rgba(20, 20, 20, 0.75) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 255, 204, 0.3) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    h1, h2, h3, p, span, label, .stMarkdown {
        color: #f0f0f0 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }

    .award-card {
        background: rgba(0, 255, 204, 0.1);
        border: 1px solid rgba(0, 255, 204, 0.4);
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        margin-bottom: 10px;
    }

    .award-title {
        color: #00ffcc !important;
        font-weight: bold;
        font-size: 0.9rem;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    .status-haste { color: #00ffcc !important; text-shadow: 0 0 15px #00ffcc; font-weight: bold; }
    .status-poison { color: #ff4b4b !important; text-shadow: 0 0 15px #ff4b4b; font-weight: bold; }

    .stTabs [data-baseweb="tab-list"] { background-color: rgba(0, 0, 0, 0.6); border-radius: 15px; padding: 5px 20px; }
    .stTabs [aria-selected="true"] { color: #00ffcc !important; border-bottom: 2px solid #00ffcc !important; }

    div[data-testid="stImage"] img {
        max-height: 140px !important;
        filter: drop-shadow(0px 0px 12px rgba(0, 255, 204, 0.5));
        transition: transform 0.4s;
    }
    
    div[data-testid="stImage"] img:hover { transform: scale(1.1) rotate(2deg); }

    [data-testid="stMetricValue"] { color: #00ffcc !important; font-family: 'Courier New', Courier, monospace; }
    div[data-testid="stProgress"] > div > div > div > div { background-color: #00ffcc !important; }
    </style>
    """, unsafe_allow_html=True)

# --- MASTER DATA CONFIG ---
SHOP_ITEMS = {
    "15 mins extra lunch": 600, "15 mins leave early": 600,
    "10 mins extra lunch": 400, "10 mins leave early": 400,
    "5 mins extra lunch": 200, "5 mins leave early": 200
}

AVATARS = {
    "Sophie (Yuffie)": "https://raw.githubusercontent.com/BHSESM/midgar-ops/main/Yuffie_Kisaragi.png",
    "Bryan (Cloud)": "https://raw.githubusercontent.com/BHSESM/midgar-ops/main/Cloud_Strife.png",
    "Jo (Aerith)": "https://raw.githubusercontent.com/BHSESM/midgar-ops/main/Aerith_Gainsborough.png",
    "Amy (Jessie)": "https://raw.githubusercontent.com/BHSESM/midgar-ops/main/Jessie_from_Final_Fantasy_VII_Remake_render.webp",
    "Alisia (Tifa)": "https://raw.githubusercontent.com/BHSESM/midgar-ops/main/Tifa_Lockhart_from_FFVII_Remake_promo_render.webp",
    "Victor (Vincent)": "https://raw.githubusercontent.com/BHSESM/midgar-ops/main/Vincent_Valentine_from_FFVII_Rebirth_promo_render.webp"
}

TITLES = ["Sector 7 Recruit 🧰", "Midgar Mechanic 🔧", "Shinra Support Agent 🖥️", "Turk-in-Training 💼", "Materia Engineer 💠", "Junon Operative ⚙️", "Rocket Town Specialist 🚀", "Nibelheim Technician 🔩", "SOLDIER Tech 3rd Class ⚔️", "SOLDIER Tech 2nd Class ⚔️", "SOLDIER Tech 1st Class ⚔️", "Midgar Hero 🛡️", "Planet’s Defender 🌿", "Lifestream Sage 💫", "Ancient of the LAN ✨"]

def load_data():
    if "staff_json" in st.secrets:
        return json.loads(st.secrets["staff_json"])
    return {name: {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 1.0, "updated": "N/A", "spent": 0, "history": []} for name in AVATARS.keys()}

def get_stats(stats):
    exp = stats["in"] + stats["out"] + stats["open"] + stats["close"]
    level = int(math.sqrt(exp / 50))
    rank = TITLES[min(max(level - 1, 0), len(TITLES) - 1)]
    max_hp = 10 * (level**2) if level > 0 else 100
    damage = round(((1 - (stats["ans"]/100)) * 800) + (stats["awol"] * 9))
    current_hp = max(0, max_hp - damage)
    hp_pct = current_hp / max_hp if max_hp > 0 else 0
    weight = stats.get("weight", 1.0)
    total_earned = round((exp / weight)**0.9) if exp > 0 else 0
    current_gil = total_earned - stats.get("spent", 0)
    
    status = []
    if stats["ans"] >= 100: status.append("⚡ Haste")
    if stats["awol"] > 15: status.append("🐌 Slow")
    if hp_pct < 0.20: status.append("🤢 Poison")
    
    return {"Level": level, "Rank": rank, "HP": f"{current_hp}/{max_hp}", "HP_Pct": hp_pct, "GIL": current_gil, "EXP": exp, "Status": status}

if "master_data" not in st.session_state:
    st.session_state.master_data = load_data()

tabs = st.tabs(["⚔️ Active Party", "📊 Tactical Overview", "💰 Wall Market", "🔐 Admin"])

# --- TAB 1: PARTY VIEW ---
with tabs[0]:
    st.title("Midgar Operations: MTD Status")
    cols = st.columns(3)
    for i, (name, stats) in enumerate(st.session_state.master_data.items()):
        res = get_stats(stats)
        with cols[i % 3]:
            with st.container(border=True):
                st.image(AVATARS.get(name))
                st.markdown(f"### <center>{name}</center>", unsafe_allow_html=True)
                if res["Status"]:
                    status_str = ' '.join(res['Status'])
                    color_class = "status-poison" if "Poison" in status_str else "status-haste"
                    st.markdown(f"<center><span class='{color_class}'>{status_str}</span></center>", unsafe_allow_html=True)
                else: st.markdown("<center><br></center>", unsafe_allow_html=True)
                
                st.markdown(f"<center><small style='color: #bbb;'>{res['Rank']}</small></center>", unsafe_allow_html=True)
                st.write(f"❤️ Vitality: {res['HP']}")
                st.progress(res["HP_Pct"])
                c1, c2 = st.columns(2)
                c1.metric("Level", res["Level"])
                c2.metric("GIL", f"💰 {res['GIL']}")

# --- TAB 2: TACTICAL OVERVIEW & AWARDS ---
with tabs[1]:
    st.title("📈 Tactical Command Overview")
    data_list = []
    for name, s in st.session_state.master_data.items():
        res = get_stats(s)
        data_list.append({"Operative": name, "Inbound": s["in"], "Outbound": s["out"], "Opened": s["open"], "Closed": s["close"], "Ans Rate": s["ans"], "AWOL": s["awol"], "Wallet": f"{res['GIL']} GIL"})
    df = pd.DataFrame(data_list)
    st.table(df)

    st.divider()
    st.subheader("🏆 Sector 7 Honors (Top Performers)")
    def get_tops(metric, high_is_best=True):
        val = df[metric].max() if high_is_best else df[metric].min()
        winners = df[df[metric] == val]["Operative"].tolist()
        return ", ".join(winners)

    a1, a2, a3 = st.columns(3)
    a4, a5, a6 = st.columns(3)
    metrics = [(a1, "📞 Inbound King/Queen", "Inbound", True), (a2, "☎️ Outbound Ace", "Outbound", True), (a3, "📂 Request Opener", "Opened", True), (a4, "✅ Ticket Crusher", "Closed", True), (a5, "💯 Comms Master", "Ans Rate", True), (a6, "🛡️ Always Ready", "AWOL", False)]
    for col, label, key, high in metrics:
        with col: st.markdown(f'<div class="award-card"><div class="award-title">{label}</div><div>{get_tops(key, high)}</div></div>', unsafe_allow_html=True)

# --- TAB 3: WALL MARKET ---
with tabs[2]:
    st.title("🛍️ Wall Market Item Shop")
    col_s1, col_s2 = st.columns([1, 2])
    with col_s1:
        buyer = st.selectbox("Who is shopping?", list(st.session_state.master_data.keys()))
        item = st.selectbox("Select Perk", list(SHOP_ITEMS.keys()))
        cost = SHOP_ITEMS[item]
        current_bal = get_stats(st.session_state.master_data[buyer])["GIL"]
        st.markdown(f"### Cost: 💰 {cost} GIL")
        st.write(f"Wallet: 💰 {current_bal} GIL")
        if st.button("Confirm Purchase"):
            if current_bal >= cost:
                st.session_state.master_data[buyer]["spent"] += cost
                st.session_state.master_data[buyer].setdefault("history", []).insert(0, f"{datetime.now().strftime('%d/%m %H:%M')}: Bought {item}")
                st.success("Authorized!")
                st.rerun()
            else: st.error("Insufficient GIL!")
    with col_s2:
        h_name = st.selectbox("View History:", list(st.session_state.master_data.keys()))
        for log in st.session_state.master_data[h_name].get("history", []): st.write(log)

# --- TAB 4: ADMIN ---
with tabs[3]:
    st.header("Admin Command Center")
    if st.text_input("Password", type="password") == "shinra2026":
        target = st.selectbox("Update Target", list(st.session_state.master_data.keys()))
        ca, cb = st.columns(2)
        with ca:
            st.session_state.master_data[target]["in"] = st.number_input("Inbound", value=st.session_state.master_data[target]["in"])
            st.session_state.master_data[target]["out"] = st.number_input("Outbound", value=st.session_state.master_data[target]["out"])
            st.session_state.master_data[target]["ans"] = st.slider("Ans Rate %", 0, 100, int(st.session_state.master_data[target]["ans"]))
        with cb:
            st.session_state.master_data[target]["open"] = st.number_input("Opened", value=st.session_state.master_data[target]["open"])
            st.session_state.master_data[target]["close"] = st.number_input("Closed", value=st.session_state.master_data[target]["close"])
            st.session_state.master_data[target]["awol"] = st.number_input("AWOL Mins", value=st.session_state.master_data[target]["awol"])
        if st.button("Save Stats"):
            st.session_state.master_data[target]["updated"] = datetime.now().strftime("%d/%m %H:%M")
            st.rerun()
        st.divider()
        st.code(f'staff_json = \'{json.dumps(st.session_state.master_data)}\'')
