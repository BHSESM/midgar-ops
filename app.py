import streamlit as st
import pandas as pd
import math
import json
import os

# --- RPG CONFIGURATION ---
st.set_page_config(page_title="Shinra Ops Dashboard", layout="wide")

TITLES = [
    "Sector 7 Recruit 🧰", "Midgar Mechanic 🔧", "Shinra Support Agent 🖥️",
    "Turk-in-Training 💼", "Materia Engineer 💠", "Junon Operative ⚙️",
    "Rocket Town Specialist 🚀", "Nibelheim Technician 🔩", 
    "SOLDIER Tech 3rd Class ⚔️", "SOLDIER Tech 2nd Class ⚔️",
    "SOLDIER Tech 1st Class ⚔️", "Midgar Hero 🛡️", "Planet’s Defender 🌿",
    "Lifestream Sage 💫", "Ancient of the LAN ✨"
]

# --- DATABASE LOGIC (All-in-One) ---
DB_FILE = "staff_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {
        "Sophie (Yuffie)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0},
        "Bryan (Cloud)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0},
        "Jo (Aerith)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0},
        "Amy (Jessie)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0},
        "Alisia (Tifa)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0},
        "Victor (Vincent)": {"in": 0, "out": 0, "open": 0, "close": 0, "ans": 100, "awol": 0}
    }

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def get_stats(stats):
    exp = stats["in"] + stats["out"] + stats["open"] + stats["close"]
    level = int(math.sqrt(exp / 50))
    rank = TITLES[min(max(level - 1, 0), len(TITLES) - 1)]
    max_hp = 10 * (level**2)
    damage = round(((1 - (stats["ans"]/100)) * 800) + (stats["awol"] * 9))
    current_hp = max(0, max_hp - damage)
    gil = round(exp**0.9)
    return {"Level": level, "Rank": rank, "HP": f"{current_hp}/{max_hp}", "HP_Pct": current_hp/max_hp if max_hp > 0 else 0, "GIL": gil, "EXP": exp}

# --- APP INTERFACE ---
data = load_data()

tab1, tab2 = st.tabs(["⚔️ Active Party", "🔐 Shinra Admin"])

with tab1:
    st.title("Midgar Operations: MTD Status")
    cols = st.columns(3)
    for i, (name, stats) in enumerate(data.items()):
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

with tab2:
    st.header("Admin Command Center")
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == "shinra2026":
        st.success("Access Granted, Director.")
        target = st.selectbox("Update Technician", list(data.keys()))
        
        col_a, col_b = st.columns(2)
        with col_a:
            new_in = st.number_input("Inbound Calls", value=data[target]["in"])
            new_out = st.number_input("Outbound Calls", value=data[target]["out"])
            new_ans = st.slider("Answer Rate (%)", 0, 100, int(data[target]["ans"]))
        with col_b:
            new_open = st.number_input("Tickets Opened", value=data[target]["open"])
            new_close = st.number_input("Tickets Closed", value=data[target]["close"])
            new_awol = st.number_input("AWOL Minutes", value=data[target]["awol"])
            
        if st.button("Update Battle Stats"):
            data[target] = {"in": new_in, "out": new_out, "open": new_open, "close": new_close, "ans": new_ans, "awol": new_awol}
            save_data(data)
            st.rerun()
    elif password:
        st.error("Access Denied. Turks have been dispatched.")
