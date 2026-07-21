import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. PAGE CONFIG
# ==========================================
st.set_page_config(page_title="E4GRID - Global Shield", layout="wide")
st.title("⚡ E4GRID")
st.caption("Pakistan's Industrial Immune System | Global Cyber & Compliance Grid")

# ==========================================
# 2. SESSION STATE (Login)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "client" not in st.session_state:
    st.session_state.client = None

# ==========================================
# 3. DATA (Factories)
# ==========================================
factories = pd.DataFrame([
    {"id": 1, "name": "Saga Sports (Sialkot)", "status": "Green", "risk": "Low", "client": "Nike"},
    {"id": 2, "name": "Forward Sports (Sialkot)", "status": "Green", "risk": "Low", "client": "Nike"},
    {"id": 3, "name": "Phoenix Sports (Sialkot)", "status": "Red", "risk": "High", "client": "Adidas"},
    {"id": 4, "name": "Butt Sports (Sialkot)", "status": "Yellow", "risk": "Medium", "client": "Adidas"},
    {"id": 5, "name": "Al-Karam Textile (FSD)", "status": "Yellow", "risk": "Medium", "client": "Nike"},
    {"id": 6, "name": "Gul Ahmed (Karachi)", "status": "Green", "risk": "Low", "client": "Puma"},
])

# MNC Clients (Passwords)
mnc_clients = {
    "Nike": "Nike@2026",
    "Adidas": "Adidas@2026",
    "Puma": "Puma@2026"
}

# Global Agencies
global_agencies = {
    "Pakistan": {"password": "Pak@1799", "helpline": "1799"},
    "USA": {"password": "FBI@911", "helpline": "911"},
    "UK": {"password": "UK@999", "helpline": "999"},
    "UAE": {"password": "Dubai@901", "helpline": "901"}
}

# Cyber Alerts
if "cyber_alerts" not in st.session_state:
    st.session_state.cyber_alerts = []

# Admin Password
ADMIN_PASSWORD = "esha4t4boss"

# ==========================================
# 4. LOGIN FORM
# ==========================================
def login_form():
    with st.sidebar:
        st.header("🔐 Login")
        user_type = st.selectbox("I am a...", ["Public (Free)", "MNC (Nike/Adidas)", "Global Agency (FIA/Police)", "Admin (Owner)"])
        
        if user_type == "Public (Free)":
            if st.button("Enter as Public"):
                st.session_state.logged_in = True
                st.session_state.role = "public"
                st.rerun()
        else:
            identifier = st.text_input("Username/Country")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if user_type == "Admin (Owner)" and password == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.role = "admin"
                    st.rerun()
                elif user_type == "MNC (Nike/Adidas)" and identifier in mnc_clients and mnc_clients[identifier] == password:
                    st.session_state.logged_in = True
                    st.session_state.role = "mnc"
                    st.session_state.client = identifier
                    st.rerun()
                elif user_type == "Global Agency (FIA/Police)" and identifier in global_agencies and global_agencies[identifier]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.role = "agency"
                    st.session_state.client = identifier
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials!")

# ==========================================
# 5. LOGOUT
# ==========================================
def logout():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.client = None
        st.rerun()

# ==========================================
# 6. DASHBOARDS (Roles)
# ==========================================

def public_dashboard():
    st.header("🌍 Public Portal - Report Cybercrime")
    with st.form("public_report"):
        name = st.text_input("Your Name (Optional)")
        complaint = st.text_area("Describe what happened (e.g., Blackmail, Hack)")
        country = st.selectbox("Select your country", list(global_agencies.keys()) + ["Other"])
        submitted = st.form_submit_button("🚔 Submit Report")
        if submitted and complaint:
            st.session_state.cyber_alerts.append({
                "id": len(st.session_state.cyber_alerts)+1,
                "text": complaint,
                "country": country,
                "status": "Pending",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.success("✅ Report submitted! Authorities have been alerted (or Admin will forward).")
    st.divider()
    st.subheader("Recent Public Reports")
    if st.session_state.cyber_alerts:
        df = pd.DataFrame(st.session_state.cyber_alerts)
        st.dataframe(df[["id", "text", "country", "status", "time"]])
    else:
        st.info("No reports yet. System secure.")

def admin_dashboard():
    st.header("⚡ Admin Panel (Boss Only)")
    st.subheader("🏭 Factories")
    st.dataframe(factories)
    st.subheader("📢 MNCs & Agencies")
    st.write("MNCs:", mnc_clients)
    st.write("Agencies:", global_agencies)
    st.subheader("🚨 Pending Cyber Reports")
    if st.session_state.cyber_alerts:
        df = pd.DataFrame(st.session_state.cyber_alerts)
        st.dataframe(df)
        for i, alert in enumerate(st.session_state.cyber_alerts):
            if st.button(f"✅ Resolve #{alert['id']}", key=f"resolve_{i}"):
                st.session_state.cyber_alerts.pop(i)
                st.rerun()
    else:
        st.info("No pending reports.")

def mnc_dashboard(client):
    st.header(f"🏢 {client} - Compliance Dashboard")
    df = factories[factories["client"] == client]
    if df.empty:
        st.warning("No factories assigned.")
    else:
        st.dataframe(df)

def agency_dashboard(agency):
    st.header(f"🛡️ {agency} - Cyber Crime Dashboard")
    pending = [a for a in st.session_state.cyber_alerts if a["country"] == agency and a["status"] == "Pending"]
    if pending:
        for a in pending:
            st.warning(f"🚨 {a['text']} (ID: {a['id']}, Time: {a['time']})")
    else:
        st.success("✅ No pending cases.")

# ==========================================
# 7. MAIN APP FLOW
# ==========================================

if not st.session_state.logged_in:
    login_form()
else:
    logout()
    if st.session_state.role == "public":
        public_dashboard()
    elif st.session_state.role == "admin":
        admin_dashboard()
    elif st.session_state.role == "mnc":
        mnc_dashboard(st.session_state.client)
    elif st.session_state.role == "agency":
        agency_dashboard(st.session_state.client)
