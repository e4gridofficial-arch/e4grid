# ==========================================
# 1. LIBRARIES IMPORT (Ye sab tools hain)
# ==========================================
import streamlit as st  # Web app banane ke liye
import pandas as pd      # Data tables ke liye
from datetime import datetime  # Time stamp ke liye
import json              # Data save karne ke liye
import os                # Files check karne ke liye

# ==========================================
# 2. DATA FOLDER BANAO (Agar nahi hai toh)
# ==========================================
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)  # "data" naam ka folder banao

# ==========================================
# 3. FILE HELPERS (Data save/load karne ke functions)
# ==========================================
def load_json(filename, default):
    """File se data utha kar lao, agar file nahi hai toh default value do"""
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(filename, data):
    """Data ko file mein save karo (taake sab devices ko same data dikhe)"""
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ==========================================
# 4. MASTER DATA (Saari information yahan load hoti hai)
# ==========================================

# --- Factories (Sab factories ki list) ---
if "factories" not in st.session_state:
    st.session_state.factories = load_json("factories.json", [
        {"id": 1, "name": "Saga Sports", "status": "Green", "risk": "Low", "client": "Nike"},
        {"id": 2, "name": "Forward Sports", "status": "Green", "risk": "Low", "client": "Nike"},
        {"id": 3, "name": "Phoenix Sports", "status": "Red", "risk": "High", "client": "Adidas"},
    ])

# --- MNC Clients (Nike, Adidas ke passwords) ---
if "mnc_clients" not in st.session_state:
    st.session_state.mnc_clients = load_json("mnc_clients.json", {
        "Nike": {"password": "Nike@2026", "active": True},
        "Adidas": {"password": "Adidas@2026", "active": True}
    })

# --- Global Agencies (Pakistan, USA jaise countries) ---
if "agencies" not in st.session_state:
    st.session_state.agencies = load_json("agencies.json", {
        "Pakistan": {"password": "Pak@1799", "helpline": "1799", "active": True},
        "USA": {"password": "FBI@911", "helpline": "911", "active": True}
    })

# --- Cyber Alerts (Public aur manual reports yahan store hoti hain) ---
if "cyber_alerts" not in st.session_state:
    st.session_state.cyber_alerts = load_json("alerts.json", [])

# --- Admin Password (Isko badalna hai toh yahan change karo) ---
ADMIN_PASSWORD = "esha4t4boss"

# ==========================================
# 5. SAVE ALL FUNCTION (Har change ke baad yeh call hota hai)
# ==========================================
def save_all():
    """Saare data ko files mein save kardo (taake sab devices ko same data dikhe)"""
    save_json("factories.json", st.session_state.factories)
    save_json("mnc_clients.json", st.session_state.mnc_clients)
    save_json("agencies.json", st.session_state.agencies)
    save_json("alerts.json", st.session_state.cyber_alerts)

# ==========================================
# 6. UI SETUP (Webpage ka title aur layout)
# ==========================================
st.set_page_config(page_title="E4GRID - Global Shield", layout="wide")
st.title("⚡ E4GRID")
st.caption("Global Industrial Immune System | Owner: Esha")

# --- Session State (Login info yahan store hoti hai) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "client" not in st.session_state:
    st.session_state.client = None

# ==========================================
# 7. LOGIN FORM (Sidebar mein dikhega)
# ==========================================
def login_form():
    with st.sidebar:
        st.header("🔐 Login")
        user_type = st.selectbox("I am a...", ["Public (Free)", "MNC", "Global Agency", "Admin"])
        
        # --- Public (Free) - Koi password nahi ---
        if user_type == "Public (Free)":
            if st.button("Enter as Public"):
                st.session_state.logged_in = True
                st.session_state.role = "public"
                st.rerun()
        
        # --- Baki sab ke liye password maangega ---
        else:
            identifier = st.text_input("Username/Country")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                # Admin Login
                if user_type == "Admin" and password == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.role = "admin"
                    st.rerun()
                
                # MNC Login (Nike/Adidas)
                elif user_type == "MNC" and identifier in st.session_state.mnc_clients:
                    if st.session_state.mnc_clients[identifier]["password"] == password and st.session_state.mnc_clients[identifier]["active"]:
                        st.session_state.logged_in = True
                        st.session_state.role = "mnc"
                        st.session_state.client = identifier
                        st.rerun()
                
                # Agency Login (Pakistan/USA Police)
                elif user_type == "Global Agency" and identifier in st.session_state.agencies:
                    if st.session_state.agencies[identifier]["password"] == password and st.session_state.agencies[identifier]["active"]:
                        st.session_state.logged_in = True
                        st.session_state.role = "agency"
                        st.session_state.client = identifier
                        st.rerun()
                
                st.error("❌ Invalid Credentials")

