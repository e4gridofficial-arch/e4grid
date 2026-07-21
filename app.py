import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# ==========================================
# 1. FILE HELPERS (Data save/load)
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
# 2. MASTER DATA (Load from files)
# ==========================================

# Factories
if "factories_df" not in st.session_state:
    factories_data = load_json("factories.json", [
        {"id": 1, "name": "Saga Sports", "status": "Green", "risk": "Low", "client": "Nike"},
        {"id": 2, "name": "Forward Sports", "status": "Green", "risk": "Low", "client": "Nike"},
        {"id": 3, "name": "Phoenix Sports", "status": "Red", "risk": "High", "client": "Adidas"},
    ])
    st.session_state.factories = factories_data

# MNC Clients
if "mnc_clients" not in st.session_state:
    st.session_state.mnc_clients = load_json("mnc_clients.json", {
        "Nike": {"password": "Nike@2026", "active": True},
        "Adidas": {"password": "Adidas@2026", "active": True}
    })

# Agencies
if "agencies" not in st.session_state:
    st.session_state.agencies = load_json("agencies.json", {
        "Pakistan": {"password": "Pak@1799", "helpline": "1799", "active": True},
        "USA": {"password": "FBI@911", "helpline": "911", "active": True}
    })

# Cyber Alerts
if "cyber_alerts" not in st.session_state:
    st.session_state.cyber_alerts = load_json("alerts.json", [])

# Admin Pass (fixed)
ADMIN_PASSWORD = "esha4t4boss"

# ==========================================
# 3. SAVE FUNCTIONS (Called on every change)
# ==========================================
def save_all():
    save_json("factories.json", st.session_state.factories)
    save_json("mnc_clients.json", st.session_state.mnc_clients)
    save_json("agencies.json", st.session_state.agencies)
    save_json("alerts.json", st.session_state.cyber_alerts)

# ==========================================
# 4. UI SETUP
# ==========================================
st.set_page_config(page_title="E4GRID - Global Shield", layout="wide")
st.title("⚡ E4GRID")
st.caption("Global Industrial Immune System | Owner: Esha")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "client" not in st.session_state:
    st.session_state.client = None

# ==========================================
# 5. LOGIN
# ==========================================
def login_form():
    with st.sidebar:
        st.header("🔐 Login")
        user_type = st.selectbox("I am a...", ["Public (Free)", "MNC", "Global Agency", "Admin"])
        if user_type == "Public (Free)":
            if st.button("Enter as Public"):
                st.session_state.logged_in = True; st.session_state.role = "public"; st.rerun()
        else:
            identifier = st.text_input("Username/Country")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if user_type == "Admin" and password == ADMIN_PASSWORD:
                    st.session_state.logged_in = True; st.session_state.role = "admin"; st.rerun()
                elif user_type == "MNC" and identifier in st.session_state.mnc_clients:
                    if st.session_state.mnc_clients[identifier]["password"] == password and st.session_state.mnc_clients[identifier]["active"]:
                        st.session_state.logged_in = True; st.session_state.role = "mnc"; st.session_state.client = identifier; st.rerun()
                elif user_type == "Global Agency" and identifier in st.session_state.agencies:
                    if st.session_state.agencies[identifier]["password"] == password and st.session_state.agencies[identifier]["active"]:
                        st.session_state.logged_in = True; st.session_state.role = "agency"; st.session_state.client = identifier; st.rerun()
                st.error("❌ Invalid")

def logout():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False; st.session_state.role = None; st.session_state.client = None; st.rerun()

# ==========================================
# 6. DASHBOARDS
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
                st.success("✅ Report Submitted! Admin will see it.")
    st.dataframe(pd.DataFrame(st.session_state.cyber_alerts) if st.session_state.cyber_alerts else pd.DataFrame())

