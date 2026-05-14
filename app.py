import streamlit as st
import pandas as pd
import math
import json

# --- RPG CONFIGURATION ---
st.set_page_config(page_title="Shinra Ops Dashboard", layout="wide")

TITLES = [
    "Sector 7 Recruit 🰰", "Midgar Mechanic 🔧", "Shinra Support Agent 🖥️",
    "Turk-in-Training 💼", "Materia Engineer 💠", "Junon Operative ⚙️",
    "Rocket Town Specialist 🚀", "Nibelheim Technician 🔩", 
    "SOLDIER Tech 3rd Class ⚔️", "SOLDIER Tech 2nd Class ⚔️",
    "SOLDIER Tech 1st Class ⚔️", "Midgar Hero 🛡️", "Planet’s Defender 🌿",
    "Lifestream Sage 💫", "Ancient of the LAN ✨"
]

# --- THE "CONTAINED" DATABASE LOGIC ---
# This looks for a hidden secret called 'staff_json'
def load_data():
    if "staff_json" in st.secrets:
        return json.loads(st.secrets["staff_json"])
    else:
        # Default starting data if secret is empty
        return {
            "Sophie (Yuffie)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 1.0},
            "Bryan (Cloud)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 1.0},
            "Jo (Aerith)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 0.8},
            "Amy (Jessie)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 1.0},
            "Alisia (Tifa)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 1.0},
            "Victor (Vincent)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0, "weight": 0.4}
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
# We store the data in 'session_state' so it updates live while you use it
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
                st.subheader(name)
                st.caption(res["Rank"])
                st.write(f"❤️ HP: {res['HP']}")
                st.progress(res["HP_Pct"])
                c1, c2 = st.columns(2)
                c1.metric("Level", res["Level"])
                c2.metric("GIL", f"💰 {res['GIL']}")
                st.write(f"✨ Total EXP: {res['EXP']}")

with tab2:
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
            st.session_state.master_data[target].update({"in": new_in, "out": new_out, "open": new_open, "close": new_close, "ans": new_ans, "awol": new_awol})
            st.success(f"Stats updated for {target}! To save permanently, copy the 'Current Data' below into your Streamlit Secrets.")
            
        # This gives you the string to paste into your secrets to "Save"
        st.divider()
        st.subheader("Data Saver")
        st.write("To save these levels permanently, copy this entire block into your Streamlit Cloud Secrets:")
        st.code(f'staff_json = \'{json.dumps(st.session_state.master_data)}\'')