# ==========================================
# 8. LOGOUT BUTTON (Sidebar mein)
# ==========================================
def logout():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.client = None
        st.rerun()

# ==========================================
# 9. PUBLIC DASHBOARD (Jo aam logon ko dikhega)
# ==========================================
def public_dashboard():
    st.header("🌍 Report Cybercrime")
    st.info("📢 Agar aap ko blackmail ya hack kiya ja raha hai, toh neche form submit karein. Yeh report E4GRID Admin tak pahunchegi.")
    
    with st.form("public_report"):
        name = st.text_input("Your Name (Optional)")
        complaint = st.text_area("Describe what happened (e.g., Blackmail, Hack, Fraud)")
        country = st.selectbox("Select your country", list(st.session_state.agencies.keys()) + ["Other"])
        
        if st.form_submit_button("🚔 Submit Report"):
            if complaint:
                # Naya alert banayein
                new_alert = {
                    "id": len(st.session_state.cyber_alerts) + 1,
                    "text": complaint,
                    "country": country,
                    "status": "Pending",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.cyber_alerts.append(new_alert)
                save_all()  # File mein save karo (taake Admin ko dikhe)
                st.success("✅ Report Submitted! Admin will review it shortly.")
            else:
                st.error("❌ Please describe the issue.")

    # --- 🔒 PUBLIC REPORTS YAHAN NAHI DIKHEIN GI (Main ne hata di hai) ---
    # Public ko sirf form dikhega, reports nahi dikhengi.

# ==========================================
# 10. ADMIN DASHBOARD (Sirf Aap ko dikhega - 4 Tabs)
# ==========================================
def admin_dashboard():
    st.header("👑 Super Admin Panel (Full Control)")
    st.warning("⚠️ Boss, yahan koi bhi change karoge toh sab ke liye change ho jayega. Save automatically hota hai.")
    
    # --- 4 Tabs banayein ---
    tab1, tab2, tab3, tab4 = st.tabs(["🏭 Factories", "🏢 MNCs", "🌍 Agencies", "🚨 Reports"])

    # ==================== TAB 1: FACTORIES ====================
    with tab1:
        st.subheader("Manage Factories")
        
        # Existing factories dikhao
        st.write("**Existing Factories:**")
        df = pd.DataFrame(st.session_state.factories)
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        
        # Naya factory add karo
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("➕ Add New Factory")
            new_name = st.text_input("Factory Name")
            new_client = st.selectbox("Assign to MNC", list(st.session_state.mnc_clients.keys()))
            new_status = st.selectbox("Status", ["Green", "Yellow", "Red"])
            if st.button("Add Factory"):
                if new_name:
                    new_id = max([f["id"] for f in st.session_state.factories]) + 1 if st.session_state.factories else 1
                    st.session_state.factories.append({
                        "id": new_id,
                        "name": new_name,
                        "status": new_status,
                        "risk": "Low" if new_status == "Green" else "Medium" if new_status == "Yellow" else "High",
                        "client": new_client
                    })
                    save_all()
                    st.success("✅ Factory added!")
                    st.rerun()
                else:
                    st.error("❌ Please enter a name.")
        
        with col2:
            st.subheader("🗑️ Delete Factory")
            delete_id = st.number_input("Enter Factory ID to Delete", min_value=1, step=1)
            if st.button("Delete Factory"):
                st.session_state.factories = [f for f in st.session_state.factories if f["id"] != delete_id]
                save_all()
                st.success("✅ Factory deleted!")
                st.rerun()

    # ==================== TAB 2: MNCs ====================
    with tab2:
        st.subheader("Manage MNCs (Nike/Adidas)")
        
        # Har MNC ka password aur status
        for name, data in st.session_state.mnc_clients.items():
            st.divider()
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**{name}**")
            with col2:
                new_pass = st.text_input(f"New Password for {name}", value=data["password"], key=f"pass_{name}")
                if new_pass != data["password"]:
                    st.session_state.mnc_clients[name]["password"] = new_pass
                    save_all()
                    st.success("✅ Password updated!")
            with col3:
                active = st.checkbox("Active", value=data["active"], key=f"act_{name}")
                if active != data["active"]:
                    st.session_state.mnc_clients[name]["active"] = active
                    save_all()
                    st.rerun()
        
        st.divider()
        
        # Naya MNC add karo
        st.subheader("➕ Add New MNC")
        new_mnc = st.text_input("New MNC Name")
        new_mnc_pass = st.text_input("Set Password")
        if st.button("Add MNC"):
            if new_mnc and new_mnc_pass:
                st.session_state.mnc_clients[new_mnc] = {"password": new_mnc_pass, "active": True}
                save_all()
                st.success("✅ MNC added!")
                st.rerun()
            else:
                st.error("❌ Please enter both name and password.")

    # ==================== TAB 3: AGENCIES ====================
    with tab3:
        st.subheader("Manage Global Agencies (Police/FIA)")
        
        # Har agency ka password aur status
        for name, data in st.session_state.agencies.items():
            st.divider()
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                st.write(f"**{name}**")
            with col2:
                new_pass = st.text_input(f"Pass for {name}", value=data["password"], key=f"ag_pass_{name}")
                if new_pass != data["password"]:
                    st.session_state.agencies[name]["password"] = new_pass
                    save_all()
                    st.success("✅ Password updated!")
            with col3:
                helpline = st.text_input(f"Helpline", value=data.get("helpline", ""), key=f"hl_{name}")
                if helpline != data.get("helpline", ""):
                    st.session_state.agencies[name]["helpline"] = helpline
                    save_all()
            with col4:
                active = st.checkbox("Active", value=data["active"], key=f"ag_act_{name}")
                if active != data["active"]:
                    st.session_state.agencies[name]["active"] = active
                    save_all()
                    st.rerun()
        
        st.divider()
        
        # Manual Crime Report (Agency ke liye)
        st.subheader("📝 Manually Add Crime Report to Agency")
        with st.form("manual_crime"):
            agency_select = st.selectbox("Target Agency", list(st.session_state.agencies.keys()))
            crime_text = st.text_area("Crime Details (e.g., Blackmail case in Lahore)")
            if st.form_submit_button("Add to Agency"):
                if crime_text:
                    st.session_state.cyber_alerts.append({
                        "id": len(st.session_state.cyber_alerts) + 1,
                        "text": f"[MANUAL] {crime_text}",
                        "country": agency_select,
                        "status": "Pending",
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    save_all()
                    st.success("✅ Crime added to agency dashboard!")
                else:
                    st.error("❌ Please enter crime details.")
        
        st.divider()
        
        # Naya Agency add karo
        st.subheader("➕ Add New Agency")
        new_ag = st.text_input("Country Name")
        new_ag_pass = st.text_input("Password")
        new_ag_hl = st.text_input("Helpline")
        if st.button("Add Agency"):
            if new_ag and new_ag_pass:
                st.session_state.agencies[new_ag] = {"password": new_ag_pass, "helpline": new_ag_hl, "active": True}
                save_all()
                st.success("✅ Agency added!")
                st.rerun()
            else:
                st.error("❌ Please enter country and password.")

    # ==================== TAB 4: REPORTS ====================
    with tab4:
        st.subheader("Global Cyber Reports (Admin Only)")
        st.info("📢 Yahan saari public reports aur manual reports aayengi. Aap unhe Resolve kar sakti hain.")
        
        alerts_df = pd.DataFrame(st.session_state.cyber_alerts)
        if not alerts_df.empty:
            st.dataframe(alerts_df, use_container_width=True)
            st.divider()
            st.subheader("✅ Resolve Reports")
            for i, alert in enumerate(st.session_state.cyber_alerts):
                if st.button(f"✅ Resolve #{alert['id']} - {alert['country']}", key=f"res_{i}"):
                    st.session_state.cyber_alerts.pop(i)
                    save_all()
                    st.rerun()
        else:
            st.success("✅ No pending reports. System secure.")

# ==========================================
# 11. MNC DASHBOARD (Nike/Adidas ko dikhega)
# ==========================================
def mnc_dashboard(client):
    st.header(f"🏢 {client} - Compliance Dashboard")
    st.write(f"Welcome {client}! Yeh rahi aap ki monitored factories:")
    
    df = pd.DataFrame([f for f in st.session_state.factories if f["client"] == client])
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No factories assigned yet.")

# ==========================================
# 12. AGENCY DASHBOARD (Police/FIA ko dikhega)
# ==========================================
def agency_dashboard(agency):
    st.header(f"🛡️ {agency} - Cyber Crime Dashboard")
    st.write(f"Welcome {agency}! Yeh rahi pending cases for your country:")
    
    pending = [a for a in st.session_state.cyber_alerts if a["country"] == agency and a["status"] == "Pending"]
    if pending:
        df = pd.DataFrame(pending)
        st.dataframe(df, use_container_width=True)
    else:
        st.success("✅ No pending cases for your country.")

# ==========================================
# 13. MAIN ROUTER (App ka mughayya)
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
