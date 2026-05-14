import streamlit as st
import pandas as pd
import math
import json
from datetime import datetime

# --- RPG CONFIGURATION ---
st.set_page_config(page_title="Shinra Ops Dashboard", layout="wide")

# Center the images with a bit of custom CSS
st.markdown("""
    <style>
    [data-testid="stImage"] {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """, unsafe_url_segments=True)

# Corrected RAW GitHub Links for Images
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
    "Rocket Town Specialist 🚀", "Nibelheim Technician 🔩", 
    "SOLDIER Tech 3rd Class ⚔️", "SOLDIER Tech 2nd Class ⚔️",
    "SOLDIER Tech 1st Class ⚔️", "Midgar Hero 🛡️", "Planet’s Defender 🌿",
    "Lifestream Sage 💫", "Ancient of the LAN ✨"
]

def load_data():
    if "staff_json" in st.secrets:
        return json.loads(st.secrets["staff_json"])
    return {
        "Sophie (Yuffie)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 1.0, "updated": "N/A"},
        "Bryan (Cloud)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 1.0, "updated": "N/A"},
        "Jo (Aerith)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 0.8, "updated": "N/A"},
        "Amy (Jessie)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 1.0, "updated": "N/A"},
        "Alisia (Tifa)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 1.0, "updated": "N/A"},
        "Victor (Vincent)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 0.4, "updated": "N/A"}
    }

def get_stats(stats):
    exp = stats["in"] + stats["out"] + stats["open"] + stats["close"]
    level = int(math.sqrt(exp / 50))
    rank = TITLES[min(max(level - 1, 0), len(TITLES) - 1)]
    max_hp = 10 * (level**2)
    damage = round(((1 - (stats["ans"]/100)) * 800) + (stats["awol"] * 9))
    current_hp = max(0, max_hp - damage)
    weight = stats.get("weight", 1.0)
    gil = round((exp / weight)**0.9) if exp > 0 else 0
    return {"Level": level, "Rank": rank, "HP": f"{current_hp}/{max_hp}", "HP_Pct": current_hp/max_hp if max_hp > 0 else 0, "GIL": gil, "EXP": exp}

# --- APP INTERFACE ---
if "master_data" not in st.session_state:
    st.session_state.master_data = load_data()

tab1, tab2 = st.tabs(["⚔️ Active Party", "🔐 Shinra Admin"])

with tab1:
    st.title("Midgar Operations: MTD Status")
    cols = st.columns(3)
    for i, (name, stats) in enumerate(st.session_state.master_data.items()):
        res = get_stats(stats)
        with cols[i % 3]:
            with st.container(border=True):
                # Standardized smaller image display
                st.image(AVATARS.get(name), width=80)
                
                # Center the header text
                st.markdown(f"<h3 style='text-align: center;'>{name}</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: gray;'>{res['Rank']}</p>", unsafe_allow_html=True)
                
                # Health Bar
                st.write(f"❤️ HP: {res['HP']}")
                st.progress(res["HP_Pct"])
                
                # Level and GIL metrics
                c1, c2 = st.columns(2)
                c1.metric("Level", res["Level"])
                c2.metric("GIL", f"💰 {res['GIL']}")
                
                st.write(f"✨ Total EXP: {res['EXP']}")
                st.caption(f"🕒 Last Battle Update: {stats.get('updated', 'N/A')}")

with tab2:
    st.header("Admin Command Center")
    pwd = st.text_input("Enter Admin Password", type="password")
    
    if pwd == "shinra2026":
        st.success("Welcome back, Director.")
        target = st.selectbox("Update Technician", list(st.session_state.master_data.keys()))
        
        col_a, col_b = st.columns(2)
        with col_a:
            new_in = st.number_input("Inbound Calls (MTD)", value=st.session_state.master_data[target]["in"])
            new_out = st.number_input("Outbound Calls (MTD)", value=st.session_state.master_data[target]["out"])
            new_ans = st.slider("Answer Rate (%)", 0, 100, int(st.session_state.master_data[target]["ans"]))
        with col_b:
            new_open = st.number_input("Tickets Opened (MTD)", value=st.session_state.master_data[target]["open"])
            new_close = st.number_input("Tickets Closed (MTD)", value=st.session_state.master_data[target]["close"])
            new_awol = st.number_input("AWOL Minutes (MTD)", value=st.session_state.master_data[target]["awol"])
            
        if st.button("Update Battle Stats"):
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            st.session_state.master_data[target].update({
                "in": new_in, "out": new_out, "open": new_open, "close": new_close, 
                "ans": new_ans, "awol": new_awol, "updated": now
            })
            st.success(f"Stats updated for {target}!")
            st.rerun()
            
        st.divider()
        st.subheader("Data Saver")
        st.write("To save these levels permanently, copy this entire block into your Streamlit Cloud Secrets:")
        st.code(f'staff_json = \'{json.dumps(st.session_state.master_data)}\'')
