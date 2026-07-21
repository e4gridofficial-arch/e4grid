import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# ==========================================
# DATA FOLDER
# ==========================================
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def load_json(filename, default):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ==========================================
# MASTER DATA
# ==========================================
if "factories" not in st.session_state:
    st.session_state.factories = load_json("factories.json", [
        {"id": 1, "name": "Saga Sports", "status": "Green", "risk": "Low", "client": "Nike"},
        {"id": 2, "name": "Forward Sports", "status": "Green", "risk": "Low", "client": "Nike"},
        {"id": 3, "name": "Phoenix Sports", "status": "Red", "risk": "High", "client": "Adidas"},
    ])

if "mnc_clients" not in st.session_state:
    st.session_state.mnc_clients = load_json("mnc_clients.json", {
        "Nike": {"password": "Nike@2026", "active": True},
        "Adidas": {"password": "Adidas@2026", "active": True}
    })

if "agencies" not in st.session_state:
    st.session_state.agencies = load_json("agencies.json", {
        "Pakistan": {"password": "Pak@1799", "helpline": "1799", "active": True},
        "USA": {"password": "FBI@911", "helpline": "911", "active": True}
    })

if "cyber_alerts" not in st.session_state:
    st.session_state.cyber_alerts = load_json("alerts.json", [])

ADMIN_PASSWORD = "esha4t4boss"

def save_all():
    save_json("factories.json", st.session_state.factories)
    save_json("mnc_clients.json", st.session_state.mnc_clients)
    save_json("agencies.json", st.session_state.agencies)
    save_json("alerts.json", st.session_state.cyber_alerts)

# ==========================================
# UI SETUP
# ==========================================
st.set_page_config(page_title="E4GRID - Global Shield", layout="wide")
st.title("⚡ E4GRID")
st.caption("Global Industrial Immune System")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "client" not in st.session_state:
    st.session_state.client = None

# ==========================================
# LOGIN
# ==========================================
def login_form():
    with st.sidebar:
        st.header("🔐 Login")
        user_type = st.selectbox("I am a...", ["Public (Free)", "MNC", "Global Agency", "Admin"])
        if user_type == "Public (Free)":
            if st.button("Enter as Public"):
                st.session_state.logged_in = True
                st.session_state.role = "public"
                st.rerun()
        else:
            identifier = st.text_input("Username/Country")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if user_type == "Admin" and password == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.role = "admin"
                    st.rerun()
                elif user_type == "MNC" and identifier in st.session_state.mnc_clients:
                    if st.session_state.mnc_clients[identifier]["password"] == password and st.session_state.mnc_clients[identifier]["active"]:
                        st.session_state.logged_in = True
                        st.session_state.role = "mnc"
                        st.session_state.client = identifier
                        st.rerun()
                elif user_type == "Global Agency" and identifier in st.session_state.agencies:
                    if st.session_state.agencies[identifier]["password"] == password and st.session_state.agencies[identifier]["active"]:
                        st.session_state.logged_in = True
                        st.session_state.role = "agency"
                        st.session_state.client = identifier
                        st.rerun()
                st.error("❌ Invalid")

def logout():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.client = None
        st.rerun()