# ==========================================
# 7. ADMIN PANEL (WITH FULL EDITING)
# ==========================================
def admin_dashboard():
    st.header("👑 Super Admin Panel (Full Control)")
    st.warning("⚠️ Boss, yahan koi bhi change karoge toh sab ke liye change ho jayega. Save automatically hota hai.")
    
    # --- Tab Structure ---
    tab1, tab2, tab3, tab4 = st.tabs(["🏭 Factories", "🏢 MNCs", "🌍 Agencies", "🚨 Reports"])

    # TAB 1: FACTORIES (Problem #2 & #5)
    with tab1:
        st.subheader("Manage Factories")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Existing Factories:")
            df = pd.DataFrame(st.session_state.factories)
            st.dataframe(df, use_container_width=True)
        
        with col2:
            st.subheader("➕ Add New")
            new_name = st.text_input("Factory Name")
            new_client = st.selectbox("Assign to MNC", list(st.session_state.mnc_clients.keys()))
            new_status = st.selectbox("Status", ["Green", "Yellow", "Red"])
            if st.button("Add Factory"):
                new_id = max([f["id"] for f in st.session_state.factories]) + 1 if st.session_state.factories else 1
                st.session_state.factories.append({
                    "id": new_id,
                    "name": new_name,
                    "status": new_status,
                    "risk": "Low" if new_status=="Green" else "Medium" if new_status=="Yellow" else "High",
                    "client": new_client
                })
                save_all()
                st.rerun()
        
        st.divider()
        st.subheader("🗑️ Delete Factory")
        delete_id = st.number_input("Enter Factory ID to Delete", min_value=1, step=1)
        if st.button("Delete Factory"):
            st.session_state.factories = [f for f in st.session_state.factories if f["id"] != delete_id]
            save_all()
            st.rerun()

    # TAB 2: MNCs (Problem #4 - Passwords & Add)
    with tab2:
        st.subheader("Manage MNCs")
        for name, data in st.session_state.mnc_clients.items():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**{name}**")
            with col2:
                # Password Change
                new_pass = st.text_input(f"New pass for {name}", value=data["password"], key=f"pass_{name}")
                if new_pass != data["password"]:
                    st.session_state.mnc_clients[name]["password"] = new_pass
                    save_all()
                    st.success("Password updated!")
            with col3:
                # Toggle Active
                active = st.checkbox("Active", value=data["active"], key=f"act_{name}")
                if active != data["active"]:
                    st.session_state.mnc_clients[name]["active"] = active
                    save_all()
                    st.rerun()
        
        st.divider()
        st.subheader("➕ Add New MNC")
        new_mnc = st.text_input("New MNC Name")
        new_mnc_pass = st.text_input("Set Password")
        if st.button("Add MNC"):
            st.session_state.mnc_clients[new_mnc] = {"password": new_mnc_pass, "active": True}
            save_all()
            st.rerun()

    # TAB 3: Agencies (Problem #3 - Add Crimes & Add Agency)
    with tab3:
        st.subheader("Manage Agencies")
        for name, data in st.session_state.agencies.items():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**{name}**")
            with col2:
                new_pass = st.text_input(f"Pass for {name}", value=data["password"], key=f"ag_pass_{name}")
                if new_pass != data["password"]:
                    st.session_state.agencies[name]["password"] = new_pass
                    save_all()
                    st.success("Updated!")
            with col3:
                active = st.checkbox("Active", value=data["active"], key=f"ag_act_{name}")
                if active != data["active"]:
                    st.session_state.agencies[name]["active"] = active
                    save_all()
                    st.rerun()
        
        st.divider()
        # Manually add crime to agency (Problem #3)
        st.subheader("📝 Add Crime Report to Agency (Manual)")
        with st.form("manual_crime"):
            agency_select = st.selectbox("Target Agency", list(st.session_state.agencies.keys()))
            crime_text = st.text_area("Crime Details")
            if st.form_submit_button("Add to Agency"):
                st.session_state.cyber_alerts.append({
                    "id": len(st.session_state.cyber_alerts)+1,
                    "text": f"[MANUAL] {crime_text}",
                    "country": agency_select,
                    "status": "Pending",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_all()
                st.success("Crime added to agency dashboard!")
        
        st.subheader("➕ Add New Agency")
        new_ag = st.text_input("Country Name")
        new_ag_pass = st.text_input("Password")
        new_ag_hl = st.text_input("Helpline")
        if st.button("Add Agency"):
            st.session_state.agencies[new_ag] = {"password": new_ag_pass, "helpline": new_ag_hl, "active": True}
            save_all()
            st.rerun()

    # TAB 4: Reports (Problem #1 - Public reports ab yahan dikhengi)
    with tab4:
        st.subheader("Global Cyber Reports")
        alerts_df = pd.DataFrame(st.session_state.cyber_alerts)
        if not alerts_df.empty:
            st.dataframe(alerts_df, use_container_width=True)
            for i, alert in enumerate(st.session_state.cyber_alerts):
                if st.button(f"✅ Resolve #{alert['id']}", key=f"res_{i}"):
                    st.session_state.cyber_alerts.pop(i)
                    save_all()
                    st.rerun()
        else:
            st.success("✅ No pending reports.")

def mnc_dashboard(client):
    st.header(f"🏢 {client} Dashboard")
    df = pd.DataFrame([f for f in st.session_state.factories if f["client"] == client])
    st.dataframe(df)

def agency_dashboard(agency):
    st.header(f"🛡️ {agency} Dashboard")
    pending = [a for a in st.session_state.cyber_alerts if a["country"] == agency and a["status"] == "Pending"]
    if pending:
        st.warning("Pending Cases:")
        st.dataframe(pd.DataFrame(pending))
    else:
        st.success("✅ No pending cases.")

# ==========================================
# 8. ROUTER
# ==========================================
if not st.session_state.logged_in:
    login_form()
else:
    logout()
    if st.session_state.role == "public": public_dashboard()
    elif st.session_state.role == "admin": admin_dashboard()
    elif st.session_state.role == "mnc": mnc_dashboard(st.session_state.client)
    elif st.session_state.role == "agency": agency_dashboard(st.session_state.client)