import streamlit as st
import pandas as pd
import math
import json
from datetime import datetime

# --- RPG CONFIGURATION ---
st.set_page_config(page_title="Shinra Ops Dashboard", layout="wide")

st.markdown("""
    <style>
    div[data-testid="stImage"] img {
        max-height: 120px !important;
        width: auto !important;
        margin-left: auto;
        margin-right: auto;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# Item Shop Prices
SHOP_ITEMS = {
    "15 mins extra lunch": 600,
    "15 mins leave early": 600,
    "10 mins extra lunch": 400,
    "10 mins leave early": 400,
    "5 mins extra lunch": 200,
    "5 mins leave early": 200
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
    # Default includes 'spent' to track total spent GIL and 'history' for a log
    base = {
        "Sophie (Yuffie)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 1.0, "updated": "N/A", "spent": 0, "history": []},
        "Bryan (Cloud)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 1.0, "updated": "N/A", "spent": 0, "history": []},
        "Jo (Aerith)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 0.8, "updated": "N/A", "spent": 0, "history": []},
        "Amy (Jessie)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 1.0, "updated": "N/A", "spent": 0, "history": []},
        "Alisia (Tifa)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 1.0, "updated": "N/A", "spent": 0, "history": []},
        "Victor (Vincent)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 0.4, "updated": "N/A", "spent": 0, "history": []}
    }
    return base

def get_stats(stats):
    exp = stats["in"] + stats["out"] + stats["open"] + stats["close"]
    level = int(math.sqrt(exp / 50))
    rank = TITLES[min(max(level - 1, 0), len(TITLES) - 1)]
    max_hp = 10 * (level**2)
    damage = round(((1 - (stats["ans"]/100)) * 800) + (stats["awol"] * 9))
    current_hp = max(0, max_hp - damage)
    weight = stats.get("weight", 1.0)
    # Total Gil earned minus total Gil spent
    total_earned = round((exp / weight)**0.9) if exp > 0 else 0
    current_gil = total_earned - stats.get("spent", 0)
    return {"Level": level, "Rank": rank, "HP": f"{current_hp}/{max_hp}", "HP_Pct": current_hp/max_hp if max_hp > 0 else 0, "GIL": current_gil, "EXP": exp}

if "master_data" not in st.session_state:
    st.session_state.master_data = load_data()

tab1, tab2, tab3 = st.tabs(["⚔️ Active Party", "💰 Wall Market", "🔐 Shinra Admin"])

# --- TAB 1: PARTY VIEW ---
with tab1:
    st.title("Midgar Operations: MTD Status")
    cols = st.columns(3)
    for i, (name, stats) in enumerate(st.session_state.master_data.items()):
        res = get_stats(stats)
        with cols[i % 3]:
            with st.container(border=True):
                st.image(AVATARS.get(name), width=100)
                st.markdown(f"<h3 style='text-align: center; margin-bottom: 0;'>{name}</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: gray; margin-top: 0;'>{res['Rank']}</p>", unsafe_allow_html=True)
                st.write(f"❤️ HP: {res['HP']}")
                st.progress(res["HP_Pct"])
                c1, c2 = st.columns(2)
                c1.metric("Level", res["Level"])
                c2.metric("GIL", f"💰 {res['GIL']}")
                st.caption(f"🕒 Update: {stats.get('updated', 'N/A')}")

# --- TAB 2: ITEM SHOP ---
with tab2:
    st.title("🛍️ Wall Market Item Shop")
    st.info("Spend your hard-earned GIL on perks. Choose wisely, recruit.")
    
    col_shop1, col_shop2 = st.columns([1, 2])
    
    with col_shop1:
        buyer = st.selectbox("Who is shopping?", list(st.session_state.master_data.keys()))
        item = st.selectbox("Select Perk", list(SHOP_ITEMS.keys()))
        cost = SHOP_ITEMS[item]
        current_bal = get_stats(st.session_state.master_data[buyer])["GIL"]
        
        st.write(f"**Cost:** 💰 {cost} GIL")
        st.write(f"**Your Balance:** 💰 {current_bal} GIL")
        
        if st.button("Confirm Purchase"):
            if current_bal >= cost:
                # Deduct GIL and record history
                st.session_state.master_data[buyer]["spent"] = st.session_state.master_data[buyer].get("spent", 0) + cost
                timestamp = datetime.now().strftime("%d/%m %H:%M")
                log_entry = f"{timestamp}: Bought {item} (-{cost} GIL)"
                if "history" not in st.session_state.master_data[buyer]:
                    st.session_state.master_data[buyer]["history"] = []
                st.session_state.master_data[buyer]["history"].insert(0, log_entry)
                
                st.success(f"Transaction Complete! {item} unlocked.")
                st.balloons()
                st.rerun()
            else:
                st.error("Not enough GIL! Get back to the sector and earn some more.")

    with col_shop2:
        st.subheader("Purchase History")
        history_name = st.selectbox("View history for:", list(st.session_state.master_data.keys()), key="history_view")
        history_list = st.session_state.master_data[history_name].get("history", [])
        if history_list:
            for entry in history_list:
                st.write(entry)
        else:
            st.write("No transactions recorded yet.")

# --- TAB 3: ADMIN ---
with tab3:
    st.header("Admin Command Center")
    pwd = st.text_input("Enter Admin Password", type="password")
    if pwd == "shinra2026":
        target = st.selectbox("Update Technician", list(st.session_state.master_data.keys()))
        col_a, col_b = st.columns(2)
        with col_a:
            new_in = st.number_input("Inbound Calls", value=st.session_state.master_data[target]["in"])
            new_out = st.number_input("Outbound Calls", value=st.session_state.master_data[target]["out"])
            new_ans = st.slider("Answer Rate (%)", 0, 100, int(st.session_state.master_data[target]["ans"]))
        with col_b:
            new_open = st.number_input("Tickets Opened", value=st.session_state.master_data[target]["open"])
            new_close = st.number_input("Tickets Closed", value=st.session_state.master_data[target]["close"])
            new_awol = st.number_input("AWOL Minutes", value=st.session_state.master_data[target]["awol"])
            
        if st.button("Update Battle Stats"):
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            st.session_state.master_data[target].update({"in": new_in, "out": new_out, "open": new_open, "close": new_close, "ans": new_ans, "awol": new_awol, "updated": now})
            st.success("Stats updated!")
            st.rerun()
            
        st.divider()
        st.subheader("Final Data Save")
        st.write("IMPORTANT: After any purchase or stat update, copy this to your Secrets!")
        st.code(f'staff_json = \'{json.dumps(st.session_state.master_data)}\'')