# ==========================================
# PUBLIC
# ==========================================
def public_dashboard():
    st.header("🌍 Report Cybercrime")
    with st.form("public_report"):
        name = st.text_input("Your Name")
        complaint = st.text_area("Describe (Blackmail/Hack)")
        country = st.selectbox("Country", list(st.session_state.agencies.keys()) + ["Other"])
        if st.form_submit_button("🚔 Submit"):
            if complaint:
                st.session_state.cyber_alerts.append({
                    "id": len(st.session_state.cyber_alerts)+1,
                    "text": complaint,
                    "country": country,
                    "status": "Pending",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_all()
                st.success("✅ Report Submitted!")

# ==========================================
# ADMIN
# ==========================================
def admin_dashboard():
    st.header("👑 Super Admin Panel")
    tab1, tab2, tab3, tab4 = st.tabs(["🏭 Factories", "🏢 MNCs", "🌍 Agencies", "🚨 Reports"])

    with tab1:
        st.subheader("Manage Factories")
        st.dataframe(pd.DataFrame(st.session_state.factories), use_container_width=True)
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Factory Name")
            new_client = st.selectbox("Assign to", list(st.session_state.mnc_clients.keys()))
            new_status = st.selectbox("Status", ["Green", "Yellow", "Red"])
            if st.button("Add Factory"):
                new_id = max([f["id"] for f in st.session_state.factories]) + 1 if st.session_state.factories else 1
                st.session_state.factories.append({"id": new_id, "name": new_name, "status": new_status, "risk": "Low" if new_status=="Green" else "Medium" if new_status=="Yellow" else "High", "client": new_client})
                save_all()
                st.rerun()
        with col2:
            delete_id = st.number_input("Delete ID", min_value=1, step=1)
            if st.button("Delete Factory"):
                st.session_state.factories = [f for f in st.session_state.factories if f["id"] != delete_id]
                save_all()
                st.rerun()

    with tab2:
        st.subheader("MNCs")
        for name, data in st.session_state.mnc_clients.items():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1: st.write(f"**{name}**")
            with col2:
                new_pass = st.text_input(f"Pass", value=data["password"], key=f"pass_{name}")
                if new_pass != data["password"]: st.session_state.mnc_clients[name]["password"] = new_pass; save_all()
            with col3:
                active = st.checkbox("Active", value=data["active"], key=f"act_{name}")
                if active != data["active"]: st.session_state.mnc_clients[name]["active"] = active; save_all(); st.rerun()
        new_mnc = st.text_input("New MNC"); new_pass = st.text_input("Set Password")
        if st.button("Add MNC"): st.session_state.mnc_clients[new_mnc] = {"password": new_pass, "active": True}; save_all(); st.rerun()

    with tab3:
        st.subheader("Agencies")
        for name, data in st.session_state.agencies.items():
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1: st.write(f"**{name}**")
            with col2:
                new_pass = st.text_input(f"Pass", value=data["password"], key=f"ag_pass_{name}")
                if new_pass != data["password"]: st.session_state.agencies[name]["password"] = new_pass; save_all()
            with col3:
                hl = st.text_input("Helpline", value=data.get("helpline", ""), key=f"hl_{name}")
                if hl != data.get("helpline", ""): st.session_state.agencies[name]["helpline"] = hl; save_all()
            with col4:
                active = st.checkbox("Active", value=data["active"], key=f"ag_act_{name}")
                if active != data["active"]: st.session_state.agencies[name]["active"] = active; save_all(); st.rerun()
        with st.form("manual_crime"):
            agency = st.selectbox("Target Agency", list(st.session_state.agencies.keys()))
            crime = st.text_area("Crime Details")
            if st.form_submit_button("Add Crime"):
                st.session_state.cyber_alerts.append({"id": len(st.session_state.cyber_alerts)+1, "text": f"[MANUAL] {crime}", "country": agency, "status": "Pending", "time": datetime.now().strftime("%Y-%m-%d %H:%M")})
                save_all(); st.success("Added!")
        new_ag = st.text_input("New Country"); new_ag_pass = st.text_input("Password"); new_ag_hl = st.text_input("Helpline")
        if st.button("Add Agency"): st.session_state.agencies[new_ag] = {"password": new_ag_pass, "helpline": new_ag_hl, "active": True}; save_all(); st.rerun()

    with tab4:
        st.subheader("Reports (Admin Only)")
        df = pd.DataFrame(st.session_state.cyber_alerts)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            for i, alert in enumerate(st.session_state.cyber_alerts):
                if st.button(f"✅ Resolve #{alert['id']}", key=f"res_{i}"):
                    st.session_state.cyber_alerts.pop(i)
                    save_all()
                    st.rerun()
        else: st.success("✅ No reports.")

def mnc_dashboard(client):
    st.header(f"🏢 {client}")
    df = pd.DataFrame([f for f in st.session_state.factories if f["client"] == client])
    st.dataframe(df)

def agency_dashboard(agency):
    st.header(f"🛡️ {agency}")
    pending = [a for a in st.session_state.cyber_alerts if a["country"] == agency and a["status"] == "Pending"]
    if pending: st.dataframe(pd.DataFrame(pending))
    else: st.success("✅ No cases.")

# ==========================================
# ROUTER
# ==========================================
if not st.session_state.logged_in:
    login_form()
else:
    logout()
    if st.session_state.role == "public": public_dashboard()
    elif st.session_state.role == "admin": admin_dashboard()
    elif st.session_state.role == "mnc": mnc_dashboard(st.session_state.client)
    elif st.session_state.role == "agency": agency_dashboard(st.session_state.client)
